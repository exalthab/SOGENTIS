/* ==========================================================================
   _mother.js – Interactions cartes & modals Mères
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* ----------------------------------------------------
       1. Toggle description (Voir plus / Voir moins)
    ---------------------------------------------------- */
    const toggles = document.querySelectorAll(".story-toggle");

    toggles.forEach(btn => {
        btn.addEventListener("click", () => {
            const parent = btn.closest(".mother-story");
            const shortText = parent.querySelector(".story-short");
            const fullText  = parent.querySelector(".story-full");

            const isOpen = btn.dataset.open === "1";

            if (!isOpen) {
                shortText.style.display = "none";
                fullText.style.display = "block";
                btn.textContent = btn.dataset.less || "Voir moins";
                btn.dataset.open = "1";
            } else {
                shortText.style.display = "block";
                fullText.style.display = "none";
                btn.textContent = btn.dataset.more || "Voir plus";
                btn.dataset.open = "0";
            }
        });
    });

    /* ----------------------------------------------------
       2. Gestion des modals
    ---------------------------------------------------- */
    const modalOpenBtns = document.querySelectorAll(".open-mother-modal");

    modalOpenBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.dataset.target;
            const modal = document.querySelector(target);
            if (modal) modal.style.display = "flex";
        });
    });

    const closeModalBtns = document.querySelectorAll(".close-modal");

    closeModalBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const modal = btn.closest(".mother-modal");
            modal.style.display = "none";
        });
    });

    // Fermer modal au clic en dehors du contenu
    const modals = document.querySelectorAll(".mother-modal");
    modals.forEach(modal => {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) modal.style.display = "none";
        });
    });

    /* ----------------------------------------------------
       3. Animation fade-in on scroll
    ---------------------------------------------------- */
    const cards = document.querySelectorAll(".mother-card");

    const revealOnScroll = () => {
        const trigger = window.innerHeight * 0.88;

        cards.forEach(card => {
            const top = card.getBoundingClientRect().top;
            if (top < trigger) card.classList.add("visible");
        });
    };

    window.addEventListener("scroll", revealOnScroll);
    revealOnScroll();
});
