"""
report_generator.py - Generates premium, futuristic PDF report cards.

Design: Modern CMS-style report with consistent color scheme.
  - Premium dark-to-blue gradient header with integrated logo
  - Clean student profile card
  - Full-width subject performance table with status pills
  - Unified accent color for all section headers
  - Academic analytics with ML grade and position (well-aligned)
  - ML-driven remarks with subject analysis
  - Performance visualization bar chart
  - Topper achievement pills
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from config import (get_exam_label, get_student_dir, SCHOOL_NAME, SESSION_YEAR,
                    SUBJECT_TITLES, POSITION_TITLES)


# ──────────────────────────────────────────────
#  COLOR PALETTE — Unified & Consistent
# ──────────────────────────────────────────────

ACCENT = "#1E40AF"       # Primary accent for all section bars
ACCENT_LIGHT = "#3B82F6" # Lighter accent for highlights
BG_PAGE = "#F1F5F9"      # Page background
BG_CARD = "#FFFFFF"      # Card background
BORDER = "#E2E8F0"       # Card borders
TEXT_PRIMARY = "#0F172A"  # Main text
TEXT_SECONDARY = "#475569" # Secondary text
TEXT_MUTED = "#94A3B8"    # Muted labels
GOLD = "#D97706"          # Topper/achievement gold
GOLD_BG = "#FEF3C7"       # Gold background


# ──────────────────────────────────────────────
#  DRAWING PRIMITIVES
# ──────────────────────────────────────────────

def _draw_background(c, width, height):
    """Draw page background and header gradient."""
    c.setFillColor(colors.HexColor(BG_PAGE))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Smooth dark-to-blue gradient header
    gradient_h = 100
    steps = 50
    for i in range(steps):
        ratio = i / steps
        y = height - gradient_h + (gradient_h / steps * i)
        h = gradient_h / steps + 0.5

        r = int(0x0F + (0x1E - 0x0F) * ratio)
        g = int(0x17 + (0x40 - 0x17) * ratio)
        b = int(0x2A + (0xAF - 0x2A) * ratio)
        c.setFillColor(colors.Color(r / 255, g / 255, b / 255))
        c.rect(0, y, width, h, fill=1, stroke=0)

    # Subtle accent line at bottom of header
    c.setStrokeColor(colors.HexColor(ACCENT_LIGHT))
    c.setLineWidth(1.5)
    c.line(0, height - gradient_h, width, height - gradient_h)


def _draw_section_card(c, x, y, w, h, title=None):
    """Draw a white card with CONSISTENT accent header bar."""
    # Soft shadow
    c.setFillColor(colors.Color(0, 0, 0, 0.03))
    c.roundRect(x + 1, y - 1, w, h, 5, fill=1, stroke=0)

    # Card body
    c.setFillColor(colors.HexColor(BG_CARD))
    c.setStrokeColor(colors.HexColor(BORDER))
    c.setLineWidth(0.5)
    c.roundRect(x, y, w, h, 5, fill=1, stroke=1)

    if title:
        bar_h = 20
        c.setFillColor(colors.HexColor(ACCENT))
        c.roundRect(x, y + h - bar_h, w, bar_h, 5, fill=1, stroke=0)
        c.rect(x, y + h - bar_h, w, bar_h / 2, fill=1, stroke=0)

        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x + 10, y + h - 14, title)


def _get_status_info(pct):
    """Get status label, bg color, text color based on percentage."""
    if pct >= 90:
        return "EXCELLENT", "#DCFCE7", "#166534"
    elif pct >= 75:
        return "GOOD", "#DBEAFE", "#1E40AF"
    elif pct >= 50:
        return "AVERAGE", "#FEF3C7", "#92400E"
    else:
        return "NEEDS WORK", "#FEE2E2", "#991B1B"


def _draw_bar_chart(c, x, y, w, h, subject_data, class_averages):
    """
    Draw a horizontal bar chart showing subject performance vs class average.
    Fills the empty space at the bottom of the report card.
    """
    if not subject_data:
        return

    items = list(subject_data.items())
    bar_count = len(items)
    if bar_count == 0:
        return

    # Chart area
    chart_left = x + 90   # space for labels
    chart_right = x + w - 15
    chart_w = chart_right - chart_left
    bar_h = min(14, (h - 10) / bar_count - 2)
    gap = 2

    for idx, (subject, pct) in enumerate(items):
        bar_y = y + h - 12 - (idx * (bar_h + gap))
        avg = class_averages.get(subject, 0)

        # Subject label
        display = subject.replace("_", " ")
        if len(display) > 12:
            display = display[:11] + "."
        c.setFillColor(colors.HexColor(TEXT_SECONDARY))
        c.setFont("Helvetica", 7)
        c.drawRightString(chart_left - 5, bar_y + 3, display)

        # Background bar (light gray)
        c.setFillColor(colors.HexColor("#E2E8F0"))
        c.roundRect(chart_left, bar_y, chart_w, bar_h, 2, fill=1, stroke=0)

        # Student bar
        bar_w = max(2, chart_w * min(pct, 100) / 100)
        if pct >= 90:
            bar_col = "#22C55E"
        elif pct >= 75:
            bar_col = "#3B82F6"
        elif pct >= 50:
            bar_col = "#F59E0B"
        else:
            bar_col = "#EF4444"
        c.setFillColor(colors.HexColor(bar_col))
        c.roundRect(chart_left, bar_y, bar_w, bar_h, 2, fill=1, stroke=0)

        # Class average marker (sleek solid indicator pin)
        if avg > 0:
            avg_x = chart_left + chart_w * min(avg, 100) / 100
            c.setStrokeColor(colors.HexColor("#475569"))
            c.setLineWidth(1.2)
            c.line(avg_x, bar_y - 1, avg_x, bar_y + bar_h + 1)
            c.setFillColor(colors.HexColor("#475569"))
            c.circle(avg_x, bar_y + bar_h + 1, 1.5, fill=1, stroke=0)

        # Percentage label on bar
        c.setFillColor(colors.HexColor(TEXT_PRIMARY))
        c.setFont("Helvetica-Bold", 6)
        label_x = chart_left + bar_w + 3
        if label_x + 20 > chart_right:
            label_x = chart_left + bar_w - 22
            c.setFillColor(colors.white)
        c.drawString(label_x, bar_y + 3, f"{pct:.0f}%")

    # Legend at bottom
    legend_y = y + 4
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.setFont("Helvetica", 6)
    # Student bar legend
    c.setFillColor(colors.HexColor("#3B82F6"))
    c.rect(chart_left, legend_y, 12, 5, fill=1, stroke=0)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.setFont("Helvetica", 6)
    c.drawString(chart_left + 15, legend_y, "Student")
    # Class avg legend
    c.setStrokeColor(colors.HexColor("#475569"))
    c.setLineWidth(1.2)
    c.line(chart_left + 60, legend_y + 2.5, chart_left + 72, legend_y + 2.5)
    c.setFillColor(colors.HexColor("#475569"))
    c.circle(chart_left + 66, legend_y + 2.5, 1.5, fill=1, stroke=0)
    c.drawString(chart_left + 75, legend_y, "Class Avg")


# ──────────────────────────────────────────────
#  MAIN REPORT GENERATION
# ──────────────────────────────────────────────

def generate_student_report(student, ml_result, output_dir=None,
                            class_averages=None, topper_subjects=None,
                            position=None, badge_results=None):
    """Generate a premium PDF report card."""
    class_num = student["class_num"]
    exam_type = student["exam_type"]
    topper_subjects = topper_subjects or []
    badge_results = badge_results or {}

    if output_dir is None:
        student_id = student["student_id"]
        output_dir = get_student_dir(class_num, exam_type, student_id)
    os.makedirs(output_dir, exist_ok=True)

    student_id = student["student_id"]
    file_path = os.path.join(output_dir, "report_card.pdf")

    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    card_w = width - 60  # consistent card width

    _draw_background(c, width, height)

    # ─── Header: Logo + School Name + Exam Label ───
    logo_path = os.path.join("assets", "images", "school_logo.png")
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 30, height - 92, width=55, height=55,
                     preserveAspectRatio=True, mask='auto')

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 19)
    c.drawString(95, height - 52, SCHOOL_NAME)

    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.setFont("Helvetica", 8)
    c.drawString(95, height - 65, f"Academic Performance Report  ·  {SESSION_YEAR}")

    # Exam type — subtle glass label
    exam_label = get_exam_label(exam_type)
    c.setFont("Helvetica-Bold", 8)
    label_w = c.stringWidth(exam_label.upper(), "Helvetica-Bold", 8) + 18
    label_x = width - label_w - 30
    label_y = height - 56

    c.setFillColor(colors.Color(1, 1, 1, 0.12))
    c.roundRect(label_x, label_y, label_w, 18, 3, fill=1, stroke=0)
    c.setStrokeColor(colors.Color(1, 1, 1, 0.25))
    c.setLineWidth(0.5)
    c.roundRect(label_x, label_y, label_w, 18, 3, fill=0, stroke=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(label_x + label_w / 2, label_y + 5, exam_label.upper())

    # ─── Student Profile Card ───
    y_profile = height - 160
    _draw_section_card(c, 30, y_profile, card_w, 48)

    labels = ["STUDENT ID", "STUDENT NAME", "CLASS"]
    values = [str(student_id), student["name"].upper(), f"Class {class_num}"]
    val_colors = [TEXT_PRIMARY, ACCENT_LIGHT, TEXT_PRIMARY]
    x_positions = [48, 190, 460]

    for i, (lbl, val) in enumerate(zip(labels, values)):
        c.setFillColor(colors.HexColor(TEXT_MUTED))
        c.setFont("Helvetica", 7)
        c.drawString(x_positions[i], y_profile + 30, lbl)

        c.setFillColor(colors.HexColor(val_colors[i]))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_positions[i], y_profile + 14, val)

    # ─── Subject Performance Table (FULL WIDTH) ───
    marks_data = student["marks"]
    max_marks_data = student["max_marks_per_subject"]
    percentages = student["subject_percentages"]
    class_averages = class_averages or {}

    table_data = [["Subject", "Marks", "Max", "%", "Class Avg", "vs Avg", "Status"]]
    for subject in marks_data:
        obtained = int(marks_data[subject])
        max_mark = int(max_marks_data.get(subject, 0))
        pct = percentages.get(subject, 0)
        avg = class_averages.get(subject, 0)
        diff = pct - avg
        diff_str = f"+{diff:.0f}%" if diff >= 0 else f"{diff:.0f}%"
        status, _, _ = _get_status_info(pct)
        is_topper = subject in topper_subjects
        display_subject = subject.replace("_", " ")
        if is_topper:
            display_subject = f"★ {display_subject}"
        table_data.append([display_subject, str(obtained), str(max_mark),
                           f"{pct:.0f}%", f"{avg:.0f}%", diff_str, status])

    # Full-width columns
    total_w = card_w - 36
    col_widths = [
        int(total_w * 0.24),  # Subject
        int(total_w * 0.11),  # Marks
        int(total_w * 0.10),  # Max
        int(total_w * 0.11),  # %
        int(total_w * 0.14),  # Class Avg
        int(total_w * 0.12),  # vs Avg
        int(total_w * 0.18),  # Status
    ]

    table = Table(table_data, colWidths=col_widths)

    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor(TEXT_SECONDARY)),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor(TEXT_PRIMARY)),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(BORDER)),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFBFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]

    # Color status and vs-avg columns
    subject_list = list(marks_data.keys())
    for row_idx in range(1, len(table_data)):
        subj = subject_list[row_idx - 1]
        pct = percentages.get(subj, 0)
        avg = class_averages.get(subj, 0)
        _, bg_col, txt_col = _get_status_info(pct)

        style_commands.append(("BACKGROUND", (-1, row_idx), (-1, row_idx), colors.HexColor(bg_col)))
        style_commands.append(("TEXTCOLOR", (-1, row_idx), (-1, row_idx), colors.HexColor(txt_col)))
        style_commands.append(("FONTNAME", (-1, row_idx), (-1, row_idx), "Helvetica-Bold"))

        diff = pct - avg
        if diff >= 5:
            style_commands.append(("TEXTCOLOR", (-2, row_idx), (-2, row_idx), colors.HexColor("#166534")))
        elif diff <= -5:
            style_commands.append(("TEXTCOLOR", (-2, row_idx), (-2, row_idx), colors.HexColor("#DC2626")))

        if subj in topper_subjects:
            style_commands.append(("TEXTCOLOR", (0, row_idx), (0, row_idx), colors.HexColor(GOLD)))
            style_commands.append(("FONTNAME", (0, row_idx), (0, row_idx), "Helvetica-Bold"))

    table.setStyle(TableStyle(style_commands))

    _, table_h = table.wrap(total_w, height)
    card_height = table_h + 32
    table_card_y = y_profile - 10 - card_height
    _draw_section_card(c, 30, table_card_y, card_w, card_height, "Subject Performance")
    table.drawOn(c, 48, table_card_y + card_height - 28 - table_h)

    # ─── Academic Analytics Card (FIXED LAYOUT) ───
    # Two-part layout: left = 4 metrics, right = grade circle + position
    analytics_h = 76
    analytics_y = table_card_y - analytics_h - 8
    _draw_section_card(c, 30, analytics_y, card_w, analytics_h, "Academic Analytics")

    # Left side: 4 metrics evenly spaced in left 75%
    metrics = [
        ("TOTAL SCORE", f"{int(student['total_marks'])} / {int(student['max_marks'])}"),
        ("PERCENTAGE", f"{student['percentage']:.1f}%"),
        ("OBEDIENCE", f"{student['obedient']} / 10"),
        ("PUNCTUALITY", f"{student['punctual']} / 10"),
    ]

    metrics_zone_w = card_w * 0.72
    metric_w = metrics_zone_w / 4
    for idx, (label, value) in enumerate(metrics):
        mx = 48 + idx * metric_w

        c.setFillColor(colors.HexColor(TEXT_MUTED))
        c.setFont("Helvetica", 7)
        c.drawString(mx, analytics_y + 36, label)

        if idx == 1:
            pct_v = student['percentage']
            col = "#166534" if pct_v >= 80 else ACCENT_LIGHT if pct_v >= 60 else GOLD
        else:
            col = TEXT_PRIMARY
        c.setFillColor(colors.HexColor(col))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(mx, analytics_y + 15, value)

    # Right side: Premium grade badge + position (properly centered)
    grade = ml_result["grade"]
    grade_colors = {
        "A+": ("#166534", "#DCFCE7"),
        "A":  ("#1E40AF", "#DBEAFE"),
        "B":  ("#92400E", "#FEF3C7"),
        "C":  ("#991B1B", "#FEE2E2"),
        "D":  ("#831843", "#FCE7F3"),
    }
    g_txt, g_bg = grade_colors.get(grade, ("#1E293B", "#F1F5F9"))

    right_zone_x = 30 + card_w * 0.78
    right_zone_center = right_zone_x + (card_w * 0.22) / 2
    
    # Draw premium badge container
    # Shadow
    c.setFillColor(colors.Color(0, 0, 0, 0.03))
    c.roundRect(right_zone_center - 36 + 1.5, analytics_y + 6 - 1.5, 72, 44, 6, fill=1, stroke=0)
    
    # Colored background
    c.setFillColor(colors.HexColor(g_bg))
    c.roundRect(right_zone_center - 36, analytics_y + 6, 72, 44, 6, fill=1, stroke=0)
    
    # Outer border
    c.setStrokeColor(colors.HexColor(g_txt))
    c.setLineWidth(1.2)
    c.roundRect(right_zone_center - 36, analytics_y + 6, 72, 44, 6, fill=0, stroke=1)
    
    # Inner border (inset by 2 points)
    c.setStrokeColor(colors.HexColor(g_txt))
    c.setLineWidth(0.4)
    c.roundRect(right_zone_center - 34, analytics_y + 8, 68, 40, 4, fill=0, stroke=1)

    # "ML GRADE" label inside badge
    c.setFillColor(colors.HexColor(g_txt))
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(right_zone_center, analytics_y + 39, "ML GRADE")

    # Grade letter + Position layout
    has_position = position and position in (1, 2, 3)
    if has_position:
        pos_colors_map = {1: "#D97706", 2: "#64748B", 3: "#B45309"}
        pos_col = pos_colors_map.get(position, "#475569")
        pos_label = POSITION_TITLES.get(position, f"#{position}").upper()

        # Grade letter (classy serif)
        c.setFillColor(colors.HexColor(g_txt))
        c.setFont("Times-Bold", 16)
        c.drawCentredString(right_zone_center, analytics_y + 21, grade)

        # Position label inside badge
        c.setFillColor(colors.HexColor(pos_col))
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(right_zone_center, analytics_y + 11, pos_label)
    else:
        # Grade letter perfectly centered (classy serif)
        c.setFillColor(colors.HexColor(g_txt))
        c.setFont("Times-Bold", 20)
        c.drawCentredString(right_zone_center, analytics_y + 18, grade)

    # ─── Remarks & Achievements Card ───
    ach_card_h = 90
    ach_y = analytics_y - ach_card_h - 8
    _draw_section_card(c, 30, ach_y, card_w, ach_card_h, "Remarks & Achievements")

    # ML-driven remarks
    c.setFillColor(colors.HexColor(TEXT_SECONDARY))
    c.setFont("Helvetica-Oblique", 8)
    remarks = f'"{ml_result["remarks"]}"'

    max_remark_width = card_w - 60
    remark_y = ach_y + ach_card_h - 34
    words = remarks.split()
    lines = []
    current_line = ""
    for word in words:
        test = current_line + " " + word if current_line else word
        if c.stringWidth(test, "Helvetica-Oblique", 8) <= max_remark_width:
            current_line = test
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    for i, line in enumerate(lines[:3]):
        c.drawString(48, remark_y - i * 12, line)

    # Topper achievements — gold pills
    if topper_subjects:
        pill_y = remark_y - len(lines[:3]) * 12 - 6
        ach_x = 48

        c.setFillColor(colors.HexColor(GOLD))
        c.setFont("Helvetica-Bold", 7)
        c.drawString(ach_x, pill_y + 2, "TOPPER AWARDS:")
        ach_x += 85

        for subj in topper_subjects:
            title = SUBJECT_TITLES.get(subj, f"{subj} Topper")
            pill_text = f"★ {title}"
            tw = c.stringWidth(pill_text, "Helvetica-Bold", 7) + 10

            c.setFillColor(colors.HexColor(GOLD_BG))
            c.roundRect(ach_x, pill_y - 3, tw, 14, 3, fill=1, stroke=0)
            c.setStrokeColor(colors.HexColor("#FCD34D"))
            c.setLineWidth(0.3)
            c.roundRect(ach_x, pill_y - 3, tw, 14, 3, fill=0, stroke=1)

            c.setFillColor(colors.HexColor("#92400E"))
            c.setFont("Helvetica-Bold", 7)
            c.drawString(ach_x + 5, pill_y, pill_text)
            ach_x += tw + 4

            if ach_x > width - 80:
                ach_x = 48
                pill_y -= 16

    # ─── Performance Visualization Card (fills bottom space) ───
    viz_top = ach_y - 8
    viz_bottom = 30  # above footer
    viz_h = viz_top - viz_bottom
    if viz_h > 40:
        _draw_section_card(c, 30, viz_bottom, card_w, viz_h,
                           "Performance Overview")
        _draw_bar_chart(c, 48, viz_bottom + 4, card_w - 36, viz_h - 28,
                        percentages, class_averages)

    # ─── Footer ───
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.setFont("Helvetica", 7)
    c.drawCentredString(width / 2, 14,
                         f"Generated by AI-Powered Academic Reporting Module  ·  {SCHOOL_NAME}  ·  {SESSION_YEAR}")

    c.save()
    return file_path
