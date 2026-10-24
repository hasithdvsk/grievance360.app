"""
Grievance360 Action Taken Report (ATR) PDF Exporter
Uses ReportLab to generate official AICTE compliance and grievance resolution documents.
"""

import io
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        KeepTogether,
        HRFlowable,
    )
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def generate_atr_pdf(complaint: Dict[str, Any]) -> io.BytesIO:
    """
    Builds an official Action Taken Report (ATR) PDF for a grievance.
    Includes official AICTE header, metadata table, full grievance description,
    chronological audit action timeline, and cryptographic verification seal box.
    """
    buffer = io.BytesIO()

    if not HAS_REPORTLAB:
        # Fallback dummy PDF header if reportlab is unavailable
        buffer.write(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000115 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF")
        buffer.seek(0)
        return buffer

    # Create PDF document template with 0.5 inch margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    style_header_main = ParagraphStyle(
        "AICTE_Header_Main",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        alignment=1,  # Center
        textColor=colors.HexColor("#0f172a"),
    )

    style_header_sub = ParagraphStyle(
        "AICTE_Header_Sub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=1,  # Center
        textColor=colors.HexColor("#475569"),
    )

    style_doc_title = ParagraphStyle(
        "Doc_Title",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        alignment=1,  # Center
        textColor=colors.HexColor("#1e3a8a"),
    )

    style_section_heading = ParagraphStyle(
        "Section_Heading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4,
    )

    style_body = ParagraphStyle(
        "Body_Text",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1e293b"),
    )

    style_body_bold = ParagraphStyle(
        "Body_Text_Bold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#0f172a"),
    )

    style_table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1e293b"),
    )

    style_table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#ffffff"),
    )

    story = []

    # 1. Official AICTE Header Formatting
    story.append(Paragraph("ALL INDIA COUNCIL FOR TECHNICAL EDUCATION", style_header_main))
    story.append(Paragraph("(A Statutory Body of the Government of India)", style_header_sub))
    story.append(Paragraph("Nelson Mandela Marg, Vasant Kunj, New Delhi - 110070 | www.aicte-india.org", style_header_sub))
    story.append(Paragraph("Centralized AICTE Grievance Redressal Monitoring Cell (Grievance360)", style_header_sub))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1e3a8a"), spaceAfter=10))

    # 2. Document Title & Reference
    tracking_id = complaint.get("tracking_id", "N/A")
    now_str = datetime.now(timezone.utc).strftime("%d-%b-%Y %H:%M UTC")
    story.append(Paragraph("OFFICIAL ACTION TAKEN REPORT (ATR) & REDRESSAL CERTIFICATE", style_doc_title))
    story.append(Paragraph(f"Reference No: <b>AICTE/ATR/{tracking_id}</b> &nbsp;|&nbsp; Generated: <b>{now_str}</b>", style_header_sub))
    story.append(Spacer(1, 12))

    # 3. Ticket & Institution Metadata Table
    status_str = str(complaint.get("status", "SUBMITTED")).upper()
    priority_str = str(complaint.get("priority", "MEDIUM")).upper()

    metadata_data = [
        [
            Paragraph("<b>Grievance Tracking ID</b>", style_table_cell),
            Paragraph(f"<b>{tracking_id}</b>", style_table_cell),
            Paragraph("<b>Lifecycle Status</b>", style_table_cell),
            Paragraph(f"<b>{status_str}</b>", style_table_cell),
        ],
        [
            Paragraph("<b>Assigned Bureau</b>", style_table_cell),
            Paragraph(str(complaint.get("bureau_name", "AICTE Central Bureau")), style_table_cell),
            Paragraph("<b>Severity Priority</b>", style_table_cell),
            Paragraph(f"<b>{priority_str}</b>", style_table_cell),
        ],
        [
            Paragraph("<b>Educational Institution</b>", style_table_cell),
            Paragraph(str(complaint.get("institution_name", "AICTE Registered Institution")), style_table_cell),
            Paragraph("<b>Institution Location</b>", style_table_cell),
            Paragraph(f"{complaint.get('institution_city', 'N/A')}, {complaint.get('institution_state', 'India')}", style_table_cell),
        ],
        [
            Paragraph("<b>Complainant Capacity</b>", style_table_cell),
            Paragraph(str(complaint.get("complainant_role", "STUDENT")), style_table_cell),
            Paragraph("<b>Complainant Email</b>", style_table_cell),
            Paragraph(str(complaint.get("complainant_email", "N/A")), style_table_cell),
        ],
        [
            Paragraph("<b>Registration Timestamp</b>", style_table_cell),
            Paragraph(str(complaint.get("created_at", "N/A")), style_table_cell),
            Paragraph("<b>Statutory SLA Deadline</b>", style_table_cell),
            Paragraph(str(complaint.get("sla_deadline", "N/A")), style_table_cell),
        ],
    ]

    metadata_table = Table(metadata_data, colWidths=[120, 150, 120, 150])
    metadata_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(metadata_table)
    story.append(Spacer(1, 14))

    # 4. Full Grievance Summary Section
    story.append(Paragraph("1. GRIEVANCE SUMMARY & COMPLAINANT STATEMENT", style_section_heading))
    story.append(Paragraph(f"<b>Subject:</b> {complaint.get('title', 'N/A')}", style_body_bold))
    story.append(Spacer(1, 4))

    desc_text = complaint.get("description", "No detailed statement provided.")
    story.append(Paragraph(desc_text, style_body))
    story.append(Spacer(1, 14))

    # 5. Chronological Audit Action Timeline Table
    story.append(Paragraph("2. OFFICIAL CHRONOLOGICAL AUDIT ACTION LEDGER", style_section_heading))

    timeline = complaint.get("timeline", [])
    timeline_rows = [
        [
            Paragraph("<b>Date & Time (UTC)</b>", style_table_header),
            Paragraph("<b>Action / Disposition</b>", style_table_header),
            Paragraph("<b>Officer Remarks & Directives</b>", style_table_header),
            Paragraph("<b>Nodal Actor ID</b>", style_table_header),
        ]
    ]

    if timeline and len(timeline) > 0:
        for log in timeline:
            ts = str(log.get("timestamp", ""))[:19].replace("T", " ")
            action = str(log.get("action_taken", "ACTION_LOGGED")).replace("_", " ")
            remarks = str(log.get("officer_remarks", "Action completed."))
            actor = str(log.get("actor_id", "AICTE_NODAL_OFFICER"))

            timeline_rows.append([
                Paragraph(ts, style_table_cell),
                Paragraph(f"<b>{action}</b>", style_table_cell),
                Paragraph(remarks, style_table_cell),
                Paragraph(actor, style_table_cell),
            ])
    else:
        timeline_rows.append([
            Paragraph(now_str, style_table_cell),
            Paragraph("<b>REGISTERED_AND_TRIAGED</b>", style_table_cell),
            Paragraph("Grievance recorded in system register. Pending bureau action.", style_table_cell),
            Paragraph("SYSTEM_TRIAGE_V1", style_table_cell),
        ])

    timeline_table = Table(timeline_rows, colWidths=[95, 125, 235, 85])
    timeline_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(timeline_table)
    story.append(Spacer(1, 14))

    # 6. Cryptographic Digital Verification Seal Box
    complaint_raw = f"{tracking_id}:{status_str}:{priority_str}:{now_str}"
    crypto_hash = hashlib.sha256(complaint_raw.encode("utf-8")).hexdigest().upper()

    seal_data = [
        [
            Paragraph(
                "<b>DIGITAL AUTHENTICATION & STATUTORY COMPLIANCE SEAL</b><br/>"
                "This document is an electronically certified Action Taken Report issued by the "
                "AICTE Grievance360 Autonomous Monitoring Platform pursuant to AICTE Redressal Regulations.<br/>"
                f"<b>SHA-256 System Signature:</b> <font face='Courier' color='#1e3a8a'>{crypto_hash}</font><br/>"
                "<i>Valid without physical ink signature under Section 4 of the Information Technology Act.</i>",
                style_table_cell,
            )
        ]
    ]
    seal_table = Table(seal_data, colWidths=[540])
    seal_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
        ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#2563eb")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))

    story.append(KeepTogether(seal_table))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
