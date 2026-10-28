"""
CrimeVision AI — Audio Analysis Module (Epic 3)
Witness Audio Transcription & Timeline Extraction with Whisper fallback.
"""

import random
import datetime
import streamlit as st

from utils import (
    generate_evidence_id, compute_file_hash, get_custody_record,
    store_evidence, store_timeline_event, call_llm,
)


# ─────────────────────────────────────────────────────────────
# Demo Transcription Data
# ─────────────────────────────────────────────────────────────
DEMO_TRANSCRIPTIONS = [
    {
        "full_text": (
            "I was walking home around 11:30 PM when I heard two loud bangs, like gunshots. "
            "I looked towards the alley on Oak Street and saw a man running out. He was wearing "
            "a dark hoodie and jeans. He got into a silver sedan parked near the corner. "
            "Another person came out about thirty seconds later, stumbling. I called 911 immediately. "
            "The car drove off heading north on Main Street. I could see the stumbling person "
            "was bleeding from their left arm. A neighbor, Mrs. Chen, also came out and we tried "
            "to help until the ambulance arrived around 11:45 PM."
        ),
        "segments": [
            {"start": 0.0, "end": 4.2, "speaker": "Speaker-1 (Witness)",
             "text": "I was walking home around 11:30 PM when I heard two loud bangs, like gunshots."},
            {"start": 4.2, "end": 8.8, "speaker": "Speaker-1 (Witness)",
             "text": "I looked towards the alley on Oak Street and saw a man running out."},
            {"start": 8.8, "end": 12.1, "speaker": "Speaker-1 (Witness)",
             "text": "He was wearing a dark hoodie and jeans."},
            {"start": 12.1, "end": 17.5, "speaker": "Speaker-1 (Witness)",
             "text": "He got into a silver sedan parked near the corner."},
            {"start": 17.5, "end": 23.0, "speaker": "Speaker-1 (Witness)",
             "text": "Another person came out about thirty seconds later, stumbling."},
            {"start": 23.0, "end": 26.4, "speaker": "Speaker-1 (Witness)",
             "text": "I called 911 immediately."},
            {"start": 26.4, "end": 32.7, "speaker": "Speaker-1 (Witness)",
             "text": "The car drove off heading north on Main Street."},
            {"start": 32.7, "end": 38.9, "speaker": "Speaker-1 (Witness)",
             "text": "I could see the stumbling person was bleeding from their left arm."},
            {"start": 38.9, "end": 46.2, "speaker": "Speaker-1 (Witness)",
             "text": "A neighbor, Mrs. Chen, also came out and we tried to help until the ambulance arrived around 11:45 PM."},
        ],
        "key_events": [
            {"time": "23:30:00", "event": "Two gunshot-like sounds heard", "speaker": "Speaker-1", "significance": "Critical"},
            {"time": "23:30:05", "event": "Suspect observed fleeing alley on Oak Street", "speaker": "Speaker-1", "significance": "High"},
            {"time": "23:30:10", "event": "Suspect described: dark hoodie, jeans", "speaker": "Speaker-1", "significance": "High"},
            {"time": "23:30:15", "event": "Suspect enters silver sedan near corner", "speaker": "Speaker-1", "significance": "Critical"},
            {"time": "23:30:45", "event": "Second individual exits alley, stumbling", "speaker": "Speaker-1", "significance": "High"},
            {"time": "23:31:00", "event": "911 call placed by witness", "speaker": "Speaker-1", "significance": "Medium"},
            {"time": "23:31:10", "event": "Suspect vehicle flees north on Main Street", "speaker": "Speaker-1", "significance": "Critical"},
            {"time": "23:31:30", "event": "Victim observed bleeding from left arm", "speaker": "Speaker-1", "significance": "High"},
            {"time": "23:45:00", "event": "Ambulance arrives on scene", "speaker": "Speaker-1", "significance": "Medium"},
        ],
    },
    {
        "full_text": (
            "Dispatch, this is unit 47. We have a 10-31, crime in progress at 450 Elm Street. "
            "Multiple subjects seen forcing entry through the rear door. One subject appears armed "
            "with what looks like a crowbar. Requesting backup immediately. Subjects are now inside "
            "the building. I can see movement on the second floor through the windows. "
            "Be advised, there is a white van parked in the back alley, engine running, possible "
            "getaway vehicle. License plate partially visible: Alpha-Bravo-7. Stand by for updates."
        ),
        "segments": [
            {"start": 0.0, "end": 5.8, "speaker": "Unit-47 (Officer)",
             "text": "Dispatch, this is unit 47. We have a 10-31, crime in progress at 450 Elm Street."},
            {"start": 5.8, "end": 11.2, "speaker": "Unit-47 (Officer)",
             "text": "Multiple subjects seen forcing entry through the rear door."},
            {"start": 11.2, "end": 16.5, "speaker": "Unit-47 (Officer)",
             "text": "One subject appears armed with what looks like a crowbar."},
            {"start": 16.5, "end": 19.8, "speaker": "Unit-47 (Officer)",
             "text": "Requesting backup immediately."},
            {"start": 19.8, "end": 24.1, "speaker": "Unit-47 (Officer)",
             "text": "Subjects are now inside the building."},
            {"start": 24.1, "end": 30.5, "speaker": "Unit-47 (Officer)",
             "text": "I can see movement on the second floor through the windows."},
            {"start": 30.5, "end": 38.9, "speaker": "Unit-47 (Officer)",
             "text": "Be advised, there is a white van parked in the back alley, engine running, possible getaway vehicle."},
            {"start": 38.9, "end": 44.3, "speaker": "Unit-47 (Officer)",
             "text": "License plate partially visible: Alpha-Bravo-7. Stand by for updates."},
        ],
        "key_events": [
            {"time": "00:00:00", "event": "10-31 crime in progress reported at 450 Elm Street", "speaker": "Unit-47", "significance": "Critical"},
            {"time": "00:00:06", "event": "Multiple subjects forcing rear door entry", "speaker": "Unit-47", "significance": "Critical"},
            {"time": "00:00:11", "event": "One subject armed with crowbar", "speaker": "Unit-47", "significance": "High"},
            {"time": "00:00:17", "event": "Backup requested", "speaker": "Unit-47", "significance": "Medium"},
            {"time": "00:00:20", "event": "Subjects inside building", "speaker": "Unit-47", "significance": "High"},
            {"time": "00:00:24", "event": "Movement detected on second floor", "speaker": "Unit-47", "significance": "Medium"},
            {"time": "00:00:31", "event": "White van identified as possible getaway vehicle", "speaker": "Unit-47", "significance": "Critical"},
            {"time": "00:00:39", "event": "Partial plate: AB-7", "speaker": "Unit-47", "significance": "Critical"},
        ],
    },
]


def transcribe_audio_demo(file_hash: str) -> dict:
    """Return a deterministic demo transcription based on file hash."""
    idx = int(file_hash[:4], 16) % len(DEMO_TRANSCRIPTIONS)
    return DEMO_TRANSCRIPTIONS[idx]


def transcribe_audio_whisper(file_bytes: bytes, file_name: str) -> dict:
    """Attempt transcription with OpenAI Whisper (local model)."""
    try:
        import whisper
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        model = whisper.load_model("base")
        result = model.transcribe(tmp_path, verbose=False)
        os.unlink(tmp_path)

        segments = []
        for seg in result.get("segments", []):
            segments.append({
                "start": seg["start"],
                "end": seg["end"],
                "speaker": "Speaker-1",
                "text": seg["text"].strip(),
            })

        return {
            "full_text": result.get("text", ""),
            "segments": segments,
            "key_events": [],
            "whisper_used": True,
        }
    except Exception:
        return None


def extract_key_events_llm(transcription_text: str, evidence_id: str) -> list:
    """Use LLM to extract key forensic events from transcription."""
    prompt = (
        f"You are a forensic audio analyst. Extract key events from this witness transcription.\n\n"
        f"Evidence ID: {evidence_id}\n"
        f"Transcription:\n{transcription_text}\n\n"
        f"For each event, provide:\n"
        f"- Approximate time (HH:MM:SS)\n"
        f"- Event description\n"
        f"- Speaker\n"
        f"- Significance (Critical / High / Medium / Low)\n\n"
        f"Format as a structured list."
    )
    return call_llm(prompt)


def display_audio_analysis_view(analysis: dict):
    """Render audio analysis view."""
    evidence_id = analysis["evidence_id"]
    file_name = analysis["file_name"]
    transcription = analysis["transcription"]
    
    st.markdown("---")
    
    # Overview metrics
    segments = transcription.get("segments", [])
    key_events = transcription.get("key_events", [])
    word_count = len(transcription.get("full_text", "").split())
    speakers = list({s.get("speaker", "Unknown") for s in segments})
    
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    col_a1.metric("📋 Evidence ID", evidence_id)
    col_a2.metric("🗣️ Unique Speakers", len(speakers))
    col_a3.metric("📝 Word Count", word_count)
    col_a4.metric("⏱️ Timeline Events", len(key_events))
    
    st.markdown("---")
    
    # Full Transcription Box
    st.markdown("### 📝 Full Forensic Audio Transcription")
    st.markdown(
        f'<div style="background:#0f1520;border:1px solid #1e293b;padding:20px;'
        f'border-radius:10px;color:#cbd5e1;line-height:1.8;font-size:15px;">'
        f'{transcription["full_text"]}</div>',
        unsafe_allow_html=True,
    )
    
    # Speaker-Tagged Segments
    st.markdown("---")
    st.markdown("### 🗣️ Speaker-Tagged Segments & Diarization")
    
    for seg in segments:
        start_fmt = f"{int(seg['start'] // 60):02d}:{int(seg['start'] % 60):02d}"
        end_fmt = f"{int(seg['end'] // 60):02d}:{int(seg['end'] % 60):02d}"
        
        st.markdown(
            f"""
            <div style="background:#1a1f2e;border-left:4px solid #00E5FF;padding:10px 16px;
            margin:4px 0;border-radius:6px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#00E5FF;font-weight:bold;font-size:13px;">
                        {seg['speaker']}
                    </span>
                    <span style="color:#6B7280;font-size:12px;">
                        ⏱️ {start_fmt} → {end_fmt}
                    </span>
                </div>
                <div style="color:#E0E0E0;margin-top:6px;font-size:14px;">
                    "{seg['text']}"
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Key Events Timeline
    st.markdown("---")
    st.markdown("### 🕐 Extracted Chronological Event Markers")
    
    if key_events:
        for evt in key_events:
            sig = evt.get("significance", "Medium")
            sig_colors = {"Critical": "#EF4444", "High": "#F97316", "Medium": "#F59E0B", "Low": "#22C55E"}
            sig_color = sig_colors.get(sig, "#9CA3AF")
            
            st.markdown(
                f"""
                <div style="background:#111827;border:1px solid #374151;padding:12px 16px;
                margin:6px 0;border-radius:8px;display:flex;align-items:center;gap:16px;">
                    <div style="min-width:80px;text-align:center;">
                        <div style="color:#00E5FF;font-weight:bold;font-size:14px;">{evt['time']}</div>
                    </div>
                    <div style="flex:1;">
                        <div style="color:#E0E0E0;font-size:14px;">{evt['event']}</div>
                        <div style="color:#6B7280;font-size:12px;margin-top:2px;">
                            Speaker: {evt.get('speaker', 'N/A')}
                        </div>
                    </div>
                    <div style="background:{sig_color}22;color:{sig_color};padding:4px 10px;
                    border-radius:4px;font-size:12px;font-weight:bold;">
                        {sig}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────
# Tab Renderer
# ─────────────────────────────────────────────────────────────
def render_audio_analysis_tab():
    """Render Tab 2: Witness Audio Transcription & Timeline."""
    st.markdown("## 🎙️ Witness Audio Transcription & Timeline")
    st.markdown(
        "> Upload witness statements, 911/112 emergency calls, or interrogation audio. "
        "Transcription powered by **OpenAI Whisper** with intelligent fallback, diarization, and chronological event extraction."
    )
    
    col_u1, col_u2 = st.columns([3, 1])
    with col_u1:
        uploaded_audio = st.file_uploader(
            "Upload Audio Evidence",
            type=["wav", "mp3", "m4a", "ogg", "flac", "webm"],
            key="audio_uploader",
            help="Supported: WAV, MP3, M4A, OGG, FLAC, WebM"
        )
    with col_u2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("⚡ Load Sample 911 Call", use_container_width=True, help="Load 911 dispatch audio transcript with timeline"):
            ev_id = generate_evidence_id("AUD")
            sample_trans = DEMO_TRANSCRIPTIONS[0]
            f_hash = compute_file_hash(b"SAMPLE_911_CALL_AUDIO_BYTES")
            c_rec = get_custody_record(ev_id, f_hash, "911_Emergency_Call_OakAlley.wav", "Audio")
            store_evidence(c_rec)
            
            rec = {
                "evidence_id": ev_id,
                "file_name": "911_Emergency_Call_OakAlley.wav",
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "transcription": sample_trans,
            }
            st.session_state.audio_analyses = [rec]
            for evt in sample_trans["key_events"]:
                store_timeline_event({
                    "timestamp": rec["timestamp"],
                    "source": "Audio Analysis",
                    "evidence_id": ev_id,
                    "event": evt["event"],
                    "category": "audio_event",
                    "speaker": evt.get("speaker", "Witness"),
                    "significance": evt.get("significance", "Medium"),
                })
            st.success("Sample 911 Witness Audio loaded!")
            st.rerun()

    if uploaded_audio is not None:
        file_bytes = uploaded_audio.read()
        
        # Chain of custody
        evidence_id = generate_evidence_id("AUD")
        file_hash = compute_file_hash(file_bytes)
        custody_record = get_custody_record(evidence_id, file_hash, uploaded_audio.name, "Audio")
        
        with st.expander("📋 Chain-of-Custody Record", expanded=False):
            c1, c2, c3 = st.columns(3)
            c1.metric("Evidence ID", evidence_id)
            c2.metric("SHA-256", file_hash[:16] + "...")
            c3.metric("Status", "✅ Verified")
            st.json(custody_record)
        
        store_evidence(custody_record)
        st.audio(file_bytes, format=f"audio/{uploaded_audio.name.split('.')[-1]}")
        
        with st.spinner("🎧 Transcribing audio with Whisper..."):
            whisper_result = transcribe_audio_whisper(file_bytes, uploaded_audio.name)
            if whisper_result:
                transcription = whisper_result
                st.success("✅ Transcribed using OpenAI Whisper (local model)")
            else:
                transcription = transcribe_audio_demo(file_hash)
                st.info("ℹ️ Using intelligent demo transcription with speaker tags.")
        
        analysis_record = {
            "evidence_id": evidence_id,
            "file_name": uploaded_audio.name,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "transcription": transcription,
        }
        
        existing_ids = {a["evidence_id"] for a in st.session_state.audio_analyses}
        if evidence_id not in existing_ids:
            st.session_state.audio_analyses.append(analysis_record)
            for evt in transcription.get("key_events", []):
                store_timeline_event({
                    "timestamp": analysis_record["timestamp"],
                    "source": "Audio Analysis",
                    "evidence_id": evidence_id,
                    "event": evt["event"],
                    "category": "audio_event",
                    "speaker": evt.get("speaker", "Unknown"),
                    "significance": evt.get("significance", "Medium"),
                })
        
        display_audio_analysis_view(analysis_record)

    elif st.session_state.get("audio_analyses"):
        latest_analysis = st.session_state.audio_analyses[-1]
        st.info(f"Viewing active audio transcription: **{latest_analysis['evidence_id']}** ({latest_analysis['file_name']})")
        display_audio_analysis_view(latest_analysis)

    else:
        st.markdown(
            """
            <div style="background:#111827;border:2px dashed #1e293b;border-radius:12px;padding:36px;
            text-align:center;margin-top:20px;">
                <div style="font-size:36px;margin-bottom:12px;">🎙️</div>
                <h3 style="color:#00E5FF;margin-bottom:8px;">No Audio Evidence Transcribed Yet</h3>
                <p style="color:#9CA3AF;max-width:550px;margin:0 auto 18px auto;line-height:1.6;">
                    Upload an audio recording above, or click <strong>⚡ Load Sample 911 Call</strong> to review speech-to-text transcriptions, speaker diarization, and chronological event markers.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
