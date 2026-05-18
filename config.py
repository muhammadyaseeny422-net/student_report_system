"""
config.py - Central configuration for the Multi-Class, Multi-Exam Student Report System.

Defines:
  - Supported classes and exam types
  - Subject structures and max marks per class/exam
  - Trait configuration
  - Data source toggle (Excel vs future CMS)
  - Helper functions for dynamic config lookup
"""

# ──────────────────────────────────────────────
#  CLASSES & EXAM TYPES
# ──────────────────────────────────────────────

CLASSES = [6, 7, 8, 9, 10]

EXAM_TYPES = ["midterm", "final", "bimonthly_1", "bimonthly_2"]

# Human-readable exam type labels (used in report headers)
EXAM_TYPE_LABELS = {
    "midterm": "MIDTERM",
    "final": "FINAL TERM",
    "bimonthly_1": "BIMONTHLY 1",
    "bimonthly_2": "BIMONTHLY 2",
}

# ──────────────────────────────────────────────
#  TRAIT CONFIGURATION (same for all classes)
# ──────────────────────────────────────────────

TRAIT_CONFIG = {
    "Obedient": 10,
    "Punctual": 10,
}

# ──────────────────────────────────────────────
#  SUBJECT STRUCTURES — CLASSES 6, 7, 8
# ──────────────────────────────────────────────
# All 9 subjects. Midterm/Final out of 100, Bimonthly out of 50.

_CLASS_6_8_MIDTERM_FINAL = {
    "Urdu": 100,
    "English": 100,
    "Maths": 100,
    "Biology": 100,
    "Computer": 100,
    "Chemistry": 100,
    "Physics": 100,
    "Islamiat": 100,
    "Pak_Studies": 100,
}

_CLASS_6_8_BIMONTHLY = {
    "Urdu": 50,
    "English": 50,
    "Maths": 50,
    "Biology": 50,
    "Computer": 50,
    "Chemistry": 50,
    "Physics": 50,
    "Islamiat": 50,
    "Pak_Studies": 50,
}

CLASS_6_8_SUBJECTS = {
    "midterm": _CLASS_6_8_MIDTERM_FINAL,
    "final": _CLASS_6_8_MIDTERM_FINAL,
    "bimonthly_1": _CLASS_6_8_BIMONTHLY,
    "bimonthly_2": _CLASS_6_8_BIMONTHLY,
}

# ──────────────────────────────────────────────
#  SUBJECT STRUCTURES — CLASSES 9, 10
# ──────────────────────────────────────────────
# Biology/Computer is a single combined column (student takes one or the other).
# Different max marks per exam type.

_CLASS_9_10_MIDTERM_FINAL = {
    "Urdu": 100,
    "English": 100,
    "Maths": 100,
    "Biology/Computer": 65,
    "Chemistry": 65,
    "Physics": 65,
    "Islamiat": 50,
    "Pak_Studies": 50,
}

_CLASS_9_10_BIMONTHLY = {
    "Urdu": 50,
    "English": 50,
    "Maths": 50,
    "Biology/Computer": 50,
    "Chemistry": 50,
    "Physics": 50,
    "Islamiat": 25,
    "Pak_Studies": 25,
}

CLASS_9_10_SUBJECTS = {
    "midterm": _CLASS_9_10_MIDTERM_FINAL,
    "final": _CLASS_9_10_MIDTERM_FINAL,
    "bimonthly_1": _CLASS_9_10_BIMONTHLY,
    "bimonthly_2": _CLASS_9_10_BIMONTHLY,
}

# ──────────────────────────────────────────────
#  SUBJECT TITLES (for certificates & badges)
# ──────────────────────────────────────────────

SUBJECT_TITLES = {
    "Urdu": "Urdu Scholar",
    "English": "English Excellence",
    "Maths": "Maths Scholar",
    "Biology": "Biology Expert",
    "Computer": "Computer Science Excellence",
    "Biology/Computer": "Science Excellence",
    "Chemistry": "Chemistry Star",
    "Physics": "Physics Excellence",
    "Islamiat": "Islamiat Scholar",
    "Pak_Studies": "Pak Studies Scholar",
}

# ──────────────────────────────────────────────
#  DATA SOURCE TOGGLE
# ──────────────────────────────────────────────

# Switch between "excel" (current) and "cms" (future)
DATA_SOURCE = "excel"

# Default Excel file path
DEFAULT_EXCEL_FILE = "data/students_marks.xlsx"

# ──────────────────────────────────────────────
#  SESSION INFO
# ──────────────────────────────────────────────

SESSION_YEAR = "2025-2026"
SCHOOL_NAME = "THE LEADERS ACADEMY"

# ──────────────────────────────────────────────
#  BADGE TIERS (percentage thresholds)
# ──────────────────────────────────────────────

BADGE_TIERS = {
    "Genius": 90,
    "Expert": 80,
    "Star": 70,
}

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
    """
    Get the subject -> max_marks mapping for a given class and exam type.

    Args:
        class_num: int (6, 7, 8, 9, or 10)
        exam_type: str ("midterm", "final", "bimonthly_1", "bimonthly_2")

    Returns:
        dict of {subject_name: max_marks}
    """
    if class_num not in CLASSES:
        raise ValueError(f"Unsupported class: {class_num}. Must be one of {CLASSES}")
    if exam_type not in EXAM_TYPES:
        raise ValueError(f"Unsupported exam type: {exam_type}. Must be one of {EXAM_TYPES}")

    if class_num in (6, 7, 8):
        return CLASS_6_8_SUBJECTS[exam_type]
    else:  # 9 or 10
        return CLASS_9_10_SUBJECTS[exam_type]


def get_sheet_name(class_num, exam_type):
    """
    Get the Excel sheet name for a given class and exam type.
    Example: class_7_midterm, class_10_bimonthly_1
    """
    return f"class_{class_num}_{exam_type}"


def get_report_dir(class_num, exam_type):
    """Get the output directory for report cards."""
    return f"media/class_{class_num}/{exam_type}/reports"


def get_certificate_dir(class_num):
    """Get the output directory for certificates (final term only)."""
    return f"media/class_{class_num}/final/certificates"


def get_exam_label(exam_type):
    """Get the human-readable label for an exam type."""
    return EXAM_TYPE_LABELS.get(exam_type, exam_type.upper())
