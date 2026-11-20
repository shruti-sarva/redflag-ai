"""Styles for the two-screen flow and the PactLens.ai review workspace."""
import streamlit as st


def apply_review_styles():
    st.html("""
    <style>
    .rf-flow {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 18px 0 26px;
        font-size: 13px;
        color: #65758d;
    }
    .rf-flow-step { display: inline-flex; align-items: center; gap: 9px; white-space: nowrap; }
    .rf-flow-number {
        display: inline-grid;
        place-items: center;
        width: 27px;
        height: 27px;
        border-radius: 50%;
        background: #E7EDF5;
        color: #65758d;
        font-weight: 700;
        font-size: 12px;
    }
    .rf-flow-active { color: #273957; font-weight: 750; }
    .rf-flow-active .rf-flow-number { color: #fff; background: #6254E8; }
    .rf-flow-complete .rf-flow-number { color: #fff; background: #217A63; }
    .rf-flow-line { height: 1px; width: 48px; background: #D7E0EB; }
    .rf-screen-intro { margin: 10px 0 25px; max-width: 780px; }
    .rf-screen-eyebrow { color: #6558E8; letter-spacing: 1.4px; font-weight: 800; font-size: 11px; margin: 0 0 8px; }
    .rf-screen-intro h1, .rf-result-hero h1 {
        color: #17233B;
        font-size: clamp(29px, 4vw, 43px);
        letter-spacing: -1.35px;
        line-height: 1.12;
        margin: 0 0 10px;
        font-weight: 780;
    }
    .rf-screen-intro > p:last-child, .rf-result-hero > p:last-child {
        font-size: 15px;
        color: #62738A;
        line-height: 1.6;
        margin: 0;
    }
    .rf-result-hero { margin: 8px 0 19px; }
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #DAE3ED;
        border-radius: 12px;
        padding: 17px;
        box-shadow: 0 4px 18px rgba(25,40,68,.035);
    }
    .st-key-rf_contract_panel, .st-key-rf_findings_panel {
        background: #FFFFFF;
        border: 1px solid #DAE3ED;
        border-radius: 14px;
        padding: 18px;
        margin-top: 14px;
        min-width: 0;
    }
    .rf-real-paper {
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        font-family: Georgia, 'Times New Roman', serif;
        color: #35445D;
        background: #FBFCFE;
        border: 1px solid #E4EAF1;
        border-radius: 10px;
        padding: 23px;
        font-size: 14px;
        line-height: 1.85;
    }
    .rf-real-highlight { padding: 1px 2px; border-radius: 3px; box-decoration-break: clone; }
    .rf-real-high { background: #FFE0E5; color: #852A3C; }
    .rf-real-medium { background: #FFF0D0; color: #805711; }
    .st-key-rf_findings_panel [data-testid="stExpander"] {
        border-radius: 10px;
        border-color: #E3E9F2;
        margin-top: 8px;
    }
    @media (max-width: 760px) {
        .rf-flow { gap: 7px; font-size: 11px; }
        .rf-flow-line { width: 20px; }
        .rf-flow-number { height: 23px; width: 23px; }
        .rf-screen-intro, .rf-result-hero { margin-bottom: 18px; }
        .rf-real-paper { padding: 14px; font-size: 13px; }
        .st-key-rf_contract_panel, .st-key-rf_findings_panel { padding: 12px; }
    }
    </style>
    """)
