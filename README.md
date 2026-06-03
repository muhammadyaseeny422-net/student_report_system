# 🎓 AI-Powered Student Report System

> An intelligent academic reporting module that uses **Machine Learning** to generate premium PDF report cards, gaming-style achievement badges, and diploma-style certificates — all powered by a Random Forest classifier.

---

## 📋 Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [The ML Model](#the-ml-model)
- [File-by-File Breakdown](#file-by-file-breakdown)
- [Output Structure](#output-structure)
- [Running the Project](#running-the-project)
- [Certificate & Badge Logic](#certificate--badge-logic)
- [Configuration](#configuration)

---

## Overview

This system takes student academic data (marks, behavior scores) and produces:

1. **PDF Report Cards** — Modern, dashboard-style report cards with:
   - Gradient header with school logo
   - Full-width subject performance table with class comparison
   - ML-predicted grade (A+, A, B, C, D)
   - Performance visualization bar chart
   - Personalized ML-driven remarks

2. **Achievement Badges** — High-quality gaming-style PNG badges for:
   - Subject toppers (one per subject per class)
   - Grade A+ achievers (>= 90% overall)
   - Position holders (1st, 2nd, 3rd)
   - Discipline & attendance excellence

3. **Diploma Certificates** — Premium PDF certificates based on **yearly** performance:
   - Academic Excellence, Subject Topper, Discipline, Attendance, Position Holder
   - Based on aggregated performance across ALL exam types (midterm + final + bimonthly)
   - Includes integrated achievement badges with circular mask

---

## How It Works

### Workflow (what happens when you run `python main.py`)

```
┌─────────────────────────────────────────────────────────┐
│  Step 1: Initialize Database (SQLite)                   │
│  Creates tables if they don't exist                     │
├─────────────────────────────────────────────────────────┤
│  Step 2: Seed Sample Data                               │
│  18 students × 4 exam types = 72 student-exam records   │
│  Each student gets either Biology OR Computer            │
├─────────────────────────────────────────────────────────┤
│  Step 3: Train/Load ML Model                            │
│  Random Forest classifier trained on synthetic data     │
│  Predicts grade (A+/A/B/C/D) from percentages           │
├─────────────────────────────────────────────────────────┤
│  Step 4: For each class × exam type:                    │
│  → Compute class averages per subject                   │
│  → Identify subject toppers (highest scorer)            │
│  → Identify position holders (top 3 overall)            │
│  → For each student:                                    │
│    → ML predicts grade + generates personalized remarks │
│    → Generate PDF report card                           │
│    → Generate achievement badge PNGs                    │
├─────────────────────────────────────────────────────────┤
│  Step 5: Generate Yearly Certificates                   │
│  → Aggregate ALL exam types into yearly performance     │
│  → Award certificates to worthy students                │
│  → Badges integrated into certificates with PIL masking │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
Student Marks (DB) → Feature Vector (9 subjects + behavior)
                   → Random Forest Prediction → Grade (A+/A/B/C/D)
                   → Personalized Remarks (ML-driven)
                   → PDF Report Card
                   → Badge PNGs (if earned)
                   → Certificates (yearly, if earned)
```

---

## Project Structure

```
student_report_system/
│
├── main.py                  # Entry point — orchestrates the entire pipeline
├── config.py                # Central configuration (subjects, grades, paths)
├── database.py              # SQLite database layer (CRUD, queries, seeder)
├── model.py                 # ML model (Random Forest training & prediction)
├── report_generator.py      # PDF report card generation (ReportLab)
├── certificate_generator.py # PDF certificate generation (diploma-style)
├── badge_generator.py       # Achievement badge PNG generation
│
├── assets/
│   ├── badges/              # 16 HQ gaming-style badge assets
│   │   ├── physics.png, chemistry.png, maths.png, ...
│   │   ├── biology.png, computer.png (separate electives)
│   │   ├── position_1st.png, position_2nd.png, position_3rd.png
│   │   ├── discipline.png, attendance.png, academic_excellence.png
│   │   └── grade_aplus.png
│   └── images/
│       └── school_logo.png  # School logo for reports & certificates
│
├── data/
│   └── academic.db          # SQLite database (auto-created)
│
├── models/
│   └── grade_model.pkl      # Trained ML model (auto-created)
│
└── media/                   # Generated output (auto-created)
    └── class_9/
        ├── midterm/         # Per-exam report cards
        ├── final/
        ├── bimonthly_1/
        ├── bimonthly_2/
        └── annual/          # Yearly certificates
```

---

## The ML Model

### How it works

The system uses a **Random Forest Classifier** from scikit-learn to predict student grades.

#### Feature Vector (12 features)

For each student, a feature vector is built:

| Index | Feature | Scale |
|-------|---------|-------|
| 0-8 | Subject percentages (Urdu, English, Maths, Biology, Computer, Chemistry, Physics, Islamiat, Pak Studies) | 0-100 |
| 9 | Average of non-zero subject percentages | 0-100 |
| 10 | Obedient score (scaled to 0-100) | 0-100 |
| 11 | Punctual score (scaled to 0-100) | 0-100 |

> **Note:** Biology and Computer are elective subjects — a student has only one. The other is 0 in the feature vector.

#### Training

- **2000 synthetic samples** generated with realistic distributions
- 5 grade classes: A+ (90-100%), A (80-89%), B (65-79%), C (50-64%), D (30-49%)
- **80/20 train/test split** with stratification
- **100 decision trees**, max depth 10
- Typical accuracy: **85-90%**

#### Prediction

```python
features = _build_feature_vector(student)    # 12 floats
grade_label = model.predict([features])[0]   # 0-4
grade = GRADE_MAP[grade_label]["grade"]       # "A+", "A", etc.
```

#### ML-Driven Remarks

Remarks are **NOT hardcoded**. The system:
1. Gets the base remark from the ML grade prediction
2. Analyzes subject percentages to find strongest/weakest subjects
3. Adds personalized subject-specific insights
4. Analyzes behavior scores for conduct remarks

Example output:
> *"Excellent work! Keep up the great effort. Outstanding in Maths (100%). Could strengthen Islamiat performance. Exemplary discipline and attendance record."*

---

## File-by-File Breakdown

### `config.py` — Central Configuration

Defines everything the system needs to know:

- **CLASSES**: `[9]` — currently Class 9 only
- **EXAM_TYPES**: `["midterm", "final", "bimonthly_1", "bimonthly_2"]`
- **Subject structures**: max marks per subject per exam type
- **ELECTIVE_SUBJECTS**: `["Biology", "Computer"]` — student has only one
- **Badge file mappings**: which PNG file for each achievement type
- **Grade definitions**: grade labels, ranges, and base remarks
- **Path helpers**: `get_student_dir()`, `get_certificate_dir()`, etc.

### `database.py` — SQLite Database Layer

**Tables:**
- `students`: student_id, name, class_num
- `exam_marks`: marks per subject per exam
- `student_behavior`: obedient/punctual scores per exam
- `generated_reports`: metadata for generated PDFs
- `generated_certificates`: metadata for generated certificates

**Key functions:**
- `get_class_exam_students()` — fetch all students with marks for a class/exam
- `get_subject_toppers()` — find highest scorer per subject
- `get_position_holders()` — rank students by overall percentage
- `get_yearly_student_summary()` — **aggregate** performance across ALL exams
- `get_yearly_subject_toppers()` — toppers based on yearly combined data
- `get_yearly_position_holders()` — positions based on yearly combined data
- `seed_sample_data()` — generates 18 realistic sample students

### `model.py` — ML Grading System

- `_build_feature_vector()` — converts student data to 12-feature array
- `_generate_synthetic_data()` — creates 2000 training samples
- `train_and_save_model()` — trains Random Forest, saves to .pkl
- `load_model()` — loads or trains model
- `predict_student()` — predicts grade + generates personalized remarks
- `predict_class_batch()` — batch prediction for a class

### `report_generator.py` — PDF Report Cards

Uses ReportLab to generate modern dashboard-style reports:

- **Header**: gradient background, school logo, exam type label
- **Student card**: ID, name, class
- **Subject table**: full-width, 7 columns (Subject, Marks, Max, %, Class Avg, vs Avg, Status)
- **Analytics card**: total score, percentage, behavior, ML grade circle, position
- **Remarks card**: ML-driven personalized text + topper award pills
- **Performance chart**: horizontal bar chart comparing student vs class average

### `certificate_generator.py` — Diploma Certificates

Generates landscape PDF certificates with:

- Navy triangular corner decorations
- School logo + name at top
- Certificate title in gold
- Student name in elegant italic serif font
- Achievement description
- Badge integrated with PIL circular mask + gold ring border
- Signature lines for teacher and principal

### `badge_generator.py` — Achievement Badges

Copies high-quality badge PNGs from `assets/badges/` to student directories.
Badge types: subject topper, grade A+, position, discipline, attendance.

### `main.py` — Pipeline Orchestrator

Runs the entire pipeline in 5 steps:
1. Database init
2. Data seeding
3. ML model loading
4. Report + badge generation (per exam)
5. Yearly certificate generation (aggregated)

---

## Output Structure

After running, the `media/` directory contains:

```
media/
├── class_9/
│   ├── midterm/
│   │   ├── C9-1001/
│   │   │   ├── report_card.pdf
│   │   │   └── badges/
│   │   │       └── (earned badge PNGs)
│   │   ├── C9-1002/
│   │   │   ├── report_card.pdf
│   │   │   └── badges/
│   │   └── ...
│   ├── final/
│   │   └── (same structure)
│   ├── bimonthly_1/
│   │   └── (same structure)
│   ├── bimonthly_2/
│   │   └── (same structure)
│   └── annual/
│       ├── C9-1002/
│       │   └── certificates/
│       │       ├── academic_C9-1002.pdf
│       │       ├── topper_Biology_C9-1002.pdf
│       │       ├── behavior_C9-1002.pdf
│       │       └── position_3_C9-1002.pdf
│       └── ...
└── _temp/
    └── (temporary badge renders for certificates)
```

---

## Running the Project

### Prerequisites

- Python 3.8+
- Virtual environment recommended

### Install Dependencies

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install reportlab scikit-learn numpy pandas joblib pillow
```

### Run

```bash
python main.py
```

This will:
1. Create `data/academic.db` with sample data
2. Train the ML model (saved to `models/grade_model.pkl`)
3. Generate all reports, badges, and certificates in `media/`

### Re-run

To regenerate everything from scratch:
```bash
# Delete old outputs
rmdir /s /q media
del data\academic.db
del models\grade_model.pkl

# Run fresh
python main.py
```

---

## Certificate & Badge Logic

### Who Gets What?

| Award | Criteria | Count per Class |
|-------|----------|-----------------|
| **Subject Topper Badge** | Highest scorer in a subject (per exam) | 1 per subject |
| **Grade A+ Badge** | >= 90% overall (per exam) | Variable |
| **Position Badge** | 1st, 2nd, 3rd in class (per exam) | 3 |
| **Discipline Badge** | Perfect 10/10 obedient (per exam) | Very rare |
| **Attendance Badge** | Perfect 10/10 punctual (per exam) | Very rare |

### Certificates (Yearly — Aggregated)

Certificates are awarded based on **whole-year** performance:

| Certificate | Criteria | Based On |
|-------------|----------|----------|
| Academic Excellence | >= 90% in ALL subjects | Yearly total |
| Subject Topper | Highest scorer per subject | Yearly total |
| Discipline Award | Average obedient >= 9/10 | Yearly average |
| Attendance Champion | Average punctual >= 9/10 | Yearly average |
| Position Holder | 1st, 2nd, 3rd overall | Yearly total |

### Biology vs Computer

- Students are assigned **either** Biology **or** Computer (not both)
- First 10 students → Biology, last 8 → Computer
- Separate badges and toppers for each
- A Biology student can never earn a Computer badge and vice versa

---

## Configuration

### School Info

Edit `config.py`:
```python
SESSION_YEAR = "2025-2026"
SCHOOL_NAME = "THE LEADERS ACADEMY"
```

### Subjects & Max Marks

Edit `_CLASS_9_MIDTERM_FINAL` and `_CLASS_9_BIMONTHLY` in `config.py`.

### Grade Thresholds

Edit `GRADE_MAP` in `config.py`:
```python
GRADE_MAP = {
    0: {"grade": "A+", "remarks": "Outstanding performance!..."},
    1: {"grade": "A",  "remarks": "Excellent work!..."},
    # ...
}
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11 |
| ML | scikit-learn (Random Forest) |
| PDF Generation | ReportLab |
| Image Processing | Pillow (PIL) |
| Database | SQLite3 |
| Data Processing | NumPy, Pandas |

---

*Built with ❤️ using AI-Powered Academic Intelligence*
