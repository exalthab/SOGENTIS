/* ============================================
   _team_member.js — Toggle tabs Conseil / Employés
============================================ */

document.addEventListener("DOMContentLoaded", () => {
    const tabs = document.querySelectorAll(".team-tab");
    const contents = document.querySelectorAll(".team-tab-content");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            // Désactiver tous les onglets et cacher tous les contenus
            tabs.forEach(t => t.classList.remove("active"));
            contents.forEach(c => c.classList.add("hidden"));

            // Activer l'onglet cliqué
            tab.classList.add("active");
            const target = tab.dataset.tab;
            document.getElementById(`team-${target}`).classList.remove("hidden");
        });
    });
});
