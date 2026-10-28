# 🔬 CrimeVision AI — Intelligent Multimodal Forensic Analysis Platform

**NASSCOM FutureSkills — Skill Wallet Capstone Project 2**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

---

## 📋 Overview

CrimeVision AI is an automated forensic intelligence platform that fuses **image**, **video**, and **audio** evidence to:

- 🔍 **Detect** people, weapons, blood spatter, and forced entry points (RT-DETR simulation)
- 🎙️ **Transcribe** witness audio via OpenAI Whisper with speaker tagging
- 📹 **Analyze** CCTV footage with frame-by-frame event tracking
- 🔗 **Fuse** all evidence into a unified master forensic timeline
- 💬 **Chat** with evidence using grounded RAG (zero hallucination, citation-based)
- 📄 **Export** court-admissible PDF reports via ReportLab

---

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Streamlit Community Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy with:
   - **Main file path:** `app.py`
   - **Python version:** 3.9+

---

## 🏗️ Architecture

```
nasscom/
├── app.py                 # Main Streamlit entry point
├── utils.py               # Configuration, chain-of-custody, LLM wrappers
├── image_analysis.py      # Tab 1: RT-DETR object detection simulation
├── audio_analysis.py      # Tab 2: Whisper transcription & timeline
├── video_analysis.py      # Tab 3: CCTV frame analysis & tracking
├── fusion_chat.py         # Tab 4: Multimodal fusion & evidence chat
├── pdf_report.py          # Tab 5: ReportLab PDF export
├── requirements.txt       # Python dependencies
├── packages.txt           # System dependencies (Streamlit Cloud)
└── .streamlit/
    └── config.toml        # Theme configuration
```

---

## 🔐 API Configuration

| Provider | Model | Key Format |
|----------|-------|------------|
| **Groq** | Llama 3.1 70B | `gsk_...` |
| **Google Gemini** | Gemini 1.5 Flash | `AIza...` |

> **Demo Mode**: The platform operates fully without an API key using intelligent simulated responses.

---

## 📊 Epics Coverage

| Epic | Description | Status |
|------|-------------|--------|
| Epic 1 | Initialization & Environment | ✅ |
| Epic 2 | RT-DETR Object Detection & Scene Captioning | ✅ |
| Epic 3 | Whisper Audio Transcription & Timeline | ✅ |
| Epic 4 | Video Frame Tracking & Crime Classification | ✅ |
| Epic 5 | Multimodal Timeline Fusion & Evidence Chat | ✅ |
| Epic 6 | Dashboard, Testing, ReportLab PDF Export | ✅ |

---

## 🛡️ Features

- **Chain-of-Custody Tracking**: SHA-256 file hashing, Evidence IDs, timestamps
- **Zero External Database Dependencies**: All state managed in Streamlit session
- **Dark Forensic Theme**: Professional UI with micro-animations
- **Demo Fallback**: Works without API keys or ML models installed
- **Court-Admissible PDF Reports**: Professional ReportLab-generated documents

---

## 📜 License

Built for educational purposes — NASSCOM FutureSkills Skill Wallet Program.
