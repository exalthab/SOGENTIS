// global/js/theme.js
(function () {
  function qs(id) { return document.getElementById(id); }

  const body = document.body;
  const btnDesktop = qs("themeToggle");
  const btnMobile  = qs("themeToggleMobile");
  const iconDesktop = qs("themeIcon");         // optionnel
  const iconMobile  = qs("themeIconMobile");   // optionnel

  // =========================================================
  // Logo fallback (brand): cache le nom si logo OK
  // =========================================================
  function initBrandLogo() {
    const brand = document.querySelector(".topbar .topbar-brand");
    if (!brand) return;

    const logoUrl = "/static/global/image/logo.png";
    const img = new Image();

    img.onload = function () {
      brand.classList.add("brand--has-logo");
      brand.classList.remove("brand--no-logo");
    };

    img.onerror = function () {
      brand.classList.remove("brand--has-logo");
      brand.classList.add("brand--no-logo");
    };

    // cache-buster léger (évite cache agressif en dev)
    // En prod, tu peux enlever ?v=1 ou le versionner.
    img.src = logoUrl + "?v=1";
  }

  // état initial : localStorage > prefers-color-scheme > clair
  function initialMode() {
    const saved = (localStorage.getItem("theme") || "").toLowerCase();
    if (saved === "dark" || saved === "light") return saved;
    try {
      return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark" : "light";
    } catch { return "light"; }
  }

  function apply(mode) {
    const isDark = mode === "dark";
    body.classList.toggle("dark-mode", isDark);
    // MAJ icônes si elles existent
    if (iconDesktop) iconDesktop.textContent = isDark ? "☀️" : "🌙";
    if (iconMobile)  iconMobile.textContent  = isDark ? "☀️" : "🌙";
    try { localStorage.setItem("theme", isDark ? "dark" : "light"); } catch {}
  }

  function current() {
    return body.classList.contains("dark-mode") ? "dark" : "light";
  }

  function toggle() {
    apply(current() === "dark" ? "light" : "dark");
  }

  // Init
  apply(initialMode());
  initBrandLogo();

  // Bind boutons s'ils existent
  if (btnDesktop) btnDesktop.addEventListener("click", toggle);
  if (btnMobile)  btnMobile.addEventListener("click", toggle);

  // API publique (optionnel)
  window.SogentisTheme = { apply, toggle, current };
})();






// // global/js/theme.js - good
// (function () {
//   function qs(id) { return document.getElementById(id); }

//   const body = document.body;
//   const btnDesktop = qs("themeToggle");
//   const btnMobile  = qs("themeToggleMobile");
//   const iconDesktop = qs("themeIcon");         // optionnel
//   const iconMobile  = qs("themeIconMobile");   // optionnel

//   // état initial : localStorage > prefers-color-scheme > clair
//   function initialMode() {
//     const saved = (localStorage.getItem("theme") || "").toLowerCase();
//     if (saved === "dark" || saved === "light") return saved;
//     try {
//       return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
//         ? "dark" : "light";
//     } catch { return "light"; }
//   }

//   function apply(mode) {
//     const isDark = mode === "dark";
//     body.classList.toggle("dark-mode", isDark);
//     // MAJ icônes si elles existent
//     if (iconDesktop) iconDesktop.textContent = isDark ? "☀️" : "🌙";
//     if (iconMobile)  iconMobile.textContent  = isDark ? "☀️" : "🌙";
//     try { localStorage.setItem("theme", isDark ? "dark" : "light"); } catch {}
//   }

//   function current() {
//     return body.classList.contains("dark-mode") ? "dark" : "light";
//   }

//   function toggle() {
//     apply(current() === "dark" ? "light" : "dark");
//   }

//   // Init
//   apply(initialMode());

//   // Bind boutons s'ils existent
//   if (btnDesktop) btnDesktop.addEventListener("click", toggle);
//   if (btnMobile)  btnMobile.addEventListener("click", toggle);

//   // API publique (optionnel)
//   window.SogentisTheme = { apply, toggle, current };
// })();




// document.addEventListener("DOMContentLoaded", function () {
//     const body = document.body;
//     const toggleBtn = document.getElementById("themeToggle");
//     const themeIcon = document.getElementById("themeIcon");

//     // Récupération du thème sauvegardé
//     const savedTheme = localStorage.getItem("theme");
//     if (savedTheme === "dark") {
//       body.classList.add("dark-mode");
//       themeIcon.textContent = "☀️";
//     }

//     // Bascule entre sombre et clair
//     toggleBtn?.addEventListener("click", () => {
//       body.classList.toggle("dark-mode");
//       const isDark = body.classList.contains("dark-mode");
//       themeIcon.textContent = isDark ? "☀️" : "🌙";
//       localStorage.setItem("theme", isDark ? "dark" : "light");
//     });
//   });




  
// document.addEventListener("DOMContentLoaded", function () {
//   const body = document.body;
//   const toggleBtn = document.getElementById("themeToggle");
//   const themeIcon = document.getElementById("themeIcon");

//   // Fonction pour appliquer le thème
//   function applyTheme(theme) {
//     if (theme === "dark") {
//       body.classList.add("dark-mode");
//       themeIcon.textContent = "☀️";
//     } else {
//       body.classList.remove("dark-mode");
//       themeIcon.textContent = "🌙";
//     }
//   }

//   // Récupération du thème sauvegardé
//   const savedTheme = localStorage.getItem("theme") || "light";
//   applyTheme(savedTheme);

//   // Bascule entre sombre et clair
//   toggleBtn?.addEventListener("click", () => {
//     const isDark = body.classList.toggle("dark-mode");
//     const newTheme = isDark ? "dark" : "light";
//     themeIcon.textContent = isDark ? "☀️" : "🌙";
//     localStorage.setItem("theme", newTheme);
//   });
// });
