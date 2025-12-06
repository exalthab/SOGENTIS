// ================================
// _children.js - Gestion des modals enfants
// ================================

document.addEventListener("DOMContentLoaded", function () {
    // Récupérer tous les boutons "Voir description"
    const openButtons = document.querySelectorAll(".open-child-modal");

    openButtons.forEach((btn) => {
        btn.addEventListener("click", function () {
            const targetId = btn.getAttribute("data-target");
            const modal = document.querySelector(targetId);
            if (modal) {
                modal.classList.add("show");
            }
        });
    });

    // Boutons de fermeture dans toutes les modals
    const closeButtons = document.querySelectorAll(".child-modal .close-modal");

    closeButtons.forEach((btn) => {
        btn.addEventListener("click", function () {
            const modal = btn.closest(".child-modal");
            if (modal) {
                modal.classList.remove("show");
            }
        });
    });

    // Fermer la modal si clic en dehors du contenu
    const modals = document.querySelectorAll(".child-modal");
    modals.forEach((modal) => {
        modal.addEventListener("click", function (e) {
            if (e.target === modal) {
                modal.classList.remove("show");
            }
        });
    });

    // Animation fade-in des cartes enfants
    const cards = document.querySelectorAll(".child-card");
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add("visible");
        }, index * 100); // Effet de cascade
    });
});
