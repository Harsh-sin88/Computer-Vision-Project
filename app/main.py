"""
Module: main
FastAPI application wiring together enrollment, recognition, attendance, and
reporting modules behind a REST API, and serving the static dashboard.

Run with:  uvicorn app.main:app --reload
"""
from datetime import datetime, timedelta

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles

from app import database, enrollment, recognition, reports, attendance_service

app = FastAPI(title="Smart Attendance System", version="1.0.0")


@app.post("/students")
def create_student(name: str = Form(...), roll_number: str = Form(...)):
    conn = database.get_connection()
    try:
        label_id = enrollment.register_student(conn, name, roll_number)
    finally:
        conn.close()
    return {"label_id": label_id, "name": name, "roll_number": roll_number}


@app.get("/students")
def list_students():
    conn = database.get_connection()
    try:
        students = database.list_students(conn)
    finally:
        conn.close()
    return [s.__dict__ for s in students]


@app.post("/students/{label_id}/samples")
async def upload_sample(label_id: int, file: UploadFile = File(...)):
    image_bytes = await file.read()
    result = enrollment.save_uploaded_sample(label_id, image_bytes)
    if not result["saved"]:
        raise HTTPException(status_code=422, detail=result["reason"])
    return result


@app.post("/model/train")
def train_model():
    try:
        stats = enrollment.train_recognizer()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    recognition.reload_recognizer()
    return stats


@app.post("/attendance/recognize")
async def recognize(file: UploadFile = File(...)):
    image_bytes = await file.read()
    try:
        result = recognition.recognize_from_bytes(image_bytes)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return result


@app.get("/attendance/today")
def attendance_today():
    conn = database.get_connection()
    try:
        summary = attendance_service.todays_summary(conn)
    finally:
        conn.close()
    return summary


@app.get("/attendance/report.csv")
def attendance_csv(start: str = None, end: str = None):
    end = end or datetime.now().date().isoformat()
    start = start or (datetime.now().date() - timedelta(days=7)).isoformat()
    conn = database.get_connection()
    try:
        csv_text = reports.generate_csv(conn, start, end)
    finally:
        conn.close()
    return PlainTextResponse(csv_text, media_type="text/csv")


@app.get("/attendance/report.pdf")
def attendance_pdf(start: str = None, end: str = None):
    end = end or datetime.now().date().isoformat()
    start = start or (datetime.now().date() - timedelta(days=7)).isoformat()
    conn = database.get_connection()
    try:
        pdf_bytes = reports.generate_pdf(conn, start, end)
    finally:
        conn.close()
    return Response(pdf_bytes, media_type="application/pdf")


# Serve the dashboard (index.html, style.css, app.js) at the site root.
# Mounted last so it doesn't shadow the API routes above.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
