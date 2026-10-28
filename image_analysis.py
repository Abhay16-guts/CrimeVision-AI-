"""
CrimeVision AI — Image Analysis Module (Epic 2)
Crime Scene Visual Evidence Tagger with simulated RT-DETR object detection.
"""

import random
import datetime
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

from utils import (
    generate_evidence_id, compute_file_hash, get_custody_record,
    store_evidence, store_timeline_event, call_llm,
    THREAT_LEVELS, SCENE_CLASSIFICATIONS,
)


# ─────────────────────────────────────────────────────────────
# Detection Simulation (RT-DETR Style)
# ─────────────────────────────────────────────────────────────
FORENSIC_OBJECTS = [
    {"label": "Person", "category": "human", "threat_weight": 0.3},
    {"label": "Firearm (Handgun)", "category": "weapon", "threat_weight": 0.95},
    {"label": "Firearm (Rifle)", "category": "weapon", "threat_weight": 0.98},
    {"label": "Edged Weapon (Knife)", "category": "weapon", "threat_weight": 0.85},
    {"label": "Blood Spatter Pattern", "category": "biological", "threat_weight": 0.7},
    {"label": "Forced Entry Point", "category": "structural", "threat_weight": 0.6},
    {"label": "Vehicle", "category": "vehicle", "threat_weight": 0.2},
    {"label": "Broken Glass", "category": "structural", "threat_weight": 0.4},
    {"label": "Shell Casing", "category": "ballistic", "threat_weight": 0.8},
    {"label": "Footprint", "category": "trace", "threat_weight": 0.3},
    {"label": "Surveillance Camera", "category": "equipment", "threat_weight": 0.1},
    {"label": "Drug Paraphernalia", "category": "contraband", "threat_weight": 0.65},
    {"label": "Blunt Object", "category": "weapon", "threat_weight": 0.7},
    {"label": "Mask / Disguise", "category": "concealment", "threat_weight": 0.5},
    {"label": "Mobile Phone", "category": "digital_evidence", "threat_weight": 0.15},
]


def simulate_detection(image: Image.Image, seed: int = None) -> list:
    """Simulate RT-DETR forensic object detection on an image."""
    if seed is not None:
        random.seed(seed)
    
    w, h = image.size
    num_detections = random.randint(3, 8)
    
    # Always include at least one person and one weapon/evidence item
    mandatory = [FORENSIC_OBJECTS[0]]  # Person
    mandatory.append(random.choice([obj for obj in FORENSIC_OBJECTS if obj["category"] == "weapon"]))
    
    remaining_pool = [obj for obj in FORENSIC_OBJECTS if obj not in mandatory]
    additional = random.sample(remaining_pool, min(num_detections - 2, len(remaining_pool)))
    
    selected = mandatory + additional
    detections = []
    
    for obj in selected:
        bw = random.randint(int(w * 0.05), int(w * 0.25))
        bh = random.randint(int(h * 0.05), int(h * 0.3))
        x1 = random.randint(0, max(1, w - bw))
        y1 = random.randint(0, max(1, h - bh))
        x2 = min(x1 + bw, w)
        y2 = min(y1 + bh, h)
        
        confidence = round(random.uniform(0.72, 0.99), 3)
        
        detections.append({
            "label": obj["label"],
            "category": obj["category"],
            "confidence": confidence,
            "bbox": [x1, y1, x2, y2],
            "center": [(x1 + x2) // 2, (y1 + y2) // 2],
            "threat_weight": obj["threat_weight"],
        })
    
    return detections


def draw_detections(image: Image.Image, detections: list) -> Image.Image:
    """Draw bounding boxes and labels on the image."""
    img_copy = image.copy().convert("RGB")
    draw = ImageDraw.Draw(img_copy)
    
    color_map = {
        "human": "#00E5FF",
        "weapon": "#FF1744",
        "biological": "#FF6D00",
        "structural": "#FFEA00",
        "vehicle": "#00E676",
        "ballistic": "#FF4081",
        "trace": "#7C4DFF",
        "equipment": "#64FFDA",
        "contraband": "#FF9100",
        "concealment": "#E040FB",
        "digital_evidence": "#448AFF",
    }
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except (IOError, OSError):
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        except (IOError, OSError):
            font = ImageFont.load_default()
    
    for det in detections:
        color = color_map.get(det["category"], "#FFFFFF")
        x1, y1, x2, y2 = det["bbox"]
        
        # Bounding box border
        for i in range(3):
            draw.rectangle([x1 - i, y1 - i, x2 + i, y2 + i], outline=color)
        
        # Label box
        label_text = f'{det["label"]} {det["confidence"]:.1%}'
        text_bbox = draw.textbbox((0, 0), label_text, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        
        label_y = max(0, y1 - text_h - 6)
        draw.rectangle([x1, label_y, x1 + text_w + 8, label_y + text_h + 6], fill=color)
        draw.text((x1 + 4, label_y + 2), label_text, fill="#000000", font=font)
        
        # Center crosshair
        cx, cy = det["center"]
        draw.line([(cx - 8, cy), (cx + 8, cy)], fill=color, width=2)
        draw.line([(cx, cy - 8), (cx, cy + 8)], fill=color, width=2)
    
    return img_copy


def compute_threat_level(detections: list) -> str:
    """Compute overall threat level from detections."""
    if not detections:
        return "Low"
    max_threat = max(d["confidence"] * d["threat_weight"] for d in detections)
    if max_threat >= 0.8:
        return "Critical"
    elif max_threat >= 0.6:
        return "High"
    elif max_threat >= 0.35:
        return "Medium"
    return "Low"


def classify_scene(detections: list) -> str:
    """Classify crime scene type based on detected objects."""
    labels = {d["label"].lower() for d in detections}
    categories = {d["category"] for d in detections}
    
    if any("firearm" in l for l in labels) or "shell casing" in labels:
        if any("blood" in l for l in labels):
            return "Homicide / Aggravated Assault"
        return "Armed Assault / Robbery"
    if "forced entry point" in labels or "broken glass" in labels:
        return "Burglary / Breaking & Entering"
    if any("blood" in l for l in labels):
        return "Homicide"
    if "drug paraphernalia" in labels:
        return "Drug Offense"
    if "vehicle" in categories:
        return "Traffic Incident / Hit & Run"
    return random.choice(["Vandalism", "Assault", "Burglary"])


def generate_investigative_leads(detections: list, scene_class: str) -> list:
    """Generate prioritized investigative leads."""
    leads = []
    categories_found = {d["category"] for d in detections}
    
    if "weapon" in categories_found:
        weapon_dets = [d for d in detections if d["category"] == "weapon"]
        for wd in weapon_dets:
            leads.append({
                "priority": "🔴 CRITICAL",
                "lead": f"Recover and process {wd['label']} detected at coordinates ({wd['center'][0]}, {wd['center'][1]}) — confidence {wd['confidence']:.1%}",
                "action": "Dispatch forensics team for immediate evidence collection. Initiate ballistics/blade analysis.",
            })
    
    if "biological" in categories_found:
        leads.append({
            "priority": "🟠 HIGH",
            "lead": "Biological evidence (blood spatter) detected — collect DNA samples",
            "action": "Deploy biohazard kit. Photograph spatter patterns before collection. Submit for DNA profiling.",
        })
    
    if "ballistic" in categories_found:
        leads.append({
            "priority": "🟠 HIGH",
            "lead": "Spent cartridge / ballistic casing detected — initiate NIBIN caliber matching",
            "action": "Recover casing without damaging breech face marks. Submit to firearms examiner.",
        })
    
    if "human" in categories_found:
        person_count = sum(1 for d in detections if d["category"] == "human")
        leads.append({
            "priority": "🟡 MEDIUM",
            "lead": f"{person_count} individual(s) detected in scene — obtain identification",
            "action": "Cross-reference with witness statements. Check CCTV for additional angles.",
        })
    
    if "structural" in categories_found:
        leads.append({
            "priority": "🟡 MEDIUM",
            "lead": "Structural damage / forced entry detected — document entry/exit points",
            "action": "Photograph and measure damage. Check for tool marks. Dust for fingerprints.",
        })
    
    if "trace" in categories_found:
        leads.append({
            "priority": "🟢 STANDARD",
            "lead": "Trace evidence (footprints) located — cast and preserve",
            "action": "Create plaster casts. Measure dimensions. Compare with suspect footwear database.",
        })
    
    if "digital_evidence" in categories_found:
        leads.append({
            "priority": "🟡 MEDIUM",
            "lead": "Digital device detected at scene — secure for forensic extraction",
            "action": "Bag in Faraday enclosure. Submit to digital forensics lab for data extraction.",
        })
    
    if not leads:
        leads.append({
            "priority": "🟢 STANDARD",
            "lead": "General scene documentation required",
            "action": "Complete photographic documentation. Canvas area for additional witnesses.",
        })
    
    return leads


def display_image_analysis_view(analysis: dict):
    """Render the full analysis results for an image record."""
    threat_level = analysis["threat_level"]
    scene_class = analysis["scene_classification"]
    detections = analysis["detections"]
    evidence_id = analysis["evidence_id"]
    leads = analysis.get("leads", [])

    st.markdown("---")
    
    # Threat & Scene Classification Header
    tl = THREAT_LEVELS.get(threat_level, THREAT_LEVELS["Medium"])
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    col_t1.markdown(
        f"### {tl['icon']} Threat Level\n"
        f"<h2 style='color:{tl['color']};margin:0'>{threat_level}</h2>",
        unsafe_allow_html=True
    )
    col_t2.markdown(f"### 🏷️ Scene Class\n## {scene_class}")
    col_t3.markdown(f"### 🎯 Objects Found\n## {len(detections)}")
    col_t4.markdown(f"### 📋 Evidence ID\n## {evidence_id}")
    
    st.markdown("---")
    
    # Annotated Image Display
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        st.markdown("#### 📸 Original Crime Scene Photography")
        if "cached_image" in analysis and analysis["cached_image"] is not None:
            st.image(analysis["cached_image"], use_container_width=True)
        else:
            st.info("Image preview rendered with annotations on the right.")
    with col_img2:
        st.markdown("#### 🔎 RT-DETR Multimodal Bounding Box Localization")
        if "annotated_image" in analysis and analysis["annotated_image"] is not None:
            st.image(analysis["annotated_image"], use_container_width=True)
        elif "cached_image" in analysis and analysis["cached_image"] is not None:
            ann = draw_detections(analysis["cached_image"], detections)
            st.image(ann, use_container_width=True)
        else:
            st.info("Annotated visual detection active.")
    
    st.markdown("---")
    
    # Detection Table
    st.markdown("### 📊 Detected Objects — Forensic Spatial Registry")
    for det in detections:
        threat_color = "#EF4444" if det["threat_weight"] > 0.7 else (
            "#F59E0B" if det["threat_weight"] > 0.4 else "#22C55E"
        )
        st.markdown(
            f"""
            <div style="background:#1a1f2e;border-left:4px solid {threat_color};padding:12px 16px;
            margin:6px 0;border-radius:6px;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <strong style="color:#E0E0E0;font-size:15px;">{det['label']}</strong>
                    <span style="color:#9CA3AF;font-size:13px;margin-left:12px;">
                        Category: {det['category'].upper()}
                    </span>
                </div>
                <div style="display:flex;gap:24px;align-items:center;">
                    <span style="color:{threat_color};font-weight:bold;">
                        Confidence: {det['confidence']:.1%}
                    </span>
                    <span style="color:#9CA3AF;font-size:13px;">
                        📍 ({det['center'][0]}, {det['center'][1]})
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    st.markdown("---")
    
    # Investigative Leads
    st.markdown("### 🕵️ Prioritized Investigative Leads")
    for lead in leads:
        st.markdown(
            f"""
            <div style="background:#111827;border:1px solid #374151;padding:14px 18px;
            margin:8px 0;border-radius:8px;">
                <div style="font-size:13px;color:#9CA3AF;margin-bottom:4px;">{lead['priority']}</div>
                <div style="color:#E0E0E0;font-size:15px;font-weight:600;margin-bottom:6px;">
                    {lead['lead']}
                </div>
                <div style="color:#6B7280;font-size:13px;">
                    ▸ <em>{lead['action']}</em>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # LLM Narrative Summary
    st.markdown("---")
    st.markdown("### 🧠 AI Forensic Narrative Summary")
    
    if "narrative" not in analysis:
        detection_summary = "\n".join(
            f"- {d['label']} (confidence: {d['confidence']:.1%}, location: {d['center']})"
            for d in detections
        )
        narrative_prompt = (
            f"You are a senior forensic analyst. Based on the following crime scene image analysis, "
            f"write a professional forensic narrative summary suitable for an official report.\n\n"
            f"Scene Classification: {scene_class}\n"
            f"Threat Level: {threat_level}\n"
            f"Evidence ID: {evidence_id}\n"
            f"Detections:\n{detection_summary}\n\n"
            f"Write a 2-3 paragraph professional forensic narrative. Cite the evidence ID."
        )
        with st.spinner("Generating forensic narrative..."):
            analysis["narrative"] = call_llm(narrative_prompt)
    
    st.markdown(
        f'<div style="background:#0f1520;border:1px solid #1e293b;padding:20px;'
        f'border-radius:10px;color:#cbd5e1;line-height:1.7;">{analysis["narrative"]}</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────
# Tab Renderer
# ─────────────────────────────────────────────────────────────
def render_image_analysis_tab():
    """Render Tab 1: Crime Scene Visual Evidence Tagger."""
    st.markdown("## 🔍 Crime Scene Visual Evidence Tagger")
    st.markdown(
        "> Upload crime scene photography for AI-powered forensic object detection "
        "simulating **RT-DETR** (Real-Time Detection Transformer). Detects persons, firearms, edged weapons, "
        "blood spatter, forced entry points, and ballistic shell casings."
    )
    
    col_up1, col_up2 = st.columns([3, 1])
    with col_up1:
        uploaded_file = st.file_uploader(
            "Upload Crime Scene Image",
            type=["jpg", "jpeg", "png", "bmp", "tiff", "webp"],
            key="image_uploader",
            help="Supported formats: JPG, PNG, BMP, TIFF, WebP. Max 200MB."
        )
    with col_up2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("⚡ Load Sample Photo", use_container_width=True, help="Load synthetic bank vault crime scene image"):
            from sample_data import create_synthetic_crime_scene_image
            sample_img = create_synthetic_crime_scene_image()
            import io
            buf = io.BytesIO()
            sample_img.save(buf, format="PNG")
            raw_bytes = buf.getvalue()
            
            ev_id = generate_evidence_id("IMG")
            f_hash = compute_file_hash(raw_bytes)
            c_rec = get_custody_record(ev_id, f_hash, "Crime_Scene_Vault_Sector4.png", "Image")
            store_evidence(c_rec)
            
            sample_dets = [
                {"label": "Firearm (Handgun)", "category": "weapon", "confidence": 0.964, "bbox": [620, 345, 675, 385], "center": [647, 365], "threat_weight": 0.95},
                {"label": "Blood Spatter Pattern", "category": "biological", "confidence": 0.928, "bbox": [405, 390, 460, 435], "center": [432, 412], "threat_weight": 0.70},
                {"label": "Forced Entry Point", "category": "structural", "confidence": 0.941, "bbox": [55, 35, 245, 265], "center": [150, 150], "threat_weight": 0.60},
                {"label": "Footprint", "category": "trace", "confidence": 0.885, "bbox": [200, 360, 310, 425], "center": [255, 392], "threat_weight": 0.30},
                {"label": "Shell Casing", "category": "ballistic", "confidence": 0.912, "bbox": [580, 330, 610, 360], "center": [595, 345], "threat_weight": 0.80}
            ]
            ann_img = draw_detections(sample_img, sample_dets)
            t_lvl = compute_threat_level(sample_dets)
            s_cls = "Burglary / Aggravated Assault"
            l_leads = generate_investigative_leads(sample_dets, s_cls)
            
            rec = {
                "evidence_id": ev_id,
                "file_name": "Crime_Scene_Vault_Sector4.png",
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "detections": sample_dets,
                "threat_level": t_lvl,
                "scene_classification": s_cls,
                "leads": l_leads,
                "cached_image": sample_img,
                "annotated_image": ann_img,
            }
            st.session_state.image_analyses = [rec]
            for d in sample_dets:
                store_timeline_event({
                    "timestamp": rec["timestamp"],
                    "source": "Image Analysis",
                    "evidence_id": ev_id,
                    "event": f"Detected: {d['label']} (conf: {d['confidence']:.1%})",
                    "category": d["category"],
                    "coordinates": d["center"],
                })
            st.success("Sample Crime Scene Photo loaded!")
            st.rerun()

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        image = Image.open(uploaded_file)
        
        # Chain of custody
        evidence_id = generate_evidence_id("IMG")
        file_hash = compute_file_hash(file_bytes)
        custody_record = get_custody_record(evidence_id, file_hash, uploaded_file.name, "Image")
        
        with st.expander("📋 Chain-of-Custody Record", expanded=False):
            col1, col2, col3 = st.columns(3)
            col1.metric("Evidence ID", evidence_id)
            col2.metric("SHA-256", file_hash[:16] + "...")
            col3.metric("Status", "✅ Verified")
            st.json(custody_record)
        
        store_evidence(custody_record)
        
        with st.spinner("🔬 Running RT-DETR forensic object detection..."):
            seed = int(file_hash[:8], 16) % (2**31)
            detections = simulate_detection(image, seed=seed)
            annotated_image = draw_detections(image, detections)
            threat_level = compute_threat_level(detections)
            scene_class = classify_scene(detections)
            leads = generate_investigative_leads(detections, scene_class)
        
        analysis_record = {
            "evidence_id": evidence_id,
            "file_name": uploaded_file.name,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "detections": detections,
            "threat_level": threat_level,
            "scene_classification": scene_class,
            "leads": leads,
            "cached_image": image,
            "annotated_image": annotated_image,
        }
        
        existing_ids = {a["evidence_id"] for a in st.session_state.image_analyses}
        if evidence_id not in existing_ids:
            st.session_state.image_analyses.append(analysis_record)
            for det in detections:
                store_timeline_event({
                    "timestamp": analysis_record["timestamp"],
                    "source": "Image Analysis",
                    "evidence_id": evidence_id,
                    "event": f"Detected: {det['label']} (conf: {det['confidence']:.1%})",
                    "category": det["category"],
                    "coordinates": det["center"],
                })
        
        display_image_analysis_view(analysis_record)

    elif st.session_state.get("image_analyses"):
        # Display existing analysis
        latest_analysis = st.session_state.image_analyses[-1]
        st.info(f"Viewing active image analysis: **{latest_analysis['evidence_id']}** ({latest_analysis['file_name']})")
        display_image_analysis_view(latest_analysis)

    else:
        st.markdown(
            """
            <div style="background:#111827;border:2px dashed #1e293b;border-radius:12px;padding:36px;
            text-align:center;margin-top:20px;">
                <div style="font-size:36px;margin-bottom:12px;">📸</div>
                <h3 style="color:#00E5FF;margin-bottom:8px;">No Crime Scene Image Analyzed Yet</h3>
                <p style="color:#9CA3AF;max-width:550px;margin:0 auto 18px auto;line-height:1.6;">
                    Upload an image file above, or click <strong>⚡ Load Sample Photo</strong> for instant evaluation of RT-DETR detection capabilities.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
