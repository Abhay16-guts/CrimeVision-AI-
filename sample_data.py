"""
CrimeVision AI — Sample Demonstration Dataset Generator
Provides turnkey sample forensic evidence (images, audio transcripts, CCTV video frames)
for instant zero-upload demonstration and testing on Streamlit Community Cloud.
"""

import io
import datetime
from PIL import Image, ImageDraw, ImageFont
from utils import (
    generate_evidence_id, compute_file_hash, get_custody_record,
    store_evidence, store_timeline_event,
)
from image_analysis import simulate_detection, draw_detections, compute_threat_level, classify_scene, generate_investigative_leads
from video_analysis import generate_demo_frames, analyze_frames
from audio_analysis import DEMO_TRANSCRIPTIONS

def create_synthetic_crime_scene_image() -> Image.Image:
    """Generate a realistic synthetic crime scene visualization."""
    w, h = 800, 500
    img = Image.new("RGB", (w, h), color=(22, 27, 34))
    draw = ImageDraw.Draw(img)

    # Room perspective walls and floor
    # Floor
    draw.polygon([(0, 320), (w, 320), (w, h), (0, h)], fill=(33, 38, 45))
    # Wall panels
    draw.rectangle([0, 0, w, 320], fill=(13, 17, 23))
    for x in range(100, w, 150):
        draw.line([(x, 0), (x, 320)], fill=(22, 27, 34), width=2)
    # Floor grid / tiles
    for y in range(330, h, 30):
        draw.line([(0, y), (w, y)], fill=(48, 54, 61), width=1)
    for x in range(0, w, 80):
        draw.line([(x, 320), (x - 60, h)], fill=(48, 54, 61), width=1)

    # Window with forced entry
    draw.rectangle([60, 40, 240, 260], outline=(88, 166, 255), width=3)
    draw.line([(60, 150), (240, 150)], fill=(88, 166, 255), width=2)
    draw.line([(150, 40), (150, 260)], fill=(88, 166, 255), width=2)
    # Shattered glass lines
    draw.line([(110, 100), (180, 210)], fill=(240, 246, 252), width=2)
    draw.line([(180, 210), (130, 240)], fill=(240, 246, 252), width=1)
    draw.line([(130, 120), (210, 140)], fill=(240, 246, 252), width=2)

    # Doorway / rear exit
    draw.rectangle([540, 60, 720, 320], fill=(10, 12, 16), outline=(139, 148, 158), width=3)
    draw.rectangle([550, 70, 710, 315], fill=(7, 10, 13))

    # Evidence markers (Yellow cones)
    def draw_marker(cx, cy, number):
        draw.polygon([(cx, cy - 25), (cx - 15, cy + 10), (cx + 15, cy + 10)], fill=(245, 158, 11), outline=(0, 0, 0))
        draw.text((cx - 3, cy - 5), str(number), fill=(0, 0, 0))

    draw_marker(210, 370, 1)
    draw_marker(430, 410, 2)
    draw_marker(640, 350, 3)

    # Blood spatter pattern near marker 2
    for offset in [(-10, -5), (5, -8), (-3, 6), (12, 4), (-15, 12), (18, -12), (0, 0)]:
        bx = 430 + offset[0]
        by = 410 + offset[1]
        draw.ellipse([bx - 6, by - 4, bx + 6, by + 4], fill=(185, 28, 28))

    # Footprints near marker 1
    for fx, fy in [(210, 370), (250, 390), (290, 410)]:
        draw.ellipse([fx, fy, fx + 18, fy + 8], fill=(20, 20, 20), outline=(48, 54, 61))

    # Handgun weapon near marker 3
    draw.rectangle([630, 355, 665, 365], fill=(70, 80, 95))
    draw.rectangle([630, 365, 642, 380], fill=(45, 55, 65))

    # Forensic scale bar at bottom left
    draw.rectangle([30, 460, 130, 475], fill=(240, 246, 252), outline=(0, 0, 0))
    for sx in range(30, 130, 10):
        fill_c = (0, 0, 0) if (sx // 10) % 2 == 0 else (255, 255, 255)
        draw.rectangle([sx, 460, sx + 10, 475], fill=fill_c)
    draw.text((40, 442), "FORENSIC SCALE (10cm)", fill=(139, 148, 158))

    # Timestamp and forensic watermark
    draw.text((w - 280, 20), "FORENSIC CRIME SCENE PHOTOGRAPHY", fill=(0, 229, 255))
    draw.text((w - 280, 38), f"CASE: CRV-2026-9041 | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", fill=(139, 148, 158))

    return img

def load_sample_case_data(session_state):
    """Populate session state with a complete, coherent multimodal crime case."""
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Set default investigator if empty
    if not session_state.get("investigator_name"):
        session_state.investigator_name = "Det. Sarah Jenkins (Forensics Unit 4)"

    # 1. Image Evidence
    sample_img = create_synthetic_crime_scene_image()
    img_byte_arr = io.BytesIO()
    sample_img.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    
    img_ev_id = "IMG-DEMO8412"
    img_hash = compute_file_hash(img_bytes)
    img_custody = get_custody_record(img_ev_id, img_hash, "Crime_Scene_Vault_Sector4.png", "Image")
    
    # Specific deterministic detections matching the synthesized crime scene
    detections = [
        {
            "label": "Firearm (Handgun)",
            "category": "weapon",
            "confidence": 0.964,
            "bbox": [620, 345, 675, 385],
            "center": [647, 365],
            "threat_weight": 0.95
        },
        {
            "label": "Blood Spatter Pattern",
            "category": "biological",
            "confidence": 0.928,
            "bbox": [405, 390, 460, 435],
            "center": [432, 412],
            "threat_weight": 0.70
        },
        {
            "label": "Forced Entry Point",
            "category": "structural",
            "confidence": 0.941,
            "bbox": [55, 35, 245, 265],
            "center": [150, 150],
            "threat_weight": 0.60
        },
        {
            "label": "Footprint",
            "category": "trace",
            "confidence": 0.885,
            "bbox": [200, 360, 310, 425],
            "center": [255, 392],
            "threat_weight": 0.30
        },
        {
            "label": "Shell Casing",
            "category": "ballistic",
            "confidence": 0.912,
            "bbox": [580, 330, 610, 360],
            "center": [595, 345],
            "threat_weight": 0.80
        }
    ]
    
    annotated_img = draw_detections(sample_img, detections)
    threat_level = compute_threat_level(detections)
    scene_class = "Burglary / Aggravated Assault"
    leads = generate_investigative_leads(detections, scene_class)
    
    img_analysis = {
        "evidence_id": img_ev_id,
        "file_name": "Crime_Scene_Vault_Sector4.png",
        "timestamp": now_iso,
        "detections": detections,
        "threat_level": threat_level,
        "scene_classification": scene_class,
        "leads": leads,
        "cached_image": sample_img,
        "annotated_image": annotated_img,
    }

    # 2. Audio Evidence (911 Dispatch Witness Call)
    aud_ev_id = "AUD-DEMO3194"
    aud_bytes = b"MOCK_AUDIO_FORENSIC_STREAM_BYTES_SAMPLE"
    aud_hash = compute_file_hash(aud_bytes)
    aud_custody = get_custody_record(aud_ev_id, aud_hash, "911_Emergency_Call_OakAlley.wav", "Audio")
    
    sample_transcription = DEMO_TRANSCRIPTIONS[0]
    aud_analysis = {
        "evidence_id": aud_ev_id,
        "file_name": "911_Emergency_Call_OakAlley.wav",
        "timestamp": now_iso,
        "transcription": sample_transcription,
    }

    # 3. Video Evidence (CCTV Surveillance)
    vid_ev_id = "VID-DEMO9521"
    vid_bytes = b"MOCK_CCTV_SURVEILLANCE_VIDEO_STREAM_BYTES"
    vid_hash = compute_file_hash(vid_bytes)
    vid_custody = get_custody_record(vid_ev_id, vid_hash, "CCTV_Cam04_Alley_North.mp4", "Video")
    
    demo_frames, duration, fps = generate_demo_frames(vid_hash, num_frames=8)
    frame_events = analyze_frames(demo_frames, vid_hash)
    
    vid_analysis = {
        "evidence_id": vid_ev_id,
        "file_name": "CCTV_Cam04_Alley_North.mp4",
        "timestamp": now_iso,
        "duration": 48.0,
        "fps": 30.0,
        "frames_sampled": len(demo_frames),
        "frames": demo_frames,
        "events": frame_events,
    }

    # Reset and store
    session_state.evidence_chain = [img_custody, aud_custody, vid_custody]
    session_state.image_analyses = [img_analysis]
    session_state.audio_analyses = [aud_analysis]
    session_state.video_analyses = [vid_analysis]
    session_state.master_timeline = []
    
    # Populate timeline
    for det in detections:
        store_timeline_event({
            "timestamp": now_iso,
            "source": "Image Analysis",
            "evidence_id": img_ev_id,
            "event": f"Physical Evidence Detected: {det['label']} (conf: {det['confidence']:.1%})",
            "category": det["category"],
            "coordinates": det["center"],
        })
    for evt in sample_transcription["key_events"]:
        store_timeline_event({
            "timestamp": now_iso,
            "source": "Audio Analysis",
            "evidence_id": aud_ev_id,
            "event": evt["event"],
            "category": "audio_event",
            "speaker": evt.get("speaker", "Witness"),
            "significance": evt.get("significance", "Medium"),
        })
    for evt in frame_events:
        store_timeline_event({
            "timestamp": now_iso,
            "source": "Video Analysis",
            "evidence_id": vid_ev_id,
            "event": evt["event"],
            "category": evt["category"],
            "frame": evt["frame_number"],
            "video_timestamp": evt["timestamp_fmt"],
        })

    # Sample initial grounded Q&A
    session_state.chat_history = [
        {
            "role": "user",
            "content": "Was a weapon visible before the suspect fled the scene?"
        },
        {
            "role": "assistant",
            "content": (
                "**Cross-Modal Forensic Grounding Report:**\n\n"
                "1. **Physical Evidence Confirmation:** In crime scene photography **[IMG-DEMO8412]**, a "
                "**Firearm (Handgun)** was localized at coordinates (647, 365) with 96.4% confidence adjacent to spent cartridge casings.\n\n"
                "2. **Witness Account Correlation:** Per emergency 911 audio **[AUD-DEMO3194]**, Witness Speaker-1 reported "
                "two gunshot-like discharges at timeline index T+23:30:00 prior to observing the armed subject flee in a silver sedan.\n\n"
                "3. **CCTV Trajectory Correlation:** Surveillance camera **[VID-DEMO9521]** captures the suspect at Frame #2 "
                "(T+00:06) carrying a concealed weapon before breaching the rear perimeter.\n\n"
                "**Investigative Conclusion:** Physical and chronological evidence confirms weapon display prior to perimeter exit. "
                "Chain-of-custody verified for all cited items."
            )
        }
    ]
