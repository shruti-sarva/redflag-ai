
from collections import Counter
import streamlit as st


def as_dict(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value if isinstance(value, dict) else {}


def render_results(analysis, *, document_name: str, contract_text: str):
    data = as_dict(analysis)

    findings = data.get("flags", data.get("red_flags", []))

    findings = [as_dict(f) for f in findings]

    counts = Counter(
        str(f.get("severity", "")).lower()
        for f in findings
    )

    st.header("Contract review")
    st.text(document_name)
    if data.get("verdict_headline"):
        st.write(data["verdict_headline"])

    score_col, high_col, medium_col = st.columns(3)
    score = data.get("risk_score")
    score_col.metric("Risk score", f"{score}/100" if score is not None else "—")
    high_col.metric("High risk", counts["high"])
    medium_col.metric("Medium risk", counts["medium"])

    st.divider()

    document, findings_panel = st.columns(2)
    with document:
        st.subheader("Original contract")
        with st.container(height=480, border=True):
            st.text(contract_text, wrap=True)

    with findings_panel:
        render_findings(findings)


def render_findings(findings):
    st.markdown("### Flagged clauses")

    if not findings:
        st.info(
            "No flagged clauses were returned. "
            "This does not guarantee the contract is safe."
        )

    for index, finding in enumerate(findings):
        title = finding.get(
            "title", f"Finding {index + 1}"
        )
        severity = finding.get(
            "severity", "Unclassified"
        )

        with st.expander(
            f"{title} — {severity}",
            expanded=index == 0,
        ):
            st.markdown("**Original clause**")
            st.info(
                finding.get("exact_quote")
                or finding.get("clause_text")
                or "Clause reference unavailable."
            )

            st.markdown("**Why this matters**")
            st.write(
                finding.get("plain_english", finding.get("explanation", ""))
            )

            suggestion = finding.get(
                "redline_replacement", finding.get("suggested_rewrite", "")
            )

            if suggestion:
                st.markdown("**Suggested revision**")
                st.text_area(
                    "Proposed wording",
                    value=suggestion,
                    height=120,
                    key=f"revision_{index}",
                )
