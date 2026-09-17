# Smart Attendance System — Face Recognition (CSE3010 Computer Vision Project)

A face-recognition based attendance system built for the VITyarthi "Build
Your Own Project" evaluation for CSE3010 Computer Vision. It detects and
recognizes enrolled students from a camera or uploaded image, marks their
attendance automatically, and exposes a small dashboard for monitoring and
exporting reports.

See [`statement.md`](statement.md) for the problem statement and scope, and
[`docs/architecture.md`](docs/architecture.md) for the architecture, workflow,
UML, and ER diagrams.

## Features

- **Enrollment** — register a student and capture labelled face samples via
  webcam (CLI) or image upload (API/dashboard).
- **Recognition & Attendance Marking** — Haar-cascade face detection +
  histogram-equalization preprocessing + LBPH recognition, with a confidence
  threshold and automatic one-mark-per-day enforcement.
- **Reporting & Analytics** — live daily summary on the dashboard, plus
  CSV/PDF export for any date range.
- **Two ways to run recognition**: a live webcam loop (`scripts/`) for local
  use with a laptop camera, and a REST API (`/attendance/recognize`) that
  accepts an uploaded frame — useful for testing without a physical camera.

## Tech Stack

| Layer | Technology |
|---|---|
| Computer Vision | OpenCV (Haar cascades, LBPH face recognizer) |
| Backend / API | FastAPI, Uvicorn |
| Database | SQLite (stdlib `sqlite3`) |
| Reporting | ReportLab (PDF), stdlib `csv` |
| Frontend | Vanilla HTML/CSS/JS dashboard served as static files |
| Testing | Pytest |

## Project Structure

```
attendance-system/
├── app/
│   ├── config.py              # paths & tunable parameters
│   ├── models.py               # SQLite schema (Student, AttendanceRecord)
│   ├── database.py             # connection + CRUD helpers
│   ├── face_utils.py           # detection & preprocessing (shared)
│   ├── enrollment.py           # Module 1: enrollment + training
│   ├── recognition.py          # Module 2: recognition + attendance marking
│   ├── attendance_service.py   # confidence check, duplicate-mark rules
│   ├── reports.py              # Module 3: CSV/PDF report generation
│   └── main.py                 # FastAPI app & routes
├── static/                     # dashboard (index.html, style.css, app.js)
├── scripts/                    # CLI tools for local webcam use
│   ├── enroll_cli.py
│   ├── train_cli.py
│   └── recognize_cli.py
├── tests/                      # pytest unit tests
├── docs/architecture.md        # architecture, workflow, UML, ER diagrams
├── data/                       # runtime data: face samples, model, DB (git-ignored)
├── statement.md
├── requirements.txt
└── README.md
```

## Install & Run

1. **Clone and set up a virtual environment**
   ```bash
   git clone <your-repo-url>
   cd attendance-system
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Start the API + dashboard**
   ```bash
   uvicorn app.main:app --reload
   ```
   Open http://127.0.0.1:8000 for the dashboard.

3. **Enroll students**

   Either through the dashboard ("Enroll a Student" + "Add Face Sample",
   uploading a few photos per student), or from the terminal using your
   laptop's webcam:
   ```bash
   python scripts/enroll_cli.py "Jane Doe" "21BCE1234"
   ```

4. **Train the recognizer** (after enrolling students)
   ```bash
   python scripts/train_cli.py
   ```
   or click "Train Recognizer" on the dashboard.

5. **Mark attendance**

   Live webcam loop:
   ```bash
   python scripts/recognize_cli.py
   ```
   or upload a frame under "Recognize / Mark Attendance" on the dashboard.

6. **View reports** — the dashboard's summary panel shows today's
   attendance; CSV/PDF export links pull from `/attendance/report.csv` and
   `/attendance/report.pdf`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/students` | Register a new student |
| GET | `/students` | List enrolled students |
| POST | `/students/{label_id}/samples` | Upload a face sample image |
| POST | `/model/train` | (Re)train the recognizer on all samples |
| POST | `/attendance/recognize` | Recognize a face in an uploaded image and mark attendance |
| GET | `/attendance/today` | Today's attendance summary |
| GET | `/attendance/report.csv?start=&end=` | CSV export |
| GET | `/attendance/report.pdf?start=&end=` | PDF export |

## Testing

Unit tests cover the image-processing utilities and the attendance business
logic (duplicate-mark prevention, confidence thresholding, summary counts)
using an isolated temporary SQLite database — no camera or trained model is
required to run them:

```bash
pytest
```

## Non-Functional Requirements

- **Performance** — recognition runs per-frame on a single face crop
  (200x200), fast enough for near-real-time use on a laptop CPU.
- **Security** — only processed grayscale face crops are stored, never raw
  identity documents; the SQLite file and face samples are excluded from
  version control via `.gitignore`.
- **Reliability** — attendance marking is rejected gracefully (not crashed)
  when no face is detected, confidence is too low, or the label is unknown.
- **Usability** — a minimal one-page dashboard covers the full workflow
  (enroll → sample → train → recognize → report) without needing to touch
  the API directly.
- **Maintainability** — each functional module (enrollment, recognition,
  reporting) is isolated in its own file with a single responsibility.
- **Scalability** — recognition is O(1) per frame against a trained model
  file; re-training after adding students is a separate, explicit step so it
  doesn't block the live recognition path.

## Future Enhancements

- Replace LBPH with a deep embedding model (e.g., FaceNet) for higher
  accuracy across lighting/pose variation.
- Add basic liveness detection to reduce photo-spoofing risk.
- Support multiple class sessions per day instead of one mark per day.
