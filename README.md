# 📚 Student Report & Certificate Generation System

> A Python-based system that reads student marks from Excel, uses **Machine Learning** to predict grades and badges, then generates beautiful **PDF report cards** and **certificates** — all organized by class and exam type.

---

## 📖 Table of Contents

1. [What Does This Project Do?](#-what-does-this-project-do)
2. [Project Structure (Files Explained)](#-project-structure-files-explained)
3. [How the System Works (Step by Step)](#-how-the-system-works-step-by-step)
4. [Understanding the Data Flow](#-understanding-the-data-flow)
5. [The Excel Input Format](#-the-excel-input-format)
6. [Class & Exam Rules](#-class--exam-rules)
7. [How Machine Learning Works Here](#-how-machine-learning-works-here)
8. [Output: Reports & Certificates](#-output-reports--certificates)
9. [CMS Integration (For Future)](#-cms-integration-for-future)
10. [How to Run the Project](#-how-to-run-the-project)
11. [Common Questions](#-common-questions)

---

## 🎯 What Does This Project Do?

Imagine you are a school administrator with **90 students across 5 classes** (Class 6 to Class 10). Each class takes **4 exams** per year (Midterm, Final, Bimonthly 1, Bimonthly 2). That's **360 report cards** to create!

This system does it all **automatically**:

```
Excel File (student marks)
        ↓
   Python reads it
        ↓
   ML predicts grades, remarks, badges
        ↓
   Beautiful PDF report cards are generated
        ↓
   Certificates are generated (for final term only)
```

**In simple words:** You put marks in Excel → Run the program → Get professional PDFs.

---

## 📁 Project Structure (Files Explained)

Here's every file in the project and what it does:

```
student_report_system/
│
├── main.py                  ← 🚀 The START button. Run this to generate everything.
├── config.py                ← ⚙️  All the RULES live here (subjects, marks, classes)
├── data_loader.py           ← 📥 Reads student marks from Excel
├── model.py                 ← 🤖 The ML brain — predicts grades & badges
├── report_generator.py      ← 📄 Creates the PDF report cards
├── certificate_generator.py ← 🏆 Creates the PDF certificates
├── cms_integration.py       ← 🌐 API functions for future CMS/website integration
├── compose_badges.py        ← 🎨 One-time script to create badge images
├── requirements.txt         ← 📦 List of Python libraries needed
│
├── data/
│   └── students_marks.xlsx  ← 📊 The Excel file with ALL student marks (20 sheets)
│
├── assets/
│   ├── badges/              ← 🏅 Badge images (Genius, Expert, Star, etc.)
│   └── images/
│       └── school_logo.png  ← 🏫 School logo used in reports
│
├── models/
│   └── grade_model.pkl      ← 🧠 Saved ML model (auto-created on first run)
│
└── media/                   ← 📂 ALL generated output goes here
    ├── class_6/
    │   ├── midterm/reports/
    │   ├── final/reports/
    │   ├── final/certificates/
    │   ├── bimonthly_1/reports/
    │   └── bimonthly_2/reports/
    ├── class_7/  (same structure)
    ├── class_8/  (same structure)
    ├── class_9/  (same structure)
    └── class_10/ (same structure)
```

### What Each File Does (In Simple Language)

| File | Think of it as... | What it does |
|------|-------------------|-------------|
| `main.py` | **The Manager** | Calls all other files in the right order. You only run this one. |
| `config.py` | **The Rule Book** | Contains all the rules: which subjects each class has, max marks for each exam, grade definitions, etc. |
| `data_loader.py` | **The Data Reader** | Opens the Excel file, reads a specific sheet (like "class_7_midterm"), validates the marks, and returns clean student data. |
| `model.py` | **The ML Brain** | Takes student marks, converts them to percentages, feeds them into a trained Random Forest model, and predicts the grade (A+, A, B, C, D), remarks, and badge eligibility. |
| `report_generator.py` | **The Report Printer** | Takes a student's data + ML predictions and creates a beautiful PDF report card with tables, grades, remarks, and badges. |
| `certificate_generator.py` | **The Certificate Printer** | Checks if a student qualifies for any certificates (Academic, Subject, Behavior, Punctuality) and creates professional PDF certificates. |
| `cms_integration.py` | **The API Layer** | Provides functions that a future website/CMS can call to generate reports, update marks, and access documents. |

---

## 🔄 How the System Works (Step by Step)

When you run `python main.py`, here's exactly what happens:

### Step 1: Load the ML Model
```
main.py calls → model.py → load_model()
```
- Checks if a trained model exists in `models/grade_model.pkl`
- If YES → loads it (fast!)
- If NO → trains a new model using synthetic data (takes a few seconds, only happens once)

### Step 2: Loop Through Every Class and Exam
```
For each class (6, 7, 8, 9, 10):
    For each exam (midterm, final, bimonthly_1, bimonthly_2):
        → Load students from that Excel sheet
        → Predict grades for each student
        → Generate PDF reports
        → If it's the FINAL exam → Also generate certificates
```

### Step 3: Load Student Data
```
main.py calls → data_loader.py → load_data(class_num=7, exam_type="midterm")
```
- Opens `data/students_marks.xlsx`
- Goes to sheet `class_7_midterm`
- Reads each row (each row = one student)
- Validates marks (checks if they're within allowed range)
- Calculates percentages per subject and overall
- Returns a list of student dictionaries (like mini databases)

### Step 4: ML Prediction
```
main.py calls → model.py → predict_student(model, student)
```
For each student:
- Takes their marks percentages (not raw marks!)
- Feeds into the Random Forest model
- Gets back: Grade (A+/A/B/C/D), Remarks, Badge list
- **Important:** This does NOT change the actual marks! It only classifies.

### Step 5: Generate Report Card PDF
```
main.py calls → report_generator.py → generate_student_report(student, ml_result)
```
- Creates a beautiful PDF with:
  - School header with logo
  - Student name, ID, class
  - Exam type (e.g., "MIDTERM PERFORMANCE REPORT")
  - Marks table showing ACTUAL marks (not ML-modified)
  - Total, percentage, grade
  - Teacher remarks (from ML)
  - Achievement badges

### Step 6: Generate Certificates (Final Term Only!)
```
main.py calls → certificate_generator.py → generate_all_certificates(student)
```
- Only runs for the **final** exam, not midterm or bimonthly
- Checks eligibility:
  - **Academic Excellence:** 90%+ in ALL subjects
  - **Subject Excellence:** 90%+ in any single subject
  - **Behavior Excellence:** Obedient 9+ AND Punctual 9+
  - **Punctuality:** Punctual 9+
- Generates professional landscape certificates for eligible students

---

## 🔀 Understanding the Data Flow

Here's how data moves through the system:

```
┌─────────────────────────────────────────────────────────┐
│                    EXCEL FILE                            │
│   data/students_marks.xlsx                               │
│   (20 sheets: class_6_midterm, class_6_final, ...)       │
└────────────────────┬────────────────────────────────────┘
                     │ data_loader.py reads specific sheet
                     ▼
┌─────────────────────────────────────────────────────────┐
│              STUDENT DATA (Python Dictionary)            │
│                                                          │
│  {                                                       │
│    "student_id": "C7-1001",                              │
│    "name": "Ali Khan",                                   │
│    "class_num": 7,                                       │
│    "exam_type": "midterm",                               │
│    "marks": {"Urdu": 78, "English": 82, "Maths": 90...} │  ← ACTUAL marks
│    "subject_percentages": {"Urdu": 78.0, ...},           │  ← For ML input
│    "max_marks_per_subject": {"Urdu": 100, ...},          │  ← For report display
│    "percentage": 82.5,                                   │
│    "obedient": 9,                                        │
│    "punctual": 10                                        │
│  }                                                       │
└───────────┬─────────────────────────────┬───────────────┘
            │                             │
            ▼                             ▼
   ┌────────────────┐           ┌──────────────────┐
   │   model.py     │           │ report_generator  │
   │                │           │      .py          │
   │ Takes % values │           │                   │
   │ Predicts:      │           │ Takes ACTUAL marks│
   │  - Grade       │──────────▶│ + ML results      │
   │  - Remarks     │ ML result │ Creates PDF with: │
   │  - Badges      │           │  - Real marks     │
   └────────────────┘           │  - ML grade       │
                                │  - ML remarks     │
                                │  - Badges         │
                                └──────────────────┘
                                        │
                                        ▼
                                ┌──────────────────┐
                                │   PDF Report      │
                                │   Card File       │
                                │                   │
                                │ media/class_7/    │
                                │ midterm/reports/  │
                                │ C7-1001.pdf       │
                                └──────────────────┘
```

**Key concept:** The ML model uses **percentages** internally (so it works the same for all classes and exams). But the **report card shows actual marks** exactly as entered in Excel.

---

## 📊 The Excel Input Format

The Excel file `data/students_marks.xlsx` has **20 sheets** (5 classes × 4 exams).

### Sheet Naming Convention
```
class_{NUMBER}_{EXAM_TYPE}

Examples:
  class_6_midterm
  class_7_final
  class_9_bimonthly_1
  class_10_bimonthly_2
```

### Columns for Classes 6, 7, 8
```
Student_ID | Name | Urdu | English | Maths | Biology | Computer | Chemistry | Physics | Islamiat | Pak_Studies | Obedient | Punctual
```
All 9 subjects. Biology and Computer are SEPARATE columns.

### Columns for Classes 9, 10
```
Student_ID | Name | Urdu | English | Maths | Biology/Computer | Chemistry | Physics | Islamiat | Pak_Studies | Obedient | Punctual
```
Only 8 subjects. Biology and Computer are COMBINED into one column (`Biology/Computer`) because a student takes only one of them.

---

## 📏 Class & Exam Rules

All these rules are defined in `config.py`:

### Classes 6, 7, 8 — Max Marks per Subject

| Exam Type | Urdu | English | Maths | Biology | Computer | Chemistry | Physics | Islamiat | Pak Studies |
|-----------|------|---------|-------|---------|----------|-----------|---------|----------|-------------|
| Midterm | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| Final | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| Bimonthly 1 | 50 | 50 | 50 | 50 | 50 | 50 | 50 | 50 | 50 |
| Bimonthly 2 | 50 | 50 | 50 | 50 | 50 | 50 | 50 | 50 | 50 |

### Classes 9, 10 — Max Marks per Subject

| Exam Type | Urdu | English | Maths | Bio/Comp | Chemistry | Physics | Islamiat | Pak Studies |
|-----------|------|---------|-------|----------|-----------|---------|----------|-------------|
| Midterm | 100 | 100 | 100 | 65 | 65 | 65 | 50 | 50 |
| Final | 100 | 100 | 100 | 65 | 65 | 65 | 50 | 50 |
| Bimonthly 1 | 50 | 50 | 50 | 50 | 50 | 50 | 25 | 25 |
| Bimonthly 2 | 50 | 50 | 50 | 50 | 50 | 50 | 25 | 25 |

### Behavioral Traits (All Classes)
- **Obedient:** Score from 0 to 10
- **Punctual:** Score from 0 to 10

---

## 🤖 How Machine Learning Works Here

### What is the ML model doing?

Instead of writing manual rules like:
```python
# OLD WAY (hardcoded if/else)
if percentage >= 90:
    grade = "A+"
elif percentage >= 80:
    grade = "A"
...
```

We use a **trained Machine Learning model** that learns patterns:
```python
# NEW WAY (ML-driven)
grade = model.predict(student_features)  # Model decides!
```

### How does it learn?

Since we don't have thousands of real historical records, the model is trained on **synthetic data** — computer-generated examples that simulate realistic student performance patterns.

```
Training Process:
  1. Generate 2000 fake students with marks in different ranges
  2. Label them (90-100% = A+, 80-89% = A, 65-79% = B, etc.)
  3. Train a Random Forest classifier on this data
  4. Save the trained model to models/grade_model.pkl
  5. Next time, just load the saved model (no retraining needed!)
```

### What's a Random Forest?

Think of it like asking **100 teachers** to look at a student's marks and vote on the grade. Each teacher (called a "decision tree") might weigh different subjects differently. The final grade is whatever the **majority votes** for. That's Random Forest!

### Feature Normalization (The Smart Part)

The system handles a tricky problem: different classes have different max marks!

```
Class 7 Midterm:  English out of 100 → student got 80 → 80%
Class 9 Bimonthly: Islamiat out of 25 → student got 20 → 80%
```

Both are equally good (80%), but the raw numbers are very different (80 vs 20).

**Solution:** Convert ALL marks to percentages before feeding to ML. This way, the same model works for every class and exam type.

```python
# Inside model.py — what happens internally:
features = [78.0, 82.0, 90.0, ...]  # All percentages (0-100 scale)
grade = model.predict([features])     # Model sees consistent data
```

### What ML Outputs

For each student, the ML model produces:

| Output | Example | Used In |
|--------|---------|---------|
| **Grade** | "A+", "A", "B", "C", "D" | Report card |
| **Remarks** | "Outstanding performance! A very well-behaved student." | Report card |
| **Subject Badges** | ["Maths_Genius.png", "English_Expert.png"] | Report card |
| **Trait Badges** | ["obedient.png", "punctual.png"] | Report card |

### Badge Tiers (ML-Driven)

Badges are only awarded to students predicted as B grade or above:

| Tier | Requirement | Badge Image |
|------|------------|-------------|
| 🥇 Genius | 90%+ in a subject | `Subject_Genius.png` |
| 🥈 Expert | 80%+ in a subject | `Subject_Expert.png` |
| 🥉 Star | 70%+ in a subject | `Subject_Star.png` |

---

## 📄 Output: Reports & Certificates

### Report Cards (Generated for ALL exams)

Each student gets a PDF report card per exam with:
- 🏫 School logo and name
- 📝 Dynamic header (e.g., "MIDTERM PERFORMANCE REPORT")
- 👤 Student ID, name, and class
- 📊 Marks table with actual obtained marks, max marks, and percentage
- 📈 Total marks, overall percentage
- 🏅 ML-predicted grade (big colored letter)
- 💬 Teacher remarks (generated by ML)
- 🎖️ Achievement badges

### Certificates (Generated for FINAL TERM only)

| Certificate Type | Condition | Example |
|-----------------|-----------|---------|
| **Academic Excellence** | 90%+ in ALL subjects | Rare — requires excellence everywhere |
| **Subject Excellence** | 90%+ in any ONE subject | "Maths Scholar", "Physics Excellence" |
| **Behavior Excellence** | Obedient ≥ 9 AND Punctual ≥ 9 | For well-disciplined students |
| **Punctuality** | Punctual ≥ 9 | For consistently punctual students |

### Where to Find the Output

```
media/
├── class_6/
│   ├── midterm/reports/           ← 18 PDF report cards
│   ├── final/reports/             ← 18 PDF report cards
│   ├── final/certificates/        ← Certificates for eligible students
│   ├── bimonthly_1/reports/       ← 18 PDF report cards
│   └── bimonthly_2/reports/       ← 18 PDF report cards
├── class_7/ ... (same structure)
├── class_8/ ... (same structure)
├── class_9/ ... (same structure)
└── class_10/ ... (same structure)
```

---

## 🌐 CMS Integration (For Future)

### What is CMS Integration?

CMS = **Content Management System** (like a school portal website).

Right now, the system reads from Excel files. In the future, it could connect to a **web-based school portal** where teachers enter marks online. The system is already prepared for this!

### How is it Prepared?

In `data_loader.py`, there are two functions:

```python
# Currently used — reads from Excel
load_data_from_excel(class_num=7, exam_type="midterm")

# Future — will read from a database
load_data_from_cms(class_num=7, exam_type="midterm")  # Not yet implemented

# The smart wrapper — automatically picks the right source
load_data(class_num=7, exam_type="midterm")  # Uses DATA_SOURCE from config.py
```

To switch from Excel to CMS in the future, you just change ONE line in `config.py`:

```python
DATA_SOURCE = "excel"   # ← Current (reads from Excel)
DATA_SOURCE = "cms"     # ← Future (reads from database)
```

### CMS API Functions (in `cms_integration.py`)

These functions are ready to be called by a website:

```python
# For STUDENTS — view their own documents
get_student_access("C7-1001", class_num=7)
# Returns: paths to all their reports and certificates

# For TEACHERS — view/edit their class
get_teacher_access(["C7-1001", "C7-1002"], class_num=7)
# Returns: all documents for those students

update_student_marks("C7-1001", {"Maths": 95}, class_num=7, exam_type="midterm")
# Updates marks and regenerates the report card!

# For ADMINS — view everything
get_admin_access(class_num=7, exam_type="final")
# Returns: all students, all documents for that class/exam
```

### Role-Based Access

| Role | Can Do |
|------|--------|
| **Student** | View own reports & certificates |
| **Teacher** | View class data, edit marks, regenerate reports |
| **Admin** | View everything, generate all reports |

---

## 🚀 How to Run the Project

### Prerequisites
- Python 3.8 or higher
- The required libraries (pandas, scikit-learn, reportlab, etc.)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Make Sure Your Data is Ready
Place your Excel file at `data/students_marks.xlsx` with the correct sheet names (see Excel format section above).

### Step 3: Run the System
```bash
python main.py
```

### Step 4: Find Your Output
- Report cards → `media/class_N/exam_type/reports/`
- Certificates → `media/class_N/final/certificates/`

---

## ❓ Common Questions

### Q: What if I only want to generate reports for one class?
Right now, `main.py` processes all classes. You can use `cms_integration.py` functions to target specific classes:
```python
from cms_integration import generate_all_reports
generate_all_reports(class_num=7)  # Only Class 7, all exams
generate_all_reports(class_num=9, exam_type="final")  # Only Class 9 Final
```

### Q: What if a student got 0 marks in a subject?
The system handles it correctly. Zero marks = 0% = still valid.

### Q: Why are there no Academic Excellence certificates?
Academic Excellence requires 90%+ in **ALL** subjects. With the current data, no student achieved this. It's a very high bar!

### Q: Can I add more classes (like Class 11 or 12)?
Yes! Add the class number to `CLASSES` in `config.py` and define the subject structure. The rest of the system will handle it automatically.

### Q: How do I add a new subject?
Add it to the subject config dictionaries in `config.py`. No need to change any other file.

### Q: What if the ML model gives wrong grades?
You can retrain it by deleting `models/grade_model.pkl` and running again. You can also adjust the grade ranges in `model.py`'s `_generate_synthetic_data()` function.

### Q: Can I change the report card design?
Yes! Edit `report_generator.py`. The design uses the `reportlab` library. You can change colors, fonts, layout, etc.

---

## 🧩 Quick Reference: Config Cheat Sheet

Everything configurable lives in `config.py`:

| Setting | What it Controls |
|---------|-----------------|
| `CLASSES` | Which classes are supported (default: 6-10) |
| `EXAM_TYPES` | Which exam types exist |
| `CLASS_6_8_SUBJECTS` | Subject→max_marks for classes 6-8 |
| `CLASS_9_10_SUBJECTS` | Subject→max_marks for classes 9-10 |
| `TRAIT_CONFIG` | Behavioral trait max scores |
| `DATA_SOURCE` | "excel" or "cms" (future) |
| `DEFAULT_EXCEL_FILE` | Path to the Excel data file |
| `SESSION_YEAR` | Academic year shown on certificates |
| `SCHOOL_NAME` | School name shown on all PDFs |
| `BADGE_TIERS` | Percentage thresholds for badge levels |
| `GRADE_MAP` | Grade labels and remarks for each ML class |

---

*Built with ❤️ using Python, scikit-learn, and ReportLab*
