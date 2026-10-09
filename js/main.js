(function () {
  "use strict";
  var root = document.documentElement;
  var $ = function (s) { return document.querySelector(s); };
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  // Theme: dark by default, remembered after the first toggle
  root.classList.toggle("dark", (store.get("theme") || "dark") === "dark");

  // CV language (PT/EN): only runs where the language buttons exist (cv.html)
  var langButtons = document.querySelectorAll("[data-lang-option]");
  if (langButtons.length) {
    var pt = (navigator.languages || [navigator.language || ""]).some(function (l) { return /^pt/i.test(l); });
    var current = store.get("lang") || (pt ? "pt" : "en");
    var applyLang = function (dict, lang) {
      root.lang = lang;
      document.querySelectorAll("[data-i18n]").forEach(function (el) {
        var v = dict[el.dataset.i18n];
        if (v === undefined) return;
        if (el.dataset.i18nAttr) el.setAttribute(el.dataset.i18nAttr, v); else el.textContent = v;
      });
      document.querySelectorAll("[data-i18n-aria]").forEach(function (el) {
        el.setAttribute("aria-label", dict[el.dataset.i18nAria]);
      });
      langButtons.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.langOption === lang); });
      $("[data-cv-download]").href = "assets/cv/joao-coelho-cv-" + lang + ".pdf";
    };
    // if the fetch fails (file:// without a server) the English text in the HTML stays
    fetch("data/i18n.json").then(function (r) { return r.json(); }).then(function (data) {
      applyLang(data[current], current);
      langButtons.forEach(function (b) {
        b.addEventListener("click", function () {
          current = b.dataset.langOption;
          store.set("lang", current);
          applyLang(data[current], current);
        });
      });
    }).catch(function () {});
  }

  document.addEventListener("DOMContentLoaded", function () {
    $("[data-theme-toggle]").addEventListener("click", function () {
      store.set("theme", root.classList.toggle("dark") ? "dark" : "light");
    });

    // Mobile menu
    var toggle = $("[data-nav-toggle]"), links = $("[data-nav-links]");
    if (toggle && links) {
      var setOpen = function (open) {
        links.classList.toggle("open", open);
        toggle.setAttribute("aria-expanded", open);
      };
      toggle.addEventListener("click", function () { setOpen(!links.classList.contains("open")); });
      links.querySelectorAll("a").forEach(function (a) { a.addEventListener("click", function () { setOpen(false); }); });

      // Menu highlight follows the clicked / visible section
      var anchors = links.querySelectorAll('a[href^="#"]');
      var mark = function (hash) {
        anchors.forEach(function (a) {
          if (a.getAttribute("href") === hash) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
        });
      };
      var spy = function () {
        var p = $("#projects").getBoundingClientRect().top < innerHeight * 0.4;
        mark(p || innerHeight + scrollY >= document.body.scrollHeight - 4 ? "#projects" : "#top");
      };
      anchors.forEach(function (a) { a.addEventListener("click", function () { mark(a.getAttribute("href")); }); });
      addEventListener("scroll", spy, { passive: true });
      spy();
    }

    // CV print button: open the PDF and print it (Safari's PDF viewer can't be
    // printed programmatically, so there it just opens in a new tab)
    var printBtn = $("[data-print]");
    if (printBtn) printBtn.addEventListener("click", function () {
      var w = window.open($("[data-cv-download]").href, "_blank");
      if (!w || /^((?!chrome|android).)*safari/i.test(navigator.userAgent)) return;
      var done = false, go = function () { if (done) return; done = true; try { w.focus(); w.print(); } catch (e) {} };
      w.addEventListener("load", go);
      setTimeout(go, 1000);
    });
  });
})();
