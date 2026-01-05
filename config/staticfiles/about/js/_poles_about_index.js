document.addEventListener("DOMContentLoaded", () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("reveal-visible");
            }
        });
    }, { threshold: 0.2 });

    document.querySelectorAll(".section-reveal, .pole-card").forEach(el => {
        observer.observe(el);
    });
});
