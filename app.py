import os
import time
import html
import streamlit as st
from pypdf import PdfReader
from pydantic import BaseModel, Field
from typing import List, Literal
from google import genai
from google.genai import types

# --- 1. PAGE CONFIG & HIGH-CRAFT SAAS STYLING ---
st.set_page_config(
    page_title="RedFlag.ai | Contract & Lease Risk Scanner",
    page_icon="🚩",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: radial-gradient(ellipse 80% 45% at 50% -10%, rgba(239, 68, 68, 0.16), transparent),
                    #070b14;
        color: #f8fafc;
    }

    #MainMenu, footer {visibility: hidden;}
    header {background: transparent !important;}

    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 3.5rem;
        max-width: 720px;
    }

    /* Hero Header */
    .hero-wrap {
        text-align: center;
        margin-bottom: 26px;
    }
    .hero-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.28);
        color: #fda4af;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 5px 14px;
        border-radius: 999px;
        margin-bottom: 14px;
    }
    .hero-title {
        font-size: 2.75rem;
        font-weight: 800;
        letter-spacing: -0.035em;
        margin: 0;
        line-height: 1.1;
    }
    .hero-title-text {
        background: linear-gradient(180deg, #ffffff 20%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 1.02rem;
        max-width: 540px;
        margin: 10px auto 0 auto;
        line-height: 1.5;
    }

    /* Main Studio Card Container */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(15, 23, 42, 0.72) !important;
        backdrop-filter: blur(16px);
        border: 1px solid rgba(148, 163, 184, 0.14) !important;
        border-radius: 20px !important;
        padding: 18px 20px 22px 20px !important;
        box-shadow: 0 24px 48px -12px rgba(0, 0, 0, 0.6);
    }

    /* Sample Quick-Load Pills (Secondary Buttons) */
    .stButton > button[kind="secondary"] {
        background: #111827 !important;
        color: #cbd5e1 !important;
        border: 1px solid #1e293b !important;
        border-radius: 10px !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        padding: 0.45rem 0.75rem !important;
        transition: all 0.15s ease;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: rgba(239, 68, 68, 0.5) !important;
        color: #ffffff !important;
        background: rgba(239, 68, 68, 0.08) !important;
    }

    /* Fix File Uploader Dropzone Color */
    [data-testid="stFileUploaderDropzone"] {
        background-color: #090e1a !important;
        border: 1px dashed #293548 !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #ef4444 !important;
    }

    /* Fix Textarea & Selectbox Backgrounds */
    textarea, [data-baseweb="select"] > div {
        background-color: #090e1a !important;
        border-color: #1e293b !important;
        color: #f8fafc !important;
        border-radius: 12px !important;
    }
    textarea:focus {
        border-color: #ef4444 !important;
        box-shadow: 0 0 0 1px rgba(239, 68, 68, 0.35) !important;
    }

    /* Primary Scan Button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        box-shadow: 0 10px 25px -5px rgba(239, 68, 68, 0.45);
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 30px -5px rgba(239, 68, 68, 0.6);
    }

    .trust-strip {
        text-align: center;
        color: #64748b;
        font-size: 0.76rem;
        margin-top: 10px;
    }

    /* Scorecard Result Card */
    .score-card {
        background: radial-gradient(circle at top right, rgba(239, 68, 68, 0.15), transparent 55%),
                    #0f172a;
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 20px;
        padding: 24px;
        margin: 22px 0;
        display: flex;
        align-items: center;
        gap: 22px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.45);
    }
    .pill-meta {
        display: inline-block;
        background: rgba(30, 41, 59, 0.9);
        color: #cbd5e1;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 4px 10px;
        border-radius: 6px;
        margin-bottom: 8px;
    }

    /* Flag Cards */
    .flag-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 12px;
    }
    .flag-high { border-left: 4px solid #ef4444; }
    .flag-medium { border-left: 4px solid #f59e0b; }
    .flag-green { border-left: 4px solid #10b981; background: rgba(16, 185, 129, 0.06); }

    .badge-high {
        background: rgba(239, 68, 68, 0.14);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.3);
        font-size: 0.68rem;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 999px;
        float: right;
    }
    .badge-medium {
        background: rgba(245, 158, 11, 0.14);
        color: #fcd34d;
        border: 1px solid rgba(245, 158, 11, 0.3);
        font-size: 0.68rem;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 999px;
        float: right;
    }
    .quote-box {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #94a3b8;
        background: #070b14;
        border: 1px solid #1e293b;
        padding: 10px 12px;
        border-radius: 8px;
        margin: 10px 0;
        line-height: 1.5;
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
if "draft_contract" not in st.session_state:
    st.session_state.draft_contract = ""

MAX_FREE_SCANS = 5

# --- 4. SAMPLE CONTRACTS ---
SAMPLES = {
    "lease": """RESIDENTIAL TENANCY SPECIAL CONDITIONS:
14.2 Tenant agrees to pay a non-refundable $450 'End of Lease Air-Con & Blind Sanitization Fee' deducted automatically from the bond regardless of property condition.
18.5 Landlord or agents may enter the premises at any time without prior written notice to conduct marketing inspections or photography.
22.1 Should Tenant break the lease early, Tenant forfeits the entire security deposit plus 3 months of future rent as liquidated damages.""",
    "freelance": """INDEPENDENT CONTRACTOR AGREEMENT:
7.1 Intellectual Property: All work product, including pre-existing code libraries, tools, and drafts created before or during this engagement, shall belong exclusively to Client in perpetuity.
9.4 Payment Terms: Invoices are payable Net-90 days AFTER Client receives final payment from its own end-customer.
11.2 Non-Compete: Contractor shall not provide software or AI consulting services to any business globally for 24 months post-termination.""",
    "job": """EXECUTIVE EMPLOYMENT OFFER:
6.3 Side Projects: Any software, invention, or creative work conceived by Employee at any time during employment—including evenings, weekends, and on personal devices—shall automatically vest in the Company.
10.1 Probation & Notice: Company may terminate Employee immediately without notice or severance during the first 12 months, while Employee must provide 90 days written notice to resign."""
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
        "Brutal Roast": "Use sharp, witty, brutally honest commentary in the plain_english explanations while keeping quotes and redlines accurate."
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
            temperature=0.25 if lens != "Brutal Roast" else 0.6,
        ),
    )
    return ContractReport.model_validate_json(response.text)

def render_svg_gauge(score: int, color: str) -> str:
    radius = 44
    circumference = 2 * 3.14159 * radius
    offset = circumference - (score / 100) * circumference
    return f"""
    <svg width="108" height="108" viewBox="0 0 112 112" style="flex-shrink:0;">
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

# --- 6. HERO HEADER ---
st.markdown("""
<div class="hero-wrap">
    <div class="hero-pill">⚡ Instant Contract & Lease Shield</div>
    <h1 class="hero-title">🚩 <span class="hero-title-text">RedFlag.ai</span></h1>
    <p class="hero-sub">Drop a lease, job offer, or freelance contract to uncover hidden traps and generate ready-to-send pushback redlines.</p>
</div>
""", unsafe_allow_html=True)

# --- 7. GLASS SCANNER STUDIO CARD ---
with st.container(border=True):
    st.caption("TRY A 1-CLICK SAMPLE:")
    s1, s2, s3 = st.columns(3)
    if s1.button("🏠 Shady Rental Lease", use_container_width=True):
        st.session_state.draft_contract = SAMPLES["lease"]
    if s2.button("💻 Trap Freelance Gig", use_container_width=True):
        st.session_state.draft_contract = SAMPLES["freelance"]
    if s3.button("💼 Sneaky Job Offer", use_container_width=True):
        st.session_state.draft_contract = SAMPLES["job"]

    uploaded_pdf = st.file_uploader("Upload PDF contract", type=["pdf"], label_visibility="collapsed")
    if uploaded_pdf is not None:
        st.session_state.draft_contract = extract_text_from_pdf(uploaded_pdf)
        st.caption(f"✅ Extracted `{uploaded_pdf.name}` ({len(st.session_state.draft_contract):,} characters)")

    contract_text = st.text_area(
        "Contract text",
        value=st.session_state.draft_contract,
        height=155,
        placeholder="Paste clauses here or upload a PDF above...",
        label_visibility="collapsed",
    )
    st.session_state.draft_contract = contract_text

    c_reg, c_lens = st.columns([1.1, 1.5])
    with c_reg:
        jurisdiction = st.selectbox("Jurisdiction", ["Australia (VIC/NSW)", "United States", "United Kingdom", "Global / Remote"])
    with c_lens:
        lens = st.selectbox("Audit Tone", ["Strict Advocate", "Balanced Review", "Brutal Roast"])

    scan_clicked = st.button("Scan Contract for Red Flags →", type="primary", use_container_width=True)

st.markdown('<div class="trust-strip">🔒 Zero documents stored • Educational risk audit • Instant redlines</div>', unsafe_allow_html=True)

if scan_clicked:
    if not contract_text.strip():
        st.warning("Pick one of the sample pills above, upload a PDF, or paste text to scan.")
    elif st.session_state.scan_count >= MAX_FREE_SCANS:
        st.error("You've reached the free scan limit for this session.")
    else:
        with st.spinner(f"Auditing clauses ({lens})..."):
            try:
                report = analyze_contract(contract_text, jurisdiction, lens)
                st.session_state.scan_count += 1
                st.session_state.last_report = report
                st.session_state.scanned_text = contract_text
                st.session_state.chat_history = []
            except Exception as e:
                st.error(f"Scan error: {e}")

# --- 8. RENDER INTERACTIVE SCORECARD ---
if "last_report" in st.session_state:
    report: ContractReport = st.session_state.last_report
    score_color = "#ef4444" if report.risk_score >= 70 else ("#f59e0b" if report.risk_score >= 40 else "#10b981")
    gauge_svg = render_svg_gauge(report.risk_score, score_color)

    st.markdown(f"""
    <div class="score-card">
        {gauge_svg}
        <div>
            <div class="pill-meta">{html.escape(report.contract_type)} • {html.escape(lens)}</div>
            <div style="font-size: 1.32rem; font-weight: 800; color: #f8fafc; line-height: 1.3; margin-bottom: 6px;">
                {html.escape(report.verdict_headline)}
            </div>
            <div style="font-size: 0.88rem; color: #94a3b8;">
                Caught <b style="color:#f8fafc;">{len(report.flags)} red flag(s)</b> and <b style="color:#34d399;">{len(report.green_flags)} fair term(s)</b>.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_flags, tab_negotiate, tab_chat = st.tabs(["🚩 Clause Breakdown", "✉️ Redlines & Email", "💬 Ask Contract"])

    with tab_flags:
        for idx, flag in enumerate(report.flags, 1):
            card_cls = "flag-high" if flag.severity == "HIGH" else "flag-medium"
            badge_cls = "badge-high" if flag.severity == "HIGH" else "badge-medium"
            badge_txt = "🚨 HIGH RISK" if flag.severity == "HIGH" else "⚠️ WATCH OUT"
            st.markdown(f"""
            <div class="flag-card {card_cls}">
                <span class="{badge_cls}">{badge_txt}</span>
                <div style="font-weight: 700; font-size: 1rem; color: #f8fafc;">{idx}. {html.escape(flag.title)}</div>
                <div class="quote-box">"{html.escape(flag.exact_quote)}"</div>
                <div style="color:#cbd5e1; font-size:0.9rem; line-height:1.55;">{html.escape(flag.plain_english)}</div>
            </div>
            """, unsafe_allow_html=True)

        if report.green_flags:
            st.markdown("#### ✅ Fair / Protective Terms")
            for gf in report.green_flags:
                st.markdown(f'<div class="flag-card flag-green" style="padding:12px 16px; color:#a7f3d0;">✓ {html.escape(gf)}</div>', unsafe_allow_html=True)

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

    st.divider()
    share_summary = f"🚩 RedFlag.ai ({lens}) scanned my {report.contract_type}: {report.risk_score}/100 Risk Score — \"{report.verdict_headline}\" ({len(report.flags)} traps caught before signing)."
    st.caption("📋 Copy & share your scorecard:")
    st.code(share_summary, language=None)
