// static/economic/ecommerce/js/product_detail.js
(() => {
  "use strict";

  // ============================================================
  // HARD GUARD: empêche double exécution
  // ============================================================
  const INIT_KEY = "sogentisProductDetailInit";
  if (document.documentElement.dataset[INIT_KEY] === "1") return;
  document.documentElement.dataset[INIT_KEY] = "1";

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

    // Button / input
    if ("disabled" in el) {
      el.disabled = disabled;
      if (el.classList) el.classList.toggle("disabled", disabled);
      if (disabled) el.setAttribute("aria-disabled", "true");
      else el.removeAttribute("aria-disabled");
      return;
    }

    // <a>
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

  const flashQty = (kind = "warn") => {
    const wrap = $(".pd-qty");
    if (!wrap) return;
    wrap.classList.remove("pd-qty--warn", "pd-qty--ok");
    wrap.classList.add(kind === "ok" ? "pd-qty--ok" : "pd-qty--warn");
    window.setTimeout(() => wrap.classList.remove("pd-qty--warn", "pd-qty--ok"), 350);
  };

  // ============================================================
  // Gallery (thumbs)
  // ============================================================
  (() => {
    const mainImg = $("#pdMainImage");
    if (!mainImg) return;

    const zoom = $(".pd-zoom");
    const thumbs = $$(".pd-thumb-btn[data-src]");

    thumbs.forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const src = btn.getAttribute("data-src");
        if (!src) return;

        mainImg.src = src;

        thumbs.forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");

        if (zoom) zoom.href = src;
      });
    });
  })();

  // ============================================================
  // Quantity + stock + sync BuyNow URL
  // ============================================================
  const buybox = $(".pd-buybox");
  if (!buybox) return;

  // Stock "vivant" : on le garde en variable, mais on peut le changer via setStock()
  let stock = clamp(toInt(buybox.dataset.stock, 0), 0, 1_000_000);

  const qtyInput = $("#pdQtyInput");
  const qtyMinus = $("#pdQtyMinus");
  const qtyPlus = $("#pdQtyPlus");
  const qtyHidden = $("#pdQtyHidden");

  const qtyMaxText = $("#pdQtyMaxText");

  const addForm = $("#pdAddToCartForm");
  const addBtn = $("#pdAddToCartBtn");

  const buyNowBtn = $("#pdBuyNowBtn"); // <a>
  const buyNowForm = $("#pdBuyNowForm"); // optionnel

  const buyNowBaseHref =
    buyNowBtn?.tagName === "A" ? (buyNowBtn.getAttribute("href") || "") : "";

  const isOut = () => stock <= 0;

  const readQty = () => {
    const raw = (qtyInput?.value ?? "1").toString().replace(/[^\d]/g, "");
    const n = toInt(raw || "1", 1);
    return n >= 0 ? n : 0;
  };

  const writeQty = (n) => {
    if (qtyInput) qtyInput.value = String(n);
    if (qtyHidden) qtyHidden.value = String(n);

    const buyHidden = $("#pdQtyHiddenBuyNow");
    if (buyHidden) buyHidden.value = String(n);
  };

  const setMaxText = () => {
    if (qtyMaxText) qtyMaxText.textContent = String(Math.max(0, stock));
    const wrap = $(".pd-qty");
    if (wrap) wrap.dataset.max = String(Math.max(0, stock));
  };

  const syncBuyNowHref = (qty) => {
    if (!buyNowBtn || buyNowBtn.tagName !== "A") return;

    const baseHref = buyNowBaseHref || buyNowBtn.getAttribute("href") || "";
    if (!baseHref) return;

    const u = new URL(baseHref, window.location.origin);

    u.searchParams.set("buy_now", "1");
    u.searchParams.set("qty", String(qty));

    const pid =
      (buybox.dataset.productId || "").trim() ||
      u.searchParams.get("product_id") ||
      "";

    if (pid) u.searchParams.set("product_id", pid);

    const checkout = (buybox.dataset.checkoutUrl || "").trim();
    if (checkout) u.pathname = checkout;

    buyNowBtn.setAttribute("href", u.pathname + "?" + u.searchParams.toString());
  };

  const syncUI = (qty) => {
    // “+” se désactive si stock=0 OU qty>=stock
    setDisabled(qtyPlus, isOut() || (stock > 0 && qty >= stock));

    // “−” : on autorise de descendre à 0 (retirer). Donc désactivé seulement si qty<=0
    setDisabled(qtyMinus, qty <= 0);

    // actions bloquées si out of stock OU qty==0
    const blockActions = isOut() || qty <= 0;
    setDisabled(addBtn, blockActions);
    setDisabled(buyNowBtn, blockActions);

    // si stock existe et qty > stock (cas changement stock), on corrige visuellement
    if (stock > 0 && qty > stock) flashQty("warn");
  };

  const applyQty = (requestedQty, reason = "") => {
    // ✅ règle: si stock=0 => qty doit rester 0 (car on ne peut pas acheter)
    if (isOut()) {
      writeQty(0);
      setMaxText();
      syncUI(0);
      syncBuyNowHref(0);
      return 0;
    }

    // ✅ règle: qty peut être 0 (retirer), sinon 1..stock
    const qty = clamp(requestedQty, 0, stock);

    writeQty(qty);
    setMaxText();
    syncUI(qty);

    // buyNow ne doit pas générer qty=0 (sinon checkout inutile)
    if (qty > 0) syncBuyNowHref(qty);

    // feedback léger
    if (reason === "minus_to_zero") flashQty("warn");
    return qty;
  };

  // API interne: si ton UI met à jour data-stock dynamiquement, appelle setStock(newStock)
  const setStock = (newStock) => {
    stock = clamp(toInt(newStock, 0), 0, 1_000_000);
    buybox.dataset.stock = String(stock);

    const currentQty = readQty();
    // si stock devient 0 => qty=0 et actions off
    if (stock <= 0) {
      applyQty(0, "stock_zero");
    } else {
      // si qty > stock => on rabaisse
      applyQty(Math.min(currentQty, stock), "stock_update");
    }
  };

  // expose optionnel pour debug (sans polluer global)
  buybox._setStock = setStock;

  // init qty: si stock=0 => qty=0, sinon on force à 1
  if (isOut()) applyQty(0, "init_out");
  else applyQty(Math.max(1, readQty()), "init");

  if (qtyMinus) {
    qtyMinus.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();

      const q = readQty();
      const next = q - 1;

      // ✅ si on arrive à 0 => "retire l'article" (sur page produit = qty=0 + boutons disabled)
      if (next <= 0) {
        applyQty(0, "minus_to_zero");
        return;
      }

      applyQty(next, "minus");
    });
  }

  if (qtyPlus) {
    qtyPlus.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();

      // si stock=0 => pas d’augmentation
      if (isOut()) {
        applyQty(0, "stock_zero");
        return;
      }

      const current = readQty();
      if (current >= stock) {
        syncUI(current);
        flashQty("warn");
        return;
      }

      applyQty(current + 1, "plus");
    });
  }

  if (qtyInput) {
    qtyInput.addEventListener("input", () => {
      const v = readQty();
      // autoriser 0..stock
      applyQty(v, "input");
    });
    qtyInput.addEventListener("blur", () => {
      const v = readQty();
      // si stock>0 et user laisse vide/0 involontaire => on garde 0 (retirer) par design
      applyQty(v, "blur");
    });
  }

  // Empêcher click BuyNow si disabled (cas <a>)
  if (buyNowBtn && buyNowBtn.tagName === "A") {
    buyNowBtn.addEventListener("click", (e) => {
      const qty = readQty();
      const blocked =
        isOut() ||
        qty <= 0 ||
        buyNowBtn.classList.contains("disabled") ||
        buyNowBtn.getAttribute("aria-disabled") === "true";

      if (blocked) {
        e.preventDefault();
        e.stopPropagation();
      }
    });
  }

  // Submit add-to-cart: empêcher qty=0 + anti double submit
  if (addForm) {
    addForm.addEventListener("submit", (e) => {
      const qty = readQty();

      // ✅ si qty=0 => "retirer l'article" => on ne poste pas
      if (isOut() || qty <= 0) {
        e.preventDefault();
        e.stopPropagation();
        flashQty("warn");
        return;
      }

      // sécuriser qty <= stock
      applyQty(qty, "submit_add");

      if (addForm.dataset.submitting === "1") {
        e.preventDefault();
        e.stopPropagation();
        return;
      }
      addForm.dataset.submitting = "1";
      setTimeout(() => (addForm.dataset.submitting = "0"), 1200);
    });
  }

  if (buyNowForm) {
    buyNowForm.addEventListener("submit", (e) => {
      const qty = readQty();
      if (isOut() || qty <= 0) {
        e.preventDefault();
        e.stopPropagation();
        flashQty("warn");
        return;
      }
      applyQty(qty, "submit_buynow");

      if (buyNowForm.dataset.submitting === "1") {
        e.preventDefault();
        e.stopPropagation();
        return;
      }
      buyNowForm.dataset.submitting = "1";
      setTimeout(() => (buyNowForm.dataset.submitting = "0"), 1200);
    });
  }

  // ============================================================
  // Share links (WhatsApp / Facebook / X / Telegram + Copy)
  // ============================================================
  (() => {
    const productUrl = (buybox.dataset.productUrl || window.location.href).trim();
    const productName = (buybox.dataset.productName || document.title || "Produit").trim();

    const wa = $("#pdShareWhatsApp");
    const fb = $("#pdShareFacebook");
    const x = $("#pdShareX");
    const tg = $("#pdShareTelegram");
    const copyBtn = $("#pdCopyLink");

    const encUrl = encodeURIComponent(productUrl);
    const shareText = `${productName} - ${productUrl}`;
    const encText = encodeURIComponent(shareText);

    if (wa) wa.href = `https://wa.me/?text=${encText}`;
    if (fb) fb.href = `https://www.facebook.com/sharer/sharer.php?u=${encUrl}`;
    if (x) x.href = `https://twitter.com/intent/tweet?text=${encText}`;
    if (tg) tg.href = `https://t.me/share/url?url=${encUrl}&text=${encodeURIComponent(productName)}`;

    if (copyBtn) {
      const original = copyBtn.textContent;
      copyBtn.addEventListener("click", async (e) => {
        e.preventDefault();
        try {
          await navigator.clipboard.writeText(productUrl);
          copyBtn.textContent = "✅ Lien copié";
          setTimeout(() => (copyBtn.textContent = original || "🔗 Copier le lien"), 1200);
        } catch (_err) {
          const ta = document.createElement("textarea");
          ta.value = productUrl;
          document.body.appendChild(ta);
          ta.select();
          document.execCommand("copy");
          document.body.removeChild(ta);
          copyBtn.textContent = "✅ Lien copié";
          setTimeout(() => (copyBtn.textContent = original || "🔗 Copier le lien"), 1200);
        }
      });
    }
  })();

  // ============================================================
  // Delivery zone estimation (offline)
  // ============================================================
  (() => {
    const zoneSelect = $("#pdZoneSelect");
    const distEl = $("#pdDist");
    const etaEl = $("#pdEta");
    const etaWinEl = $("#pdEtaWindow");
    const summaryEl = $("#pdDeliverySummary");
    if (!zoneSelect && !summaryEl) return;

    const zones = {
      dakar: { name: "Dakar", km: 8, mode: "city" },
      pikine: { name: "Pikine / Guédiawaye", km: 18, mode: "city" },
      rufisque: { name: "Rufisque", km: 35, mode: "city" },
      thies: { name: "Thiès", km: 70, mode: "road" },
      mbour: { name: "Mbour / Saly", km: 95, mode: "road" },
      saint_louis: { name: "Saint-Louis", km: 260, mode: "road" },
      touba: { name: "Touba", km: 190, mode: "road" },
      kaolack: { name: "Kaolack", km: 200, mode: "road" },
      ziguinchor: { name: "Ziguinchor", km: 450, mode: "road" },
    };

    const fmt = (hours) => {
      const h = Math.floor(hours);
      const m = Math.round((hours - h) * 60);
      if (h <= 0) return `${m} min`;
      if (m <= 0) return `${h} h`;
      return `${h} h ${m} min`;
    };

    const estimate = (km, mode) => {
      const speed = mode === "city" ? 25 : 60;
      const base = km / speed;

      const prep = mode === "city" ? 0.5 : 1.2;
      const low = base + prep;
      const high = low + (mode === "city" ? 0.8 : 1.8);

      let windowTxt = "24–48h";
      if (km <= 40) windowTxt = "Aujourd’hui / 24h";
      else if (km <= 120) windowTxt = "24–48h";
      else windowTxt = "2–4 jours";

      return { low, high, windowTxt };
    };

    const renderEmpty = () => {
      if (distEl) distEl.textContent = "—";
      if (etaEl) etaEl.textContent = "—";
      if (etaWinEl) etaWinEl.textContent = "—";
      if (summaryEl) summaryEl.textContent = "Selon zone";
    };

    const update = (key) => {
      const z = zones[key];
      if (!z) return renderEmpty();

      const { low, high, windowTxt } = estimate(z.km, z.mode);

      if (distEl) distEl.textContent = `${z.km} km`;
      if (etaEl) etaEl.textContent = `${fmt(low)} – ${fmt(high)}`;
      if (etaWinEl) etaWinEl.textContent = windowTxt;
      if (summaryEl) summaryEl.textContent = `${z.name} · ${windowTxt}`;
    };

    if (zoneSelect) {
      zoneSelect.addEventListener("change", () => update(zoneSelect.value));
      update(zoneSelect.value);
    } else {
      renderEmpty();
    }
  })();
})();
