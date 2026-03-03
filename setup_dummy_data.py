import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont

data = {
    "Student Name": [
        "Ahsanullah s/o Zaitullah", "Rifatullah s/o Rehmatullah", "Asman s/o Sher Badshah",
        "Afnan s/o Dawood", "Shoaib s/o Noor Rehman", "Ajmal s/o Sardar",
        "Talha s/o Imranuddin", "Osaid s/o Imranuddin", "Najeebullah s/o Bakhtamal",
        "Muneer s/o Ikramullah", "Sameer s/o Mujeed", "Abdullah s/o Khan Zaman",
        "Zulfiqar s/o Inam Shah", "Hussain s/o Moosa"
    ],
    "Urdu (100)": [78, 71, 66, 80, 73, 69, 84, 75, 68, 82, 64, 77, 70, 83],
    "English (100)": [65, 69, 61, 74, 68, 63, 77, 70, 62, 76, 59, 71, 66, 75],
    "Maths (100)": [82, 75, 70, 85, 78, 72, 88, 80, 73, 86, 68, 81, 74, 87],
    "Biology (65)": [54, 50, 48, 56, 51, 47, 59, 52, 46, 58, 45, 53, 49, 57],
    "Computer (65)": [58, 55, 52, 60, 57, 50, 62, 59, 49, 61, 48, 58, 54, 63],
    "Chemistry (65)": [49, 47, 45, 53, 50, 44, 56, 51, 43, 55, 42, 52, 46, 54],
    "Physics (65)": [52, 51, 46, 55, 49, 45, 58, 53, 44, 57, 43, 54, 48, 56],
    "Islamiat (50)": [41, 39, 36, 43, 40, 35, 45, 42, 34, 44, 33, 41, 38, 45],
    "Pak Studies (50)": [44, 42, 38, 46, 41, 37, 47, 43, 36, 46, 35, 44, 40, 48],
    "Obedient": ["Yes", "Yes", "No", "Yes", "Yes", "No", "Yes", "Yes", "No", "Yes", "No", "Yes", "Yes", "Yes"],
    "Punctual": ["Yes", "No", "Yes", "Yes", "No", "Yes", "Yes", "Yes", "No", "Yes", "Yes", "Yes", "No", "Yes"]
}

df = pd.DataFrame(data)
os.makedirs("data", exist_ok=True)
df.to_excel("data/students_marks.xlsx", index=False)
print("Created data/students_marks.xlsx")

# Graphical Badge Generator
os.makedirs("assets/badges", exist_ok=True)

def create_circular_badge(text_lines, filename, border_color, inner_color, text_color):
    size = (300, 300)
    img = Image.new("RGBA", size, (255, 255, 255, 0)) # Transparent background
    draw = ImageDraw.Draw(img)
    
    # Draw outer glow/border
    draw.ellipse([10, 10, 290, 290], fill=border_color, outline=(0,0,0,50), width=3)
    # Draw inner circle
    draw.ellipse([25, 25, 275, 275], fill=inner_color, outline=(255,255,255,100), width=5)
    
    # Try to load a nice font, fallback to default
    try:
        font_large = ImageFont.truetype("arialbd.ttf", 46)
        font_small = ImageFont.truetype("arial.ttf", 32)
    except IOError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw text
    y_start = 110 if len(text_lines) == 2 else 130
    for i, line in enumerate(text_lines):
        font = font_large if i == 0 else font_small
        
        # Calculate text width instead of using deprecated textsize
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (size[0] - text_width) / 2
        
        # Drop shadow
        draw.text((x+2, y_start+2), line, fill=(0,0,0,120), font=font)
        # Actual text
        draw.text((x, y_start), line, fill=text_color, font=font)
        y_start += 50
        
    img.save(filename)

# General trait badges
create_circular_badge(["Obedient", "Student"], "assets/badges/obedient.png", "#2E7D32", "#4CAF50", "white") # Green theme
create_circular_badge(["Punctual", "Student"], "assets/badges/punctual.png", "#1565C0", "#2196F3", "white") # Blue theme

# Generate Subject Badges
subjects = ["Urdu", "English", "Maths", "Biology", "Computer", "Chemistry", "Physics", "Islamiat", "Pak Studies"]
for sub in subjects:
    create_circular_badge([sub, "Genius"], f"assets/badges/{sub}_Genius.png", "#F57F17", "#FFD600", "black") # Gold
    create_circular_badge([sub, "Expert"], f"assets/badges/{sub}_Expert.png", "#006064", "#00BCD4", "white") # Diamond/Cyan
    create_circular_badge([sub, "Star"], f"assets/badges/{sub}_Star.png", "#424242", "#9E9E9E", "white")   # Silver

print("Created fancy sample badges in assets/badges/")
