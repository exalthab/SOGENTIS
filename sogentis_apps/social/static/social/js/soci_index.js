(() => {
  // 1) Hero: applique les backgrounds via data-bg (évite inline style)
  document.querySelectorAll(".hero-slide[data-bg]").forEach((el) => {
    const bg = el.getAttribute("data-bg");
    if (bg) el.style.background = `center/cover no-repeat url("${bg}")`;
    el.style.minHeight = "100vh";
  });

  // 2) Toggle description docs (utilise hidden au lieu de display:none)
  document.addEventListener("click", (e) => {
    const a = e.target.closest(".desc-toggle");
    if (!a) return;
    e.preventDefault();

    const id = a.getAttribute("data-doc");
    const target = a.getAttribute("data-target");
    if (!id || !target) return;

    const shortEl = document.getElementById(`desc-short-${id}`);
    const fullEl = document.getElementById(`desc-full-${id}`);
    if (!shortEl || !fullEl) return;

    const showFull = target === "desc-full";
    fullEl.hidden = !showFull;
    shortEl.hidden = showFull;
  });
})();
