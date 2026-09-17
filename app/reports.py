"""
Module: reports (Functional Module 3 — Reporting & Analytics)
Generates CSV and PDF exports and summary analytics from attendance data.
"""
import csv
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from app import database


def generate_csv(conn, start_date: str, end_date: str) -> str:
    rows = database.get_attendance_between(conn, start_date, end_date)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["name", "roll_number", "date", "time", "confidence"])
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def generate_pdf(conn, start_date: str, end_date: str) -> bytes:
    rows = database.get_attendance_between(conn, start_date, end_date)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph("Attendance Report", styles["Title"]),
        Paragraph(f"Period: {start_date} to {end_date}", styles["Normal"]),
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]),
        Spacer(1, 12),
    ]

    table_data = [["Name", "Roll Number", "Date", "Time", "Confidence"]]
    for r in rows:
        table_data.append([r["name"], r["roll_number"], r["date"], r["time"], f"{r['confidence']:.1f}"])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
    ]))
    elements.append(table)
    doc.build(elements)
    return buffer.getvalue()
