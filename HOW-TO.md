# Portfolio — como editar

```
index.html        página principal (projetos = copiar um <article>)
cv.html           CV (texto com data-i18n → data/i18n.json)
data/i18n.json    textos do CV em EN e PT (só aqui se escreve cada texto 2x)
css/style.css     todo o estilo (cores/tema no topo, em :root)
js/main.js        tema, menu, idioma do CV
gen_cv_pdf.py     gera assets/cv/*.pdf a partir do cv.html
```

**Novo projeto:** copia um `<article class="project-card">` em `index.html` e troca título, link, texto e stack.

**Editar o CV:** muda o texto em `cv.html` (EN) e a mesma chave em `data/i18n.json` (EN e PT).
Depois regenera os PDFs: `python3 gen_cv_pdf.py` (precisa de `wkhtmltopdf` e `beautifulsoup4`).

**Cores:** variáveis no topo de `css/style.css` — `:root` é o modo escuro, `html:not(.dark)` o claro.
