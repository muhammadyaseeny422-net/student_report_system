"""
report_generator.py - Generates visually professional PDF report cards.

Features:
  - Dynamic subjects per class/exam (reads from student dict)
  - Exam-type-specific headers (Midterm, Final, Bimonthly 1/2)
  - Actual obtained marks displayed (not ML-modified)
  - ML-driven grade, remarks, and badges
  - Class-wise and exam-wise output folders
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from config import get_exam_label, get_report_dir, SCHOOL_NAME


def _draw_background(c, width, height):
    """Draw the report card background with header and borders."""
    # Soft background
    c.setFillColor(colors.HexColor("#FAFAFA"))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Header band
    c.setFillColor(colors.HexColor("#0D47A1"))
    c.rect(0, height - 140, width, 140, fill=1, stroke=0)

    # Outer gold border
    c.setStrokeColor(colors.HexColor("#FFB300"))
    c.setLineWidth(4)
    c.roundRect(15, 15, width - 30, height - 30, 10)

    # Inner blue border
    c.setStrokeColor(colors.HexColor("#1976D2"))
    c.setLineWidth(1)
    c.roundRect(22, 22, width - 44, height - 44, 8)


def generate_student_report(student, ml_result, output_dir=None):
    """
    Generate a PDF report card for one student.

    Displays ACTUAL obtained marks from the student dict.
    Uses ML results only for grade, remarks, and badges.

    Args:
        student: dict from data_loader (student_id, name, marks, class_num, exam_type, etc.)
        ml_result: dict from model.predict_student (grade, remarks, badges)
        output_dir: override output directory (auto-generated from class/exam if None)

    Returns:
        path to the generated PDF
    """
    class_num = student["class_num"]
    exam_type = student["exam_type"]

    if output_dir is None:
        output_dir = get_report_dir(class_num, exam_type)
    os.makedirs(output_dir, exist_ok=True)

    student_id = student["student_id"]
    file_path = os.path.join(output_dir, f"{student_id}.pdf")

    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # Background
    _draw_background(c, width, height)

    # --- Header ---
    logo_path = "assets/images/school_logo.png"
    if os.path.exists(logo_path):
        c.drawImage(logo_path, width / 2 - 30, height - 90,
                     width=60, height=60, mask='auto')

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 120, SCHOOL_NAME)

    # Dynamic exam type header
    exam_label = get_exam_label(exam_type)
    c.setFillColor(colors.HexColor("#FFCC80"))
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, height - 135,
                        f"{exam_label}   P E R F O R M A N C E   R E P O R T")

    # --- Student Info Section ---
    y_info = height - 190
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.lightgrey)
    c.roundRect(40, y_info - 10, width - 80, 45, 8, fill=1, stroke=1)

    c.setFillColor(colors.HexColor("#333333"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y_info + 10, f"ID: {student_id}")

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor("#1565C0"))
    c.drawString(170, y_info + 10, student["name"])

    # Class info on the right
    c.setFillColor(colors.HexColor("#555555"))
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width - 60, y_info + 10, f"Class {class_num}")

    # --- Marks Table ---
    # Read subjects directly from student's marks (dynamic per class/exam)
    marks = student["marks"]
    subject_percentages = student["subject_percentages"]
    max_marks_per_subject = student["max_marks_per_subject"]

    data = [["SUBJECT", "MAX MARKS", "OBTAINED", "PERCENTAGE"]]
    for subject in marks:
        obtained = marks[subject]
        max_mark = max_marks_per_subject[subject]
        pct = subject_percentages[subject]

        display_name = subject.replace("_", " ")
        data.append([
            display_name,
            str(int(max_mark)),
            str(int(obtained)),
            f"{pct:.1f}%"
        ])

    # Dynamic column widths based on number of subjects
    table = Table(data, colWidths=[140, 90, 90, 100])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1565C0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#B0BEC5")),
    ])

    # Zebra striping
    for i in range(1, len(data)):
        bg = colors.HexColor("#E3F2FD") if i % 2 == 0 else colors.white
        style.add('BACKGROUND', (0, i), (-1, i), bg)

    table.setStyle(style)
    w, h = table.wrap(width, height)
    table_y = y_info - 15 - h
    table.drawOn(c, (width - w) / 2, table_y)

    # --- Summary & Grade ---
    summary_y = table_y - 25

    c.setFillColor(colors.white)
    c.setStrokeColor(colors.lightgrey)
    c.roundRect(40, summary_y - 65, width - 80, 80, 8, fill=1, stroke=1)

    c.setFillColor(colors.HexColor("#424242"))
    c.setFont("Helvetica-Bold", 12)

    c.drawString(60, summary_y - 5, "Total:")
    c.setFont("Helvetica", 12)
    c.drawString(105, summary_y - 5,
                 f"{int(student['total_marks'])} / {int(student['max_marks'])}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(230, summary_y - 5, "Percentage:")
    c.setFont("Helvetica", 12)
    c.drawString(310, summary_y - 5, f"{student['percentage']:.2f}%")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, summary_y - 5, "Obedient:")
    c.setFont("Helvetica", 12)
    c.drawString(465, summary_y - 5, f"{student['obedient']}/10")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, summary_y - 30, "Final Grade:")

    # Large colored grade
    grade = ml_result["grade"]
    grade_colors = {
        "A+": "#2E7D32", "A": "#1565C0", "B": "#F57F17",
        "C": "#E65100", "D": "#C62828"
    }
    c.setFillColor(colors.HexColor(grade_colors.get(grade, "#424242")))
    c.setFont("Helvetica-Bold", 22)
    c.drawString(145, summary_y - 32, grade)

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#424242"))
    c.drawString(230, summary_y - 30, "Punctual:")
    c.setFont("Helvetica", 12)
    c.drawString(300, summary_y - 30, f"{student['punctual']}/10")

    # --- Remarks ---
    remarks_y = summary_y - 85
    c.setFillColor(colors.HexColor("#424242"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, remarks_y, "Teacher Remarks:")
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.HexColor("#616161"))

    # Word-wrap remarks to fit
    remarks = ml_result["remarks"]
    max_width = width - 120
    if c.stringWidth(remarks, "Helvetica-Oblique", 10) > max_width:
        words = remarks.split()
        line1, line2 = "", ""
        for word in words:
            test = line1 + " " + word if line1 else word
            if c.stringWidth(test, "Helvetica-Oblique", 10) <= max_width:
                line1 = test
            else:
                line2 += " " + word if line2 else word
        c.drawString(150, remarks_y, line1)
        if line2:
            c.drawString(40, remarks_y - 14, line2)
            remarks_y -= 14
    else:
        c.drawString(150, remarks_y, remarks)

    # --- Badges Section ---
    badges_y = remarks_y - 30

    # Badge title bar
    c.setFillColor(colors.HexColor("#FFB300"))
    c.roundRect(40, badges_y - 12, width - 80, 20, 4, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, badges_y - 6, "EXCELLENCE & ACHIEVEMENTS")

    badge_x = 55
    badge_start_y = badges_y - 70

    all_badges = ml_result["subject_badges"] + ml_result["trait_badges"]

    if len(all_badges) == 0:
        c.setFillColor(colors.HexColor("#9E9E9E"))
        c.setFont("Helvetica-Oblique", 11)
        c.drawCentredString(width / 2, badge_start_y + 30,
                            "No special achievements awarded for this term.")
    else:
        for badge in all_badges:
            badge_path = os.path.join("assets", "badges", badge)
            if os.path.exists(badge_path):
                c.drawImage(badge_path, badge_x, badge_start_y,
                            width=50, height=50, mask='auto')
                badge_x += 55
                if badge_x > width - 105:
                    badge_x = 55
                    badge_start_y -= 55

    # --- Footer ---
    c.setFillColor(colors.HexColor("#BDBDBD"))
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width / 2, 35,
                        "Generated securely via the Automated Student Report System.")

    c.save()
    return file_path
