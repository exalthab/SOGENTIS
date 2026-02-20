// static/economic/ecommerce/js/product8_detail.js
(() => {
  "use strict";

  // ============================================================
  // HARD GUARD: empêche double exécution (cause principale du +2)
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
  // Quantity + stock rules
  // - + désactivé si qty >= stock
  // - - reste actif si qty > 1 (même si + est désactivé)
  // - Ajout/Payer désactivés si stock=0
  // ============================================================
  const buybox = $(".pd-buybox");
  const stock = clamp(toInt(buybox?.dataset.stock, 0), 0, 1_000_000);
  const out = stock <= 0;

  const qtyInput = $("#pdQtyInput");
  const qtyMinus = $("#pdQtyMinus");
  const qtyPlus = $("#pdQtyPlus");
  const qtyHidden = $("#pdQtyHidden");

  const addForm = $("#pdAddToCartForm");
  const addBtn = $("#pdAddToCartBtn");
  const buyNowBtn = $("#pdBuyNowBtn");

  const setDisabled = (el, v) => {
    if (!el) return;
    el.disabled = !!v;
    if (el.classList) el.classList.toggle("disabled", !!v);
    if (!!v) el.setAttribute("aria-disabled", "true");
    else el.removeAttribute("aria-disabled");
  };

  const readQty = () => {
    const raw = (qtyInput?.value ?? "1").toString().replace(/[^\d]/g, "");
    const n = toInt(raw || "1", 1);
    return n > 0 ? n : 1;
  };

  const writeQty = (n) => {
    if (qtyInput) qtyInput.value = String(n);
    if (qtyHidden) qtyHidden.value = String(n);
  };

  const syncUI = (qty) => {
    // qty est déjà clampé
    setDisabled(qtyMinus, qty <= 1);
    setDisabled(qtyPlus, out || qty >= stock);

    // désactiver achat/panier si stock=0
    setDisabled(addBtn, out);
    setDisabled(buyNowBtn, out);
  };

  const applyQty = (requestedQty) => {
    // si stock=0 => qty reste 1 (mais actions bloquées)
    const max = stock > 0 ? stock : 1;
    const qty = clamp(requestedQty, 1, max);
    writeQty(qty);
    syncUI(qty);
    return qty;
  };

  // init qty
  applyQty(readQty());

  // events (1 clic = 1 incrément)
  if (qtyMinus) {
    qtyMinus.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      applyQty(readQty() - 1);
    });
  }

  if (qtyPlus) {
    qtyPlus.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      // si déjà max, ne rien faire (et rester désactivé)
      const current = readQty();
      if (stock > 0 && current >= stock) {
        syncUI(current);
        return;
      }
      applyQty(current + 1);
    });
  }

  if (qtyInput) {
    qtyInput.addEventListener("input", () => {
      // nettoie pendant saisie + clamp
      applyQty(readQty());
    });
    qtyInput.addEventListener("blur", () => {
      applyQty(readQty());
    });
  }

  // sécurité serveur-côté: empêcher submit si stock=0
  if (addForm) {
    addForm.addEventListener("submit", (e) => {
      // force sync hidden qty avant submit
      const qty = applyQty(readQty());

      if (out || qty <= 0) {
        e.preventDefault();
        e.stopPropagation();
        return;
      }

      // anti double submit (spam click)
      if (addForm.dataset.submitting === "1") {
        e.preventDefault();
        e.stopPropagation();
        return;
      }
      addForm.dataset.submitting = "1";
      setTimeout(() => {
        // relâche après court délai (si réponse lente)
        addForm.dataset.submitting = "0";
      }, 1200);
    });
  }

  // ============================================================
  // Share links (WhatsApp / Facebook / X / Telegram + Copy)
  // ============================================================
  (() => {
    const productUrl = (buybox?.dataset.productUrl || window.location.href).trim();
    const productName = (buybox?.dataset.productName || document.title || "Produit").trim();

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

  // ============================================================
  // NOTE: "J'aime" doit être actif => on ne touche pas pdLikeBtn.
  // ============================================================
})();










// /* static/economic/ecommerce/js/product_detail.js */
// /* ---------------------------------------------------------
//    Product detail interactions (no deps):
//    - Gallery thumbs -> main image + zoom href
//    - Quantity +/- with stock max + sync hidden input
//    - Buy now => submit add-to-cart form (redirect via next)
//    - Share links + copy link
//    - Delivery modal (simple SN zones estimation)
// --------------------------------------------------------- */

// (function () {
//   "use strict";

//   const $ = (sel, root = document) => root.querySelector(sel);
//   const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

//   function clampInt(val, min, max) {
//     const n = parseInt(String(val ?? ""), 10);
//     if (!Number.isFinite(n)) return min;
//     return Math.min(Math.max(n, min), max);
//   }

//   function safeText(el, txt) {
//     if (el) el.textContent = txt;
//   }

//   function buildShareUrls({ url, text }) {
//     const u = encodeURIComponent(url);
//     const t = encodeURIComponent(text);

//     return {
//       whatsapp: `https://wa.me/?text=${t}%20${u}`,
//       facebook: `https://www.facebook.com/sharer/sharer.php?u=${u}`,
//       x: `https://twitter.com/intent/tweet?text=${t}&url=${u}`,
//       telegram: `https://t.me/share/url?url=${u}&text=${t}`,
//     };
//   }

//   async function copyToClipboard(text) {
//     try {
//       if (navigator.clipboard && window.isSecureContext) {
//         await navigator.clipboard.writeText(text);
//         return true;
//       }
//     } catch (e) {}
//     try {
//       const ta = document.createElement("textarea");
//       ta.value = text;
//       ta.setAttribute("readonly", "");
//       ta.style.position = "fixed";
//       ta.style.top = "-9999px";
//       document.body.appendChild(ta);
//       ta.select();
//       document.execCommand("copy");
//       document.body.removeChild(ta);
//       return true;
//     } catch (e) {
//       return false;
//     }
//   }

//   document.addEventListener("DOMContentLoaded", () => {
//     // ---------------------------
//     // Elements
//     // ---------------------------
//     const buybox = $(".pd-buybox");
//     const mainImg = $("#pdMainImage");
//     const zoomLink = $(".pd-zoom");
//     const thumbs = $$(".pd-thumb-btn");

//     const qtyMinus = $("#pdQtyMinus");
//     const qtyPlus = $("#pdQtyPlus");
//     const qtyInput = $("#pdQtyInput");
//     const qtyHidden = $("#pdQtyHidden");
//     const qtyMaxText = $("#pdQtyMaxText");

//     const addForm = $("#pdAddToCartForm");
//     const buyNowBtn = $("#pdBuyNowBtn");

//     const shareWhatsApp = $("#pdShareWhatsApp");
//     const shareFacebook = $("#pdShareFacebook");
//     const shareX = $("#pdShareX");
//     const shareTelegram = $("#pdShareTelegram");
//     const copyLinkBtn = $("#pdCopyLink");

//     // Delivery modal elements
//     const zoneSelect = $("#pdZoneSelect");
//     const pdDist = $("#pdDist");
//     const pdEta = $("#pdEta");
//     const pdEtaWindow = $("#pdEtaWindow");
//     const pdDeliverySummary = $("#pdDeliverySummary");

//     // ---------------------------
//     // Basic data
//     // ---------------------------
//     const stock = clampInt(buybox?.dataset.stock ?? 0, 0, 999999);
//     const productName = (buybox?.dataset.productName || "").trim() || document.title;
//     const productUrl =
//       (buybox?.dataset.productUrl || "").trim() || window.location.href;

//     // ---------------------------
//     // Gallery thumbs
//     // ---------------------------
//     function setMain(src) {
//       if (!src) return;
//       if (mainImg) mainImg.src = src;
//       if (zoomLink) zoomLink.href = src;
//     }

//     thumbs.forEach((btn) => {
//       btn.addEventListener("click", () => {
//         thumbs.forEach((b) => b.classList.remove("is-active"));
//         btn.classList.add("is-active");
//         const src = btn.getAttribute("data-src");
//         setMain(src);
//       });
//     });

//     // Ensure zoom href aligned
//     if (mainImg && zoomLink && !zoomLink.getAttribute("href")) {
//       zoomLink.href = mainImg.src;
//     }

//     // ---------------------------
//     // Quantity logic
//     // ---------------------------
//     const maxQty = stock > 0 ? stock : 1;

//     function syncQty(value) {
//       const v = clampInt(value ?? qtyInput?.value ?? 1, 1, maxQty);
//       if (qtyInput) qtyInput.value = String(v);
//       if (qtyHidden) qtyHidden.value = String(v);
//       if (qtyMaxText) qtyMaxText.textContent = String(stock || 0);

//       // Disable +/- when needed
//       if (qtyMinus) qtyMinus.disabled = v <= 1;
//       if (qtyPlus) qtyPlus.disabled = v >= maxQty;

//       // Disable buy/add when OOS
//       const isOOS = stock <= 0;
//       if (buyNowBtn) buyNowBtn.disabled = isOOS;
//       const addBtn = $("#pdAddToCartBtn");
//       if (addBtn) addBtn.disabled = isOOS;
//     }

//     syncQty(1);

//     qtyMinus?.addEventListener("click", () => {
//       syncQty((parseInt(qtyInput?.value || "1", 10) || 1) - 1);
//     });

//     qtyPlus?.addEventListener("click", () => {
//       syncQty((parseInt(qtyInput?.value || "1", 10) || 1) + 1);
//     });

//     qtyInput?.addEventListener("input", () => syncQty(qtyInput.value));
//     qtyInput?.addEventListener("blur", () => syncQty(qtyInput.value));

//     // Prevent non-numeric typing (soft)
//     qtyInput?.addEventListener("keypress", (e) => {
//       const ch = e.key;
//       if (!/[0-9]/.test(ch)) e.preventDefault();
//     });

//     // ---------------------------
//     // Buy now behavior
//     // (type="button" => needs JS)
//     // Strategy:
//     // - submit add-to-cart form
//     // - set next to cart_url if provided by dataset, else keep current next
//     // ---------------------------
//     buyNowBtn?.addEventListener("click", () => {
//       if (!addForm) return;
//       if (stock <= 0) return;

//       syncQty(qtyInput?.value || 1);

//       // set next to cart if provided
//       const cartUrl = addForm.dataset.cartUrl;
//       if (cartUrl) {
//         const next = addForm.querySelector('input[name="next"]');
//         if (next) next.value = cartUrl;
//       }

//       addForm.submit();
//     });

//     // ---------------------------
//     // Share links + copy link
//     // ---------------------------
//     const share = buildShareUrls({
//       url: productUrl,
//       text: productName,
//     });

//     if (shareWhatsApp) shareWhatsApp.href = share.whatsapp;
//     if (shareFacebook) shareFacebook.href = share.facebook;
//     if (shareX) shareX.href = share.x;
//     if (shareTelegram) shareTelegram.href = share.telegram;

//     copyLinkBtn?.addEventListener("click", async () => {
//       const ok = await copyToClipboard(productUrl);
//       if (!ok) return;
//       copyLinkBtn.textContent = "✅ Lien copié";
//       setTimeout(() => {
//         copyLinkBtn.textContent = "🔗 Copier le lien";
//       }, 1400);
//     });

//     // ---------------------------
//     // Delivery modal estimation (simple model)
//     // ---------------------------
//     const ZONES = {
//       dakar: { dist: 8, eta: 30, win: "Aujourd’hui / Demain" },
//       pikine: { dist: 18, eta: 60, win: "Demain" },
//       rufisque: { dist: 35, eta: 110, win: "1–2 jours" },
//       thies: { dist: 70, eta: 180, win: "1–2 jours" },
//       mbour: { dist: 95, eta: 240, win: "2–3 jours" },
//       saint_louis: { dist: 265, eta: 420, win: "2–4 jours" },
//       touba: { dist: 195, eta: 360, win: "2–3 jours" },
//       kaolack: { dist: 190, eta: 360, win: "2–3 jours" },
//       ziguinchor: { dist: 455, eta: 720, win: "3–5 jours" },
//     };

//     function fmtEta(mins) {
//       if (!mins || mins <= 0) return "—";
//       if (mins < 60) return `${mins} min`;
//       const h = Math.round(mins / 60);
//       return `${h} h`;
//     }

//     function updateDelivery(zoneKey) {
//       const z = ZONES[zoneKey];
//       if (!z) {
//         safeText(pdDist, "—");
//         safeText(pdEta, "—");
//         safeText(pdEtaWindow, "—");
//         safeText(pdDeliverySummary, "Selon zone");
//         return;
//       }
//       safeText(pdDist, `${z.dist} km`);
//       safeText(pdEta, fmtEta(z.eta));
//       safeText(pdEtaWindow, z.win);
//       safeText(pdDeliverySummary, z.win);
//     }

//     zoneSelect?.addEventListener("change", () => {
//       updateDelivery(zoneSelect.value);
//     });

//     // When modal opens, reset summary if needed
//     updateDelivery(zoneSelect?.value || "");
//   });
// })();
