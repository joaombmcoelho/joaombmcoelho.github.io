#!/usr/bin/env python3
"""
Gera os PDFs do CV (en/pt) a partir do PRÓPRIO cv.html — não de um
layout paralelo. Isto substitui a abordagem anterior (reportlab a
redesenhar tudo à mão num ficheiro à parte), que obrigava a manter
dois layouts sincronizados manualmente e facilmente desalinhava.

Como funciona:
  1. Lê cv.html e resolve cada elemento [data-i18n] com o texto do
     idioma pedido (o mesmo data/i18n.json que o site usa) — o mesmo
     que o main.js faz no browser, só que aqui de antemão.
  2. Remove <script> (não precisamos de JS: o texto já está resolvido)
     para não confundir o PDF gerado.
  3. Escreve um HTML temporário na raiz do site (para os caminhos
     relativos a css/ e assets/ continuarem a funcionar) e imprime-o
     com wkhtmltopdf --print-media-type, que aplica exatamente o
     @media print do cv.css — o mesmo bloco que rege a versão
     "imprimir" no browser.

Resultado: HTML e PDF partilham 100% do layout/CSS; a única
diferença é a que o próprio @media print define (sem foto, sem
toolbar, sem a nota "example entry").

Correr com:
    pip install beautifulsoup4 --break-system-packages
    sudo apt install wkhtmltopdf fonts-ibm-plex
    python3 gen_cv_pdf.py
"""

import json
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
    # Point at a local-fonts-only copy of style.css (see build_pdf) so
    # wkhtmltopdf never needs the network for the Google Fonts @import —
    # IBM Plex is installed as a system font, so it resolves locally.
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


def build_pdf(path: Path, lang: str) -> None:
    html = render_static_html(lang)
    tmp_path = BASE_DIR / f"_cv_print_{lang}.tmp.html"
    style_src = BASE_DIR / "css" / "style.css"
    style_tmp = BASE_DIR / "css" / "_pdf_style.tmp.css"
    # Strip the Google Fonts @import (must be the file's first rule, so
    # it can't be overridden from outside) — IBM Plex is installed
    # locally, so plain font-family matching still finds it, no network.
    style_css = style_src.read_text(encoding="utf-8")
    style_css = "\n".join(
        line for line in style_css.splitlines() if "@import" not in line
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
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    build_pdf(OUT_DIR / "joao-coelho-cv-en.pdf", "en")
    build_pdf(OUT_DIR / "joao-coelho-cv-pt.pdf", "pt")
    print("done")
