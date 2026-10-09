#!/usr/bin/env python3
"""Gera os PDFs do CV (en/pt) a partir do próprio cv.html.

Resolve os [data-i18n] com data/i18n.json, força o modo PDF (sem foto/toolbar)
e imprime com wkhtmltopdf. Usa as fontes como fontes de sistema (copia os .ttf
de assets/fonts/ttf), para o texto do PDF ficar selecionável.

    pip install beautifulsoup4 --break-system-packages
    sudo apt install wkhtmltopdf      # macOS: brew install --cask wkhtmltopdf
    python3 gen_cv_pdf.py
"""

import json
import platform
import shutil
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent
I18N_PATH = BASE_DIR / "data" / "i18n.json"
CV_HTML_PATH = BASE_DIR / "cv.html"
OUT_DIR = BASE_DIR / "assets" / "cv"


def render_static_html(lang: str) -> str:
    """Return cv.html with every data-i18n element resolved to plain
    text for `lang`, JS stripped, and PDF-irrelevant bits removed."""
    dict_ = json.loads(I18N_PATH.read_text(encoding="utf-8"))[lang]
    soup = BeautifulSoup(CV_HTML_PATH.read_text(encoding="utf-8"), "html.parser")

    soup.html["lang"] = lang
    # wkhtmltopdf here ignores --print-media-type (unpatched Qt build),
    # so force the print rules on via a class instead of @media print.
    soup.body["class"] = soup.body.get("class", []) + ["pdf-mode"]
    # Point at a temp copy of style.css without @font-face (see build_pdf);
    # the same fonts are used via the system copies from ensure_fonts().
    style_link = soup.select_one('link[href="css/style.css"]')
    if style_link:
        style_link["href"] = "css/_pdf_style.tmp.css"

    for el in soup.select("[data-i18n]"):
        key = el.get("data-i18n")
        if key not in dict_:
            continue
        if el.has_attr("data-i18n-attr"):
            el[el["data-i18n-attr"]] = dict_[key]
        else:
            el.string = dict_[key]

    for el in soup.select("[data-i18n-aria]"):
        key = el.get("data-i18n-aria")
        if key in dict_:
            el["aria-label"] = dict_[key]

    # No JS needed — the text above is already resolved, and running
    # main.js would just try to re-fetch i18n.json and re-toggle langs.
    for script in soup.find_all("script"):
        script.decompose()

    return str(soup)


FONT_SRC = BASE_DIR / "assets" / "fonts" / "ttf"


def ensure_fonts() -> None:
    """Make Geist / Geist Mono / Instrument Sans available as *system*
    fonts. wkhtmltopdf turns web fonts (@font-face) into outlines, which
    leaves a PDF with no selectable text — useless for ATS parsers. System
    fonts are embedded as real text, so the PDF gets the same typefaces as
    the site AND stays machine-readable. The TTFs in assets/fonts/ttf are
    copied into the user font folder (no admin rights needed)."""
    if platform.system() == "Darwin":
        dest = Path.home() / "Library" / "Fonts"
    else:
        dest = Path.home() / ".fonts"
    dest.mkdir(parents=True, exist_ok=True)
    copied = False
    for ttf in FONT_SRC.glob("*.ttf"):
        target = dest / ttf.name
        if not target.exists():
            shutil.copy2(ttf, target)
            copied = True
    if copied:
        print(f"fonts: installed into {dest}")
        if shutil.which("fc-cache"):
            subprocess.run(["fc-cache", "-f"], check=False, capture_output=True)


def build_pdf(path: Path, lang: str) -> None:
    html = render_static_html(lang)
    tmp_path = BASE_DIR / f"_cv_print_{lang}.tmp.html"
    style_src = BASE_DIR / "css" / "style.css"
    style_tmp = BASE_DIR / "css" / "_pdf_style.tmp.css"
    # Drop @font-face / @import: the PDF must use the system-installed
    # copies of the same fonts (see ensure_fonts) so text stays real text.
    style_css = style_src.read_text(encoding="utf-8")
    style_css = "\n".join(
        line for line in style_css.splitlines()
        if "@import" not in line and not line.lstrip().startswith("@font-face")
    )
    style_tmp.write_text(style_css, encoding="utf-8")
    tmp_path.write_text(html, encoding="utf-8")
    try:
        subprocess.run(
            [
                "wkhtmltopdf",
                "--disable-javascript",
                "--enable-local-file-access",
                "--load-error-handling", "ignore",
                "--page-size", "A4",
                "--margin-top", "13mm", "--margin-bottom", "13mm",
                "--margin-left", "16mm", "--margin-right", "16mm",
                str(tmp_path), str(path),
            ],
            check=True, capture_output=True, cwd=BASE_DIR,
        )
    finally:
        tmp_path.unlink(missing_ok=True)
        style_tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    ensure_fonts()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    build_pdf(OUT_DIR / "joao-coelho-cv-en.pdf", "en")
    build_pdf(OUT_DIR / "joao-coelho-cv-pt.pdf", "pt")
    print("done")
