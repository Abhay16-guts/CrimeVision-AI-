"""
CrimeVision AI — PDF Report Generation Module (Epic 6)
Court-admissible forensic summary PDF export using ReportLab.
"""

import io
import datetime
import streamlit as st

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


# ─────────────────────────────────────────────────────────────
# Custom Styles
# ─────────────────────────────────────────────────────────────
def get_forensic_styles():
    """Create custom forensic report styles."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='ForensicTitle',
        parent=styles['Title'],
        fontSize=22,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    ))

    styles.add(ParagraphStyle(
        name='ForensicSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#4a4a6a'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica',
    ))

    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a1a2e'),
        spaceBefore=18,
        spaceAfter=8,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=colors.HexColor('#0066cc'),
        borderPadding=4,
    ))

    styles.add(ParagraphStyle(
        name='SubSection',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=colors.HexColor('#333366'),
        spaceBefore=10,
        spaceAfter=6,
        fontName='Helvetica-Bold',
    ))

    styles.add(ParagraphStyle(
        name='BodyText2',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leading=13,
    ))

    styles.add(ParagraphStyle(
        name='EvidenceID',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#0066cc'),
        fontName='Courier',
    ))

    styles.add(ParagraphStyle(
        name='Disclaimer',
        parent=styles['Normal'],
        fontSize=7,
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER,
        spaceBefore=20,
    ))

    styles.add(ParagraphStyle(
        name='CellText',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#333333'),
        leading=10,
    ))

    return styles


# ─────────────────────────────────────────────────────────────
# PDF Builder
# ─────────────────────────────────────────────────────────────
def generate_forensic_pdf() -> bytes:
    """Generate a complete forensic report PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=25 * mm,
        bottomMargin=20 * mm,
    )

    styles = get_forensic_styles()
    elements = []
    now = datetime.datetime.now(datetime.timezone.utc)
    investigator = st.session_state.get("investigator_name", "System Auto-Generated")

    # ── Cover Page ──
    elements.append(Spacer(1, 60))
    elements.append(Paragraph("CRIMEVISION AI", styles['ForensicTitle']))
    elements.append(Paragraph("Intelligent Multimodal Forensic Analysis Report", styles['ForensicSubtitle']))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="80%", thickness=2, color=colors.HexColor('#0066cc')))
    elements.append(Spacer(1, 20))

    # Case information table
    case_data = [
        ["Report Generated:", now.strftime("%Y-%m-%d %H:%M:%S UTC")],
        ["Investigator:", investigator if investigator else "N/A"],
        ["Case Reference:", f"CV-{now.strftime('%Y%m%d')}-{hash(str(now)) % 10000:04d}"],
        ["Classification:", "CONFIDENTIAL — LAW ENFORCEMENT SENSITIVE"],
        ["Total Evidence Items:", str(len(st.session_state.get("evidence_chain", [])))],
        ["Platform Version:", "CrimeVision AI v2.0.0"],
    ]

    case_table = Table(case_data, colWidths=[150, 300])
    case_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f7fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dde1e7')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(case_table)
    elements.append(PageBreak())

    # ── Section 1: Chain of Custody ──
    elements.append(Paragraph("1. CHAIN OF CUSTODY", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dde1e7')))
    elements.append(Spacer(1, 8))

    chain = st.session_state.get("evidence_chain", [])
    if chain:
        chain_header = [["Evidence ID", "Type", "File Name", "SHA-256 (partial)", "Status", "Timestamp"]]
        chain_rows = []
        for record in chain:
            chain_rows.append([
                Paragraph(record["evidence_id"], styles['EvidenceID']),
                Paragraph(record["evidence_type"], styles['CellText']),
                Paragraph(record["file_name"][:25], styles['CellText']),
                Paragraph(record["sha256_hash"][:20] + "...", styles['CellText']),
                Paragraph(record["status"], styles['CellText']),
                Paragraph(record["ingestion_timestamp"][:19], styles['CellText']),
            ])

        chain_table = Table(chain_header + chain_rows,
                            colWidths=[70, 45, 100, 105, 70, 80])
        chain_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dde1e7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f7fa')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(chain_table)
    else:
        elements.append(Paragraph("No evidence items have been ingested.", styles['BodyText2']))

    elements.append(Spacer(1, 16))

    # ── Section 2: Image Analysis Results ──
    elements.append(Paragraph("2. CRIME SCENE IMAGE ANALYSIS", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dde1e7')))
    elements.append(Spacer(1, 8))

    image_analyses = st.session_state.get("image_analyses", [])
    if image_analyses:
        for analysis in image_analyses:
            elements.append(Paragraph(
                f"Evidence: {analysis['evidence_id']} — {analysis['file_name']}",
                styles['SubSection']
            ))
            elements.append(Paragraph(
                f"Threat Level: <b>{analysis.get('threat_level', 'N/A')}</b> | "
                f"Scene Classification: <b>{analysis.get('scene_classification', 'N/A')}</b>",
                styles['BodyText2']
            ))

            # Detections table
            det_header = [["Object", "Category", "Confidence", "Position"]]
            det_rows = []
            for det in analysis.get("detections", []):
                det_rows.append([
                    Paragraph(det["label"], styles['CellText']),
                    Paragraph(det["category"].upper(), styles['CellText']),
                    Paragraph(f"{det['confidence']:.1%}", styles['CellText']),
                    Paragraph(f"({det['center'][0]}, {det['center'][1]})", styles['CellText']),
                ])

            if det_rows:
                det_table = Table(det_header + det_rows, colWidths=[150, 80, 70, 80])
                det_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dde1e7')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                elements.append(det_table)

            # Investigative leads
            leads = analysis.get("leads", [])
            if leads:
                elements.append(Spacer(1, 8))
                elements.append(Paragraph("Investigative Leads:", styles['SubSection']))
                for lead in leads:
                    elements.append(Paragraph(
                        f"• [{lead['priority']}] {lead['lead']}<br/>"
                        f"  <i>Action: {lead['action']}</i>",
                        styles['BodyText2']
                    ))

            elements.append(Spacer(1, 12))
    else:
        elements.append(Paragraph("No image evidence has been analyzed.", styles['BodyText2']))

    # ── Section 3: Audio Transcription ──
    elements.append(Paragraph("3. AUDIO TRANSCRIPTION & TIMELINE", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dde1e7')))
    elements.append(Spacer(1, 8))

    audio_analyses = st.session_state.get("audio_analyses", [])
    if audio_analyses:
        for analysis in audio_analyses:
            elements.append(Paragraph(
                f"Evidence: {analysis['evidence_id']} — {analysis['file_name']}",
                styles['SubSection']
            ))

            transcription = analysis.get("transcription", {})
            full_text = transcription.get("full_text", "N/A")
            elements.append(Paragraph(f"<b>Full Transcription:</b>", styles['BodyText2']))
            elements.append(Paragraph(f'"{full_text}"', styles['BodyText2']))

            # Key events
            key_events = transcription.get("key_events", [])
            if key_events:
                elements.append(Spacer(1, 6))
                elements.append(Paragraph("Key Chronological Events:", styles['SubSection']))

                evt_header = [["Time", "Event", "Speaker", "Significance"]]
                evt_rows = []
                for evt in key_events:
                    evt_rows.append([
                        Paragraph(evt["time"], styles['CellText']),
                        Paragraph(evt["event"], styles['CellText']),
                        Paragraph(evt.get("speaker", "N/A"), styles['CellText']),
                        Paragraph(evt.get("significance", "N/A"), styles['CellText']),
                    ])

                evt_table = Table(evt_header + evt_rows, colWidths=[65, 210, 70, 65])
                evt_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dde1e7')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                elements.append(evt_table)

            elements.append(Spacer(1, 12))
    else:
        elements.append(Paragraph("No audio evidence has been analyzed.", styles['BodyText2']))

    # ── Section 4: Video Analysis ──
    elements.append(Paragraph("4. CCTV VIDEO ANALYSIS", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dde1e7')))
    elements.append(Spacer(1, 8))

    video_analyses = st.session_state.get("video_analyses", [])
    if video_analyses:
        for analysis in video_analyses:
            elements.append(Paragraph(
                f"Evidence: {analysis['evidence_id']} — {analysis['file_name']}",
                styles['SubSection']
            ))
            elements.append(Paragraph(
                f"Duration: {analysis.get('duration', 0):.1f}s | "
                f"FPS: {analysis.get('fps', 0):.0f} | "
                f"Frames Sampled: {analysis.get('frames_sampled', 0)}",
                styles['BodyText2']
            ))

            vid_header = [["Time", "Frame", "Event", "Penal Code", "Severity"]]
            vid_rows = []
            for evt in analysis.get("events", []):
                vid_rows.append([
                    Paragraph(evt["timestamp_fmt"], styles['CellText']),
                    Paragraph(f"#{evt['frame_number']}", styles['CellText']),
                    Paragraph(evt["event"], styles['CellText']),
                    Paragraph(evt["penal_code"][:40], styles['CellText']),
                    Paragraph(evt["severity"], styles['CellText']),
                ])

            if vid_rows:
                vid_table = Table(vid_header + vid_rows, colWidths=[45, 35, 160, 140, 50])
                vid_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 7),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dde1e7')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                elements.append(vid_table)

            elements.append(Spacer(1, 12))
    else:
        elements.append(Paragraph("No video evidence has been analyzed.", styles['BodyText2']))

    # ── Section 5: Master Timeline ──
    elements.append(PageBreak())
    elements.append(Paragraph("5. UNIFIED MASTER FORENSIC TIMELINE", styles['SectionHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dde1e7')))
    elements.append(Spacer(1, 8))

    from fusion_chat import build_master_timeline
    master_timeline = build_master_timeline()

    if master_timeline:
        tl_header = [["#", "Source", "Evidence ID", "Event", "Severity"]]
        tl_rows = []
        for i, evt in enumerate(master_timeline[:50]):  # Limit to 50 for PDF
            tl_rows.append([
                Paragraph(str(i + 1), styles['CellText']),
                Paragraph(evt["source_type"], styles['CellText']),
                Paragraph(evt["evidence_id"], styles['EvidenceID']),
                Paragraph(evt["event"][:60], styles['CellText']),
                Paragraph(evt.get("severity", "N/A"), styles['CellText']),
            ])

        tl_table = Table(tl_header + tl_rows, colWidths=[25, 55, 75, 220, 55])
        tl_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dde1e7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f7fa')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(tl_table)
    else:
        elements.append(Paragraph("No events in the master timeline.", styles['BodyText2']))

    # ── Footer / Disclaimer ──
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dde1e7')))
    elements.append(Paragraph(
        "DISCLAIMER: This report was generated by CrimeVision AI — Intelligent Multimodal Forensic Analysis Platform. "
        "All analysis results are AI-assisted and must be independently verified by qualified forensic professionals "
        "before use in legal proceedings. AI-generated detections are simulations and should be corroborated with "
        "physical forensic evidence. This document is classified as LAW ENFORCEMENT SENSITIVE.",
        styles['Disclaimer']
    ))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        f"Generated: {now.strftime('%Y-%m-%d %H:%M:%S UTC')} | "
        f"CrimeVision AI v{2}.0.0 | "
        f"Investigator: {investigator if investigator else 'N/A'}",
        styles['Disclaimer']
    ))

    # Build PDF
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


# ─────────────────────────────────────────────────────────────
# Tab Renderer
# ─────────────────────────────────────────────────────────────
def render_pdf_export_tab():
    """Render Tab 5: Automated Forensic PDF Export."""
    st.markdown("## 📄 Automated Forensic PDF Report Export")
    st.markdown(
        "> Generate a comprehensive, court-admissible forensic summary report. "
        "Includes chain-of-custody, all analysis results, and the unified master timeline."
    )

    # Report summary
    evidence_count = len(st.session_state.get("evidence_chain", []))
    image_count = len(st.session_state.get("image_analyses", []))
    audio_count = len(st.session_state.get("audio_analyses", []))
    video_count = len(st.session_state.get("video_analyses", []))

    st.markdown("### 📋 Report Contents Preview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Evidence Items", evidence_count)
    col2.metric("🖼️ Image Analyses", image_count)
    col3.metric("🎙️ Audio Analyses", audio_count)
    col4.metric("📹 Video Analyses", video_count)

    st.markdown("---")

    # Report sections checklist
    st.markdown("#### Report Sections:")
    sections = [
        ("✅" if evidence_count > 0 else "⬜", "Chain of Custody Records", evidence_count > 0),
        ("✅" if image_count > 0 else "⬜", "Crime Scene Image Analysis (RT-DETR Detections)", image_count > 0),
        ("✅" if audio_count > 0 else "⬜", "Audio Transcription & Timeline", audio_count > 0),
        ("✅" if video_count > 0 else "⬜", "CCTV Video Event Log", video_count > 0),
        ("✅" if evidence_count > 0 else "⬜", "Unified Master Forensic Timeline", evidence_count > 0),
    ]

    for icon, label, active in sections:
        color = "#22C55E" if active else "#4B5563"
        st.markdown(
            f'<div style="padding:6px 12px;margin:3px 0;color:{color};font-size:14px;">'
            f'{icon} {label}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Investigator sign-off
    investigator = st.text_input(
        "👤 Investigator Name (for report sign-off)",
        value=st.session_state.get("investigator_name", ""),
        placeholder="Enter your name for the official report",
        key="pdf_investigator",
    )
    if investigator:
        st.session_state.investigator_name = investigator

    st.markdown("---")

    # Generate button
    if evidence_count == 0:
        st.warning(
            "⚠️ No evidence has been ingested yet. Upload and analyze evidence in the preceding tabs "
            "before generating the report."
        )

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        generate_clicked = st.button(
            "🔒 Generate Court-Admissible PDF Report",
            use_container_width=True,
            type="primary",
            disabled=evidence_count == 0,
        )

    if generate_clicked:
        with st.spinner("📝 Compiling forensic report with ReportLab..."):
            try:
                pdf_bytes = generate_forensic_pdf()

                st.success("✅ Forensic report generated successfully!")
                st.balloons()

                now = datetime.datetime.now()
                filename = f"CrimeVision_AI_Report_{now.strftime('%Y%m%d_%H%M%S')}.pdf"

                st.download_button(
                    label="⬇️ Download Forensic Report PDF",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                )

                st.markdown(
                    f'<div style="background:#0f2a1a;border:1px solid #22C55E;padding:16px;'
                    f'border-radius:8px;margin-top:12px;">'
                    f'<div style="color:#22C55E;font-weight:bold;font-size:14px;">📄 Report Ready</div>'
                    f'<div style="color:#86efac;font-size:13px;margin-top:4px;">'
                    f'File: {filename}<br/>'
                    f'Size: {len(pdf_bytes) / 1024:.1f} KB<br/>'
                    f'Evidence Items: {evidence_count}<br/>'
                    f'Generated: {now.strftime("%Y-%m-%d %H:%M:%S")}'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

            except Exception as e:
                st.error(f"❌ Report generation failed: {e}")
                st.exception(e)
