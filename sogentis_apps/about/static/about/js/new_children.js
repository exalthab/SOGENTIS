// about/static/about/js/_children.js

document.addEventListener("DOMContentLoaded", function () {
    // Boutons "Voir description"
    const openButtons = document.querySelectorAll(".open-child-modal");

    openButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetSelector = btn.getAttribute("data-target");
            if (!targetSelector) return;

            const modal = document.querySelector(targetSelector);
            if (!modal) return;

            modal.style.display = "flex";
            modal.setAttribute("aria-hidden", "false");
        });
    });

    // Boutons de fermeture (croix)
    const closeButtons = document.querySelectorAll(".child-modal .close-modal");

    closeButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const modal = btn.closest(".child-modal");
            if (!modal) return;

            modal.style.display = "none";
            modal.setAttribute("aria-hidden", "true");
        });
    });

    // Fermer en cliquant sur le fond sombre
    const modals = document.querySelectorAll(".child-modal");

    modals.forEach(modal => {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) {
                modal.style.display = "none";
                modal.setAttribute("aria-hidden", "true");
            }
        });
    });
});
