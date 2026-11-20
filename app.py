"""PactLens.ai — scanner and review screens, using the existing Gemini backend."""

import logging
from time import perf_counter

import streamlit as st
from pypdf.errors import PyPdfError

from backend.analyzer import MissingGeminiKeyError, analyze_contract
from backend.pdf_processor import extract_text_from_pdf
from ui.results import render_results
from ui.review_styles import apply_review_styles
from ui.scanner import render_scanner
from ui.styles import apply_styles, render_header

LOGGER = logging.getLogger(__name__)
GEMINI_INPUT_LIMIT = 28_000  # Mirrors backend/analyzer.py; not a document-length guarantee.

st.set_page_config(
    page_title="PactLens.ai | Contract Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def clear_review():
    """Go back to the scanner and clear per-report UI state."""
    st.session_state.pop("contract_review", None)
    st.session_state.pop("rf_severity_filter", None)


def render_progress(step: int):
    scanner_class = "rf-flow-active" if step == 1 else "rf-flow-complete"
    review_class = "rf-flow-active" if step == 2 else ""
    st.html(
        f"""
        <nav class="rf-flow" aria-label="Contract review progress">
          <span class="rf-flow-step {scanner_class}">
            <span class="rf-flow-number">1</span> Upload contract
          </span>
          <span class="rf-flow-line" aria-hidden="true"></span>
          <span class="rf-flow-step {review_class}">
            <span class="rf-flow-number">2</span> Review insights
          </span>
        </nav>
        """
    )


def run_analysis(request):
    """Process the submitted contract once; keep Gemini's existing schema/model."""
    with st.status("Preparing contract review...", expanded=True) as status:
        try:
            uploaded_file = request["file"]
            if uploaded_file is not None:
                started = perf_counter()
                uploaded_file.seek(0)
                contract_text = extract_text_from_pdf(uploaded_file)
                pdf_seconds = perf_counter() - started
                document_name = uploaded_file.name
                LOGGER.info("PDF extraction completed in %.2fs", pdf_seconds)
                st.write("Contract text extracted.")
            else:
                contract_text = request["text"]
                document_name = "Pasted contract"

            if not contract_text or not contract_text.strip():
                status.update(label="No readable text", state="error")
                st.error("No readable contract text found. Try another PDF or paste text.")
                return

            if len(contract_text) > GEMINI_INPUT_LIMIT:
                st.warning(
                    "This contract is longer than the current model input limit. "
                    "The review will cover only the first 28,000 characters "
                    "and must not be treated as a full-document review."
                )

            status.update(label="Reviewing your contract…")
            started = perf_counter()
            result = analyze_contract(
                contract_text=contract_text,
                contract_type=request["contract_type"],
                jurisdiction=request["jurisdiction"],
                role=request["role"],
                review_mode=request["review_mode"],
            )
            analysis_seconds = perf_counter() - started
            LOGGER.info("Gemini analysis completed in %.2fs", analysis_seconds)

            if result is None:
                status.update(label="Review failed", state="error")
                st.error("The AI returned no review. Please try again.")
                return

        except MissingGeminiKeyError as error:
            status.update(label="Review failed", state="error")
            st.error(str(error))
            return
        except PyPdfError:
            status.update(label="Review failed", state="error")
            st.error("Could not read this PDF. Try another PDF or paste the contract text.")
            return
        except RuntimeError as error:
            status.update(label="Review unavailable", state="error")
            if "Gemini is temporarily busy" in str(error):
                st.warning("Contract analysis is temporarily unavailable. Please try again in a moment.")
            else:
                LOGGER.exception("Gemini review failed")
                st.error("Contract analysis failed. Please try again.")
            return
        except Exception:
            status.update(label="Review failed", state="error")
            LOGGER.exception("Contract analysis failed")
            st.error("Contract analysis failed. Please check your input and try again.")
            return

        status.update(label="Analysis complete", state="complete", expanded=False)

    st.session_state["contract_review"] = {
        "analysis": result,
        "document_name": document_name,
        "contract_text": contract_text,
        "partial_review": len(contract_text) > GEMINI_INPUT_LIMIT,
    }
    st.rerun()


def main():
    apply_styles()
    apply_review_styles()
    render_header()

    review = st.session_state.get("contract_review")
    if review is None:
        # SCREEN 1: Scanner — never render the results below the form.
        render_progress(step=1)
        st.html(
            """
            <section class="rf-screen-intro">
              <p class="rf-screen-eyebrow">AI CONTRACT INTELLIGENCE</p>
              <h1>Understand the fine print.</h1>
              <p>Upload your contract to explore the clauses, risks and
                 negotiation opportunities that deserve your attention.</p>
            </section>
            """
        )
        request = render_scanner()
        if request is not None:
            run_analysis(request)
        return

    # SCREEN 2: Dedicated review workspace — hide the scanner entirely.
    render_progress(step=2)
    left, right = st.columns([4, 1], vertical_alignment="center")
    with left:
        st.caption("PACTLENS.AI  /  CONTRACT REVIEW WORKSPACE")
    with right:
        st.button("← New analysis", on_click=clear_review, width="stretch")

    if review.get("partial_review"):
        st.warning(
            "Partial review: Gemini received only the first 28,000 characters. "
            "Important clauses later in the document were not analysed."
        )

    render_results(
        review["analysis"],
        document_name=review["document_name"],
        contract_text=review["contract_text"],
        partial_review=review.get("partial_review", False),
    )


if __name__ == "__main__":
    main()
