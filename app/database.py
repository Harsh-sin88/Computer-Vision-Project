"""
Module: database
Connection management and CRUD operations for students and attendance.

The UNIQUE(student_id, date) constraint on the attendance table (see
models.py) is what enforces "one attendance mark per student per day" at the
storage layer, so business logic never has to race against itself.
"""
import sqlite3
from datetime import datetime
from typing import Optional

from app import config
from app.models import init_db, Student


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """Open (and initialize, if needed) a SQLite connection. Pass db_path to
    point at an isolated database, e.g. for tests."""
    path = db_path or config.DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


def add_student(conn, label_id: int, name: str, roll_number: str) -> int:
    cur = conn.execute(
        "INSERT INTO students (label_id, name, roll_number, created_at) VALUES (?, ?, ?, ?)",
        (label_id, name, roll_number, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    return cur.lastrowid


def get_student_by_label(conn, label_id: int) -> Optional[Student]:
    row = conn.execute("SELECT * FROM students WHERE label_id = ?", (label_id,)).fetchone()
    if row is None:
        return None
    return Student(row["id"], row["label_id"], row["name"], row["roll_number"], row["created_at"])


def list_students(conn):
    rows = conn.execute("SELECT * FROM students ORDER BY name").fetchall()
    return [Student(r["id"], r["label_id"], r["name"], r["roll_number"], r["created_at"]) for r in rows]


def mark_attendance(conn, student_id: int, confidence: float, when: datetime = None) -> bool:
    """
    Insert an attendance row for "today" if one doesn't already exist.
    Returns True if a new record was inserted, False if attendance for that
    student was already marked earlier today.
    """
    when = when or datetime.now()
    today = when.date().isoformat()
    time_str = when.strftime("%H:%M:%S")
    try:
        conn.execute(
            "INSERT INTO attendance (student_id, date, time, confidence) VALUES (?, ?, ?, ?)",
            (student_id, today, time_str, confidence),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def get_attendance_for_date(conn, date_str: str):
    rows = conn.execute(
        """
        SELECT s.name, s.roll_number, a.time, a.confidence
        FROM attendance a JOIN students s ON a.student_id = s.id
        WHERE a.date = ?
        ORDER BY a.time
        """,
        (date_str,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_attendance_between(conn, start_date: str, end_date: str):
    rows = conn.execute(
        """
        SELECT s.name, s.roll_number, a.date, a.time, a.confidence
        FROM attendance a JOIN students s ON a.student_id = s.id
        WHERE a.date BETWEEN ? AND ?
        ORDER BY a.date, a.time
        """,
        (start_date, end_date),
    ).fetchall()
    return [dict(r) for r in rows]
