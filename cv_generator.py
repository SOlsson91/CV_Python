#!/usr/bin/env python3
"""
CV Generator
Usage: python cv_generator.py              # reads cv.yml by default
       python cv_generator.py mydata.yml   # reads a custom file
       python cv_generator.py mydata.json  # also works with JSON
"""

import sys
import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle


# Load data

def load_data(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        if path.suffix in (".yml", ".yaml"):
            try:
                import yaml
                return yaml.safe_load(f)
            except ImportError:
                print("PyYAML not installed. Run: pip install pyyaml")
                sys.exit(1)
        elif path.suffix == ".json":
            return json.load(f)
        else:
            print(f"Unsupported file type: {path.suffix}  (use .yml, .yaml, or .json)")
            sys.exit(1)


# Colors

BLACK      = colors.HexColor("#111111")
GRAY       = colors.HexColor("#555555")
LIGHT_GRAY = colors.HexColor("#999999")
RULE_COLOR = colors.HexColor("#CCCCCC")

# Drawing helpers

W, H = A4
PAD_L  = 20 * mm
PAD_R  = 20 * mm
TEXT_W = W - PAD_L - PAD_R


def rule(c, y):
    c.setStrokeColor(RULE_COLOR)
    c.setLineWidth(0.5)
    c.line(PAD_L, y, W - PAD_R, y)


def section_header(c, label, y):
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(BLACK)
    c.drawString(PAD_L, y, label.upper())
    rule(c, y - 2)
    return y - 8 * mm


def draw_entry(c, title, org, location, date, bullets, y):
    c.setFont("Helvetica-Bold", 9.5)
    c.setFillColor(BLACK)
    c.drawString(PAD_L, y, title)

    c.setFont("Helvetica", 8.5)
    c.setFillColor(LIGHT_GRAY)
    date_w = c.stringWidth(date, "Helvetica", 8.5)
    c.drawString(W - PAD_R - date_w, y, date)
    y -= 4.5 * mm

    c.setFont("Helvetica", 8.5)
    c.setFillColor(GRAY)
    c.drawString(PAD_L, y, f"{org}, {location}")
    y -= 5 * mm

    bullet_style = ParagraphStyle("bul",
        fontName="Helvetica", fontSize=8.5,
        textColor=colors.HexColor("#333333"),
        leading=12, leftIndent=9, firstLineIndent=-9,
    )
    for b in bullets:
        p = Paragraph(f"– {b}", bullet_style)
        _, ph = p.wrap(TEXT_W, 300)
        p.drawOn(c, PAD_L, y - ph + 2)
        y -= ph + 1

    return y - 4 * mm


# Build PDF

def build(data: dict, output: Path):
    c = canvas.Canvas(str(output), pagesize=A4)
    y = H - 18 * mm

    # Header
    contact = data["contact"]
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(BLACK)
    c.drawString(PAD_L, y, data["name"])
    y -= 7 * mm

    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    contact_line = f"{contact['location']}  ·  {contact['phone']}  ·  {contact['email']}"
    c.drawString(PAD_L, y, contact_line)
    y -= 5 * mm

    rule(c, y)
    y -= 8 * mm

    # Profile
    y = section_header(c, "Profile", y)
    profile_style = ParagraphStyle("prof",
        fontName="Helvetica", fontSize=8.5,
        textColor=colors.HexColor("#333333"), leading=12,
    )
    p = Paragraph(data["profile"].strip(), profile_style)
    _, ph = p.wrap(TEXT_W, 100)
    p.drawOn(c, PAD_L, y - ph + 2)
    y -= ph + 6 * mm

    # Experience
    y = section_header(c, "Work Experience", y)
    for job in data["experience"]:
        y = draw_entry(c,
            job["title"], job["company"], job["location"],
            job["date"], job["bullets"], y,
        )

    y -= 2 * mm

    # Education
    y = section_header(c, "Education", y)
    for edu in data["education"]:
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(BLACK)
        c.drawString(PAD_L, y, edu["degree"])
        dw = c.stringWidth(edu["date"], "Helvetica", 8.5)
        c.setFont("Helvetica", 8.5)
        c.setFillColor(LIGHT_GRAY)
        c.drawString(W - PAD_R - dw, y, edu["date"])
        y -= 4.5 * mm
        c.setFont("Helvetica", 8.5)
        c.setFillColor(GRAY)
        c.drawString(PAD_L, y, f"{edu['school']}, {edu['location']}")
        y -= 7 * mm

    y -= 2 * mm

    # Skills
    y = section_header(c, "Skills & Languages", y)
    for row in data["skills"]:
        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(BLACK)
        c.drawString(PAD_L, y, row["label"])
        c.setFont("Helvetica", 8.5)
        c.setFillColor(GRAY)
        c.drawString(PAD_L + 35 * mm, y, row["value"])
        y -= 5 * mm

    # Footer
    c.setFont("Helvetica", 7.5)
    c.setFillColor(LIGHT_GRAY)
    c.drawString(PAD_L, 10 * mm, "References available upon request.")

    c.save()
    print(f"Generated: {output}")


# Entry point

if __name__ == "__main__":
    data_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("cv.yml")

    if not data_file.exists():
        print(f"File not found: {data_file}")
        sys.exit(1)

    data = load_data(data_file)
    output_file = data_file.with_suffix(".pdf")
    build(data, output_file)
