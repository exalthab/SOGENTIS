(function () {
  const mainImg = document.getElementById("pdMainImage");
  const thumbs = document.querySelectorAll(".pd-thumb");
  const qtyInput = document.getElementById("pdQtyInput");
  const qtyHidden = document.getElementById("pdQtyHidden");

  // Gallery
  thumbs.forEach(btn => {
    btn.addEventListener("click", () => {
      thumbs.forEach(t => t.classList.remove("active"));
      btn.classList.add("active");
      const src = btn.getAttribute("data-src");
      if (src && mainImg) mainImg.src = src;
    });
  });

  // Qty controls
  document.querySelectorAll("[data-qty]").forEach(b => {
    b.addEventListener("click", () => {
      const op = b.getAttribute("data-qty");
      let v = parseInt(qtyInput.value || "1", 10);
      if (op === "+1") v++;
      if (op === "-1") v = Math.max(1, v - 1);
      qtyInput.value = v;
      if (qtyHidden) qtyHidden.value = String(v);
    });
  });

  if (qtyInput) {
    qtyInput.addEventListener("input", () => {
      let v = parseInt(qtyInput.value || "1", 10);
      if (!v || v < 1) v = 1;
      qtyInput.value = v;
      if (qtyHidden) qtyHidden.value = String(v);
    });
  }

  // Share
  const shareBtn = document.getElementById("pdShareBtn");
  if (shareBtn) {
    shareBtn.addEventListener("click", async () => {
      const url = window.location.href;
      try {
        if (navigator.share) {
          await navigator.share({ title: document.title, url });
        } else {
          await navigator.clipboard.writeText(url);
          alert("Lien copié !");
        }
      } catch (e) {}
    });
  }
})();
