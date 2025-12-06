document.addEventListener("DOMContentLoaded", function () {
    const tabsContainer = document.querySelector(".about-tabs");
    if (!tabsContainer) return;

    const buttons = tabsContainer.querySelectorAll(".tab-btn");
    const contents = tabsContainer.querySelectorAll(".tab-content");

    if (!buttons.length || !contents.length) return;

    // Activer le premier onglet
    buttons[0].classList.add("active");
    contents[0].classList.add("active");
    contents[0].classList.remove("hidden");

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            const id = button.getAttribute("data-id");

            // Désactiver tous
            buttons.forEach(b => b.classList.remove("active"));
            contents.forEach(c => {
                c.classList.remove("active");
                c.classList.add("hidden");
            });

            // Activer celui choisi
            button.classList.add("active");
            const target = document.getElementById(`tab-${id}`);

            if (target) {
                target.classList.add("active");
                target.classList.remove("hidden");
            }
        });
    });
});
