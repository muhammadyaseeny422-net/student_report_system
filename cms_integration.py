"""
cms_integration.py - CMS integration module for the Multi-Class Student Report System.

Provides role-based access functions for Students, Teachers, and Admins.
All functions are class-aware and exam-aware.
Designed as a module to be imported by a CMS portal.
"""

import os
from data_loader import load_data, apply_teacher_overrides, get_student_by_id
from model import load_model, predict_student
from report_generator import generate_student_report
from certificate_generator import generate_all_certificates
from config import (
    CLASSES, EXAM_TYPES, get_subject_config,
    get_report_dir, get_certificate_dir, TRAIT_CONFIG,
)


# ──────────────────────────────────────────────
#  FILE ACCESS FUNCTIONS (return paths)
# ──────────────────────────────────────────────

def get_student_report(student_id, class_num, exam_type):
    """Get the file path of a student's report card. Returns None if not found."""
    report_dir = get_report_dir(class_num, exam_type)
    path = os.path.join(report_dir, f"{student_id}.pdf")
    return path if os.path.exists(path) else None


def get_academic_certificate(student_id, class_num):
    """Get the file path of a student's academic excellence certificate."""
    cert_dir = get_certificate_dir(class_num)
    path = os.path.join(cert_dir, f"academic_{student_id}.pdf")
    return path if os.path.exists(path) else None


def get_behavior_certificate(student_id, class_num):
    """Get the file path of a student's behavior excellence certificate."""
    cert_dir = get_certificate_dir(class_num)
    path = os.path.join(cert_dir, f"behavior_{student_id}.pdf")
    return path if os.path.exists(path) else None


def get_punctuality_certificate(student_id, class_num):
    """Get the file path of a student's punctuality certificate."""
    cert_dir = get_certificate_dir(class_num)
    path = os.path.join(cert_dir, f"punctuality_{student_id}.pdf")
    return path if os.path.exists(path) else None


# ──────────────────────────────────────────────
#  GENERATION FUNCTIONS
# ──────────────────────────────────────────────

def generate_report(student_id, class_num, exam_type, data_file=None):
    """
    Generate report card for a single student.

    Args:
        student_id: student identifier
        class_num: int (6-10)
        exam_type: str
        data_file: optional Excel file path override

    Returns: file path of the generated report
    """
    students = load_data(class_num, exam_type, data_file)
    student = get_student_by_id(students, student_id)

    if student is None:
        raise ValueError(f"Student ID {student_id} not found in class {class_num} {exam_type}")

    model = load_model()
    ml_result = predict_student(model, student)
    return generate_student_report(student, ml_result)


def generate_certificates(student_id, class_num, data_file=None):
    """
    Generate all applicable certificates for a student (final term only).

    Args:
        student_id: student identifier
        class_num: int (6-10)
        data_file: optional Excel file path override

    Returns: dict of {cert_type: file_path_or_None}
    """
    students = load_data(class_num, "final", data_file)
    student = get_student_by_id(students, student_id)

    if student is None:
        raise ValueError(f"Student ID {student_id} not found in class {class_num} final")

    return generate_all_certificates(student)


def regenerate_report_after_teacher_update(student_id, updated_marks, class_num, exam_type,
                                            data_file=None):
    """
    Regenerate report card after a teacher updates marks.

    Args:
        student_id: student identifier
        updated_marks: dict like {"Maths": 85, "English": 72}
        class_num: int (6-10)
        exam_type: str
        data_file: optional Excel file path override

    Returns: file path of the regenerated report
    """
    students = load_data(class_num, exam_type, data_file)

    # Apply teacher overrides
    students = apply_teacher_overrides(students, {student_id: updated_marks},
                                        class_num, exam_type)
    student = get_student_by_id(students, student_id)

    if student is None:
        raise ValueError(f"Student ID {student_id} not found after applying overrides")

    model = load_model()
    ml_result = predict_student(model, student)

    # Regenerate report
    report_path = generate_student_report(student, ml_result)

    # Regenerate certificates if this is final term
    if exam_type == "final":
        generate_all_certificates(student)

    return report_path


# ──────────────────────────────────────────────
#  TEACHER FUNCTIONS
# ──────────────────────────────────────────────

def update_student_marks(student_id, new_marks, class_num, exam_type, data_file=None):
    """
    Update student marks (teacher authority).

    Args:
        student_id: student identifier
        new_marks: dict like {"Maths": 85, "English": 72, "Obedient": 9}
        class_num: int (6-10)
        exam_type: str
        data_file: optional Excel file path override

    Returns: dict with report path and status message

    Note: Updates in-memory and regenerates documents.
    For persistent storage, the CMS should update its database.
    """
    subject_config = get_subject_config(class_num, exam_type)

    # Validate the new marks against class/exam config
    for key, value in new_marks.items():
        if key in subject_config:
            max_mark = subject_config[key]
            if not (0 <= value <= max_mark):
                raise ValueError(f"{key} mark {value} not in range 0-{max_mark}")
        elif key in TRAIT_CONFIG:
            max_mark = TRAIT_CONFIG[key]
            if not (0 <= value <= max_mark):
                raise ValueError(f"{key} mark {value} not in range 0-{max_mark}")
        else:
            raise ValueError(f"Unknown field '{key}' for class {class_num} {exam_type}")

    report_path = regenerate_report_after_teacher_update(
        student_id, new_marks, class_num, exam_type, data_file
    )

    return {
        "report": report_path,
        "message": f"Marks updated and report regenerated for {student_id} "
                   f"(class {class_num}, {exam_type})"
    }


def get_teacher_access(student_ids, class_num, exam_type="final"):
    """
    Get all reports and certificates for a list of assigned students.

    Args:
        student_ids: list of student IDs
        class_num: int (6-10)
        exam_type: str (defaults to "final")

    Returns: dict of {student_id: {report, certificates}}
    """
    result = {}
    for sid in student_ids:
        result[sid] = {
            "report": get_student_report(sid, class_num, exam_type),
            "academic": get_academic_certificate(sid, class_num),
            "behavior": get_behavior_certificate(sid, class_num),
            "punctuality": get_punctuality_certificate(sid, class_num),
        }
    return result


# ──────────────────────────────────────────────
#  STUDENT FUNCTIONS
# ──────────────────────────────────────────────

def get_student_access(student_id, class_num):
    """
    Get all available documents for a student (student role).

    Returns documents across all exam types for the student's class.
    """
    docs = {"student_id": student_id, "class": class_num, "reports": {}, "certificates": {}}

    # Reports for each exam type
    for exam_type in EXAM_TYPES:
        report = get_student_report(student_id, class_num, exam_type)
        if report:
            docs["reports"][exam_type] = report

    # Certificates (final term only)
    docs["certificates"] = {
        "academic": get_academic_certificate(student_id, class_num),
        "behavior": get_behavior_certificate(student_id, class_num),
        "punctuality": get_punctuality_certificate(student_id, class_num),
    }

    return docs


# ──────────────────────────────────────────────
#  ADMIN FUNCTIONS
# ──────────────────────────────────────────────

def get_admin_access(class_num=None, exam_type=None, data_file=None):
    """
    Get all student reports and certificates (admin access).

    Args:
        class_num: specific class (or None for all)
        exam_type: specific exam (or None for all)
        data_file: optional Excel file path override

    Returns: nested dict organized by class and exam
    """
    classes = [class_num] if class_num else CLASSES
    exams = [exam_type] if exam_type else EXAM_TYPES

    result = {}
    for cls in classes:
        result[f"class_{cls}"] = {}
        for exam in exams:
            try:
                students = load_data(cls, exam, data_file)
                student_docs = {}
                for student in students:
                    sid = student["student_id"]
                    student_docs[sid] = {
                        "name": student["name"],
                        "report": get_student_report(sid, cls, exam),
                    }
                    if exam == "final":
                        student_docs[sid]["academic"] = get_academic_certificate(sid, cls)
                        student_docs[sid]["behavior"] = get_behavior_certificate(sid, cls)
                        student_docs[sid]["punctuality"] = get_punctuality_certificate(sid, cls)
                result[f"class_{cls}"][exam] = student_docs
            except (ValueError, FileNotFoundError):
                result[f"class_{cls}"][exam] = {}

    return result


def generate_all_reports(class_num=None, exam_type=None, data_file=None):
    """
    Generate reports and certificates for students.

    Args:
        class_num: specific class (or None for all classes)
        exam_type: specific exam (or None for all exams)
        data_file: optional Excel file path override

    Returns: summary dict with counts
    """
    classes = [class_num] if class_num else CLASSES
    exams = [exam_type] if exam_type else EXAM_TYPES

    model = load_model()
    total_reports = 0
    cert_counts = {"academic": 0, "subject": 0, "behavior": 0, "punctuality": 0}

    for cls in classes:
        for exam in exams:
            try:
                students = load_data(cls, exam, data_file)
            except (ValueError, FileNotFoundError) as e:
                print(f"  Skipping class {cls} {exam}: {e}")
                continue

            for student in students:
                ml_result = predict_student(model, student)
                generate_student_report(student, ml_result)
                total_reports += 1

                # Certificates only for final term
                if exam == "final":
                    certs = generate_all_certificates(student)
                    if certs["academic"]:
                        cert_counts["academic"] += 1
                    cert_counts["subject"] += len(certs["subject"])
                    if certs["behavior"]:
                        cert_counts["behavior"] += 1
                    if certs["punctuality"]:
                        cert_counts["punctuality"] += 1

    return {
        "reports_generated": total_reports,
        "certificates": cert_counts,
    }
