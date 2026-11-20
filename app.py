
import logging
from time import perf_counter

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

def clear_review():
    st.session_state.pop("contract_review", None)


def main():
    apply_styles()
    render_header()

    review = st.session_state.get("contract_review")
    if review is not None:
        st.button("New analysis", on_click=clear_review)
        render_results(
            review["analysis"],
            document_name=review["document_name"],
            contract_text=review["contract_text"],
        )
        timing = f'Gemini analysis: {review["analysis_seconds"]:.1f}s'
        if review["pdf_seconds"] is not None:
            timing += f' · PDF extraction: {review["pdf_seconds"]:.2f}s'
        st.caption(timing)
        return

    request = render_scanner()
    if request is None:
        return

    with st.status("Preparing contract review...", expanded=True) as status:
        try:
            pdf_seconds = None
            uploaded_file = request["file"]
            if uploaded_file is not None:
                started = perf_counter()
                contract_text = extract_text_from_pdf(uploaded_file)
                pdf_seconds = perf_counter() - started
                logging.info("PDF extraction completed in %.2f seconds", pdf_seconds)
                st.write(f"PDF text extracted in {pdf_seconds:.2f}s.")
                document_name = uploaded_file.name
            else:
                contract_text = request["text"]
                document_name = "Pasted contract"

            if not contract_text.strip():
                status.update(label="Contract review failed", state="error")
                st.error("No readable contract text found.")
                return

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
            logging.info("Gemini analysis completed in %.2f seconds", analysis_seconds)
            if result is None:
                status.update(label="Contract review failed", state="error")
                st.error("The analysis returned no results. Please try again.")
                return

        except MissingGeminiKeyError as error:
            status.update(label="Contract review failed", state="error")
            st.error(str(error))
        except PyPdfError:
            status.update(label="Contract review failed", state="error")
            st.error("Could not read this PDF. Try another PDF or paste the contract text.")
        except Exception:
            status.update(label="Contract review failed", state="error")
            logging.exception("Contract analysis failed")
            st.error("Contract analysis failed. Please check the input and try again.")
        else:
            status.update(
                label=f"Analysis completed in {analysis_seconds:.1f}s",
                state="complete",
                expanded=False,
            )
            st.session_state["contract_review"] = {
                "analysis": result,
                "document_name": document_name,
                "contract_text": contract_text,
                "analysis_seconds": analysis_seconds,
                "pdf_seconds": pdf_seconds,
            }
            st.rerun()


main()
