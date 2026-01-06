// static/about/js/about.js

document.addEventListener("DOMContentLoaded", () => {
  // ==========================================================
  // 1) Reveal on scroll pour .section-reveal
  // ==========================================================
  const revealSections = document.querySelectorAll(".section-reveal");

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.15,
      }
    );

    revealSections.forEach((section) => observer.observe(section));
  } else {
    // Fallback : tout afficher directement
    revealSections.forEach((section) => section.classList.add("visible"));
  }

  // ==========================================================
  // 2) Scroll fluide pour la navigation interne .about-nav
  // ==========================================================
  const navLinks = document.querySelectorAll(".about-nav a[href^='#']");

  navLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      const targetId = link.getAttribute("href").substring(1);
      const target = document.getElementById(targetId);
      if (!target) return;

      e.preventDefault();

      const yOffset = -70; // marge pour la nav sticky
      const rect = target.getBoundingClientRect();
      const y = rect.top + window.scrollY + yOffset;

      window.scrollTo({
        top: y,
        behavior: "smooth",
      });
    });
  });
});
