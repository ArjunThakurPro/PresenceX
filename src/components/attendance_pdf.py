import re
from datetime import datetime
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab import __file__ as reportlab_file
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


_FONT_NAME = "AttendanceSans"
_FONT_PATH = Path(reportlab_file).parent / "fonts" / "Vera.ttf"
pdfmetrics.registerFont(TTFont(_FONT_NAME, str(_FONT_PATH)))


def create_attendance_pdf(result, subject_name, timestamp):
    session_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    session_label = session_time.strftime("%B %d, %Y at %I:%M %p")
    filename_subject = re.sub(r"[^A-Za-z0-9_-]+", "_", subject_name).strip("_")
    filename = (
        f"attendance_{filename_subject or 'session'}_"
        f"{session_time.strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "AttendanceTitle",
        parent=styles["Title"],
        fontName=_FONT_NAME,
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#12304a"),
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "AttendanceBody",
        parent=styles["BodyText"],
        fontName=_FONT_NAME,
        fontSize=9,
        leading=12,
    )
    header_style = ParagraphStyle(
        "AttendanceHeader",
        parent=body_style,
        textColor=colors.white,
        fontName=_FONT_NAME,
    )

    rows = []
    present_count = 0
    absent_count = 0
    for record in result.to_dict(orient="records"):
        raw_status = str(record.get("Status") or "")
        status = (
            "Present"
            if "Present" in raw_status
            else "Absent"
            if "Absent" in raw_status
            else raw_status
        )
        present_count += status == "Present"
        absent_count += status == "Absent"
        rows.append(
            [
                Paragraph(escape(str(record.get("Name") or "-")), body_style),
                Paragraph(escape(str(record.get("Enrollment No") or "-")), body_style),
                Paragraph(escape(status or "Not recorded"), body_style),
            ]
        )

    pdf_buffer = BytesIO()
    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"Attendance - {subject_name}",
    )
    table_data = [
        [
            Paragraph("Student name", header_style),
            Paragraph("Enrollment No", header_style),
            Paragraph("Status", header_style),
        ],
        *rows,
    ]
    attendance_table = Table(
        table_data,
        colWidths=[72 * mm, 52 * mm, 50 * mm],
        repeatRows=1,
    )
    attendance_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12304a")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f1f5f9")],
                ),
            ]
        )
    )
    document.build(
        [
            Paragraph("Session attendance", title_style),
            Paragraph(f"<b>Subject:</b> {escape(subject_name)}", body_style),
            Paragraph(f"<b>Session:</b> {escape(session_label)}", body_style),
            Paragraph(
                f"<b>Present:</b> {present_count} &nbsp;&nbsp; "
                f"<b>Absent:</b> {absent_count} &nbsp;&nbsp; "
                f"<b>Total students:</b> {len(rows)}",
                body_style,
            ),
            Spacer(1, 8 * mm),
            attendance_table,
        ]
    )
    return pdf_buffer.getvalue(), filename
