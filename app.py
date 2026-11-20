
import logging

import streamlit as st
from pypdf.errors import PyPdfError

from backend.analyzer import MissingGeminiKeyError, analyze_contract
from backend.pdf_processor import extract_text_from_pdf
from ui.styles import apply_styles, render_header
from ui.scanner import render_scanner
from ui.results import render_results

st.set_page_config(
    page_title="PactLens.ai | Contract Intelligence",
    page_icon="🚩",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize session state
if "analysis" not in st.session_state:
    st.session_state["analysis"] = None

# Render UI
apply_styles()
render_header()

request = render_scanner()

# Process contract submission
if request is not None:
    st.session_state["analysis"] = None

    with st.spinner("Analysing your contract..."):
        try:
            uploaded_file = request["file"]
            if uploaded_file is not None:
                contract_text = extract_text_from_pdf(uploaded_file)
            else:
                contract_text = request["text"]

            if not contract_text or not contract_text.strip():
                st.error("No readable contract text found.")
                st.stop()

            result = analyze_contract(
                contract_text=contract_text,
                contract_type=request["contract_type"],
                jurisdiction=request["jurisdiction"],
                role=request["role"],
                review_mode=request["review_mode"],
            )

            st.session_state["analysis"] = result

        except MissingGeminiKeyError as error:
            st.error(str(error))
        except PyPdfError:
            st.error("Could not read this PDF. Try another PDF or paste the contract text.")
        except Exception:
            logging.exception("Contract analysis failed")
            st.error(
                "Contract analysis failed. "
                "Please check the input and try again."
            )

# Display results
if st.session_state["analysis"] is not None:
    st.divider()
    render_results(st.session_state["analysis"])
