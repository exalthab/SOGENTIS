document.addEventListener("DOMContentLoaded", () => {

    // GSAP fade-in-up
    gsap.from(".fade-in-up", { opacity:0, y:40, duration:1, stagger:0.2, ease:"power3.out" });

    // Hover animation on section cards
    document.querySelectorAll(".section-card").forEach(card => {
        card.addEventListener("mouseenter", () => gsap.to(card, { scale:1.03, duration:0.3, ease:"power2.out" }));
        card.addEventListener("mouseleave", () => gsap.to(card, { scale:1, duration:0.3, ease:"power2.out" }));
    });

    // Toggle section detail: une seule ouverte à la fois
    window.toggleDetail = function(id) {
        const section = document.getElementById(id);
        if (!section) return;
        const card = section.closest(".section-card");
        const isOpen = card.classList.contains("open");

        document.querySelectorAll(".section-card.open").forEach(c => {
            const body = c.querySelector(".section-card-body");
            gsap.to(body, { height:0, duration:0.4, ease:"power2.inOut" });
            c.setAttribute("aria-expanded", "false");
            c.classList.remove("open");
        });

        if (!isOpen) {
            card.classList.add("open");
            card.setAttribute("aria-expanded", "true");
            const body = card.querySelector(".section-card-body");
            body.style.height = "auto";
            const height = body.clientHeight + "px";
            body.style.height = "0px";
            gsap.to(body, { height:height, duration:0.4, ease:"power2.inOut" });
        }
    };
});
