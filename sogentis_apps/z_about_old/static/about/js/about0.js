/**
 * ============================================
 * 🌍 SOGENTIS - Page "À propos de nous"
 * JS interactif et animations
 * ============================================
 */

document.addEventListener("DOMContentLoaded", () => {
  // --- 1️⃣ Animation fade-in-up au scroll ---
  const fadeElements = document.querySelectorAll(".fade-in-up");
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) entry.target.classList.add("visible");
      });
    },
    { threshold: 0.15 }
  );
  fadeElements.forEach((el) => observer.observe(el));

  // --- 2️⃣ Gestion du bouton "Voir plus / Voir moins" ---
  const seeMoreButtons = document.querySelectorAll(".see-more");
  seeMoreButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const paragraph = btn.previousElementSibling;
      if (!paragraph) return;

      const expanded = paragraph.classList.toggle("expanded");
      btn.textContent = expanded ? "Voir moins ▲" : "Voir plus ▼";
    });
  });

  // --- 3️⃣ Animation du slider des partenaires ---
  const slider = document.querySelector(".partners-slider");
  if (slider) {
    slider.addEventListener("mouseenter", () => {
      slider.style.animationPlayState = "paused";
    });
    slider.addEventListener("mouseleave", () => {
      slider.style.animationPlayState = "running";
    });
  }

  // --- 4️⃣ Focus automatique sur les sections d'accordéon ouvertes ---
  const accordion = document.getElementById("aboutAccordion");
  if (accordion) {
    accordion.addEventListener("shown.bs.collapse", (event) => {
      const openSection = event.target.querySelector(".accordion-body");
      if (openSection) {
        openSection.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  }

  // --- 5️⃣ Fonction utilitaire pour enfants (story toggle) ---
  window.toggleStory = function (childId) {
    const preview = document.getElementById("story-preview-" + childId);
    const full = document.getElementById("story-full-" + childId);
    const toggleBtn = document.getElementById("toggle-btn-" + childId);
    if (!preview || !full || !toggleBtn) return;

    const isExpanded = !full.classList.contains("d-none");
    if (isExpanded) {
      full.classList.add("d-none");
      preview.classList.remove("d-none");
      toggleBtn.textContent = "Voir plus";
    } else {
      full.classList.remove("d-none");
      preview.classList.add("d-none");
      toggleBtn.textContent = "Voir moins";
    }
  };
});


// --- 6️⃣ Toggle des cartes Mission/Vision/Valeurs/Objectifs ---
function toggleDetail(detailId) {
  const detail = document.getElementById(detailId);
  const card = detail.closest(".about-card");

  if (!detail || !card) return;

  const isActive = detail.classList.contains("active");

  // Ferme toutes les autres cartes
  document.querySelectorAll(".section-detail").forEach((el) => el.classList.remove("active"));
  document.querySelectorAll(".about-card").forEach((c) => c.classList.remove("open"));

  // Ouvre ou ferme la carte cliquée
  if (!isActive) {
    detail.classList.add("active");
    card.classList.add("open");
  }
}

function toggleDetail(id) {
  const section = document.getElementById(id);
  if (!section) return;

  const card = section.closest('.about-card');
  const indicator = card.querySelector('.toggle-indicator');

  const isOpen = section.classList.toggle('open');
  if (isOpen) {
    section.style.maxHeight = section.scrollHeight + "px";
    indicator.textContent = "−";
  } else {
    section.style.maxHeight = null;
    indicator.textContent = "+";
  }
}
