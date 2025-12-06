/* =======================================================================
   SOGENTIS — TOPBAR JS PREMIUM (version simplifiée)
   Gestion du shrink de la topbar uniquement
   ======================================================================= */

/* --------------------------------------------------
   TOPBAR SHRINK (Effet au scroll)
-------------------------------------------------- */

const topbar = document.querySelector(".topbar");

window.addEventListener("scroll", () => {
    if (window.scrollY > 10) {
        topbar.classList.add("scrolled");
    } else {
        topbar.classList.remove("scrolled");
    }
});
