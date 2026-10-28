"""
╔══════════════════════════════════════════════════════════════════╗
║   CrimeVision AI — Intelligent Multimodal Forensic Analysis     ║
║   Platform (Skill Wallet Capstone Project 2)                    ║
║                                                                  ║
║   Entry Point: streamlit run app.py                              ║
║   Version: 2.0.0                                                 ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
from utils import (
    APP_TITLE, APP_SUBTITLE, VERSION,
    init_session_state, validate_api_key,
)

# ─────────────────────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{APP_TITLE} — {APP_SUBTITLE}",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": f"# {APP_TITLE} v{VERSION}\n{APP_SUBTITLE}\n\nBuilt for NASSCOM FutureSkills — Skill Wallet Capstone.",
    },
)

# Initialize session state
init_session_state()

# ─────────────────────────────────────────────────────────────
# Custom CSS — Dark Forensic Theme
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Global ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #0A0E17 0%, #0d1321 50%, #0A0E17 100%);
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #111827 100%);
        border-right: 1px solid #1e293b;
    }

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #00E5FF;
    }

    /* ── Header Strip ── */
    .forensic-header {
        background: linear-gradient(135deg, #0a1628 0%, #162447 40%, #1a1a2e 100%);
        border: 1px solid #1e3a5f;
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }

    .forensic-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #00E5FF, #7C4DFF, #FF6D00, #00E5FF);
        background-size: 200% 100%;
        animation: shimmer 3s ease-in-out infinite;
    }

    @keyframes shimmer {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    .forensic-header h1 {
        color: #00E5FF;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .forensic-header p {
        color: #94a3b8;
        font-size: 1rem;
        margin: 6px 0 0 0;
    }

    /* ── Status Badge ── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-top: 10px;
    }

    .status-demo {
        background: rgba(255, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(255, 158, 11, 0.3);
    }

    .status-live {
        background: rgba(34, 197, 94, 0.15);
        color: #22C55E;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }

    /* ── Tab Styling ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #111827;
        border-radius: 12px;
        padding: 4px;
        border: 1px solid #1e293b;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 8px;
        color: #9CA3AF;
        font-weight: 500;
        font-size: 14px;
        padding: 0 16px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00E5FF22, #7C4DFF22) !important;
        color: #00E5FF !important;
        border: 1px solid #00E5FF44;
    }

    /* ── Metrics ── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #111827, #1a1f2e);
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 14px 18px;
    }

    [data-testid="stMetricLabel"] {
        color: #9CA3AF;
        font-size: 12px;
    }

    [data-testid="stMetricValue"] {
        color: #00E5FF;
        font-weight: 700;
    }

    /* ── Buttons ── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00E5FF, #0099CC);
        color: #0A0E17;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #00FFFF, #00BBE0);
        box-shadow: 0 4px 20px rgba(0, 229, 255, 0.3);
        transform: translateY(-1px);
    }

    /* ── File Uploader ── */
    [data-testid="stFileUploader"] {
        border: 2px dashed #1e293b;
        border-radius: 12px;
        padding: 20px;
        background: #0f1520;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #00E5FF44;
        background: #111827;
    }

    /* ── Expanders ── */
    .streamlit-expanderHeader {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 8px;
        color: #E0E0E0;
    }

    /* ── Chat Input ── */
    [data-testid="stChatInput"] textarea {
        background: #111827;
        border: 1px solid #1e293b;
        color: #E0E0E0;
        border-radius: 10px;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0A0E17;
    }
    ::-webkit-scrollbar-thumb {
        background: #1e293b;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #00E5FF44;
    }

    /* ── Hide Streamlit defaults ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ── Divider ── */
    hr {
        border-color: #1e293b;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Sidebar — Configuration & Security
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="text-align:center;padding:10px 0;">'
        '<span style="font-size:40px;">🔬</span><br/>'
        '<span style="color:#00E5FF;font-size:18px;font-weight:800;letter-spacing:1px;">CRIMEVISION AI</span><br/>'
        '<span style="color:#6B7280;font-size:11px;">v2.0.0 | Forensic Intelligence</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # API Configuration
    st.markdown("### 🔐 API Configuration")

    provider = st.selectbox(
        "LLM Provider",
        options=["groq", "gemini"],
        index=0,
        format_func=lambda x: {"groq": "Groq (Llama 3.1)", "gemini": "Google Gemini"}[x],
        key="sidebar_provider",
    )
    st.session_state.api_provider = provider

    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="Enter your API key...",
        key="sidebar_api_key",
        help="Groq: gsk_... | Gemini: AIza..."
    )

    if api_key:
        if validate_api_key(provider, api_key):
            st.session_state.api_key = api_key
            st.session_state.demo_mode = False
            st.success("✅ API key validated — Live Mode")
        else:
            st.warning("⚠️ Invalid key format — Demo Mode active")
            st.session_state.demo_mode = True
    else:
        st.session_state.demo_mode = True

    # Mode indicator
    if st.session_state.demo_mode:
        st.markdown(
            '<div class="status-badge status-demo">⚡ DEMO MODE</div>',
            unsafe_allow_html=True,
        )
        st.caption("All analyses use intelligent simulated responses. Enter a valid API key for live LLM integration.")
    else:
        st.markdown(
            '<div class="status-badge status-live">🟢 LIVE MODE</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Investigator
    st.markdown("### 👤 Investigator")
    investigator = st.text_input(
        "Name",
        value=st.session_state.get("investigator_name", ""),
        placeholder="Your name for reports",
        key="sidebar_investigator",
    )
    st.session_state.investigator_name = investigator

    st.markdown("---")

    # Evidence Dashboard
    st.markdown("### 📦 Evidence Dashboard")

    evidence_chain = st.session_state.get("evidence_chain", [])
    total_evidence = len(evidence_chain)
    img_count = sum(1 for e in evidence_chain if e["evidence_type"] == "Image")
    aud_count = sum(1 for e in evidence_chain if e["evidence_type"] == "Audio")
    vid_count = sum(1 for e in evidence_chain if e["evidence_type"] == "Video")

    st.metric("Total Evidence", total_evidence)

    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("🖼️", img_count)
    col_s2.metric("🎙️", aud_count)
    col_s3.metric("📹", vid_count)

    if total_evidence > 0:
        with st.expander("📋 Evidence Registry"):
            for record in evidence_chain:
                st.markdown(
                    f'<div style="background:#0f1520;border:1px solid #1e293b;padding:8px 12px;'
                    f'border-radius:6px;margin:4px 0;font-size:11px;">'
                    f'<span style="color:#00E5FF;font-weight:bold;">{record["evidence_id"]}</span>'
                    f'<br/><span style="color:#6B7280;">{record["evidence_type"]} — {record["file_name"]}</span>'
                    f'<br/><span style="color:#22C55E;">✓ {record["status"]}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("---")
    st.markdown("### ⚡ Quick Demo")
    if st.button("⚡ Load Complete Demo Case", type="primary", use_container_width=True, help="Populate all 5 tabs with realistic multimodal crime case"):
        from sample_data import load_sample_case_data
        load_sample_case_data(st.session_state)
        st.toast("⚡ Loaded Complete Multimodal Forensic Case!")
        st.rerun()

    # Reset
    if st.button("🗑️ Clear All Evidence", use_container_width=True):
        for key in ["evidence_chain", "master_timeline", "image_analyses",
                     "audio_analyses", "video_analyses", "chat_history"]:
            st.session_state[key] = []
        st.rerun()

    st.markdown("---")
    st.markdown(
        '<div style="text-align:center;color:#4B5563;font-size:10px;">'
        'NASSCOM FutureSkills<br/>Skill Wallet Capstone Project 2<br/>'
        '© 2024 CrimeVision AI'
        '</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────
# Main Content — Header
# ─────────────────────────────────────────────────────────────
mode_label = "DEMO MODE" if st.session_state.demo_mode else "LIVE MODE"
mode_class = "status-demo" if st.session_state.demo_mode else "status-live"

st.markdown(
    f"""
    <div class="forensic-header">
        <h1>🔬 {APP_TITLE}</h1>
        <p>{APP_SUBTITLE}</p>
        <div class="status-badge {mode_class}">{mode_label}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.get("evidence_chain"):
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, rgba(0, 229, 255, 0.08) 0%, rgba(124, 77, 255, 0.08) 100%);
        border: 1px solid rgba(0, 229, 255, 0.3); border-radius: 12px; padding: 16px 22px; margin-bottom: 20px;
        display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong style="color: #00E5FF; font-size: 15px;">🚀 Quick Start: Turnkey Multimodal Forensic Demo</strong>
                <p style="color: #94a3b8; font-size: 13px; margin: 4px 0 0 0;">
                    Load a coherent crime case (Vault Burglary & Armed Assault) across photography, 911 dispatch audio, and CCTV surveillance in 1 click.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_demo_btn1, col_demo_btn2, col_demo_btn3 = st.columns([1, 2, 1])
    with col_demo_btn2:
        if st.button("⚡ Click to Load Complete Forensic Case", type="primary", use_container_width=True):
            from sample_data import load_sample_case_data
            load_sample_case_data(st.session_state)
            st.toast("⚡ Loaded Complete Multimodal Forensic Case!")
            st.rerun()

# ─────────────────────────────────────────────────────────────
# Main Content — Tabs
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Crime Scene Tagger",
    "🎙️ Audio Transcription",
    "📹 Video Analysis",
    "🔗 Fusion & Chat",
    "📄 PDF Report",
])

with tab1:
    from image_analysis import render_image_analysis_tab
    render_image_analysis_tab()

with tab2:
    from audio_analysis import render_audio_analysis_tab
    render_audio_analysis_tab()

with tab3:
    from video_analysis import render_video_analysis_tab
    render_video_analysis_tab()

with tab4:
    from fusion_chat import render_fusion_chat_tab
    render_fusion_chat_tab()

with tab5:
    from pdf_report import render_pdf_export_tab
    render_pdf_export_tab()
