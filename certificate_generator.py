"""
certificate_generator.py - Generates professional PDF certificates.

Certificate Types (generated from FINAL TERM data only):
  1. Academic Excellence - >= 90% in ALL subjects
  2. Subject Excellence  - >= 90% in any individual subject
  3. Behavior Excellence - Obedient >= 9 AND Punctual >= 9
  4. Punctuality Excellence - Punctual >= 9
"""

import os
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from config import get_certificate_dir, SUBJECT_TITLES, SESSION_YEAR, SCHOOL_NAME


def _draw_certificate_frame(c, width, height, title_color="#0D47A1"):
    """Draw professional certificate border and background."""
    # Cream background
    c.setFillColor(colors.HexColor("#FFFDF5"))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Outer ornamental border (gold)
    c.setStrokeColor(colors.HexColor("#C5961B"))
    c.setLineWidth(6)
    c.roundRect(20, 20, width - 40, height - 40, 12)

    # Inner border (thin gold)
    c.setStrokeColor(colors.HexColor("#DAA520"))
    c.setLineWidth(2)
    c.roundRect(32, 32, width - 64, height - 64, 8)

    # Second inner border for elegance
    c.setStrokeColor(colors.HexColor("#E8D5A3"))
    c.setLineWidth(0.5)
    c.roundRect(38, 38, width - 76, height - 76, 6)

    # Decorative corner elements
    corner_size = 15
    corners = [
        (40, 40), (width - 40 - corner_size, 40),
        (40, height - 40 - corner_size), (width - 40 - corner_size, height - 40 - corner_size)
    ]
    c.setFillColor(colors.HexColor("#DAA520"))
    for cx, cy in corners:
        c.rect(cx, cy, corner_size, corner_size, fill=1, stroke=0)

    # Top decorative line
    c.setStrokeColor(colors.HexColor("#DAA520"))
    c.setLineWidth(1.5)
    line_y = height - 130
    c.line(80, line_y, width - 80, line_y)

    # Diamond accent at center of line
    mid_x = width / 2
    c.setFillColor(colors.HexColor("#C5961B"))
    c.saveState()
    c.translate(mid_x, line_y)
    c.rotate(45)
    c.rect(-5, -5, 10, 10, fill=1, stroke=0)
    c.restoreState()


def _draw_header(c, width, height, title, subtitle):
    """Draw certificate header with school name and type."""
    c.setFillColor(colors.HexColor("#0D47A1"))
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 75, SCHOOL_NAME)

    c.setFillColor(colors.HexColor("#C5961B"))
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2, height - 115, title)

    c.setFillColor(colors.HexColor("#555555"))
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 145, subtitle)


def _draw_student_name(c, width, y, name, student_id, class_num):
    """Draw the 'Presented to' section with student name and class."""
    c.setFillColor(colors.HexColor("#333333"))
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, y, "This certificate is proudly presented to")

    # Student name with decorative underline
    c.setFillColor(colors.HexColor("#0D47A1"))
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, y - 40, name)

    # Decorative line under name
    name_width = c.stringWidth(name, "Helvetica-Bold", 28)
    line_start = (width - name_width) / 2 - 20
    line_end = line_start + name_width + 40
    c.setStrokeColor(colors.HexColor("#DAA520"))
    c.setLineWidth(1)
    c.line(line_start, y - 48, line_end, y - 48)

    # Student ID and Class
    c.setFillColor(colors.HexColor("#888888"))
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, y - 65,
                        f"Student ID: {student_id}  |  Class {class_num}")


def _draw_footer(c, width, session=SESSION_YEAR):
    """Draw session year, signatures, and footer."""
    y_base = 85

    c.setFillColor(colors.HexColor("#666666"))
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, y_base + 20, f"Academic Session: {session}")

    # Signature lines
    sig_y = y_base - 15
    sig_width = 150

    c.setStrokeColor(colors.HexColor("#999999"))
    c.setLineWidth(1)
    c.line(100, sig_y, 100 + sig_width, sig_y)
    c.setFillColor(colors.HexColor("#555555"))
    c.setFont("Helvetica", 10)
    c.drawCentredString(100 + sig_width / 2, sig_y - 15, "Principal")

    c.line(width - 100 - sig_width, sig_y, width - 100, sig_y)
    c.drawCentredString(width - 100 - sig_width / 2, sig_y - 15, "Class Teacher")

    c.setFillColor(colors.HexColor("#999999"))
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width / 2, sig_y - 15, "Date: _______________")


def generate_academic_certificate(student, output_dir=None):
    """
    Generate Academic Excellence certificate.
    Condition: >= 90% in ALL subjects (final term).
    Returns: file path or None if not eligible.
    """
    # Check eligibility
    for subject, pct in student["subject_percentages"].items():
        if pct < 90:
            return None

    class_num = student["class_num"]
    if output_dir is None:
        output_dir = get_certificate_dir(class_num)
    os.makedirs(output_dir, exist_ok=True)

    student_id = student["student_id"]
    file_path = os.path.join(output_dir, f"academic_{student_id}.pdf")

    width, height = landscape(letter)
    c = canvas.Canvas(file_path, pagesize=landscape(letter))

    _draw_certificate_frame(c, width, height)
    _draw_header(c, width, height,
                 "CERTIFICATE OF ACADEMIC EXCELLENCE",
                 "Awarded for outstanding academic achievement across all subjects")
    _draw_student_name(c, width, height - 175, student["name"], student_id, class_num)

    # Achievement text
    y = height - 260
    c.setFillColor(colors.HexColor("#333333"))
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, y,
                        f"For achieving an overall percentage of {student['percentage']:.1f}%")
    c.drawCentredString(width / 2, y - 18,
                        "with excellence in every subject during this academic session.")

    # Subject achievements in two columns
    y -= 50
    c.setFillColor(colors.HexColor("#0D47A1"))
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y, "Subject Achievements")

    c.setStrokeColor(colors.HexColor("#DAA520"))
    c.setLineWidth(0.5)
    c.line(width / 2 - 80, y - 5, width / 2 + 80, y - 5)

    y -= 25
    achievements = []
    for subject, pct in student["subject_percentages"].items():
        if pct >= 90:
            title = SUBJECT_TITLES.get(subject, f"{subject} Excellence")
            achievements.append(f"★ {title} ({pct:.0f}%)")

    c.setFillColor(colors.HexColor("#444444"))
    c.setFont("Helvetica", 10)

    mid = len(achievements) // 2 + len(achievements) % 2
    col1 = achievements[:mid]
    col2 = achievements[mid:]

    for i, ach in enumerate(col1):
        c.drawString(180, y - i * 16, ach)
    for i, ach in enumerate(col2):
        c.drawString(width / 2 + 30, y - i * 16, ach)

    _draw_footer(c, width)
    c.save()
    return file_path


def generate_subject_excellence_certificates(student, output_dir=None):
    """
    Generate Subject Excellence certificates for individual subjects.
    Condition: >= 90% in any subject (final term).
    Generates one certificate per qualifying subject.

    Returns: list of (subject, file_path) tuples
    """
    class_num = student["class_num"]
    if output_dir is None:
        output_dir = get_certificate_dir(class_num)
    os.makedirs(output_dir, exist_ok=True)

    student_id = student["student_id"]
    results = []

    for subject, pct in student["subject_percentages"].items():
        if pct < 90:
            continue

        safe_subject = subject.replace("/", "_")
        file_path = os.path.join(output_dir, f"subject_{safe_subject}_{student_id}.pdf")

        width, height = landscape(letter)
        c = canvas.Canvas(file_path, pagesize=landscape(letter))

        _draw_certificate_frame(c, width, height, "#1565C0")
        title = SUBJECT_TITLES.get(subject, f"{subject} Excellence")
        _draw_header(c, width, height,
                     f"CERTIFICATE OF SUBJECT EXCELLENCE",
                     f"Awarded for outstanding performance in {subject.replace('_', ' ')}")
        _draw_student_name(c, width, height - 175, student["name"], student_id, class_num)

        # Achievement text
        y = height - 260
        c.setFillColor(colors.HexColor("#333333"))
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, y,
                            f"In recognition of achieving {pct:.1f}% in {subject.replace('_', ' ')},")
        c.drawCentredString(width / 2, y - 18,
                            "demonstrating exceptional knowledge and dedication.")

        # Award title
        y -= 55
        c.setFillColor(colors.HexColor("#1565C0"))
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, y, f"★  {title}  ★")

        # Score
        y -= 30
        c.setFillColor(colors.HexColor("#2E7D32"))
        c.setFont("Helvetica-Bold", 13)
        obtained = int(student["marks"][subject])
        max_mark = student["max_marks_per_subject"][subject]
        c.drawCentredString(width / 2, y,
                            f"Score: {obtained} / {max_mark}  ({pct:.1f}%)")

        _draw_footer(c, width)
        c.save()
        results.append((subject, file_path))

    return results


def generate_behavior_certificate(student, output_dir=None):
    """
    Generate Behavior Excellence certificate.
    Condition: Obedient >= 9 AND Punctual >= 9.
    Returns: file path or None if not eligible.
    """
    if student["obedient"] < 9 or student["punctual"] < 9:
        return None

    class_num = student["class_num"]
    if output_dir is None:
        output_dir = get_certificate_dir(class_num)
    os.makedirs(output_dir, exist_ok=True)

    student_id = student["student_id"]
    file_path = os.path.join(output_dir, f"behavior_{student_id}.pdf")

    width, height = landscape(letter)
    c = canvas.Canvas(file_path, pagesize=landscape(letter))

    _draw_certificate_frame(c, width, height, "#2E7D32")
    _draw_header(c, width, height,
                 "CERTIFICATE OF BEHAVIOR EXCELLENCE",
                 "Awarded for exemplary conduct and discipline")
    _draw_student_name(c, width, height - 175, student["name"], student_id, class_num)

    y = height - 260
    c.setFillColor(colors.HexColor("#333333"))
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, y,
                        "In recognition of consistently exemplary behavior and discipline,")
    c.drawCentredString(width / 2, y - 18,
                        "demonstrating outstanding obedience and respect for school values.")

    y -= 55
    c.setFillColor(colors.HexColor("#2E7D32"))
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(width / 2 - 80, y, f"Obedience: {student['obedient']}/10")
    c.drawCentredString(width / 2 + 80, y, f"Punctuality: {student['punctual']}/10")

    _draw_footer(c, width)
    c.save()
    return file_path


def generate_punctuality_certificate(student, output_dir=None):
    """
    Generate Punctuality certificate.
    Condition: Punctual >= 9.
    Returns: file path or None if not eligible.
    """
    if student["punctual"] < 9:
        return None

    class_num = student["class_num"]
    if output_dir is None:
        output_dir = get_certificate_dir(class_num)
    os.makedirs(output_dir, exist_ok=True)

    student_id = student["student_id"]
    file_path = os.path.join(output_dir, f"punctuality_{student_id}.pdf")

    width, height = landscape(letter)
    c = canvas.Canvas(file_path, pagesize=landscape(letter))

    _draw_certificate_frame(c, width, height, "#1565C0")
    _draw_header(c, width, height,
                 "CERTIFICATE OF PUNCTUALITY",
                 "Awarded for outstanding regularity and time management")
    _draw_student_name(c, width, height - 175, student["name"], student_id, class_num)

    y = height - 260
    c.setFillColor(colors.HexColor("#333333"))
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, y,
                        "In recognition of maintaining excellent punctuality throughout")
    c.drawCentredString(width / 2, y - 18,
                        "the academic session, setting a fine example for fellow students.")

    y -= 55
    c.setFillColor(colors.HexColor("#1565C0"))
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, y, f"Punctuality Score: {student['punctual']}/10")

    _draw_footer(c, width)
    c.save()
    return file_path


def generate_all_certificates(student, output_dir=None):
    """
    Check eligibility and generate all applicable certificates for a student.
    Should ONLY be called with final term student data.

    Returns:
        dict with counts: {"academic": path, "subject": [(subj, path),...],
                           "behavior": path, "punctuality": path}
    """
    return {
        "academic": generate_academic_certificate(student, output_dir),
        "subject": generate_subject_excellence_certificates(student, output_dir),
        "behavior": generate_behavior_certificate(student, output_dir),
        "punctuality": generate_punctuality_certificate(student, output_dir),
    }
