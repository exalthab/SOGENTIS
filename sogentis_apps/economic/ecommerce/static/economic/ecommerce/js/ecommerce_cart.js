// static/economic/ecommerce/js/ecommerce_cart.js
(() => {
  "use strict";

  // ============================================================
  // Helpers
  // ============================================================
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const toInt = (v, fallback = 0) => {
    const n = parseInt(String(v ?? "").replace(/[^\d-]/g, ""), 10);
    return Number.isFinite(n) ? n : fallback;
  };

  const clamp = (n, min, max) => Math.max(min, Math.min(max, n));

  const setDisabled = (el, v) => {
    if (!el) return;
    const disabled = !!v;

    if ("disabled" in el) {
      el.disabled = disabled;
      el.classList?.toggle("disabled", disabled);
      if (disabled) el.setAttribute("aria-disabled", "true");
      else el.removeAttribute("aria-disabled");
      return;
    }

    if (el.tagName === "A") {
      el.classList.toggle("disabled", disabled);
      if (disabled) {
        el.setAttribute("aria-disabled", "true");
        el.setAttribute("tabindex", "-1");
      } else {
        el.removeAttribute("aria-disabled");
        el.removeAttribute("tabindex");
      }
    }
  };

  const sanitizeQty = (raw) => {
    const n = toInt(String(raw ?? "").replace(/[^\d]/g, ""), 0);
    return Number.isFinite(n) ? n : 0;
  };

  const flash = (el) => {
    if (!el) return;
    el.classList.add("is-flash");
    window.setTimeout(() => el.classList.remove("is-flash"), 280);
  };

  // ============================================================
  // Main
  // ============================================================
  const lines = $$("[data-cart-line]");
  if (!lines.length) return;

  const syncLineUI = (line) => {
    const stock = clamp(toInt(line.dataset.stock, 0), 0, 1_000_000);

    const controls = $("[data-cart-qty-controls]", line);
    const input = $("[data-qty-input]", line);
    const minus = $("[data-qty-minus]", line);
    const plus = $("[data-qty-plus]", line);
    const updateBtn = $("[data-update-btn]", line);
    const hint = $("[data-cart-hint]", line);

    const removeForm = $("[data-cart-remove-form]", line);
    const updateForm = $("[data-cart-update-form]", line);

    let qty = sanitizeQty(input?.value);

    // règle stock=0 -> tout bloqué + hint
    if (stock <= 0) {
      if (input) input.value = "0";
      setDisabled(minus, true);
      setDisabled(plus, true);
      setDisabled(updateBtn, true);

      if (hint) {
        hint.style.display = "";
        hint.textContent = "Produit en rupture — retirez-le du panier.";
      }
      if (controls) flash(controls);
      return;
    }

    // qty max = stock, min = 0 (0 = retirer)
    qty = clamp(qty, 0, stock);
    if (input) input.value = String(qty);

    // minus autorisé jusqu’à 0
    setDisabled(minus, qty <= 0);

    // plus désactivé si qty>=stock
    setDisabled(plus, qty >= stock);

    // update désactivé si qty==0 (car on va retirer à la place)
    setDisabled(updateBtn, qty <= 0);

    if (hint) {
      if (qty <= 0) {
        hint.style.display = "";
        hint.textContent = "Quantité à 0 : l’article sera retiré.";
      } else if (qty >= stock) {
        hint.style.display = "";
        hint.textContent = "Limite atteinte : stock maximum.";
      } else {
        hint.style.display = "none";
        hint.textContent = "";
      }
    }

    // auto-remove si qty==0 : on soumet le remove form au lieu d’update
    // (mais on ne le fait pas ici pour éviter de retirer pendant la saisie)
    // on le fait au click sur minus ou au blur si qty==0
    if (removeForm) {
      // ok
    }
    if (updateForm) {
      // ok
    }
  };

  // init UI
  lines.forEach(syncLineUI);

  // ============================================================
  // Click handlers: + / -
  // ============================================================
  document.addEventListener("click", (e) => {
    const btnMinus = e.target.closest("[data-qty-minus]");
    const btnPlus = e.target.closest("[data-qty-plus]");
    if (!btnMinus && !btnPlus) return;

    const line = e.target.closest("[data-cart-line]");
    if (!line) return;

    const stock = clamp(toInt(line.dataset.stock, 0), 0, 1_000_000);
    const input = $("[data-qty-input]", line);
    const controls = $("[data-cart-qty-controls]", line);
    const removeForm = $("[data-cart-remove-form]", line);

    if (!input) return;

    let qty = sanitizeQty(input.value);

    // rupture -> on bloque
    if (stock <= 0) {
      syncLineUI(line);
      return;
    }

    if (btnMinus) qty = qty - 1;
    if (btnPlus) qty = qty + 1;

    qty = clamp(qty, 0, stock);
    input.value = String(qty);
    syncLineUI(line);

    // ✅ si on vient de passer à 0 via minus -> retirer réel
    if (btnMinus && qty <= 0 && removeForm) {
      // petit feedback
      if (controls) flash(controls);
      // soumission remove
      removeForm.submit();
    }

    // feedback si on tape la limite
    if (btnPlus && qty >= stock) {
      if (controls) flash(controls);
    }
  });

  // ============================================================
  // Input handlers: input / blur
  // ============================================================
  document.addEventListener("input", (e) => {
    const input = e.target.closest("[data-qty-input]");
    if (!input) return;

    const line = e.target.closest("[data-cart-line]");
    if (!line) return;

    // on ne soumet pas pendant la saisie, juste UI
    syncLineUI(line);
  });

  document.addEventListener("blur", (e) => {
    const input = e.target.closest("[data-qty-input]");
    if (!input) return;

    const line = e.target.closest("[data-cart-line]");
    if (!line) return;

    const stock = clamp(toInt(line.dataset.stock, 0), 0, 1_000_000);
    const removeForm = $("[data-cart-remove-form]", line);

    let qty = sanitizeQty(input.value);

    if (stock <= 0) {
      syncLineUI(line);
      return;
    }

    qty = clamp(qty, 0, stock);
    input.value = String(qty);
    syncLineUI(line);

    // ✅ si user a tapé 0 manuellement -> retirer
    if (qty <= 0 && removeForm) {
      removeForm.submit();
    }
  }, true);

  // ============================================================
  // Safety: empêcher submit update si qty==0 (retirer à la place)
  // ============================================================
  document.addEventListener("submit", (e) => {
    const form = e.target.closest("[data-cart-update-form]");
    if (!form) return;

    const line = form.closest("[data-cart-line]");
    if (!line) return;

    const input = $("[data-qty-input]", line);
    const removeForm = $("[data-cart-remove-form]", line);
    const stock = clamp(toInt(line.dataset.stock, 0), 0, 1_000_000);

    const qty = clamp(sanitizeQty(input?.value), 0, stock);

    if (stock <= 0 || qty <= 0) {
      e.preventDefault();
      e.stopPropagation();
      syncLineUI(line);

      if (removeForm) removeForm.submit();
    }
  }, true);
})();
