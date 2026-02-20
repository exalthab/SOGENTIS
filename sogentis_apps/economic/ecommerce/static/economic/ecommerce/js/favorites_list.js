// // static/economic/ecommerce/js/favorites_list.js
(function () {
  "use strict";

  // Empêche double submit (double-click) sur "ajouter au panier"
  document.querySelectorAll(".fav-cart-form").forEach((form) => {
    const btn = form.querySelector("button[type='submit']");
    if (!btn) return;

    // éviter double binding
    if (btn.dataset.bound === "1") return;
    btn.dataset.bound = "1";

    const stock = parseInt(form.getAttribute("data-stock") || "0", 10) || 0;
    if (stock <= 0) {
      btn.disabled = true;
      form.setAttribute("aria-disabled", "true");
      return;
    }

    form.addEventListener("submit", () => {
      // si stock = 0 au moment du clic (sécurité)
      const s = parseInt(form.getAttribute("data-stock") || "0", 10) || 0;
      if (s <= 0) {
        btn.disabled = true;
        form.setAttribute("aria-disabled", "true");
        return;
      }

      btn.disabled = true;
      btn.classList.add("is-loading");
      // page reload normalement, mais si AJAX/unload annulé, on réactive après un délai
      setTimeout(() => {
        btn.disabled = false;
        btn.classList.remove("is-loading");
      }, 1600);
    });
  });
})();
