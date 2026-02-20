// static/economic/prestations/js/prestations.js

// Petit JS générique pour le pôle services
document.addEventListener("DOMContentLoaded", function () {
  const topbar = document.querySelector(".services-topbar");

  // Effet ombre sur le topbar au scroll
  if (topbar) {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        topbar.classList.add("is-scrolled");
      } else {
        topbar.classList.remove("is-scrolled");
      }
    };
    handleScroll();
    window.addEventListener("scroll", handleScroll);
  }

  // Scroll fluide pour liens internes (ex: #services-list)
  const internalLinks = document.querySelectorAll(
    '.services-shell a[href^="#"]'
  );

  internalLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      const targetId = this.getAttribute("href");
      if (!targetId || targetId === "#") return;

      const target = document.querySelector(targetId);
      if (!target) return;

      e.preventDefault();
      const topOffset = topbar ? topbar.offsetHeight + 8 : 8;
      const targetPos =
        target.getBoundingClientRect().top + window.pageYOffset - topOffset;

      window.scrollTo({
        top: targetPos,
        behavior: "smooth",
      });
    });
  });

  // Hook simple pour éventuels boutons / actions futures
  // window.Services = {
  //   openRequestModal() { ... }
  // };
});
