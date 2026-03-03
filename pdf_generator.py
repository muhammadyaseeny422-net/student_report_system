import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch

def draw_beautiful_background(c, width, height):
    # A soft overall background
    c.setFillColor(colors.HexColor("#FAFAFA"))
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Decorative Header Gradient (Simulated via multiple colored bars)
    c.setFillColor(colors.HexColor("#0D47A1"))
    c.rect(0, height - 140, width, 140, fill=1, stroke=0)
    
    # Outer elegant border
    c.setStrokeColor(colors.HexColor("#FFB300")) # Gold border
    c.setLineWidth(4)
    c.roundRect(15, 15, width - 30, height - 30, 10)
    
    # Inner elegant border
    c.setStrokeColor(colors.HexColor("#1976D2"))
    c.setLineWidth(1)
    c.roundRect(22, 22, width - 44, height - 44, 8)

def generate_report_card(student, output_dir="reports"):
    student_name = student["name"].replace("/", "-")
    file_path = os.path.join(output_dir, f"{student_name}_ReportCard.pdf")
    
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    
    # Draw Background Layer
    draw_beautiful_background(c, width, height)
    
    # --- Header Section ---
    logo_path = "assets/images/school_logo.png"
    if os.path.exists(logo_path):
        # Scale logo down and move it up aggressively
        c.drawImage(logo_path, width/2 - 30, height - 90, width=60, height=60, mask='auto')
        
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 24)
    # Move title down just below the small logo
    c.drawCentredString(width / 2, height - 120, "THE LEADERS ACADEMY")
    
    c.setFillColor(colors.HexColor("#FFCC80"))
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, height - 135, "A N N U A L   P E R F O R M A N C E   R E P O R T")
    
    # --- Student Info Section Box ---
    y_info = height - 190
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.lightgrey)
    c.roundRect(40, y_info - 10, width - 80, 45, 8, fill=1, stroke=1)
    
    c.setFillColor(colors.HexColor("#333333"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, y_info + 10, "Student Profile:")
    
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.HexColor("#1565C0"))
    c.drawString(180, y_info + 10, student['name'])
    
    # --- Table Data Preparation ---
    data = [["SUBJECT", "MAX MARKS", "OBTAINED MARKS"]]
    
    for subject, obtained in student["marks"].items():
        sub_name = subject.split('(')[0].strip()
        max_marks = subject.split('(')[1].replace(')', '')
        data.append([sub_name, max_marks, str(obtained)])
        
    table = Table(data, colWidths=[200, 100, 150])
    
    # Use slightly less padding uniformly to compress the table height
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1565C0")), # Header Color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#B0BEC5"))
    ])
    
    # Add Zebra Striping
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor("#E3F2FD"))
        else:
            style.add('BACKGROUND', (0, i), (-1, i), colors.white)
            
    table.setStyle(style)
    
    w, h = table.wrap(width, height)
    table_y = y_info - 15 - h # Push table higher up to leave mass room below
    table.drawOn(c, (width - w) / 2, table_y)
    
    # --- Summary & Grade Section ---
    summary_y = table_y - 30
    
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.lightgrey)
    c.roundRect(40, summary_y - 65, width - 80, 80, 8, fill=1, stroke=1)
    
    c.setFillColor(colors.HexColor("#424242"))
    c.setFont("Helvetica-Bold", 14)
    
    c.drawString(60, summary_y - 10, "Total:")
    c.setFont("Helvetica", 14)
    c.drawString(110, summary_y - 10, f"{student['total_marks']} / {student['max_marks']}")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(220, summary_y - 10, "Percentage:")
    c.setFont("Helvetica", 14)
    c.drawString(310, summary_y - 10, f"{student['percentage']:.2f}%")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, summary_y - 45, "Final Grade:")
    
    # Large colored grade
    grade = student['grade']
    if grade == "A+":
        c.setFillColor(colors.HexColor("#2E7D32")) # Green
    elif grade == "A":
        c.setFillColor(colors.HexColor("#1565C0")) # Blue
    elif grade == "B":
        c.setFillColor(colors.HexColor("#F57F17")) # Orange
    else:
        c.setFillColor(colors.HexColor("#C62828")) # Red
        
    c.setFont("Helvetica-Bold", 24)
    c.drawString(150, summary_y - 47, grade)
    
    # Remarks
    c.setFillColor(colors.HexColor("#424242"))
    remarks_y = summary_y - 105
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, remarks_y, "Teacher Remarks:")
    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(colors.HexColor("#616161"))
    c.drawString(160, remarks_y, student["remarks"])
    
    # --- Badges Section ---
    badges_y = remarks_y - 35
    
    # Beautiful Badge Title Box
    c.setFillColor(colors.HexColor("#FFB300"))
    c.roundRect(40, badges_y - 12, width - 80, 20, 4, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, badges_y - 6, "EXCELLENCE & ACHIEVEMENTS")
    
    badge_x = 55
    badge_start_y = badges_y - 75  # Start badges higher up
    
    all_badges = student["subject_badges"] + student["trait_badges"]
    
    if len(all_badges) == 0:
         c.setFillColor(colors.HexColor("#9E9E9E"))
         c.setFont("Helvetica-Oblique", 12)
         c.drawCentredString(width / 2, badge_start_y + 30, "No special achievements awarded for this term.")
    else:
        for badge in all_badges:
            badge_path = os.path.join("assets", "badges", badge)
            if os.path.exists(badge_path):
                # Ensure transparent PNG rendering and shrink badges slightly to fit safely
                c.drawImage(badge_path, badge_x, badge_start_y, width=50, height=50, mask='auto')
                badge_x += 55 # Tighter spacing
                
                # Wrap sooner! Bounding box right edge is ~width - 55
                if badge_x > width - 105: 
                    badge_x = 55
                    badge_start_y -= 55
                    
    # Footer
    c.setFillColor(colors.HexColor("#BDBDBD"))
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width / 2, 35, "Generated securely and confidentially via the Automated Data System.")
                
    c.save()
    print(f"Generated Spectacular Report for {student['name']}")
