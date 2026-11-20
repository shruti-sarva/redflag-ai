"""Visual styles and branded header for PactLens.ai."""
import streamlit as st


def apply_styles():
    st.html(
        """
        <style>
        .stApp { background: #EFF3F7; color: #17233B; }
        .block-container { max-width: 1240px; padding-top: 3.75rem; padding-bottom: 2.5rem; }
        .rf-nav {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px 14px;
            background: #FFFFFF;
            border: 1px solid #DAE3ED;
            border-radius: 10px;
            padding: 10px 14px;
        }
        .rf-brand { display: inline-flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 750; }
        .rf-brand-mark {
            display: grid;
            place-items: center;
            width: 27px;
            height: 27px;
            border-radius: 6px;
            background: #233F68;
            color: #FFFFFF;
        }
        .rf-nav-title { color: #52627A; font-size: 13px; }
        .st-key-rf_scanner {
            background: #FFFFFF;
            border: 1px solid #DAE3ED;
            border-radius: 10px;
            padding: 16px;
        }
        .st-key-rf_scanner div[data-testid="stForm"] {
            padding: 0;
            border: 0;
        }
        .rf-form-title { color: #17233B; font-size: 18px; font-weight: 700; margin: 0; padding: 0; }
        .rf-privacy { color: #52627A; font-size: 12px; line-height: 1.45; }

        .rf-document-preview {
            container-type: inline-size;
            background: #F7F9FC;
            color: #17233B;
            border: 1px solid #DDE5F0;
            border-radius: 10px;
            padding: 16px;
        }
        .rf-preview-header {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 6px 12px;
            margin-bottom: 14px;
        }
        .rf-preview-header h3 { color: #17233B; font-size: 19px; margin: 0; padding: 0; }
        .rf-preview-header span {
            color: #345482;
            background: #E1EAFE;
            border-radius: 6px;
            padding: 3px 8px;
            font-size: 12px;
            font-weight: 700;
        }
        .rf-preview-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.55fr) minmax(0, 1fr);
            align-items: start;
            gap: 12px;
        }
        .rf-doc-paper, .rf-doc-analysis {
            min-width: 0;
            overflow-wrap: anywhere;
            border: 1px solid #DDE5F0;
            border-radius: 12px;
            padding: 16px;
        }
        .rf-doc-paper { background: #FFFFFF; padding: clamp(16px, 4cqi, 32px); }
        .rf-doc-paper h4 {
            color: #17233B;
            font-family: Georgia, serif;
            font-size: 23px;
            font-weight: 600;
            line-height: 1.25;
            margin: 0 0 12px;
            padding: 0 0 12px;
            border-bottom: 1px solid #E5EAF2;
        }
        .rf-doc-clause + .rf-doc-clause { margin-top: 14px; }
        .rf-doc-clause-heading { font-size: 13px; font-weight: 750; margin-bottom: 4px; }
        .rf-doc-clause p { color: #34435B; font-family: Georgia, serif; font-size: 15px; line-height: 1.6; margin: 0; }
        .rf-doc-mark { color: inherit; }
        .rf-doc-mark-high { background: #DCE8FF; }
        .rf-doc-mark-medium { background: #FFF0D0; }
        .rf-doc-analysis { background: transparent; border: 0; padding: 8px 0 0; }
        .rf-doc-analysis h4 { color: #17233B; font-size: 15px; margin: 0; padding: 0; }
        .rf-doc-count { color: #52627A; font-size: 12px; margin: 3px 0 12px; }
        .rf-doc-finding {
            display: flex;
            align-items: baseline;
            gap: 8px;
            background: #FFFFFF;
            border: 1px solid #E2E8F2;
            border-radius: 8px;
            padding: 9px;
            font-size: 12px;
            line-height: 1.4;
        }
        .rf-doc-finding + .rf-doc-finding { margin-top: 8px; }
        .rf-doc-finding small { display: block; color: #52627A; font-size: 11px; margin-top: 4px; }
        .rf-doc-dot { flex: 0 0 6px; height: 6px; border-radius: 50%; }
        .rf-doc-dot.rf-dot-high { background: #486DB3; }
        .rf-doc-dot.rf-dot-medium { background: #9D650D; }
        .rf-preview-footnote { font-size: 11px; color: #52627A; margin-top: 12px; text-align: center; }

        @container (max-width: 430px) {
            .rf-preview-grid { grid-template-columns: minmax(0, 1fr); }
        }

        @media (max-width: 760px) {
            .block-container {
                padding-top: 4rem !important;
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }

        .st-key-rf_scanner [data-testid="stFileUploaderDropzone"] {
            background: #F7F9FC;
            border: 1px dashed #AABAD0;
            border-radius: 8px;
        }
        </style>
        """,
    )


def render_header():
    st.html(
        """
        <div class="rf-nav">
          <div class="rf-brand"><span class="rf-brand-mark">⚑</span>PactLens.ai</div>
          <span class="rf-nav-title">Contract review</span>
        </div>
        """,
    )
