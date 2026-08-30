#!/usr/bin/env python3
"""
ARQUIVO — gera os PDFs do design ANTIGO do CV (sidebar + skill dots),
mantido só para não perder este trabalho. O site já não liga a este
design (gen_cv_pdf.py é a versão atual, ATS-friendly); estes PDFs só
são acedidos a partir do link discreto "old design" em cv.html /
cv-legacy.html.

Correr com:
    pip install reportlab --break-system-packages
    python3 gen_cv_pdf_legacy.py
"""

import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.graphics.shapes import Drawing, Rect

BASE_DIR = Path(__file__).parent
I18N_PATH = BASE_DIR / "data" / "i18n.json"

BLACK = HexColor("#0a0a0a")
SOFT = HexColor("#5c5c5c")
BORDER = HexColor("#cccccc")
SIDEBAR_BG = HexColor("#f4f4f4")

NAME = "João Coelho"
EMAIL = "joao.mbmc@gmail.com"
FENIX = "fenix.tecnico.ulisboa.pt/homepage/ist1117964"
GITHUB = "github.com/joaombmcoelho"
LINKEDIN = "linkedin.com/in/joaombmcoelho"

# skill dot ratings — not translatable, so they live here rather than in i18n.json
PROGRAMMING_SKILLS = [("Python", 5), ("C", 4)]
TOOL_SKILLS = [("Git", 4), ("Linux", 3), ("Docker", 2)]

# which cv.pN.* keys go on the PDF, in order — keep in sync with cv.html
PROJECT_KEYS = ["p1", "p2", "p3"]


def load_content(lang):
    """Pull every string this PDF needs out of the shared i18n dict,
    under its cv.* namespace — same keys the site's CV page uses."""
    data = json.loads(I18N_PATH.read_text(encoding="utf-8"))
    t = data[lang]

    c = {
        "role": t["cv.role"],
        "contact_heading": t["cv.contact.title"],
        "skills_heading": t["cv.skills.title"],
        "programming": t["cv.skills.programming"],
        "tools": t["cv.skills.tools"],
        "languages_heading": t["cv.languages.title"],
        "lang_pt": f"{t['cv.languages.pt']} \u2014 {t['cv.languages.ptLevel']}",
        "lang_en": f"{t['cv.languages.en']} \u2014 {t['cv.languages.enLevel']}",
        "education_heading": t["cv.education.title"],
        "education_side": f"LEIC-A<br/>Instituto Superior T\u00e9cnico<br/>"
                           f"<font color='#5c5c5c'>{t['cv.education.grad']}</font>",
        "location": t["cv.location"],
        "sec_profile": t["cv.section.profile"],
        "summary": t["cv.summary"],
        "sec_projects": t["cv.section.projects"],
        "sec_education": t["cv.section.education"],
        "edu_title": t["cv.edu.name"],
        "edu_date": t["cv.edu.date"],
        "edu_sub": t["cv.edu.location"],
        "edu_desc": t["cv.edu.desc"],
        "sec_experience": t["cv.section.experience"],
        "experience_placeholder": t["cv.experience.placeholder"],
        "tag_academic": t["cv.tag.academic"],
    }

    c["projects"] = [
        {"title": t[f"cv.{key}.title"], "sub": t[f"cv.{key}.sub"], "desc": t[f"cv.{key}.desc"]}
        for key in PROJECT_KEYS
    ]
    return c


def skill_dots(level, max_level=5, size=6.5, gap=3):
    width = max_level * size + (max_level - 1) * gap
    d = Drawing(width, size)
    for i in range(max_level):
        x = i * (size + gap)
        filled = i < level
        d.add(Rect(
            x, 0, size, size,
            fillColor=BLACK if filled else None,
            strokeColor=BLACK if filled else BORDER,
            strokeWidth=0.7,
        ))
    return d, width

PAGE_W, PAGE_H = A4
SIDEBAR_W = 55 * mm
MAIN_W = PAGE_W - SIDEBAR_W - 28 * mm

styles = {
    "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=16, leading=19, textColor=BLACK),
    "role": ParagraphStyle("role", fontName="Helvetica", fontSize=8.3, leading=12, textColor=SOFT, spaceAfter=14),
    "side_h2": ParagraphStyle("side_h2", fontName="Helvetica-Bold", fontSize=7.6, leading=10, textColor=SOFT, spaceBefore=14, spaceAfter=6),
    "side_body": ParagraphStyle("side_body", fontName="Helvetica", fontSize=8.3, leading=12.5, textColor=BLACK),
    "side_link": ParagraphStyle("side_link", fontName="Helvetica", fontSize=8.3, leading=12.5, textColor=BLACK),
    "skill_group": ParagraphStyle("skill_group", fontName="Helvetica-Bold", fontSize=6.9, leading=10, textColor=SOFT, spaceBefore=6, spaceAfter=4),
    "skill_name": ParagraphStyle("skill_name", fontName="Helvetica", fontSize=8.3, leading=11, textColor=BLACK),
    "sec_title": ParagraphStyle("sec_title", fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=BLACK, spaceBefore=2, spaceAfter=8),
    "summary": ParagraphStyle("summary", fontName="Helvetica", fontSize=9, leading=13.3, textColor=BLACK, spaceAfter=14),
    "entry_title": ParagraphStyle("entry_title", fontName="Helvetica-Bold", fontSize=9.6, leading=12.5, textColor=BLACK),
    "entry_date": ParagraphStyle("entry_date", fontName="Helvetica", fontSize=7.8, leading=11, textColor=SOFT, alignment=TA_LEFT),
    "entry_sub": ParagraphStyle("entry_sub", fontName="Helvetica-Oblique", fontSize=8.2, leading=11.5, textColor=SOFT, spaceAfter=4),
    "entry_desc": ParagraphStyle("entry_desc", fontName="Helvetica", fontSize=8.5, leading=12.3, textColor=BLACK, spaceAfter=4),
    "entry_stack": ParagraphStyle("entry_stack", fontName="Helvetica", fontSize=7.6, leading=10.5, textColor=SOFT),
    "placeholder": ParagraphStyle("placeholder", fontName="Helvetica-Oblique", fontSize=8.6, leading=13, textColor=SOFT),
}


def build_sidebar(c):
    flow = [Paragraph(NAME, styles["name"]), Paragraph(c["role"], styles["role"])]

    flow.append(Paragraph(c["contact_heading"], styles["side_h2"]))
    flow.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6))
    for line in [EMAIL, FENIX, GITHUB, LINKEDIN, c["location"]]:
        flow.append(Paragraph(line, styles["side_link"]))
        flow.append(Spacer(1, 3))

    flow.append(Paragraph(c["skills_heading"], styles["side_h2"]))
    flow.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6))
    flow.extend(skill_group_table(c["programming"], PROGRAMMING_SKILLS))
    flow.extend(skill_group_table(c["tools"], TOOL_SKILLS))

    flow.append(Paragraph(c["languages_heading"], styles["side_h2"]))
    flow.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6))
    flow.append(Paragraph(c["lang_pt"], styles["side_body"]))
    flow.append(Spacer(1, 3))
    flow.append(Paragraph(c["lang_en"], styles["side_body"]))

    flow.append(Paragraph(c["education_heading"], styles["side_h2"]))
    flow.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6))
    flow.append(Paragraph(c["education_side"], styles["side_body"]))

    return flow


def skill_group_table(title, skills):
    flow = [Paragraph(title.upper(), styles["skill_group"])]
    rows = []
    dots_w = 0
    for name, level in skills:
        dots, dots_w = skill_dots(level)
        rows.append([Paragraph(name, styles["skill_name"]), dots])
    name_w = (SIDEBAR_W - 18 * mm) - dots_w
    t = Table(rows, colWidths=[name_w, dots_w])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    flow.append(t)
    return flow


def entry(title, date, sub, desc, stack):
    head = Table(
        [[Paragraph(title, styles["entry_title"]), Paragraph(date, styles["entry_date"])]],
        colWidths=[MAIN_W * 0.7, MAIN_W * 0.3],
    )
    head.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    flow = [head, Paragraph(sub, styles["entry_sub"]), Paragraph(desc, styles["entry_desc"])]
    if stack:
        flow.append(Paragraph(" &nbsp;\u00b7&nbsp; ".join(stack), styles["entry_stack"]))
    flow.append(Spacer(1, 3))
    flow.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=9))
    return flow


PROJECT_STACKS = {
    "p1": ["C", "Merge Sort", "CLI"],
    "p2": ["Python", "AI Agent"],
    "p3": ["Logisim", "ISA Design"],
}


def build_main(c):
    flow = [Paragraph(c["sec_profile"], styles["sec_title"]), Paragraph(c["summary"], styles["summary"])]

    flow.append(Paragraph(c["sec_projects"], styles["sec_title"]))
    for key, proj in zip(PROJECT_KEYS, c["projects"]):
        flow.extend(entry(proj["title"], c["tag_academic"], proj["sub"], proj["desc"], PROJECT_STACKS[key]))

    flow.append(Paragraph(c["sec_education"], styles["sec_title"]))
    flow.extend(entry(c["edu_title"], c["edu_date"], c["edu_sub"], c["edu_desc"], []))

    flow.append(Paragraph(c["sec_experience"], styles["sec_title"]))
    flow.append(Paragraph(c["experience_placeholder"], styles["placeholder"]))

    return flow


def build_pdf(path, lang="en"):
    c = load_content(lang)
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0)

    sidebar_flow = build_sidebar(c)
    main_flow = build_main(c)

    row_h = PAGE_H - 14
    sidebar_table = Table([[sidebar_flow]], colWidths=[SIDEBAR_W], rowHeights=[row_h])
    sidebar_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SIDEBAR_BG),
        ("LEFTPADDING", (0, 0), (-1, -1), 10 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 16 * mm),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    main_table = Table([[main_flow]], colWidths=[PAGE_W - SIDEBAR_W], rowHeights=[row_h])
    main_table.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 12 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 16 * mm),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    outer = Table([[sidebar_table, main_table]], colWidths=[SIDEBAR_W, PAGE_W - SIDEBAR_W])
    outer.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    doc.build([outer])


if __name__ == "__main__":
    out_dir = BASE_DIR / "assets" / "cv"
    out_dir.mkdir(parents=True, exist_ok=True)
    build_pdf(out_dir / "joao-coelho-cv-legacy-en.pdf", lang="en")
    build_pdf(out_dir / "joao-coelho-cv-legacy-pt.pdf", lang="pt")
    print("done")
