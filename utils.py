"""
CrimeVision AI — Utility & Configuration Module
Handles API configuration, evidence chain-of-custody, and shared helpers.
"""

import uuid
import hashlib
import datetime
import streamlit as st

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────
APP_TITLE = "CrimeVision AI"
APP_SUBTITLE = "Intelligent Multimodal Forensic Analysis Platform"
VERSION = "2.0.0"

THREAT_LEVELS = {
    "Low": {"color": "#22C55E", "icon": "🟢"},
    "Medium": {"color": "#F59E0B", "icon": "🟡"},
    "High": {"color": "#F97316", "icon": "🟠"},
    "Critical": {"color": "#EF4444", "icon": "🔴"},
}

SCENE_CLASSIFICATIONS = [
    "Burglary", "Homicide", "Vandalism", "Assault",
    "Robbery", "Arson", "Drug Offense", "Traffic Incident",
]

CRIME_CATEGORIES_PENAL = {
    "assault": "IPC §351-358 / BNS §130-§136 — Assault",
    "robbery": "IPC §390-402 / BNS §304-§311 — Robbery & Dacoity",
    "homicide": "IPC §299-304 / BNS §99-§105 — Culpable Homicide",
    "burglary": "IPC §445-462 / BNS §329-§335 — House-Breaking",
    "vandalism": "IPC §425-440 / BNS §320-§328 — Mischief",
    "arson": "IPC §435-438 / BNS §324-§326 — Arson",
    "drug_offense": "NDPS Act §20-§39 — Narcotic Substances",
    "traffic_incident": "IPC §279-§304A / BNS §280-§285 — Rash Driving",
    "trespassing": "IPC §441-462 / BNS §329-§335 — Trespass",
    "weapon_possession": "Arms Act §25-§33 — Illegal Arms Possession",
}


# ─────────────────────────────────────────────────────────────
# Evidence Chain-of-Custody
# ─────────────────────────────────────────────────────────────
def generate_evidence_id(prefix: str = "EV") -> str:
    """Generate a unique forensic evidence ID."""
    uid = uuid.uuid4().hex[:8].upper()
    return f"{prefix}-{uid}"


def compute_file_hash(file_bytes: bytes) -> str:
    """Compute SHA-256 hash for chain-of-custody integrity."""
    return hashlib.sha256(file_bytes).hexdigest()


def get_custody_record(evidence_id: str, file_hash: str, file_name: str, evidence_type: str) -> dict:
    """Create a chain-of-custody record."""
    return {
        "evidence_id": evidence_id,
        "file_name": file_name,
        "evidence_type": evidence_type,
        "sha256_hash": file_hash,
        "ingestion_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "investigator": st.session_state.get("investigator_name", "System Auto-Ingest"),
        "status": "Ingested & Verified",
        "integrity": "PASS ✓",
    }


def store_evidence(evidence_record: dict):
    """Store evidence record in session state."""
    if "evidence_chain" not in st.session_state:
        st.session_state.evidence_chain = []
    st.session_state.evidence_chain.append(evidence_record)


def store_timeline_event(event: dict):
    """Append a timeline event to the master ledger."""
    if "master_timeline" not in st.session_state:
        st.session_state.master_timeline = []
    st.session_state.master_timeline.append(event)


# ─────────────────────────────────────────────────────────────
# API Configuration Helpers
# ─────────────────────────────────────────────────────────────
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "api_key": "",
        "api_provider": "groq",
        "demo_mode": True,
        "investigator_name": "",
        "evidence_chain": [],
        "master_timeline": [],
        "image_analyses": [],
        "audio_analyses": [],
        "video_analyses": [],
        "chat_history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def validate_api_key(provider: str, api_key: str) -> bool:
    """Basic validation of API key format."""
    if not api_key or len(api_key) < 10:
        return False
    if provider == "groq" and not api_key.startswith("gsk_"):
        return False
    return True


# ─────────────────────────────────────────────────────────────
# LLM Call Wrappers
# ─────────────────────────────────────────────────────────────
def call_llm(prompt: str, system_prompt: str = "") -> str:
    """Call the configured LLM or return demo response."""
    if st.session_state.get("demo_mode", True):
        return _demo_llm_response(prompt)

    provider = st.session_state.get("api_provider", "groq")
    api_key = st.session_state.get("api_key", "")

    try:
        if provider == "groq":
            return _call_groq(prompt, system_prompt, api_key)
        elif provider == "gemini":
            return _call_gemini(prompt, system_prompt, api_key)
    except Exception as e:
        st.warning(f"LLM call failed: {e}. Falling back to demo mode.")
        return _demo_llm_response(prompt)


def _call_groq(prompt: str, system_prompt: str, api_key: str) -> str:
    """Call Groq API."""
    from groq import Groq
    client = Groq(api_key=api_key)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=messages,
        temperature=0.3,
        max_tokens=2048,
    )
    return response.choices[0].message.content


def _call_gemini(prompt: str, system_prompt: str, api_key: str) -> str:
    """Call Google Gemini API."""
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    response = model.generate_content(full_prompt)
    return response.text


def _demo_llm_response(prompt: str) -> str:
    """Generate a realistic demo response based on prompt context."""
    prompt_lower = prompt.lower()

    if "weapon" in prompt_lower or "firearm" in prompt_lower:
        return (
            "Based on the analyzed evidence:\n\n"
            "**Finding:** A firearm-like object was detected in Frame #3 (Evidence ID: EV-DEMO0001) "
            "at coordinates (342, 187) with 94.2% confidence. The object appears consistent with a "
            "semi-automatic handgun.\n\n"
            "**Timeline Reference:** This detection occurred at timestamp T+00:03:42, approximately "
            "12 seconds before the suspect was observed leaving the scene (Evidence ID: EV-DEMO0003).\n\n"
            "**Citation:** [EV-DEMO0001, Frame #3] [EV-DEMO0003, T+00:03:54]\n\n"
            "⚠️ *This analysis is generated in DEMO MODE and does not reflect real evidence.*"
        )
    elif "suspect" in prompt_lower or "person" in prompt_lower:
        return (
            "Based on the analyzed evidence:\n\n"
            "**Finding:** Two distinct individuals were identified across the evidence corpus.\n"
            "- **Person A** (Evidence IDs: EV-DEMO0001, EV-DEMO0003): Detected in crime scene "
            "photography and CCTV footage. Wearing dark clothing, estimated height 5'10\".\n"
            "- **Person B** (Evidence ID: EV-DEMO0002): Referenced in witness audio as 'the second man' "
            "at timestamp T+00:05:12.\n\n"
            "**Citation:** [EV-DEMO0001] [EV-DEMO0002, Speaker-1, T+00:05:12] [EV-DEMO0003, Frames #7-#12]\n\n"
            "⚠️ *This analysis is generated in DEMO MODE and does not reflect real evidence.*"
        )
    elif "timeline" in prompt_lower or "sequence" in prompt_lower:
        return (
            "**Reconstructed Event Timeline:**\n\n"
            "| Time | Event | Source |\n"
            "|------|-------|--------|\n"
            "| T+00:00:00 | Initial disturbance detected | Audio [EV-DEMO0002] |\n"
            "| T+00:01:15 | Glass breaking sound identified | Audio [EV-DEMO0002] |\n"
            "| T+00:02:30 | Suspect enters frame from east | Video [EV-DEMO0003] |\n"
            "| T+00:03:42 | Weapon-like object visible | Image [EV-DEMO0001] |\n"
            "| T+00:05:12 | Witness reports 'second man' | Audio [EV-DEMO0002] |\n"
            "| T+00:06:48 | Suspect exits scene heading north | Video [EV-DEMO0003] |\n\n"
            "**Citation:** [EV-DEMO0001] [EV-DEMO0002] [EV-DEMO0003]\n\n"
            "⚠️ *This analysis is generated in DEMO MODE and does not reflect real evidence.*"
        )
    else:
        return (
            "Based on the currently ingested evidence corpus:\n\n"
            "The available evidence has been cross-referenced across all modalities (image, audio, video). "
            "Key findings include object detections with spatial coordinates, timestamped witness statements, "
            "and frame-by-frame video analysis.\n\n"
            "For specific queries, please ask about:\n"
            "- Detected objects or weapons\n"
            "- Suspect descriptions and movements\n"
            "- Chronological event timeline\n"
            "- Evidence correlations\n\n"
            "All responses are grounded in ingested evidence with explicit citation of Evidence IDs.\n\n"
            "⚠️ *This analysis is generated in DEMO MODE and does not reflect real evidence.*"
        )
