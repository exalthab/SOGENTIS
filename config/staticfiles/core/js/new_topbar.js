// core/js/topbar.js
(function () {
  const btns = [
    document.getElementById('themeToggle'),
    document.getElementById('themeToggleMobile'),
  ].filter(Boolean);

  if (!btns.length) return;

  // Fallback minimal si theme.js n'expose pas d'API publique
  function fallbackSet(mode) {
    const root = document.documentElement;
    root.dataset.theme = mode;
    try { localStorage.setItem('theme', mode); } catch {}
  }
  function fallbackToggle() {
    const root = document.documentElement;
    const current =
      root.dataset.theme ||
      (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    fallbackSet(current === 'dark' ? 'light' : 'dark');
  }

  function toggleTheme() {
    // 1) API publique si dispo
    if (window.SogentisTheme && typeof window.SogentisTheme.toggle === 'function') {
      window.SogentisTheme.toggle();
      return;
    }
    // 2) Event pour theme.js (si écouteur custom)
    const evt = new CustomEvent('sogentis:toggle-theme', { bubbles: true });
    const accepted = window.dispatchEvent(evt);
    if (!accepted) {
      // 3) Fallback local
      fallbackToggle();
    }
  }

  btns.forEach((b) => b.addEventListener('click', toggleTheme));
})();










/* =======================================================================
   SOGENTIS — TOPBAR JS PREMIUM (version simplifiée)
   Gestion du shrink de la topbar uniquement
   ======================================================================= */

/* --------------------------------------------------
   TOPBAR SHRINK (Effet au scroll)
-------------------------------------------------- */

// const topbar = document.querySelector(".topbar");

// window.addEventListener("scroll", () => {
//     if (window.scrollY > 10) {
//         topbar.classList.add("scrolled");
//     } else {
//         topbar.classList.remove("scrolled");
//     }
// });
