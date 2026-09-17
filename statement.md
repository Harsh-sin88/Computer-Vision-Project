# Problem Statement

## Problem Statement
Manual attendance in classrooms and labs is slow, easy to manipulate (proxy
attendance), and gives no real-time visibility into who is present. This
project applies computer vision techniques from CSE3010 — image formation
and preprocessing, feature extraction, and pattern classification — to build
a Smart Attendance System that identifies students from their face and marks
attendance automatically, removing manual roll-calls and proxy marking.

## Scope of the Project
- Enroll students by capturing labelled face samples (via webcam or image
  upload) and training a face recognition model on them.
- Recognize enrolled students from a live camera feed or an uploaded image
  and automatically mark their attendance for the day.
- Prevent duplicate attendance entries for the same student on the same day.
- Provide a web dashboard to view today's attendance summary and download
  attendance reports (CSV/PDF) for a date range.
- Out of scope: liveness/anti-spoofing detection (photo attacks), attendance
  across multiple classrooms/sessions per day, and mobile app support.

## Target Users
- **Faculty / Lab administrators** — enroll students, trigger training, and
  monitor/export attendance.
- **Students** — passively marked present by looking at the camera; no
  manual sign-in required.

## High-Level Features
1. **Student Enrollment** — register student metadata and capture face
   samples (Haar-cascade detection + histogram equalization preprocessing).
2. **Face Recognition & Attendance Marking** — LBPH-based recognition
   against enrolled students, with a configurable confidence threshold and
   one-mark-per-day enforcement.
3. **Reporting & Analytics** — daily summary, and CSV/PDF exports of
   attendance over any date range.
