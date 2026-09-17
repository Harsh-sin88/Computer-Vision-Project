"""
CLI utility: (re)train the LBPH recognizer on all currently saved face samples.
Usage: python scripts/train_cli.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import enrollment  # noqa: E402


if __name__ == "__main__":
    stats = enrollment.train_recognizer()
    print(f"Trained on {stats['students_trained']} students, {stats['total_samples']} total samples.")
