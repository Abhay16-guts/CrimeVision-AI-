"""
CrimeVision AI — Multimodal Fusion & Evidence Chat Module (Epic 5)
Unified forensic event ledger + Grounded RAG evidence chat.
"""

import datetime
import streamlit as st
from utils import call_llm


# ─────────────────────────────────────────────────────────────
# Master Timeline Fusion
# ─────────────────────────────────────────────────────────────
def build_master_timeline() -> list:
    """Fuse all evidence sources into a unified master timeline."""
    events = []

    # Image analysis events
    for analysis in st.session_state.get("image_analyses", []):
        for det in analysis.get("detections", []):
            events.append({
                "source_type": "🖼️ Image",
                "evidence_id": analysis["evidence_id"],
                "timestamp": analysis["timestamp"],
                "event": f"Detected: {det['label']} (confidence: {det['confidence']:.1%})",
                "details": f"Location: ({det['center'][0]}, {det['center'][1]}) | Category: {det['category']}",
                "severity": "Critical" if det["threat_weight"] > 0.7 else ("High" if det["threat_weight"] > 0.4 else "Medium"),
            })

    # Audio analysis events
    for analysis in st.session_state.get("audio_analyses", []):
        for evt in analysis.get("transcription", {}).get("key_events", []):
            events.append({
                "source_type": "🎙️ Audio",
                "evidence_id": analysis["evidence_id"],
                "timestamp": analysis["timestamp"],
                "event": evt["event"],
                "details": f"Speaker: {evt.get('speaker', 'N/A')} | Time in audio: {evt['time']}",
                "severity": evt.get("significance", "Medium"),
            })

    # Video analysis events
    for analysis in st.session_state.get("video_analyses", []):
        for evt in analysis.get("events", []):
            events.append({
                "source_type": "📹 Video",
                "evidence_id": analysis["evidence_id"],
                "timestamp": analysis["timestamp"],
                "event": evt["event"],
                "details": f"Frame #{evt['frame_number']} | {evt['timestamp_fmt']} | ⚖️ {evt['penal_code']}",
                "severity": evt.get("severity", "Medium"),
            })

    # Sort by timestamp
    events.sort(key=lambda x: x.get("timestamp", ""))
    return events


def build_evidence_context() -> str:
    """Build a comprehensive evidence context string for RAG."""
    context_parts = []

    # Chain of custody
    chain = st.session_state.get("evidence_chain", [])
    if chain:
        context_parts.append("=== CHAIN OF CUSTODY ===")
        for record in chain:
            context_parts.append(
                f"Evidence ID: {record['evidence_id']} | Type: {record['evidence_type']} | "
                f"File: {record['file_name']} | Hash: {record['sha256_hash'][:16]}... | "
                f"Status: {record['status']}"
            )

    # Image analyses
    for analysis in st.session_state.get("image_analyses", []):
        context_parts.append(f"\n=== IMAGE ANALYSIS: {analysis['evidence_id']} ===")
        context_parts.append(f"File: {analysis['file_name']}")
        context_parts.append(f"Threat Level: {analysis.get('threat_level', 'N/A')}")
        context_parts.append(f"Scene Classification: {analysis.get('scene_classification', 'N/A')}")
        for det in analysis.get("detections", []):
            context_parts.append(
                f"  - Detected: {det['label']} | Confidence: {det['confidence']:.1%} | "
                f"Position: ({det['center'][0]}, {det['center'][1]}) | Category: {det['category']}"
            )

    # Audio analyses
    for analysis in st.session_state.get("audio_analyses", []):
        context_parts.append(f"\n=== AUDIO ANALYSIS: {analysis['evidence_id']} ===")
        context_parts.append(f"File: {analysis['file_name']}")
        transcription = analysis.get("transcription", {})
        context_parts.append(f"Full Transcription: {transcription.get('full_text', 'N/A')}")
        for evt in transcription.get("key_events", []):
            context_parts.append(
                f"  - [{evt['time']}] {evt['event']} (Speaker: {evt.get('speaker', 'N/A')}, "
                f"Significance: {evt.get('significance', 'N/A')})"
            )

    # Video analyses
    for analysis in st.session_state.get("video_analyses", []):
        context_parts.append(f"\n=== VIDEO ANALYSIS: {analysis['evidence_id']} ===")
        context_parts.append(f"File: {analysis['file_name']} | Duration: {analysis.get('duration', 0):.1f}s")
        for evt in analysis.get("events", []):
            context_parts.append(
                f"  - [{evt['timestamp_fmt']}] Frame #{evt['frame_number']}: {evt['event']} | "
                f"Category: {evt['category']} | Penal: {evt['penal_code']} | "
                f"Confidence: {evt['confidence']:.1%}"
            )

    return "\n".join(context_parts) if context_parts else "No evidence has been ingested yet."


# ─────────────────────────────────────────────────────────────
# Tab Renderer
# ─────────────────────────────────────────────────────────────
def render_fusion_chat_tab():
    """Render Tab 4: Multimodal Fusion & Grounded Evidence Chat."""
    st.markdown("## 🔗 Multimodal Fusion & Grounded Evidence Chat")
    st.markdown(
        "> Unified master forensic event ledger combining all evidence sources. "
        "Ask questions grounded in ingested evidence with **zero hallucination** — "
        "all answers cite specific Evidence IDs."
    )

    # ── Master Timeline ──
    master_timeline = build_master_timeline()

    st.markdown("### 📊 Master Forensic Event Ledger")

    if not master_timeline:
        st.info(
            "📭 No evidence has been ingested yet. Upload images, audio, or video in the "
            "preceding tabs to populate the master timeline."
        )
    else:
        # Summary stats
        source_counts = {}
        severity_counts = {}
        evidence_ids = set()

        for evt in master_timeline:
            source_counts[evt["source_type"]] = source_counts.get(evt["source_type"], 0) + 1
            severity_counts[evt["severity"]] = severity_counts.get(evt["severity"], 0) + 1
            evidence_ids.add(evt["evidence_id"])

        cols = st.columns(4)
        cols[0].metric("📦 Total Evidence Items", len(evidence_ids))
        cols[1].metric("📋 Total Events", len(master_timeline))
        cols[2].metric("🔴 Critical Events", severity_counts.get("Critical", 0))
        cols[3].metric("🟠 High Events", severity_counts.get("High", 0))

        # Source breakdown
        st.markdown("#### Evidence Source Breakdown")
        source_cols = st.columns(len(source_counts) if source_counts else 1)
        for i, (source, count) in enumerate(source_counts.items()):
            source_cols[i].metric(source, count)

        st.markdown("---")

        # Timeline display
        st.markdown("#### 🕐 Unified Chronological Timeline")

        for i, evt in enumerate(master_timeline):
            sev = evt.get("severity", "Medium")
            sev_colors = {"Critical": "#EF4444", "High": "#F97316", "Medium": "#F59E0B", "Low": "#22C55E"}
            sev_color = sev_colors.get(sev, "#9CA3AF")

            st.markdown(
                f"""
                <div style="background:#111827;border:1px solid #374151;border-left:4px solid {sev_color};
                padding:12px 18px;margin:5px 0;border-radius:6px;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div style="flex:1;">
                            <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
                                <span style="font-size:14px;">{evt['source_type']}</span>
                                <span style="color:#00E5FF;font-weight:bold;font-size:12px;">
                                    {evt['evidence_id']}
                                </span>
                                <span style="background:{sev_color}22;color:{sev_color};padding:2px 8px;
                                border-radius:4px;font-size:11px;font-weight:bold;">
                                    {sev}
                                </span>
                            </div>
                            <div style="color:#E0E0E0;font-size:14px;margin-bottom:4px;">
                                {evt['event']}
                            </div>
                            <div style="color:#6B7280;font-size:12px;">
                                {evt['details']}
                            </div>
                        </div>
                        <div style="color:#4B5563;font-size:11px;min-width:40px;text-align:right;">
                            #{i + 1}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Evidence Chat ──
    st.markdown("---")
    st.markdown("### 💬 Grounded Evidence Q&A")
    st.markdown(
        "> Ask investigative questions. All responses are grounded in ingested evidence "
        "with explicit citation of **Evidence IDs**. Zero hallucination policy enforced."
    )

    # Display chat history
    for msg in st.session_state.get("chat_history", []):
        if msg["role"] == "user":
            st.markdown(
                f'<div style="background:#1a2332;border:1px solid #2d3a4e;padding:12px 16px;'
                f'margin:8px 0;border-radius:10px 10px 2px 10px;">'
                f'<span style="color:#00E5FF;font-size:12px;font-weight:bold;">🕵️ INVESTIGATOR</span>'
                f'<div style="color:#E0E0E0;margin-top:6px;">{msg["content"]}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="background:#0f1a24;border:1px solid #1e3a4e;padding:12px 16px;'
                f'margin:8px 0;border-radius:10px 10px 10px 2px;">'
                f'<span style="color:#F59E0B;font-size:12px;font-weight:bold;">🤖 CRIMEVISION AI</span>'
                f'<div style="color:#E0E0E0;margin-top:6px;">{msg["content"]}</div></div>',
                unsafe_allow_html=True,
            )

    # Chat input
    user_query = st.chat_input(
        "Ask about the evidence (e.g., 'Was a weapon visible before the suspect fled?')",
        key="evidence_chat_input",
    )

    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})

        evidence_context = build_evidence_context()

        system_prompt = (
            "You are CrimeVision AI, a forensic evidence analysis assistant. "
            "You MUST answer questions ONLY based on the provided evidence context. "
            "You MUST cite specific Evidence IDs (e.g., [EV-XXXXXXXX]) for every claim. "
            "If the evidence does not contain information to answer the question, say so explicitly. "
            "NEVER hallucinate or fabricate evidence. "
            "Use professional forensic language suitable for court documentation."
        )

        prompt = (
            f"=== EVIDENCE CONTEXT ===\n{evidence_context}\n\n"
            f"=== INVESTIGATOR QUESTION ===\n{user_query}\n\n"
            f"Respond with a grounded analysis, citing all relevant Evidence IDs. "
            f"If the question cannot be answered from available evidence, state that clearly."
        )

        with st.spinner("🔍 Analyzing evidence corpus..."):
            response = call_llm(prompt, system_prompt)

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    # Suggested queries
    if not st.session_state.get("chat_history"):
        st.markdown("#### 💡 Suggested Investigative Queries")
        suggestions = [
            "What weapons were detected across all evidence?",
            "Reconstruct the full chronological timeline of events.",
            "Were any suspects identified? Describe their movements.",
            "What is the overall threat assessment for this case?",
            "Which evidence items require immediate forensic processing?",
        ]
        suggestion_cols = st.columns(2)
        for i, suggestion in enumerate(suggestions):
            col = suggestion_cols[i % 2]
            col.markdown(
                f'<div style="background:#1a1f2e;border:1px solid #374151;padding:10px 14px;'
                f'margin:4px 0;border-radius:6px;color:#9CA3AF;font-size:13px;cursor:pointer;">'
                f'💬 {suggestion}</div>',
                unsafe_allow_html=True,
            )
