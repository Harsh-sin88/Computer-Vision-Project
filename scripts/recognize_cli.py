"""
CLI utility: run continuous live recognition + attendance marking from a webcam.
Usage: python scripts/recognize_cli.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import recognition  # noqa: E402


if __name__ == "__main__":
    recognition.run_live_recognition()
