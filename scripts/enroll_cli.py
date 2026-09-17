"""
CLI utility: enroll a new student using a local webcam.
Usage: python scripts/enroll_cli.py "Jane Doe" "21BCE1234"
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import database, enrollment  # noqa: E402


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/enroll_cli.py <name> <roll_number>")
        sys.exit(1)

    name, roll_number = sys.argv[1], sys.argv[2]
    conn = database.get_connection()
    try:
        label_id = enrollment.register_student(conn, name, roll_number)
        print(f"Registered {name} with label_id {label_id}. Look at the camera…")
        collected = enrollment.capture_from_webcam(label_id)
        print(f"Captured {collected} face samples.")
        print("Now run: python scripts/train_cli.py")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
