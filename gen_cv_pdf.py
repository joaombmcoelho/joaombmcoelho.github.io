#!/usr/bin/env python3
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.graphics.shapes import Drawing, Rect

BLACK = HexColor("#0a0a0a")
SOFT = HexColor("#5c5c5c")
BORDER = HexColor("#cccccc")
SIDEBAR_BG = HexColor("#f4f4f4")


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
MAIN_W = PAGE_W - SIDEBAR_W - 28 * mm  # account for margins

styles = {
    "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=16, leading=19, textColor=BLACK),
    "role": ParagraphStyle("role", fontName="Helvetica", fontSize=8.3, leading=12, textColor=SOFT, spaceAfter=14),
    "side_h2": ParagraphStyle("side_h2", fontName="Helvetica-Bold", fontSize=7.6, leading=10, textColor=SOFT, spaceBefore=14, spaceAfter=6),
    "side_body": ParagraphStyle("side_body", fontName="Helvetica", fontSize=8.3, leading=12.5, textColor=BLACK),
    "side_link": ParagraphStyle("side_link", fontName="Helvetica", fontSize=8.3, leading=12.5, textColor=BLACK),
    "tag": ParagraphStyle("tag", fontName="Helvetica", fontSize=7.6, leading=11, textColor=SOFT),
    "skill_group": ParagraphStyle("skill_group", fontName="Helvetica-Bold", fontSize=6.9, leading=10, textColor=SOFT, spaceBefore=6, spaceAfter=4),
    "skill_name": ParagraphStyle("skill_name", fontName="Helvetica", fontSize=8.3, leading=11, textColor=BLACK),
    "sec_title": ParagraphStyle("sec_title", fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=SOFT, spaceBefore=2, spaceAfter=8),
    "summary": ParagraphStyle("summary", fontName="Helvetica", fontSize=9.3, leading=14, textColor=BLACK, spaceAfter=16),
    "entry_title": ParagraphStyle("entry_title", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=BLACK),
    "entry_date": ParagraphStyle("entry_date", fontName="Helvetica", fontSize=8, leading=11, textColor=SOFT, alignment=TA_LEFT),
    "entry_sub": ParagraphStyle("entry_sub", fontName="Helvetica-Oblique", fontSize=8.5, leading=12, textColor=SOFT, spaceAfter=5),
    "entry_desc": ParagraphStyle("entry_desc", fontName="Helvetica", fontSize=8.8, leading=13, textColor=BLACK, spaceAfter=5),
    "entry_stack": ParagraphStyle("entry_stack", fontName="Helvetica", fontSize=7.8, leading=11, textColor=SOFT),
    "placeholder": ParagraphStyle("placeholder", fontName="Helvetica-Oblique", fontSize=8.6, leading=13, textColor=SOFT),
}


def side_contact_line(label):
    return Paragraph(label, styles["side_link"])


def skill_group_table(title, skills):
    """title: str, skills: list of (name, level 0-5)"""
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


def build_sidebar():
    flow = []
    flow.append(Paragraph("Jo\u00e3o Coelho", styles["name"]))
    flow.append(Paragraph("Computer Science and Engineering Student", styles["role"]))

    flow.append(Paragraph("CONTACT", styles["side_h2"]))
    flow.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6))
    for line in [
        "joao.mbmc@gmail.com",
        "fenix.tecnico.ulisboa.pt/homepage/ist1117964",
        "github.com/joaombmcoelho",
        "linkedin.com/in/joaombmcoelho",
        "Lisbon, Portugal",
    ]:
        flow.append(side_contact_line(line))
        flow.append(Spacer(1, 3))

    flow.append(Paragraph("SKILLS", styles["side_h2"]))
    flow.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6))
    flow.extend(skill_group_table("Programming", [("Python", 4), ("C", 4)]))
    flow.extend(skill_group_table("Tools", [("Git", 4), ("Linux", 3), ("Docker", 2)]))

    flow.append(Paragraph("LANGUAGES", styles["side_h2"]))
    flow.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6))
    flow.append(Paragraph("Portuguese \u2014 Native", styles["side_body"]))
    flow.append(Spacer(1, 3))
    flow.append(Paragraph("English \u2014 Fluent", styles["side_body"]))

    flow.append(Paragraph("EDUCATION", styles["side_h2"]))
    flow.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6))
    flow.append(Paragraph("LEIC-A<br/>Instituto Superior T\u00e9cnico<br/><font color='#5c5c5c'>Expected 2028</font>", styles["side_body"]))

    return flow


def section_title(text):
    return Paragraph(text, styles["sec_title"])


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
    flow.append(Spacer(1, 4))
    flow.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=12))
    return flow


def build_main():
    flow = []
    flow.append(section_title("// profile"))
    flow.append(Paragraph(
        "Aspiring Software Engineer currently in my 2nd year of Computer Science at Instituto "
        "Superior T\u00e9cnico (LEIC-A). Focused on learning clean code, algorithms, and building "
        "practical projects close to the metal \u2014 from digital logic to assembly. Looking for an "
        "internship or junior role where I can contribute and learn fast.",
        styles["summary"],
    ))

    flow.append(section_title("// projects"))
    flow.extend(entry(
        "16-bit Single-Cycle Processor", "Academic",
        "Computer Architecture coursework \u2014 Instituto Superior T\u00e9cnico",
        "Designed a 16-bit single-cycle processor in Logisim, supporting a small custom "
        "instruction set (li, add, dot, dota) built on a 3-bit opcode scheme.",
        ["Logisim", "Digital Logic", "ISA Design"],
    ))
    flow.extend(entry(
        "Mini-Transformer in RISC-V", "Academic",
        "Assembly / Machine Learning coursework \u2014 Instituto Superior T\u00e9cnico",
        "Implemented the core building blocks of a Mini-Transformer directly in RISC-V assembly, "
        "run on the Ripes simulator \u2014 tokenization, attention scoring, and matrix multiplication "
        "from scratch.",
        ["RISC-V", "Assembly", "Ripes"],
    ))

    flow.append(section_title("// education"))
    flow.extend(entry(
        "LEIC-A \u2014 Computer Science and Engineering", "2024 \u2014 2028 (exp.)",
        "Instituto Superior T\u00e9cnico, Lisbon",
        "Coursework spans computer architecture, algorithms, systems programming, and mathematics.",
        [],
    ))

    flow.append(section_title("// experience"))
    flow.append(Paragraph(
        "No professional experience listed yet \u2014 add internships, part-time work, or "
        "volunteering here as you gain them.",
        styles["placeholder"],
    ))

    return flow


def build_pdf(path):
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0,
    )

    sidebar_flow = build_sidebar()
    main_flow = build_main()

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
    build_pdf("/home/claude/portfolio-site/assets/cv/joao-coelho-cv.pdf")
    print("done")
