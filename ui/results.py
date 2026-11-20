"""PactLens.ai review workspace for the existing Gemini ContractReport schema."""

from collections import Counter
from hashlib import sha256
from html import escape

import streamlit as st


def as_dict(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value if isinstance(value, dict) else {}


def _highlight_contract(text: str, findings: list[dict]) -> tuple[str, int]:
    """Highlight only verbatim quotes actually present in extracted text."""
    matches = []
    for finding in findings:
        quote = str(finding.get("exact_quote") or "").strip()
        if not quote:
            continue
        start = text.find(quote)
        if start == -1:
            continue
        severity = str(finding.get("severity", "")).lower()
        if severity not in ("high", "medium"):
            continue
        matches.append((start, start + len(quote), severity))

    matches.sort(key=lambda item: (item[0], -item[1]))
    result = []
    offset = 0
    highlighted = 0
    for start, end, severity in matches:
        if start < offset:  # Skip overlapping quotes.
            continue
        result.append(escape(text[offset:start]))
        result.append(
            f'<mark class="rf-real-highlight rf-real-{severity}">'
            f'{escape(text[start:end])}</mark>'
        )
        offset = end
        highlighted += 1
    result.append(escape(text[offset:]))
    return "".join(result), highlighted


def _render_document(text: str, findings: list[dict]):
    highlighted_html, found_count = _highlight_contract(text, findings)
    with st.container(key="rf_contract_panel"):
        st.markdown("#### Original contract")
        st.caption("Highlighted passages match exact quotes in the extracted document.")
        with st.container(height=530, border=False):
            st.html(
                '<article class="rf-real-paper" aria-label="Extracted contract text">'
                f'{highlighted_html}</article>'
            )
        quote_count = sum(bool(str(f.get("exact_quote") or "").strip()) for f in findings)
        if quote_count > found_count:
            st.caption(
                "Some AI quotations could not be matched exactly to extracted text. "
                "Verify those passages against the original PDF."
            )


def _render_findings(findings: list[dict]):
    with st.container(key="rf_findings_panel"):
        st.markdown("#### Flagged clauses")
        severity_filter = st.segmented_control(
            "Show findings",
            options=["All", "High", "Medium"],
            default="All",
            key="rf_severity_filter",
        ) or "All"
        visible = [
            flag for flag in findings
            if severity_filter == "All"
            or str(flag.get("severity", "")).lower() == severity_filter.lower()
        ]
        st.caption(f"{len(visible)} of {len(findings)} findings")
        if not visible:
            st.info("No findings match this filter. This is not a guarantee of safety.")
            return

        for index, flag in enumerate(visible):
            severity = str(flag.get("severity") or "Unclassified").upper()
            title = str(flag.get("title") or "Contract provision")
            with st.expander(f"{severity}  ·  {title}", expanded=index == 0):
                quote = flag.get("exact_quote") or ""
                if quote:
                    st.caption("CLAUSE QUOTED BY THE AI")
                    st.info(quote)
                st.markdown("**Why it matters**")
                st.write(flag.get("plain_english") or "Explanation unavailable.")
                revision = flag.get("redline_replacement") or ""
                if revision:
                    st.markdown("**Suggested alternative wording**")
                    st.code(revision, language=None, wrap_lines=True)
                st.caption("AI-generated suggestion — verify before using.")


def _report_markdown(data: dict, filename: str, findings: list[dict], *, partial_review: bool) -> str:
    lines = [
        "# PactLens.ai — Contract Review",
        "",
        f"Document: {filename}",
        f"AI risk estimate: {data.get('risk_score', 'N/A')}/100",
        f"Summary: {data.get('verdict_headline', '')}",
        "",
    ]
    if partial_review:
        lines.extend(["Partial review: Only the first 28,000 characters were analysed.", ""])
    lines.append("## Flagged clauses")
    for index, flag in enumerate(findings, 1):
        lines.extend([
            "",
            f"### {index}. {flag.get('title', 'Finding')} ({flag.get('severity', 'N/A')})",
            f"Original quote: {flag.get('exact_quote', '')}",
            f"Explanation: {flag.get('plain_english', '')}",
            f"Suggested wording: {flag.get('redline_replacement', '')}",
        ])
    lines.extend([
        "", "## Protective terms",
        *[f"- {term}" for term in (data.get("green_flags") or [])],
        "", "AI-generated educational review, not legal advice.",
    ])
    return "\n".join(lines)


def render_results(analysis, *, document_name: str, contract_text: str, partial_review: bool = False):
    """Display the second-screen workspace without calling Gemini again."""
    data = as_dict(analysis)
    findings = [as_dict(item) for item in data.get("flags", [])]
    counts = Counter(str(f.get("severity", "")).lower() for f in findings)
    score = data.get("risk_score")

    st.html(
        f"""
        <header class="rf-result-hero">
          <p class="rf-screen-eyebrow">ANALYSIS COMPLETE</p>
          <h1>Your contract, explained.</h1>
          <p>{escape(document_name)}</p>
        </header>
        """
    )
    if data.get("verdict_headline"):
        st.markdown(f"**{data['verdict_headline']}**")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("AI risk estimate", f"{score}/100" if score is not None else "—")
    col2.metric("High priority", counts["high"])
    col3.metric("Medium priority", counts["medium"])
    col4.metric("Protective terms", len(data.get("green_flags") or []))
    st.caption(
        "This score is an AI-generated estimate, not a verified measure of legal safety. "
        "Check findings and original contract language carefully."
    )

    review_tab, emails_tab, positives_tab = st.tabs(
        ["Clause review", "Negotiation emails", "Protective terms"]
    )
    with review_tab:
        document_col, findings_col = st.columns([1.15, 1], gap="large")
        with document_col:
            _render_document(contract_text, findings)
        with findings_col:
            _render_findings(findings)

    with emails_tab:
        st.markdown("### Ask for better terms")
        st.caption(
            "These drafts were created during the original Gemini analysis. "
            "Editing them here does not trigger another AI call."
        )
        version = sha256(contract_text.encode("utf-8")).hexdigest()[:12]
        email_a, email_b = st.tabs(["Collaborative", "Firm"])
        for label, tab, field, suffix in (
            ("Collaborative email", email_a, "polite_email", "polite"),
            ("Firm email", email_b, "firm_email", "firm"),
        ):
            with tab:
                key = f"rf_{suffix}_{version}"
                draft = st.text_area(
                    label,
                    value=data.get(field) or "",
                    height=320,
                    key=key,
                )
                st.download_button(
                    "Download email (.txt)",
                    data=draft,
                    file_name=f"pactlens-{suffix}-email.txt",
                    mime="text/plain",
                    key=f"rf_download_{suffix}_{version}",
                )

    with positives_tab:
        st.markdown("### Potentially protective terms")
        protective_terms = data.get("green_flags") or []
        if protective_terms:
            for term in protective_terms:
                st.success(term)
        else:
            st.info("No specific protective terms were returned by the AI.")
        st.markdown("### Export the review")
        st.download_button(
            "Download review (.md)",
            data=_report_markdown(data, document_name, findings, partial_review=partial_review),
            file_name="pactlens-contract-review.md",
            mime="text/markdown",
        )
        st.caption("The exported report includes AI-generated findings, not legal advice.")
