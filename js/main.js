(function () {
  "use strict";

  var root = document.documentElement;

  /* ---------- dark mode: stored preference > OS preference > light ---------- */
  var THEME_KEY = "theme";
  function applyTheme(theme) { root.classList.toggle("dark", theme === "dark"); }

  var storedTheme = null;
  try { storedTheme = localStorage.getItem(THEME_KEY); } catch (e) {}
  var prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(storedTheme || (prefersDark ? "dark" : "light"));

  /* ---------- CV language switch — only runs on cv.html, where the
     PT/EN buttons exist. The rest of the site is English-only and has
     no data-i18n attributes, so this fetch never happens elsewhere. ---------- */
  var DEFAULT_LANG = "en";
  var langButtons = document.querySelectorAll("[data-lang-option]");

  function detectLang() {
    var langs = navigator.languages || [navigator.language || ""];
    for (var i = 0; i < langs.length; i++) {
      if (String(langs[i]).toLowerCase().indexOf("pt") === 0) return "pt";
    }
    return DEFAULT_LANG;
  }
  function getLang() {
    var stored = null;
    try { stored = localStorage.getItem("lang"); } catch (e) {}
    return stored === "en" || stored === "pt" ? stored : detectLang();
  }
  function applyLang(dict, lang) {
    root.setAttribute("lang", lang);
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var value = dict[el.getAttribute("data-i18n")];
      if (value === undefined) return;
      if (el.hasAttribute("data-i18n-attr")) el.setAttribute(el.getAttribute("data-i18n-attr"), value);
      else el.textContent = value;
    });
    document.querySelectorAll("[data-i18n-aria]").forEach(function (el) {
      var value = dict[el.getAttribute("data-i18n-aria")];
      if (value !== undefined) el.setAttribute("aria-label", value);
    });
    langButtons.forEach(function (el) {
      el.setAttribute("aria-pressed", el.getAttribute("data-lang-option") === lang ? "true" : "false");
    });
    var dl = document.querySelector("[data-cv-download]");
    if (dl) dl.setAttribute("href", "assets/cv/joao-coelho-cv-" + lang + ".pdf");
    root.classList.add("i18n-ready");
  }

  if (langButtons.length) {
    fetch("data/i18n.json")
      .then(function (res) { return res.json(); })
      .then(function (data) {
        var lang = getLang();
        applyLang(data[lang] || data[DEFAULT_LANG], lang);
        langButtons.forEach(function (btn) {
          btn.addEventListener("click", function () {
            var next = btn.getAttribute("data-lang-option");
            if (next === getLang()) return;
            try { localStorage.setItem("lang", next); } catch (e) {}
            applyLang(data[next], next);
          });
        });
      })
      // If the fetch fails (e.g. opened via file:// without a local server),
      // leave the English text already present in the markup as a fallback.
      .catch(function () { root.classList.add("i18n-ready"); });
  }

  /* ---------- theme toggle button, mobile nav, CV print ---------- */
  document.addEventListener("DOMContentLoaded", function () {
    var themeToggle = document.querySelector("[data-theme-toggle]");
    if (themeToggle) {
      themeToggle.addEventListener("click", function () {
        var isDark = root.classList.toggle("dark");
        try { localStorage.setItem(THEME_KEY, isDark ? "dark" : "light"); } catch (e) {}
      });
    }

    var navToggle = document.querySelector("[data-nav-toggle]");
    var navLinks = document.querySelector("[data-nav-links]");
    if (navToggle && navLinks) {
      navToggle.addEventListener("click", function () {
        var open = navLinks.classList.toggle("open");
        navToggle.setAttribute("aria-expanded", open ? "true" : "false");
      });
      navLinks.querySelectorAll("a").forEach(function (a) {
        a.addEventListener("click", function () {
          navLinks.classList.remove("open");
          navToggle.setAttribute("aria-expanded", "false");
        });
      });
    }

    // Safari/WebKit's embedded PDF viewer doesn't reliably fire `load`, and
    // calling .print() on it too early renders a blank page until the user
    // hits cancel — at which point the real PDF finally shows up. Rather than
    // fight that, WebKit just gets the PDF opened in a new tab and prints
    // manually (Cmd+P works fine once it's actually on screen); every other
    // engine keeps the auto-print behaviour.
    var printBtn = document.querySelector("[data-print]");
    if (printBtn) {
      printBtn.addEventListener("click", function () {
        var downloadLink = document.querySelector("[data-cv-download]");
        var pdfUrl = downloadLink ? downloadLink.getAttribute("href") : null;
        if (!pdfUrl) { window.print(); return; }

        var pdfWindow = window.open(pdfUrl, "_blank");
        if (!pdfWindow) return; // popup blocked — PDF is still open in a new tab for manual printing

        var isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
        if (isSafari) return;

        var hasPrinted = false;
        function triggerPrint() {
          if (hasPrinted) return;
          hasPrinted = true;
          try { pdfWindow.focus(); pdfWindow.print(); } catch (e) {}
        }
        pdfWindow.addEventListener("load", triggerPrint);
        setTimeout(triggerPrint, 1000);
      });
    }
  });
})();
