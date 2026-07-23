# Como manter e estender o site

Guia rápido para quando precisares de adicionar conteúdo sem teres de
reaprender a estrutura toda de cada vez.

## Estrutura

```
index.html         homepage: hero + about + skills + projects (tudo numa página, só em inglês)
cv.html             página do CV (layout sidebar, toolbar flutuante, EN/PT)
projects.html        redirect para index.html#projects (só para não partir links antigos)
css/style.css        tokens de design + estilos partilhados (header, cards, hero, etc.)
css/cv.css           estilos específicos do CV (incluindo o seletor de idioma)
js/main.js            dark mode, menu mobile, imprimir o CV, e a troca de idioma do CV
data/i18n.json        texto do CV em EN + PT — a única coisa que precisa de
                       duas versões; usado pelo cv.html E pelo gen_cv_pdf.py
assets/images/pfp.png            a tua foto (placeholder por agora)
assets/images/projects/*.png      uma imagem por projeto (placeholders por agora)
assets/cv/*.pdf        PDFs do CV (gerados por gen_cv_pdf.py)
gen_cv_pdf.py          gera os PDFs a partir de data/i18n.json
```

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

Em `cv.html`, dentro do bloco "experience", há o mesmo tipo de
comentário `TEMPLATE`. Quando tiveres a primeira experiência: apaga o
parágrafo placeholder, cola o bloco `.cv-entry` do template, preenche
e repete para cada nova entrada. Como o CV é bilingue, usa
`data-i18n="cv.expN.xxx"` e acrescenta essas chaves nos dois
dicionários (`en` e `pt`) em `data/i18n.json`.

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

Como o `gen_cv_pdf.py` lê diretamente de `data/i18n.json`, só precisas
de mudar o JSON (para texto) — o script não tem mais nada para
atualizar à parte, exceto se adicionares/tirares um projeto (nesse
caso ajusta `PROJECT_KEYS` e `PROJECT_STACKS` no topo do ficheiro) ou
mudares as competências/idiomas (`PROGRAMMING_SKILLS`, `TOOL_SKILLS`).

```
pip install reportlab --break-system-packages
python3 gen_cv_pdf.py
```

Isto substitui os dois ficheiros em `assets/cv/`.

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
