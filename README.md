# joaombmcoelho.github.io

Personal portfolio website of João Coelho, with a bilingual (EN/PT) CV page, light/dark theme and automatic PDF generation. Built with plain HTML, CSS and JavaScript, with no frameworks and no build step.

**Live site:** https://joaombmcoelho.github.io

## Features

- Project showcase on the landing page
- CV page in English and Portuguese, switchable in the browser
- Light and dark theme
- CV exported to PDF in both languages from a single source

## Project Structure

## Project Structure
- index.html Landing page and projects
- cv.html CV page (text keyed with data-i18n)
- assets/ Images and generated CV PDFs (assets/cv/)
- data/i18n.json CV translations (EN and PT)
- css/style.css Styles; theme colors at the top, in :root
- js/main.js Theme toggle, menu, CV language switch
- gen_cv_pdf.py Generates assets/cv/*.pdf from cv.html



## Getting Started

Clone the repository and serve it with any static file server:

```bash
git clone https://github.com/joaombmcoelho/joaombmcoelho.github.io.git
cd joaombmcoelho.github.io
python3 -m http.server 8000
```

Open <http://localhost:8000>.

> Use a local server instead of opening `index.html` directly: the CV page loads `data/i18n.json` with `fetch`, which browsers block on `file://`.

## Generate CV PDFs

Requires [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) and BeautifulSoup:

```bash
pip3 install beautifulsoup4
python3 gen_cv_pdf.py
```

The PDFs are written to `assets/cv/`.

## Deployment

The site is hosted on GitHub Pages and deploys automatically on every push to `main`.