import os
import time
import html
import streamlit as st
from pypdf import PdfReader
from pydantic import BaseModel, Field
from typing import List, Literal
from google import genai
from google.genai import types

# --- 1. PAGE CONFIG & PREMIUM DARK SAAS STYLING ---
st.set_page_config(
    page_title="RedFlag.ai | Contract & Lease Risk Scanner",
    page_icon="🚩",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Canvas & Typography */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #090d16;
        color: #f1f5f9;
    }

    /* Hide default Streamlit header/footer clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background-color: transparent !important;}

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 780px;
    }

    /* Hero Header */
    .hero-wrap {
        text-align: center;
        padding: 12px 0 24px 0;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.35);
        color: #fca5a5;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 5px 14px;
        border-radius: 999px;
        margin-bottom: 12px;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin: 0;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 1rem;
        margin-top: 8px;
    }

    /* Dark Glass Inputs & Controls */
    .stSelectbox > div > div,
    .stTextArea > div > div > textarea,
    .stTextInput > div > div > input {
        background-color: #111827 !important;
        color: #f8fafc !important;
        border: 1px solid #1e293b !important;
        border-radius: 10px !important;
    }
    .stSelectbox > div > div:hover,
    .stTextArea > div > div > textarea:focus {
        border-color: #ef4444 !important;
        box-shadow: 0 0 0 1px rgba(239, 68, 68, 0.3) !important;
    }

    /* File Uploader */
    [data-testid="stFileUploader"] {
        background-color: #0f172a;
        border: 1px dashed #334155;
        border-radius: 12px;
        padding: 10px;
    }

    /* Primary CTA Button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 0.01em;
        box-shadow: 0 8px 24px rgba(239, 68, 68, 0.28);
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 28px rgba(239, 68, 68, 0.4);
    }

    /* Scorecard Container */
    .score-card {
        background: radial-gradient(circle at top right, rgba(239, 68, 68, 0.14), transparent 55%),
                    linear-gradient(180deg, #111827 0%, #0b1120 100%);
        border: 1px solid #1e293b;
        border-radius: 20px;
        padding: 26px;
        margin: 18px 0 22px 0;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.45);
        display: flex;
        align-items: center;
        gap: 24px;
    }
    .pill-meta {
        display: inline-block;
        background: #1e293b;
        color: #cbd5e1;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 4px 10px;
        border-radius: 6px;
        margin-bottom: 8px;
    }

    /* Flag Cards */
    .flag-card {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
    }
    .flag-high { border-left: 4px solid #ef4444; }
    .flag-medium { border-left: 4px solid #f59e0b; }
    .flag-green { border-left: 4px solid #10b981; background: rgba(16, 185, 129, 0.06); }

    .badge-high {
        background: rgba(239, 68, 68, 0.15);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.35);
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 999px;
        float: right;
    }
    .badge-medium {
        background: rgba(245, 158, 11, 0.15);
        color: #fcd34d;
        border: 1px solid rgba(245, 158, 11, 0.35);
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 999px;
        float: right;
    }
    .quote-box {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #94a3b8;
        background: #090d16;
        border: 1px solid #1e293b;
        padding: 10px 12px;
        border-radius: 8px;
        margin: 10px 0;
        line-height: 1.5;
    }
    .takeaway-text {
        color: #e2e8f0;
        font-size: 0.92rem;
        line-height: 1.55;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #111827;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #1e293b;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. STRUCTURED OUTPUT SCHEMA ---
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
    green_flags: List[str] = Field(description="1-3 fair or protective terms found in the document")
    flags: List[FlaggedClause]
    polite_email: str = Field(description="Warm, collaborative email asking to amend the flagged clauses")
    firm_email: str = Field(description="Direct, assertive email declining unfair terms before signing")

# --- 3. SESSION STATE ---
if "scan_count" not in st.session_state:
    st.session_state.scan_count = 0
if "unlocked_pro" not in st.session_state:
    st.session_state.unlocked_pro = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

MAX_FREE_SCANS = 5

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

# --- 5. GEMINI CLIENT WITH RETRY & FALLBACK ---
def get_client():
    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in environment or Streamlit secrets.")
    return genai.Client(api_key=api_key)

def call_gemini_with_retry(contents, config=None):
    client = get_client()
    models_to_try = ["gemini-3.8-flash", "gemini-3.8-flash-lite", "gemini-3.8-pro"]
    last_error = None

    for model_name in models_to_try:
        for attempt in range(2):
            try:
                return client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )
            except Exception as e:
                last_error = e
                if any(code in str(e) for code in ["503", "UNAVAILABLE", "429"]):
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise e
    raise RuntimeError("AI servers are momentarily busy. Please wait 5 seconds and try again.") from last_error

def extract_text_from_pdf(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    return "\n".join([page.extract_text() or "" for page in reader.pages]).strip()

def analyze_contract(text: str, jurisdiction: str, lens: str) -> ContractReport:
    lens_instructions = {
        "Strict Advocate": "Be thorough and uncompromising. Flag every subtle trap, one-sided liability, or deviation from statutory protections.",
        "Balanced Review": "Focus only on major financial, legal, or IP risks that genuinely matter in real-world negotiations.",
        "Brutal Roast Mode": "Use sharp, witty, brutally honest commentary in the plain_english explanations while keeping quotes and redlines accurate."
    }

    prompt = f"""
    You are reviewing a contract under {jurisdiction} norms.
    Style instruction: {lens_instructions[lens]}
    Note: Frame findings as educational risk flags, not formal legal representation.

    CONTRACT TEXT:
    {text[:28000]}
    """

    response = call_gemini_with_retry(
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ContractReport,
            temperature=0.25 if lens != "Brutal Roast Mode" else 0.6,
        ),
    )
    return ContractReport.model_validate_json(response.text)

def render_svg_gauge(score: int, color: str) -> str:
    radius = 44
    circumference = 2 * 3.14159 * radius
    offset = circumference - (score / 100) * circumference
    return f"""
    <svg width="112" height="112" viewBox="0 0 112 112" style="flex-shrink:0;">
        <circle cx="56" cy="56" r="{radius}" fill="none" stroke="#1e293b" stroke-width="10" />
        <circle cx="56" cy="56" r="{radius}" fill="none" stroke="{color}" stroke-width="10"
                stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{offset:.1f}"
                stroke-linecap="round" transform="rotate(-90 56 56)" />
        <text x="56" y="54" text-anchor="middle" fill="#ffffff" font-size="24" font-weight="800" font-family="Inter, sans-serif">{score}</text>
        <text x="56" y="72" text-anchor="middle" fill="#94a3b8" font-size="10" font-weight="600" font-family="Inter, sans-serif">RISK / 100</text>
    </svg>
    """

def build_markdown_report(report: ContractReport) -> str:
    lines = [
        f"# RedFlag.ai Audit Report — {report.contract_type}",
        f"**Risk Score:** {report.risk_score}/100 — *{report.verdict_headline}*\n",
        "## Flagged Clauses",
    ]
    for i, f in enumerate(report.flags, 1):
        lines.append(f"### {i}. {f.title} [{f.severity}]")
        lines.append(f"> \"{f.exact_quote}\"\n")
        lines.append(f"- **Why it's risky:** {f.plain_english}")
        lines.append(f"- **Proposed Redline:** {f.redline_replacement}\n")
    lines.append("## Negotiation Email Draft\n")
    lines.append(report.polite_email)
    return "\n".join(lines)

# --- 6. HERO HEADER & CONTROLS ---
st.markdown("""
<div class="hero-wrap">
    <div class="hero-badge">AI Contract & Lease Shield</div>
    <h1 class="hero-title">🚩 RedFlag.ai</h1>
    <p class="hero-sub">Spot predatory clauses, generate fair redlines, and interrogate any contract in 10 seconds.</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1.3, 1.3])
with col1:
    sample_choice = st.selectbox("Sample or Custom:", ["Custom Input", "Shady Rental Lease", "Trap Freelance Contract"])
with col2:
    jurisdiction = st.selectbox("Region:", ["Australia (VIC/NSW)", "United States", "United Kingdom", "Global / Remote"])
with col3:
    lens = st.selectbox("Scanner Lens:", ["Strict Advocate", "Balanced Review", "Brutal Roast Mode"])

uploaded_pdf = st.file_uploader("Upload Contract PDF (optional)", type=["pdf"])

default_text = SAMPLES.get(sample_choice, "")
if uploaded_pdf is not None:
    default_text = extract_text_from_pdf(uploaded_pdf)
    st.caption(f"✅ Loaded `{uploaded_pdf.name}` ({len(default_text):,} characters)")

contract_text = st.text_area("Or paste contract text:", value=default_text, height=160, placeholder="Paste lease clauses, NDA, or job offer...")

if st.button("🔍 Scan for Red Flags", type="primary", use_container_width=True):
    if not contract_text.strip():
        st.warning("Please paste contract text or upload a PDF first.")
    elif st.session_state.scan_count >= MAX_FREE_SCANS:
        st.error("You've reached the free scan limit for this session.")
    else:
        with st.spinner(f"Running {lens} audit..."):
            try:
                report = analyze_contract(contract_text, jurisdiction, lens)
                st.session_state.scan_count += 1
                st.session_state.last_report = report
                st.session_state.scanned_text = contract_text
                st.session_state.chat_history = []
            except Exception as e:
                st.error(f"Scan error: {e}")

# --- 7. RENDER INTERACTIVE SCORECARD ---
if "last_report" in st.session_state:
    report: ContractReport = st.session_state.last_report
    score_color = "#ef4444" if report.risk_score >= 70 else ("#f59e0b" if report.risk_score >= 40 else "#10b981")
    gauge_svg = render_svg_gauge(report.risk_score, score_color)

    st.markdown(f"""
    <div class="score-card">
        {gauge_svg}
        <div>
            <div class="pill-meta">{html.escape(report.contract_type)} • {html.escape(lens)}</div>
            <div style="font-size: 1.35rem; font-weight: 800; color: #f8fafc; line-height: 1.3; margin-bottom: 6px;">
                {html.escape(report.verdict_headline)}
            </div>
            <div style="font-size: 0.9rem; color: #94a3b8;">
                Detected <b style="color:#f8fafc;">{len(report.flags)} red flag(s)</b> and <b style="color:#34d399;">{len(report.green_flags)} fair term(s)</b>.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_flags, tab_negotiate, tab_chat = st.tabs(["🚩 Clause Breakdown", "✉️ Redlines & Email", "💬 Ask Contract"])

    # TAB 1: FLAGS
    with tab_flags:
        for idx, flag in enumerate(report.flags, 1):
            card_cls = "flag-high" if flag.severity == "HIGH" else "flag-medium"
            badge_cls = "badge-high" if flag.severity == "HIGH" else "badge-medium"
            badge_txt = "🚨 HIGH RISK" if flag.severity == "HIGH" else "⚠️ WATCH OUT"
            st.markdown(f"""
            <div class="flag-card {card_cls}">
                <span class="{badge_cls}">{badge_txt}</span>
                <div style="font-weight: 700; font-size: 1.02rem; color: #f8fafc;">{idx}. {html.escape(flag.title)}</div>
                <div class="quote-box">"{html.escape(flag.exact_quote)}"</div>
                <div class="takeaway-text">{html.escape(flag.plain_english)}</div>
            </div>
            """, unsafe_allow_html=True)

        if report.green_flags:
            st.markdown("#### ✅ Fair / Protective Terms")
            for gf in report.green_flags:
                st.markdown(f'<div class="flag-card flag-green" style="padding:12px 16px; color:#a7f3d0;">✓ {html.escape(gf)}</div>', unsafe_allow_html=True)

    # TAB 2: REDLINES & NEGOTIATION EMAIL
    with tab_negotiate:
        if not st.session_state.unlocked_pro:
            st.info("🔒 **Pro Toolkit ($5 One-Time):** Unlock copy-paste replacement clauses (redlines), tone-adjustable pushback emails, and full Markdown report export.")
            if st.button("Demo: Unlock Pro Toolkit"):
                st.session_state.unlocked_pro = True
                st.rerun()
        else:
            st.markdown("#### ✍️ Copy-Paste Replacement Clauses")
            for idx, flag in enumerate(report.flags, 1):
                with st.expander(f"Redline #{idx}: {flag.title}", expanded=True):
                    st.caption("Propose replacing the trapped wording with:")
                    st.code(flag.redline_replacement, language=None)

            st.markdown("#### ✉️ Ready-to-Send Pushback Email")
            tone = st.radio("Negotiation tone:", ["Polite & Collaborative", "Firm & Direct"], horizontal=True)
            email_body = report.polite_email if tone == "Polite & Collaborative" else report.firm_email
            st.text_area("Edit or copy email:", value=email_body, height=200)

            st.download_button(
                label="📥 Download Full Audit Report (.md)",
                data=build_markdown_report(report),
                file_name="redflag_audit_report.md",
                mime="text/markdown",
                use_container_width=True,
            )

    # TAB 3: INTERACTIVE Q&A WITH THE CONTRACT
    with tab_chat:
        st.caption("Ask any specific question grounded in this document (e.g., *'Can I keep a pet?'*, *'What is the notice period?'*).")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_q = st.chat_input("Ask a question about this contract...")
        if user_q:
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            with st.chat_message("user"):
                st.markdown(user_q)

            with st.chat_message("assistant"):
                with st.spinner("Checking clauses..."):
                    qa_prompt = f"""
                    Answer the user's question based ONLY on the contract text below. Quote relevant clause numbers or text if present. If the contract is silent on the topic, explicitly say so and warn why that silence could matter. Keep it concise.

                    CONTRACT:
                    {st.session_state.scanned_text[:28000]}

                    QUESTION:
                    {user_q}
                    """
                    ans = call_gemini_with_retry(contents=qa_prompt).text
                    st.markdown(ans)
                    st.session_state.chat_history.append({"role": "assistant", "content": ans})

    # --- VIRAL SHARE BLOCK ---
    st.divider()
    share_summary = f"🚩 RedFlag.ai ({lens}) scanned my {report.contract_type}: {report.risk_score}/100 Risk Score — \"{report.verdict_headline}\" ({len(report.flags)} traps caught before signing)."
    st.caption("📋 Copy & share your scorecard:")
    st.code(share_summary, language=None)
