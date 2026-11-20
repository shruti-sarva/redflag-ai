
"""PactLens.ai scanner interface with dynamic contract preview."""

from html import escape
from io import BytesIO
from typing import TypedDict

import streamlit as st


# -----------------------------------------
# CONTRACT TYPES AND ROLES
# -----------------------------------------

ROLE_OPTIONS = {
    "Residential lease": ["Tenant", "Landlord"],
    "Employment agreement": ["Employee", "Employer"],
    "Non-disclosure agreement": [
        "Disclosing party",
        "Receiving party",
    ],
    "Service agreement": [
        "Client",
        "Service provider",
    ],
    "Other": ["First party", "Second party"],
}


# -----------------------------------------
# SAMPLE DOCUMENTS FOR PREVIEW
# -----------------------------------------

class PreviewClause(TypedDict):
    number: str
    heading: str
    text: str
    severity: str
    finding: str


class PreviewDocument(TypedDict):
    title: str
    clauses: list[PreviewClause]


PREVIEW_DOCUMENTS: dict[str, PreviewDocument] = {
    "Residential lease": {
        "title": "Residential Tenancy Agreement",
        "clauses": [
            {
                "number": "01",
                "heading": "Property access",
                "text": (
                    "The landlord may enter the premises "
                    "at any time without prior notice."
                ),
                "severity": "high",
                "finding": "Broad property access rights",
            },
            {
                "number": "02",
                "heading": "Early termination",
                "text": (
                    "The tenant must pay six weeks of rent "
                    "when ending the agreement early."
                ),
                "severity": "medium",
                "finding": "Termination costs need review",
            },
            {
                "number": "03",
                "heading": "Rent payments",
                "text": (
                    "Rent is payable monthly on the "
                    "agreed date."
                ),
                "severity": "normal",
                "finding": "",
            },
        ],
    },

    "Employment agreement": {
        "title": "Employment Agreement",
        "clauses": [
            {
                "number": "01",
                "heading": "Variation of terms",
                "text": (
                    "The employer may change duties "
                    "and remuneration at its sole discretion."
                ),
                "severity": "high",
                "finding": "Unilateral changes to employment terms",
            },
            {
                "number": "02",
                "heading": "Termination",
                "text": (
                    "The employee must provide twelve weeks "
                    "of notice before resignation."
                ),
                "severity": "medium",
                "finding": "Potentially onerous notice requirement",
            },
            {
                "number": "03",
                "heading": "Working hours",
                "text": (
                    "The employee will work the agreed "
                    "ordinary hours."
                ),
                "severity": "normal",
                "finding": "",
            },
        ],
    },

    "Non-disclosure agreement": {
        "title": "Non-Disclosure Agreement",
        "clauses": [
            {
                "number": "01",
                "heading": "Confidential information",
                "text": (
                    "All information shall remain confidential "
                    "indefinitely, including publicly available material."
                ),
                "severity": "high",
                "finding": "Overly broad confidentiality obligations",
            },
            {
                "number": "02",
                "heading": "Liability",
                "text": (
                    "The receiving party accepts unlimited "
                    "liability for any breach."
                ),
                "severity": "medium",
                "finding": "Uncapped liability exposure",
            },
            {
                "number": "03",
                "heading": "Purpose",
                "text": (
                    "Information is shared solely for evaluating "
                    "a potential business relationship."
                ),
                "severity": "normal",
                "finding": "",
            },
        ],
    },

    "Service agreement": {
        "title": "Professional Services Agreement",
        "clauses": [
            {
                "number": "01",
                "heading": "Fee adjustments",
                "text": (
                    "The provider may increase fees at any time "
                    "without obtaining client consent."
                ),
                "severity": "high",
                "finding": "Unilateral fee increases",
            },
            {
                "number": "02",
                "heading": "Indemnification",
                "text": (
                    "The client shall indemnify the provider "
                    "against all losses regardless of cause."
                ),
                "severity": "medium",
                "finding": "One-sided indemnification",
            },
            {
                "number": "03",
                "heading": "Scope of work",
                "text": (
                    "Services will be delivered according to "
                    "the agreed statement of work."
                ),
                "severity": "normal",
                "finding": "",
            },
        ],
    },

    "Other": {
        "title": "Commercial Agreement",
        "clauses": [
            {
                "number": "01",
                "heading": "Amendments",
                "text": (
                    "One party may modify the agreement "
                    "without obtaining the other party's consent."
                ),
                "severity": "high",
                "finding": "Unilateral amendment rights",
            },
            {
                "number": "02",
                "heading": "Liability",
                "text": (
                    "One party assumes all liability "
                    "arising from this agreement."
                ),
                "severity": "medium",
                "finding": "Unequal liability allocation",
            },
            {
                "number": "03",
                "heading": "Effective date",
                "text": (
                    "This agreement takes effect on "
                    "the date of execution."
                ),
                "severity": "normal",
                "finding": "",
            },
        ],
    },
}


# -----------------------------------------
# DYNAMIC DOCUMENT PREVIEW
# -----------------------------------------

def _render_preview(contract_type: str) -> None:
    """
    Display an illustrative contract preview.

    The sample content changes according to the
    selected contract type.

    This does not analyse the uploaded contract.
    """

    document = PREVIEW_DOCUMENTS.get(
        contract_type,
        PREVIEW_DOCUMENTS["Other"],
    )

    clause_html = ""
    finding_html = ""
    flagged_count = 0

    for clause in document["clauses"]:

        number = escape(clause["number"])
        heading = escape(clause["heading"])
        content = escape(clause["text"])
        severity = clause["severity"]

        if severity in ("high", "medium"):

            flagged_count += 1

            content = f"""
                <mark class="rf-doc-mark rf-doc-mark-{severity}">
                    {content}
                </mark>
            """

            finding_html += f"""
                <div class="rf-doc-finding">
                    <span class="rf-doc-dot rf-dot-{severity}"></span>

                    <div>
                        <strong>
                            {escape(clause["finding"])}
                        </strong>

                        <small>
                            Clause {number}
                            · {severity.title()} priority
                        </small>
                    </div>
                </div>
            """

        clause_html += f"""
            <div class="rf-doc-clause">

                <div class="rf-doc-clause-heading">
                    {number}. {heading}
                </div>

                <p>{content}</p>

            </div>
        """

    st.html(
        f"""
        <div class="rf-preview rf-document-preview">

            <header class="rf-preview-header">
                <h3>Contract preview</h3>
                <span>Sample review</span>
            </header>

            <div class="rf-preview-grid">
                <article class="rf-doc-paper">
                    <h4>{escape(document["title"])}</h4>
                    {clause_html}
                </article>

                <aside class="rf-doc-analysis" aria-label="AI risk insights">
                    <h4>AI risk insights</h4>
                    <p class="rf-doc-count">{flagged_count} highlighted clauses</p>
                    {finding_html}
                </aside>
            </div>

            <div class="rf-preview-footnote">
                Illustrative examples only
                · Not a legal assessment
            </div>

        </div>
        """,
    )


# -----------------------------------------
# MAIN SCANNER INTERFACE
# -----------------------------------------

class ScanRequest(TypedDict):
    file: BytesIO | None
    text: str
    contract_type: str
    jurisdiction: str
    role: str
    review_mode: str


def render_scanner() -> ScanRequest | None:

    main, side = st.columns(
        [1, 1.8],
        gap="small",
    )

    with main:

        with st.container(key="rf_scanner"):

            st.html(
                """
                <h2 class="rf-form-title">Analyse your contract</h2>
                """,
            )

            # Keep these selectors outside st.form so
            # changing them updates the interface immediately.

            mode = st.segmented_control(
                "Document input",
                options=[
                    "Upload PDF",
                    "Paste text",
                ],
                default="Upload PDF",
                selection_mode="single",
                key="document_input",
            ) or "Upload PDF"

            contract_type = st.selectbox(
                "Contract type",
                options=list(ROLE_OPTIONS.keys()),
                key="rf_contract_type",
            ) or "Other"

            # Dynamic role options based on contract type.
            available_roles = ROLE_OPTIONS.get(
                contract_type,
                ROLE_OPTIONS["Other"],
            )

            with st.form(
                "rf_contract_form",
                border=False,
            ):

                jurisdiction = st.selectbox(
                    "Jurisdiction",
                    options=[
                        "Victoria, Australia",
                        "New South Wales, Australia",
                    ],
                ) or "Victoria, Australia"

                role = st.selectbox(
                    "Your role",
                    options=available_roles,
                    key=f"rf_role_{contract_type}",
                ) or available_roles[0]

                review_mode = st.selectbox(
                    "Review style",
                    options=[
                        "Balanced review",
                        "Strict advocate",
                        "Plain-English review",
                    ],
                ) or "Balanced review"

                uploaded_file = None
                contract_text = ""

                if mode == "Upload PDF":

                    uploaded_file = st.file_uploader(
                        "Contract PDF",
                        type=["pdf"],
                        help=(
                            "Upload a PDF contract. "
                            "Maximum size follows Streamlit configuration."
                        ),
                    )

                else:

                    contract_text = st.text_area(
                        "Contract text",
                        placeholder=(
                            "Paste the clauses or complete "
                            "contract here..."
                        ),
                        height=155,
                    )

                submitted = st.form_submit_button(
                    "✦ Analyse contract",
                    type="primary",
                    width="stretch",
                )

            st.html(
                """
                <div class="rf-privacy">
                    AI-generated review · Check important findings
                    with a qualified professional
                </div>
                """,
            )

            if submitted:

                if (
                    uploaded_file is None
                    and not contract_text.strip()
                ):
                    st.warning(
                        "Add a PDF or paste contract text to continue."
                    )
                    return None

                return {
                    "file": uploaded_file,
                    "text": contract_text,
                    "contract_type": contract_type,
                    "jurisdiction": jurisdiction,
                    "role": role,
                    "review_mode": review_mode,
                }

    # Dynamic right-hand preview.
    with side:
        _render_preview(contract_type)

    return None
