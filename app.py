import os
import json
import streamlit as st
from pypdf import PdfReader
from pydantic import BaseModel, Field
from typing import List, Literal
from google import genai
from google.genai import types

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(
    page_title="RedFlag.ai | Contract & Lease Scanner",
    page_icon="🚩",
    layout="centered",
)

st.markdown("""
<style>
    .score-card {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        color: white;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #374151;
        margin-bottom: 20px;
    }
    .flag-high {
        border-left: 5px solid #ef4444;
        background-color: #fef2f2;
        padding: 14px 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        color: #111827;
    }
    .flag-medium {
        border-left: 5px solid #f59e0b;
        background-color: #fffbeb;
        padding: 14px 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        color: #111827;
    }
    .quote-box {
        font-family: monospace;
        font-size: 0.85rem;
        background: rgba(0,0,0,0.06);
        padding: 8px 10px;
        border-radius: 6px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. STRUCTURED OUTPUT SCHEMA ---
class FlaggedClause(BaseModel):
    title: str = Field(description="Short punchy title of the trap, e.g. 'Unlawful Bond Deduction'")
    severity: Literal["HIGH", "MEDIUM"]
    exact_quote: str = Field(description="Exact verbatim snippet from the contract")
    plain_english: str = Field(description="Sharp, plain-English explanation of why this hurts the signer")
    counter_move: str = Field(description="Actionable rewrite or pushback line")

class ContractReport(BaseModel):
    risk_score: int = Field(ge=0, le=100, description="0 is completely safe, 100 is predatory")
    verdict_headline: str = Field(description="Punchy 5-8 word summary headline")
    contract_type: str = Field(description="e.g., Residential Lease, Freelance Agreement, Employment Contract")
    flags: List[FlaggedClause]
    negotiation_email: str = Field(description="Polite, firm email ready to send to the landlord/client requesting changes")

# --- 3. RATE LIMITING (PROTECT YOUR API WALLET) ---
if "scan_count" not in st.session_state:
    st.session_state.scan_count = 0
if "unlocked_pro" not in st.session_state:
    st.session_state.unlocked_pro = False

MAX_FREE_SCANS = 3

# --- 4. SAMPLE DATA ---
SAMPLES = {
    "Shady Rental Lease": """RESIDENTIAL TENANCY SPECIAL CONDITIONS:
14.2 Tenant agrees to pay a non-refundable $450 'End of Lease Air-Con & Blind Sanitization Fee' deducted automatically from the bond regardless of property condition.
18.5 Landlord or agents may enter the premises at any time without prior written notice to conduct marketing inspections or photography.
22.1 Should Tenant break the lease early, Tenant forfeits the entire security deposit plus 3 months of future rent as liquidated damages.""",
    "Trap Freelance Contract": """INDEPENDENT CONTRACTOR AGREEMENT:
7.1 Intellectual Property: All work product, including pre-existing code libraries, tools, and drafts created before or during this engagement, shall belong exclusively to Client in perpetuity.
9.4 Payment Terms: Invoices are payable Net-90 days AFTER Client receives final payment from its own end-customer.
11.2 Non-Compete: Contractor shall not provide software or AI consulting services to any business globally for 24 months post-termination."""
}

# --- 5. HELPER FUNCTIONS ---
def extract_text_from_pdf(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()

def analyze_contract(text: str, jurisdiction: str) -> ContractReport:
    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY. Set it in your environment or Streamlit secrets.")

    client = genai.Client(api_key=api_key)
    prompt = f"""
    You are an uncompromising consumer, tenant, and freelancer advocate reviewing a contract under {jurisdiction} norms.
    Analyze the contract below for hidden traps, one-sided liabilities, unlawful fees, IP grabs, or predatory clauses.
    Be sharp, practical, and easy to screenshot. Note: frame findings as educational risk flags, not formal legal representation.

    CONTRACT TEXT:
    {text[:25000]}
    """

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ContractReport,
            temperature=0.2,
        ),
    )
    return ContractReport.model_validate_json(response.text)

# --- 6. MAIN UI ---
st.title("🚩 RedFlag.ai")
st.caption("Spot hidden traps in rental leases, job offers & freelance contracts in 10 seconds.")

col1, col2 = st.columns([2, 1])
with col1:
    sample_choice = st.selectbox("Try a sample contract or upload your own:", ["Custom Input", "Shady Rental Lease", "Trap Freelance Contract"])
with col2:
    jurisdiction = st.selectbox("Region / Norms:", ["Australia (VIC/NSW)", "United States", "United Kingdom", "Global / Remote"])

uploaded_pdf = st.file_uploader("Upload Contract PDF (optional)", type=["pdf"])

default_text = SAMPLES.get(sample_choice, "")
if uploaded_pdf is not None:
    default_text = extract_text_from_pdf(uploaded_pdf)
    st.success(f"Extracted {len(default_text):,} characters from `{uploaded_pdf.name}`")

contract_text = st.text_area("Or paste contract clauses here:", value=default_text, height=180, placeholder="Paste lease terms, NDA, or offer letter...")

scan_clicked = st.button("🔍 Scan for Red Flags", type="primary", use_container_width=True)

if scan_clicked:
    if not contract_text.strip():
        st.warning("Please paste contract text or upload a PDF first.")
    elif st.session_state.scan_count >= MAX_FREE_SCANS:
        st.error("You've reached the 3 free scans limit for this session. Refresh or upgrade to Pro!")
    else:
        with st.spinner("Scanning clauses for hidden traps..."):
            try:
                report = analyze_contract(contract_text, jurisdiction)
                st.session_state.scan_count += 1
                st.session_state.last_report = report
            except Exception as e:
                st.error(f"Scan error: {e}")

# --- 7. RENDER SCORECARD ---
if "last_report" in st.session_state:
    report: ContractReport = st.session_state.last_report
    score_color = "#ef4444" if report.risk_score >= 70 else ("#f59e0b" if report.risk_score >= 40 else "#10b981")

    st.markdown(f"""
    <div class="score-card">
        <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #9ca3af;">
            {report.contract_type} • Risk Audit
        </div>
        <div style="display: flex; align-items: baseline; gap: 14px; margin: 8px 0;">
            <span style="font-size: 3rem; font-weight: 800; color: {score_color};">{report.risk_score}/100</span>
            <span style="font-size: 1.2rem; font-weight: 600;">{report.verdict_headline}</span>
        </div>
        <div style="font-size: 0.9rem; color: #d1d5db;">
            Found <b>{len(report.flags)} red flag(s)</b> that require pushback before signing.
        </div>
    </div>
    """, unsafe_allow_html=True)

    for idx, flag in enumerate(report.flags, 1):
        css_class = "flag-high" if flag.severity == "HIGH" else "flag-medium"
        badge = "🚨 HIGH RISK" if flag.severity == "HIGH" else "⚠️ WATCH OUT"
        st.markdown(f"""
        <div class="{css_class}">
            <strong>{idx}. {flag.title}</strong> <span style="font-size:0.8rem; font-weight:700;">({badge})</span>
            <div class="quote-box">"{flag.exact_quote}"</div>
            <div><b>Why it's a trap:</b> {flag.plain_english}</div>
        </div>
        """, unsafe_allow_html=True)

    # --- MONETIZATION / PAYWALL SECTION ---
    st.divider()
    st.subheader("✉️ Auto-Generated Pushback & Negotiation Script")

    if not st.session_state.unlocked_pro:
        st.info("🔒 **Pro Feature ($5 One-Time):** Unlock the exact counter-clauses and ready-to-send email to push back without sounding confrontational.")
        # Replace this button with a real Stripe Payment Link URL in production:
        # st.link_button("Unlock Full Negotiation Script — $5", "https://buy.stripe.com/your-link")
        if st.button("Demo: Simulate $5 Unlock"):
            st.session_state.unlocked_pro = True
            st.rerun()
    else:
        for idx, flag in enumerate(report.flags, 1):
            st.markdown(f"**Counter-move #{idx} ({flag.title}):** {flag.counter_move}")
        st.text_area("Ready-to-Send Email:", value=report.negotiation_email, height=180)

    # --- VIRAL SHARE BLOCK ---
    share_summary = f"🚩 RedFlag.ai scanned my {report.contract_type}: {report.risk_score}/100 Risk Score — \"{report.verdict_headline}\" ({len(report.flags)} traps caught before signing)."
    st.caption("📋 Copy & share your scorecard:")
    st.code(share_summary, language=None)
