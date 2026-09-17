# System Design & Diagrams

All diagrams below are written in Mermaid and render automatically when
viewed on GitHub.

## 1. System Architecture

```mermaid
flowchart LR
    subgraph Client
        Cam[Webcam / CLI scripts]
        Dash[Web Dashboard - static/]
    end

    subgraph API[FastAPI Backend - app/main.py]
        Enroll[Enrollment Module]
        Recog[Recognition Module]
        Attend[Attendance Service]
        Rep[Reports Module]
    end

    subgraph Core[Shared CV Core]
        FU[face_utils.py<br/>detection + preprocessing]
        Model[(LBPH Model<br/>data/lbph_model.yml)]
    end

    DB[(SQLite<br/>data/attendance.db)]

    Cam -->|face samples / frames| Dash
    Dash -->|multipart upload| API
    Enroll --> FU
    Recog --> FU
    Enroll -->|train| Model
    Recog -->|predict| Model
    Recog --> Attend
    Attend --> DB
    Enroll --> DB
    Rep --> DB
    Dash -->|GET summary / reports| Rep
    Dash -->|GET summary| Attend
```

## 2. Process / Workflow Diagram

```mermaid
flowchart TD
    A[Start] --> B[Register student metadata]
    B --> C[Capture N face samples<br/>webcam or upload]
    C --> D[Train LBPH recognizer]
    D --> E{New frame arrives}
    E --> F[Detect largest face]
    F -->|no face| E
    F -->|face found| G[Preprocess: gray + equalize]
    G --> H[LBPH predict: label, confidence]
    H --> I{confidence <= threshold?}
    I -->|No| J[Mark as Unknown]
    I -->|Yes| K{Already marked today?}
    K -->|Yes| L[No-op, return status]
    K -->|No| M[Insert attendance row]
    M --> N[Dashboard reflects update]
    J --> E
    L --> E
    N --> E
```

## 3. Use Case Diagram

```mermaid
flowchart LR
    Admin((Admin / Faculty))
    Student((Student))

    Admin -->|Register student| UC1[Enroll Student]
    Admin -->|Upload/Capture samples| UC2[Add Face Samples]
    Admin -->|Trigger| UC3[Train Recognizer]
    Admin -->|View| UC5[View Attendance Summary]
    Admin -->|Export| UC6[Generate CSV/PDF Report]
    Student -->|Look at camera| UC4[Mark Attendance via Recognition]
```

## 4. Class Diagram

```mermaid
classDiagram
    class Student {
        int id
        int label_id
        str name
        str roll_number
        str created_at
    }

    class AttendanceRecord {
        int id
        int student_id
        str date
        str time
        float confidence
    }

    class FaceUtils {
        +to_gray(image)
        +detect_faces(gray_image)
        +crop_and_resize(gray_image, box)
        +preprocess_face(face_image)
        +extract_largest_face(image)
    }

    class Enrollment {
        +register_student(conn, name, roll_number)
        +save_uploaded_sample(label_id, bytes)
        +capture_from_webcam(label_id)
        +train_recognizer()
    }

    class Recognition {
        +load_recognizer()
        +recognize_face(face_image)
        +recognize_from_bytes(bytes)
        +run_live_recognition()
    }

    class AttendanceService {
        +mark_if_confident(conn, label_id, confidence)
        +todays_summary(conn)
    }

    class Reports {
        +generate_csv(conn, start, end)
        +generate_pdf(conn, start, end)
    }

    Enrollment --> FaceUtils
    Recognition --> FaceUtils
    Recognition --> AttendanceService
    AttendanceService --> Student
    AttendanceService --> AttendanceRecord
    Reports --> AttendanceRecord
```

## 5. Sequence Diagram — Recognition & Attendance Marking

```mermaid
sequenceDiagram
    participant U as User/Camera
    participant API as FastAPI (/attendance/recognize)
    participant R as recognition.py
    participant FU as face_utils.py
    participant Model as LBPH Model
    participant AS as attendance_service.py
    participant DB as SQLite

    U->>API: POST image frame
    API->>R: recognize_from_bytes(bytes)
    R->>FU: extract_largest_face(frame)
    FU-->>R: face crop, box
    R->>Model: predict(face)
    Model-->>R: label_id, confidence
    R->>AS: mark_if_confident(label_id, confidence)
    AS->>DB: SELECT student WHERE label_id
    DB-->>AS: student row
    AS->>DB: INSERT attendance (if not already marked)
    DB-->>AS: success / IntegrityError
    AS-->>R: result dict
    R-->>API: result dict
    API-->>U: JSON response
```

## 6. ER Diagram

```mermaid
erDiagram
    STUDENTS ||--o{ ATTENDANCE : has
    STUDENTS {
        int id PK
        int label_id
        string name
        string roll_number
        string created_at
    }
    ATTENDANCE {
        int id PK
        int student_id FK
        string date
        string time
        float confidence
    }
```
