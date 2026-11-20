
from collections import Counter
import streamlit as st


def as_dict(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value if isinstance(value, dict) else {}


def render_results(analysis):
    data = as_dict(analysis)

    findings = data.get("flags", data.get("red_flags", []))

    findings = [as_dict(f) for f in findings]

    counts = Counter(
        str(f.get("severity", "")).lower()
        for f in findings
    )

    st.markdown("## Contract analysis")

    col1, col2, col3 = st.columns(3)

    col1.metric("High risk", counts["high"])
    col2.metric("Medium risk", counts["medium"])
    col3.metric("Low risk", counts["low"])

    st.divider()

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
