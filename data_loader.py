"""
data_loader.py - Loads and validates student data from Excel or CMS.

Supports:
  - Multi-class (6-10) and multi-exam loading
  - Dynamic subject validation per class/exam
  - Teacher mark overrides for CMS integration
  - Switchable data source (Excel / CMS)
"""

import pandas as pd
import os
from config import (
    get_subject_config, get_sheet_name, TRAIT_CONFIG,
    DATA_SOURCE, DEFAULT_EXCEL_FILE,
)


def validate_marks(row, subject_config):
    """
    Validate a single student's marks against the given subject config.

    Args:
        row: dict-like row from a DataFrame
        subject_config: dict of {subject: max_marks} for this class/exam

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    student_id = row.get("Student_ID", "Unknown")

    for subject, max_mark in subject_config.items():
        val = row.get(subject)
        if val is None or pd.isna(val):
            errors.append(f"Student {student_id}: Missing {subject}")
        elif not (0 <= float(val) <= max_mark):
            errors.append(f"Student {student_id}: {subject}={val} not in 0-{max_mark}")

    for trait, max_mark in TRAIT_CONFIG.items():
        val = row.get(trait)
        if val is None or pd.isna(val):
            errors.append(f"Student {student_id}: Missing {trait}")
        elif not (0 <= float(val) <= max_mark):
            errors.append(f"Student {student_id}: {trait}={val} not in 0-{max_mark}")

    return len(errors) == 0, errors


def _parse_students(df, class_num, exam_type, subject_config):
    """
    Parse a DataFrame into a list of student dicts.

    Each student dict contains:
      - student_id, name, class_num, exam_type
      - marks (original obtained marks)
      - subject_percentages (percentage per subject)
      - obedient, punctual (0-10 scores)
      - total_marks, max_marks, percentage (overall)
    """
    students = []
    all_errors = []
    total_max = sum(subject_config.values())

    for _, row in df.iterrows():
        is_valid, errors = validate_marks(row, subject_config)
        if not is_valid:
            all_errors.extend(errors)
            continue  # Skip invalid rows but keep processing

        student = {
            "student_id": str(row["Student_ID"]),
            "name": str(row["Name"]).strip(),
            "class_num": class_num,
            "exam_type": exam_type,
            "marks": {},
            "max_marks_per_subject": dict(subject_config),
            "subject_percentages": {},
            "obedient": int(row["Obedient"]),
            "punctual": int(row["Punctual"]),
        }

        total_obtained = 0
        for subject, max_mark in subject_config.items():
            obtained = float(row[subject])
            student["marks"][subject] = obtained
            student["subject_percentages"][subject] = (obtained / max_mark) * 100
            total_obtained += obtained

        student["total_marks"] = total_obtained
        student["max_marks"] = total_max
        student["percentage"] = (total_obtained / total_max) * 100

        students.append(student)

    if all_errors:
        print(f"  WARNING: {len(all_errors)} validation errors found:")
        for e in all_errors[:10]:
            print(f"    - {e}")

    return students


# ──────────────────────────────────────────────
#  EXCEL DATA SOURCE
# ──────────────────────────────────────────────

def load_data_from_excel(class_num, exam_type, file_path=None):
    """
    Load student data from an Excel file for a specific class and exam type.

    Reads from the sheet named 'class_{N}_{exam_type}'.

    Args:
        class_num: int (6-10)
        exam_type: str ("midterm", "final", "bimonthly_1", "bimonthly_2")
        file_path: path to the Excel file (defaults to config)

    Returns:
        list of student dicts
    """
    file_path = file_path or DEFAULT_EXCEL_FILE

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")

    sheet_name = get_sheet_name(class_num, exam_type)
    subject_config = get_subject_config(class_num, exam_type)

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    except ValueError:
        raise ValueError(f"Sheet '{sheet_name}' not found in {file_path}")

    # Verify required columns exist
    required = ["Student_ID", "Name"] + list(subject_config.keys()) + list(TRAIT_CONFIG.keys())
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in sheet '{sheet_name}': {missing}")

    return _parse_students(df, class_num, exam_type, subject_config)


# ──────────────────────────────────────────────
#  CMS DATA SOURCE (Future Integration)
# ──────────────────────────────────────────────

def load_data_from_cms(class_num, exam_type):
    """
    Load student data from a CMS database.

    STUB: This function is a placeholder for future CMS integration.
    When implemented, it should query the CMS database and return
    the same student dict format as load_data_from_excel().

    Args:
        class_num: int (6-10)
        exam_type: str

    Returns:
        list of student dicts
    """
    raise NotImplementedError(
        "CMS data loading is not yet implemented. "
        "Set DATA_SOURCE = 'excel' in config.py to use Excel files."
    )


# ──────────────────────────────────────────────
#  UNIFIED DATA LOADER (switchable source)
# ──────────────────────────────────────────────

def load_data(class_num, exam_type, file_path=None):
    """
    Load student data from the configured data source.

    Uses DATA_SOURCE from config.py to decide whether to load
    from Excel or CMS.

    Args:
        class_num: int (6-10)
        exam_type: str
        file_path: optional override for Excel path

    Returns:
        list of student dicts
    """
    if DATA_SOURCE == "excel":
        return load_data_from_excel(class_num, exam_type, file_path)
    elif DATA_SOURCE == "cms":
        return load_data_from_cms(class_num, exam_type)
    else:
        raise ValueError(f"Unknown DATA_SOURCE: {DATA_SOURCE}. Use 'excel' or 'cms'.")


# ──────────────────────────────────────────────
#  TEACHER OVERRIDES
# ──────────────────────────────────────────────

def apply_teacher_overrides(students, overrides, class_num, exam_type):
    """
    Apply teacher mark overrides to student data.

    Args:
        students: list of student dicts
        overrides: dict like {student_id: {"Maths": 85, "English": 72, ...}}
        class_num: int (6-10)
        exam_type: str

    Returns:
        updated students list
    """
    subject_config = get_subject_config(class_num, exam_type)
    overrides_by_id = {str(k): v for k, v in overrides.items()}
    total_max = sum(subject_config.values())

    for student in students:
        sid = student["student_id"]
        if sid not in overrides_by_id:
            continue

        updates = overrides_by_id[sid]
        for key, value in updates.items():
            if key in subject_config:
                max_mark = subject_config[key]
                if 0 <= value <= max_mark:
                    student["marks"][key] = float(value)
                    student["subject_percentages"][key] = (value / max_mark) * 100
            elif key in TRAIT_CONFIG:
                max_mark = TRAIT_CONFIG[key]
                if 0 <= value <= max_mark:
                    student[key.lower()] = int(value)

        # Recalculate totals
        student["total_marks"] = sum(student["marks"].values())
        student["percentage"] = (student["total_marks"] / total_max) * 100

    return students


# ──────────────────────────────────────────────
#  UTILITY
# ──────────────────────────────────────────────

def get_student_by_id(students, student_id):
    """Find a student by ID from a list of student dicts."""
    target = str(student_id)
    for s in students:
        if s["student_id"] == target:
            return s
    return None
