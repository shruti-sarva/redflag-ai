"""Request a structured Gemini review."""

import os
from typing import Literal

import streamlit as st
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field
from streamlit.errors import StreamlitSecretNotFoundError


class FlaggedClause(BaseModel):
    title: str = Field(description="Short punchy title of the trap")
    severity: Literal["HIGH", "MEDIUM"]
    exact_quote: str = Field(description="Exact verbatim snippet from the contract")
    plain_english: str = Field(description="Clear explanation of why this hurts the signer")
    redline_replacement: str = Field(description="Fair, balanced replacement clause text to propose instead")


class ContractReport(BaseModel):
    risk_score: int = Field(ge=0, le=100, description="0 is completely safe, 100 is predatory")
    verdict_headline: str = Field(description="Punchy 5-8 word summary headline")
    contract_type: str = Field(description="e.g., Residential Lease, Freelance Agreement, Employment Offer")
    green_flags: list[str] = Field(description="1-3 fair or protective terms found in the document")
    flags: list[FlaggedClause]
    polite_email: str = Field(description="Warm, collaborative email asking to amend the flagged clauses")
    firm_email: str = Field(description="Direct, assertive email declining unfair terms before signing")


class MissingGeminiKeyError(ValueError):
    """Gemini credentials have not been configured."""


def analyze_contract(
    contract_text: str,
    contract_type: str,
    jurisdiction: str,
    role: str,
    review_mode: str,
) -> ContractReport:
    review_instructions = {
        "Strict advocate": "Thoroughly flag one-sided terms and risks for the selected party.",
        "Balanced review": "Focus on material risks and propose balanced revisions.",
        "Plain-English review": "Explain the main risks in everyday language.",
    }
    prompt = f"""
    Review this {contract_type} under {jurisdiction} norms from the {role}'s perspective.
    Style instruction: {review_instructions[review_mode]}
    Frame findings as educational risk flags.

    CONTRACT TEXT:
    {contract_text[:28000]}
    """

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except StreamlitSecretNotFoundError:
            pass
    if not api_key:
        raise MissingGeminiKeyError("Set GEMINI_API_KEY in the environment or Streamlit secrets.")

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=ContractReport,
        temperature=0.25,
    )
    http_options = types.HttpOptions(retry_options=types.HttpRetryOptions(attempts=1))
    with genai.Client(api_key=api_key, http_options=http_options) as client:
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash", contents=prompt, config=config
            )
        except errors.APIError as error:
            if error.code in (429, 503):
                raise RuntimeError("Gemini is temporarily busy. Try again shortly.") from error
            raise

    if not response.text:
        raise ValueError("Gemini returned an empty contract review.")
    return ContractReport.model_validate_json(response.text)
