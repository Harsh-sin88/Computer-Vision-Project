"""
Module: models
Defines the SQLite schema for students and attendance records, plus the
lightweight dataclasses used to move rows between layers without leaking
sqlite3.Row objects into the rest of the app.
"""
import sqlite3
from dataclasses import dataclass


@dataclass
class Student:
    id: int
    label_id: int
    name: str
    roll_number: str
    created_at: str


@dataclass
class AttendanceRecord:
    id: int
    student_id: int
    date: str
    time: str
    confidence: float


def init_db(conn: sqlite3.Connection) -> None:
    """Create tables if they do not already exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label_id INTEGER UNIQUE NOT NULL,
            name TEXT NOT NULL,
            roll_number TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            confidence REAL NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id),
            UNIQUE (student_id, date)
        )
        """
    )
    conn.commit()
