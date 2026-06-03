"""
config.py - Central configuration for the Student Report System.

Defines:
  - Supported class (Class 9) and exam types
  - Subject structures and max marks per exam type
  - Trait configuration
  - Badge and position configuration
  - Database and data source settings
  - Helper functions for dynamic config lookup
"""

import os

# ──────────────────────────────────────────────
#  CLASS & EXAM TYPES
# ──────────────────────────────────────────────

CLASSES = [9]

EXAM_TYPES = ["midterm", "final", "bimonthly_1", "bimonthly_2"]

EXAM_TYPE_LABELS = {
    "midterm": "MIDTERM",
    "final": "FINAL TERM",
    "bimonthly_1": "BIMONTHLY 1",
    "bimonthly_2": "BIMONTHLY 2",
}

# ──────────────────────────────────────────────
#  TRAIT CONFIGURATION
# ──────────────────────────────────────────────

TRAIT_CONFIG = {
    "Obedient": 10,
    "Punctual": 10,
}

# ──────────────────────────────────────────────
#  SUBJECT STRUCTURES — CLASS 9
# ──────────────────────────────────────────────

# Students take EITHER Biology OR Computer (not both).
# The elective subject key is "Biology" or "Computer" per student.
_CLASS_9_MIDTERM_FINAL = {
    "Urdu": 100,
    "English": 100,
    "Maths": 100,
    "Biology": 65,
    "Computer": 65,
    "Chemistry": 65,
    "Physics": 65,
    "Islamiat": 50,
    "Pak_Studies": 50,
}

_CLASS_9_BIMONTHLY = {
    "Urdu": 50,
    "English": 50,
    "Maths": 50,
    "Biology": 50,
    "Computer": 50,
    "Chemistry": 50,
    "Physics": 50,
    "Islamiat": 25,
    "Pak_Studies": 25,
}

# Elective subjects — a student has only ONE of these
ELECTIVE_SUBJECTS = ["Biology", "Computer"]

CLASS_9_SUBJECTS = {
    "midterm": _CLASS_9_MIDTERM_FINAL,
    "final": _CLASS_9_MIDTERM_FINAL,
    "bimonthly_1": _CLASS_9_BIMONTHLY,
    "bimonthly_2": _CLASS_9_BIMONTHLY,
}

# ──────────────────────────────────────────────
#  SUBJECT AWARD TITLES (for certificates & badges)
# ──────────────────────────────────────────────

SUBJECT_TITLES = {
    "Urdu": "Urdu Topper",
    "English": "English Excellence",
    "Maths": "Maths Topper",
    "Biology": "Biology Topper",
    "Computer": "Computer Science Topper",
    "Chemistry": "Chemistry Star",
    "Physics": "Physics Excellence",
    "Islamiat": "Islamiat Scholar",
    "Pak_Studies": "Pak Studies Topper",
}

SPECIAL_TITLES = {
    "behavior": "Discipline Excellence",
    "punctuality": "Attendance Champion",
    "academic": "Academic Excellence",
}

# ──────────────────────────────────────────────
#  BADGE CONFIGURATION
# ──────────────────────────────────────────────

# Subject badge filename mapping (maps subject key -> badge asset filename)
# Only the subject TOPPER gets the badge (one per subject per class)
SUBJECT_BADGE_FILES = {
    "Urdu": "urdu.png",
    "English": "english.png",
    "Maths": "maths.png",
    "Biology": "biology.png",
    "Computer": "computer.png",
    "Chemistry": "chemistry.png",
    "Physics": "physics.png",
    "Islamiat": "islamiat.png",
    "Pak_Studies": "pak_studies.png",
}

# Grade badge — only A+ (>= 90% overall, exceptional achievement)
GRADE_BADGE_FILE = "grade_aplus.png"

# Position badge filename mapping
POSITION_BADGE_FILES = {
    1: "position_1st.png",
    2: "position_2nd.png",
    3: "position_3rd.png",
}

POSITION_TITLES = {
    1: "1st Position",
    2: "2nd Position",
    3: "3rd Position",
}

# Special badge filenames
SPECIAL_BADGE_FILES = {
    "discipline": "discipline.png",
    "attendance": "attendance.png",
    "academic_excellence": "academic_excellence.png",
}

BADGE_ASSETS_DIR = os.path.join("assets", "badges")

# ──────────────────────────────────────────────
#  DATABASE & DATA SOURCE
# ──────────────────────────────────────────────

DATABASE_PATH = os.path.join("data", "academic.db")

# ──────────────────────────────────────────────
#  SESSION INFO
# ──────────────────────────────────────────────

SESSION_YEAR = "2025-2026"
SCHOOL_NAME = "THE LEADERS ACADEMY"

# ──────────────────────────────────────────────
#  GRADE DEFINITIONS
# ──────────────────────────────────────────────

GRADE_MAP = {
    0: {"grade": "A+", "remarks": "Outstanding performance! A truly exceptional student."},
    1: {"grade": "A",  "remarks": "Excellent work! Keep up the great effort."},
    2: {"grade": "B",  "remarks": "Good effort, but there is room for improvement."},
    3: {"grade": "C",  "remarks": "Average performance. Needs more attention to studies."},
    4: {"grade": "D",  "remarks": "Below average. Significant improvement required."},
}


# ──────────────────────────────────────────────
#  HELPER FUNCTIONS
# ──────────────────────────────────────────────

def get_subject_config(class_num, exam_type):
    """Get the subject -> max_marks mapping for a given class and exam type."""
    if class_num not in CLASSES:
        raise ValueError(f"Unsupported class: {class_num}. Must be one of {CLASSES}")
    if exam_type not in EXAM_TYPES:
        raise ValueError(f"Unsupported exam type: {exam_type}. Must be one of {EXAM_TYPES}")
    return CLASS_9_SUBJECTS[exam_type]


def get_sheet_name(class_num, exam_type):
    """Get the Excel sheet name for a given class and exam type."""
    return f"class_{class_num}_{exam_type}"


def get_student_dir(class_num, exam_type, student_id):
    """Get the per-student output directory."""
    return os.path.join("media", f"class_{class_num}", exam_type, str(student_id))


def get_report_dir(class_num, exam_type):
    """Get the output directory for report cards (legacy, use get_student_dir)."""
    return os.path.join("media", f"class_{class_num}", exam_type)


def get_certificate_dir(class_num, exam_type="final"):
    """Get the output directory for certificates (legacy, use get_student_dir)."""
    return os.path.join("media", f"class_{class_num}", exam_type)


def get_exam_label(exam_type):
    """Get the human-readable label for an exam type."""
    return EXAM_TYPE_LABELS.get(exam_type, exam_type.upper())
