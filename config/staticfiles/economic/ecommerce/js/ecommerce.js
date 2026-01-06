/* static/economic/ecommerce/js/ecommerce.js */
(function () {
  "use strict";

  // ==============================
  // CSRF helper
  // ==============================
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
  }
  const csrfToken = getCookie("csrftoken");

  // ==============================
  // Gallery thumbnails -> main
  // ==============================
  const main = document.getElementById("pdMainImage");
  const thumbs = document.querySelectorAll(".pd-thumb-btn[data-src]");
  if (main && thumbs.length) {
    thumbs.forEach((btn) => {
      btn.addEventListener("click", () => {
        const src = btn.getAttribute("data-src");
        if (src) main.src = src;

        thumbs.forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");
      });
    });
  }

  // ==============================
  // Quantity (+ / -)
  // ==============================
  const input = document.getElementById("pdQtyInput");
  const minus = document.getElementById("pdQtyMinus");
  const plus = document.getElementById("pdQtyPlus");

  function clampQty(v) {
    v = parseInt(v || "1", 10);
    if (isNaN(v) || v < 1) v = 1;
    return v;
  }

  if (minus && plus && input) {
    minus.addEventListener("click", () => (input.value = clampQty(clampQty(input.value) - 1)));
    plus.addEventListener("click", () => (input.value = clampQty(clampQty(input.value) + 1)));
    input.addEventListener("input", () => (input.value = clampQty(input.value)));
  }

  // ==============================
  // Favorites toggle (AJAX)
  // ==============================
  const favForm = document.getElementById("pdFavForm");
  const favBtn = document.getElementById("pdFavBtn");

  function setFavUI(isFav) {
    if (!favBtn) return;

    const icon = favBtn.querySelector("i.bi");
    const text = favBtn.querySelector(".pdFavText");

    if (icon) {
      icon.classList.remove("bi-heart", "bi-heart-fill", "text-danger");
      if (isFav) {
        icon.classList.add("bi-heart-fill", "text-danger");
      } else {
        icon.classList.add("bi-heart");
      }
    }
    if (text) {
      text.textContent = isFav ? "Retirer des favoris" : "Ajouter aux favoris";
    }
  }

  if (favForm && favBtn) {
    favForm.addEventListener("submit", function (e) {
      const url = favBtn.getAttribute("data-url");
      if (!url || url === "#") return; // fallback normal

      // AJAX try
      e.preventDefault();

      const formData = new FormData(favForm);

      fetch(url, {
        method: "POST",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": csrfToken || "",
        },
        body: formData,
      })
        .then((r) => {
          if (r.status === 401 || r.status === 403) {
            // Pas connecté / refus -> fallback normal
            favForm.submit();
            return null;
          }
          return r.json();
        })
        .then((data) => {
          if (!data) return;
          if (data.ok) {
            setFavUI(!!data.favorited);

            // Optionnel: si tu as un badge global quelque part
            // ex: <span id="favCountBadge"></span>
            const badge = document.getElementById("favCountBadge");
            if (badge && typeof data.count !== "undefined") {
              badge.textContent = data.count;
              badge.style.display = data.count > 0 ? "inline-block" : "none";
            }
          } else {
            // fallback
            favForm.submit();
          }
        })
        .catch(() => favForm.submit());
    });
  }
})();
