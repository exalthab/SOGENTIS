/* ============================================================
   about.js — SOGENTIS v4.3
   ------------------------------------------------------------
   - Animation d'apparition au scroll
   - Boutons "Voir plus / Voir moins" (avec i18n Django)
   - Slider partenaires automatique
   - Effet de blur sur le header
   - Compatible toutes sections dynamiques
   ============================================================ */

document.addEventListener("DOMContentLoaded", () => {

  /* =========================================================
     🔹 1. Animation fade-in-up au scroll
  ========================================================= */
  const fadeElements = document.querySelectorAll(".fade-in-up");
  const revealOnScroll = () => {
    const triggerBottom = window.innerHeight * 0.85;
    fadeElements.forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.top < triggerBottom) el.classList.add("visible");
    });
  };
  window.addEventListener("scroll", revealOnScroll, { passive: true });
  revealOnScroll();


  /* =========================================================
     🔹 2. Boutons "Voir plus / Voir moins" (avec i18n)
  ========================================================= */
  const initSeeMore = () => {
    const cards = document.querySelectorAll(".about-card");
    if (!cards.length) return;

    const collapsedHeight = 80; // Hauteur max initiale (px)
    const showMoreText = typeof gettext !== "undefined" ? gettext("Voir plus ▼") : "Voir plus ▼";
    const showLessText = typeof gettext !== "undefined" ? gettext("Voir moins ▲") : "Voir moins ▲";

    cards.forEach(card => {
      const p = card.querySelector(".see-more-target");
      const btn = card.querySelector(".see-more");
      if (!p || !btn) return;

      // Appliquer le style de texte tronqué si nécessaire
      if (!p.classList.contains("expanded") && p.scrollHeight > collapsedHeight) {
        p.style.maxHeight = `${collapsedHeight}px`;
        p.style.overflow = "hidden";
      }

      btn.addEventListener("click", () => {
        const isExpanded = p.classList.toggle("expanded");
        if (isExpanded) {
          // Développer le texte
          p.style.maxHeight = p.scrollHeight + "px";
          btn.textContent = showLessText;
        } else {
          // Replier le texte
          p.style.maxHeight = `${collapsedHeight}px`;
          btn.textContent = showMoreText;
        }
      });
    });
  };
  initSeeMore();


  /* =========================================================
     🔹 3. Slider partenaires automatique
  ========================================================= */
  const partnersSlider = document.querySelector(".partners-slider");
  if (partnersSlider) {
    let scrollAmount = 0;
    const speed = 0.8; // Plus petit = plus lent
    const maxScroll = partnersSlider.scrollWidth / 2;

    const slide = () => {
      scrollAmount += speed;
      if (scrollAmount >= maxScroll) scrollAmount = 0;
      partnersSlider.style.transform = `translateX(-${scrollAmount}px)`;
      requestAnimationFrame(slide);
    };

    // Attendre que les images soient chargées pour éviter un calcul erroné
    if (partnersSlider.querySelectorAll("img").length) {
      window.addEventListener("load", slide);
    } else {
      slide();
    }
  }


  /* =========================================================
     🔹 4. Effet de blur du header au scroll
  ========================================================= */
  const header = document.querySelector("header, .navbar");
  if (header) {
    const toggleBlur = () => {
      header.classList.toggle("blurred", window.scrollY > 50);
    };
    window.addEventListener("scroll", toggleBlur, { passive: true });
    toggleBlur();
  }

});
