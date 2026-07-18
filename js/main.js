(function () {
  "use strict";

  var root = document.documentElement;
  var STORAGE_KEY = "theme";

  function applyTheme(theme) {
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }

  // Init: stored preference > OS preference > light
  var stored = null;
  try { stored = localStorage.getItem(STORAGE_KEY); } catch (e) {}
  var prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(stored || (prefersDark ? "dark" : "light"));

  document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.querySelector("[data-theme-toggle]");
    if (toggle) {
      toggle.addEventListener("click", function () {
        var isDark = root.classList.toggle("dark");
        try { localStorage.setItem(STORAGE_KEY, isDark ? "dark" : "light"); } catch (e) {}
      });
    }

    var printBtn = document.querySelector("[data-print]");
    if (printBtn) {
      printBtn.addEventListener("click", function () {
        window.print();
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
  });
})();
