# Como manter e estender o site

Guia rápido para quando precisares de adicionar conteúdo sem teres de
reaprender a estrutura toda de cada vez.

## Estrutura

```
index.html         homepage: hero + about + skills + projects (tudo numa página, só em inglês)
cv.html             página do CV (layout single-column ATS-friendly, toolbar flutuante, EN/PT)
projects.html        redirect para index.html#projects (só para não partir links antigos)
css/style.css        tokens de design + estilos partilhados (header, cards, hero, etc.)
css/cv.css           estilos específicos do CV atual (incluindo o seletor de idioma)
js/main.js            dark mode, menu mobile, imprimir o CV, e a troca de idioma do CV
data/i18n.json        texto do CV em EN + PT — a única coisa que precisa de
                       duas versões; usado pelo cv.html E pelo gen_cv_pdf.py
assets/images/pfp.png            a tua foto (placeholder por agora)
assets/images/projects/*.png      uma imagem por projeto (placeholders por agora)
assets/cv/*.pdf        PDFs do CV (gerados por gen_cv_pdf.py)
gen_cv_pdf.py          gera os PDFs ATS-friendly a partir de data/i18n.json

-- arquivo, não editar a não ser que queiras mesmo mexer no design antigo --
cv-legacy.html         design antigo do CV (sidebar + skill dots) — só um
                        link discreto no rodapé de cv.html aponta para aqui
css/cv-legacy.css      estilos do design antigo
gen_cv_pdf_legacy.py   gera os PDFs do design antigo (*-legacy-en/pt.pdf)
```

**Porque o CV mudou de layout:** o design antigo usava uma sidebar de
2 colunas e "skill dots" (bolinhas sem texto por trás) para mostrar
nível de cada tecnologia. Isso lê mal em leitores de CV automáticos
(ATS): o texto sai fora de ordem e as bolinhas não têm conteúdo
nenhum para extrair. O `cv.html` atual é uma coluna só, texto simples
do início ao fim — mais chato de olhar, mas o que passa num ATS de
verdade. Ambas as versões continuam a usar o mesmo `data/i18n.json`.

**Só o CV é bilingue.** O resto do site (`index.html`, `projects.html`)
é escrito diretamente em inglês no HTML, sem `data-i18n` e sem seletor
de idioma — o texto existe uma única vez, no próprio ficheiro. O CV é
a única página com botão PT/EN, por isso é a única cujo texto vive em
`data/i18n.json` (com as duas versões) em vez de estar escrito
diretamente no HTML. O `gen_cv_pdf.py` lê esse mesmo ficheiro para
gerar os dois PDFs, para nunca teres de escrever a mesma frase do CV
duas vezes em sítios diferentes do código.

`js/i18n.js` e `js/main.js` foram fundidos num único `js/main.js`,
já que a lógica de idioma só corre quando encontra os botões PT/EN
(ou seja, só em `cv.html`) — não fazia sentido manter dois ficheiros
para um site tão pequeno.

## Adicionar um novo projeto (no site)

Em `index.html`, dentro de `<div class="project-grid">`, há um bloco
comentado a dizer `TEMPLATE` no fim da lista de projetos. Copia esse
bloco `<article>...</article>` para fora do comentário (antes dele) e:

1. **Ícone** — troca o SVG dentro de `.project-icon` por outro (mesmo
   estilo: só stroke, sem fill). Fica à direita do card, ao lado da
   tag, para não ocupar altura extra por cima do título. Não há
   imagens nem cores por projeto; todos os cards são quadrados,
   monocromáticos e do mesmo tamanho, iguais ao resto do site.
2. **Texto** — tag, título, descrição e stack escrevem-se diretamente
   no HTML, em inglês, sem `data-i18n`. A descrição corta ao fim de
   3 linhas (line-clamp), por isso mantém-na curta.
3. **Link** — troca o `href` do `<a>` dentro de `.links` para o
   repositório certo.

## Adicionar experiência profissional ao CV

Em `cv.html`, dentro do bloco "experience", há uma entrada de
**exemplo** (`Software Engineering Intern (example)`, dados
inventados) só para mostrares o layout. Quando tiveres a tua própria
experiência: apaga o parágrafo `cv-example-note` e substitui o texto
do `.cv-entry` pelos teus dados reais (mesmas chaves `cv.exp1.*` em
`data/i18n.json`, nos dois idiomas). Para mais do que uma experiência,
duplica o bloco `.cv-entry` inteiro e usa `cv.exp2.*`, `cv.exp3.*`, etc.

## Traduções do CV (PT/EN)

Cada texto traduzível em `cv.html` tem um atributo
`data-i18n="cv.chave"`. Essa chave tem de existir nos dois objetos
(`en` e `pt`) dentro de `data/i18n.json`.

## Trocar a foto de perfil

`assets/images/pfp.png` é só um placeholder com as tuas iniciais —
substitui pela tua foto real (quadrada, pelo menos 256×256px fica
bem em ecrãs de alta resolução), mantendo o mesmo nome de ficheiro.
É usada tanto em `index.html` como em `cv.html`.

## Atualizar o PDF do CV

O `gen_cv_pdf.py` **não tem um layout próprio** — ele lê o teu
`cv.html`/`cv.css` normal, substitui cada `[data-i18n]` pelo texto do
idioma pedido (a partir de `data/i18n.json`) e imprime o resultado
para PDF com `wkhtmltopdf`. Ou seja: muda o `cv.html` normalmente (ou
só o JSON, para texto) e o PDF segue automaticamente — não há um
segundo layout para manter sincronizado à mão.

```
pip install beautifulsoup4 --break-system-packages
sudo apt install wkhtmltopdf fonts-ibm-plex   # fonts-ibm-plex evita
                                                # depender da Google
                                                # Fonts a gerar o PDF
python3 gen_cv_pdf.py
```

Isto substitui os dois ficheiros em `assets/cv/`.

Se mexeres no CSS do CV: as regras específicas do PDF vivem em dois
sítios em `cv.css` — `@media print` (para quando alguém faz Cmd/Ctrl+P
no browser) e `body.pdf-mode` (usado só pelo `gen_cv_pdf.py`, porque a
versão do `wkhtmltopdf` instalada ignora `--print-media-type`). As
duas têm de dizer sempre a mesma coisa. Evita também a propriedade
`gap` em flexbox no CSS do CV — o motor do `wkhtmltopdf` não a
suporta; usa `margin` no elemento a seguir, como o resto do ficheiro já faz.

## Impressão do CV no Safari

O Safari tem um bug conhecido no visualizador de PDF embutido: pedir
`.print()` a um separador recém-aberto com um PDF costuma mostrar uma
página em branco até se clicar em cancelar — só depois é que o PDF
aparece mesmo. Em vez de lutar contra isso, `js/main.js` deteta
motores WebKit não-Chromium e, nesses casos, só abre o PDF numa nova
aba sem tentar imprimir automaticamente (o utilizador faz Cmd+P
manualmente, o que funciona bem assim que o PDF já está visível).
Chrome, Firefox e Edge mantêm o comportamento automático.

## Dark mode / idioma do CV — como funcionam

Ambos são guardados em `localStorage` (chaves `theme` e `lang`) e
aplicados antes da página desenhar, para não haver "flash" da versão
errada. Não precisas de mexer nisto para adicionar conteúdo.
