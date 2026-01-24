/* ==========================================================
   Cookie Consent (vanilla JS)
   - Accept all / Reject all / Save preferences
   - Stores JSON consent in cookie "cookie_consent"
   - Shows banner only if consent not set
   ========================================================== */

(function () {
  "use strict";

  const COOKIE_NAME = "cookie_consent";
  const COOKIE_MAX_DAYS = 180; // ajustable
  const CONSENT_VERSION = 1;

  const els = {
    banner: document.querySelector("[data-cookie-banner]"),
    modal: document.querySelector("[data-cookie-modal='dialog']"),
    backdrop: document.querySelector("[data-cookie-modal='backdrop']"),
    toggles: document.querySelectorAll("[data-cookie-toggle]"),
  };

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${encodeURIComponent(name)}=`);
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(";").shift());
    return null;
  }

  function setCookie(name, value, days) {
    const maxAge = days * 24 * 60 * 60;
    document.cookie =
      `${encodeURIComponent(name)}=${encodeURIComponent(value)}; ` +
      `path=/; max-age=${maxAge}; samesite=lax`;
  }

  function parseConsent() {
    const raw = getCookie(COOKIE_NAME);
    if (!raw) return null;
    try {
      const obj = JSON.parse(raw);
      if (!obj || typeof obj !== "object") return null;
      return obj;
    } catch {
      return null;
    }
  }

  function buildConsent({ preferences, analytics, marketing }) {
    return {
      v: CONSENT_VERSION,
      necessary: true,
      preferences: !!preferences,
      analytics: !!analytics,
      marketing: !!marketing,
      updated: new Date().toISOString(),
    };
  }

  function applyConsent(consent) {
    // Ici, tu peux déclencher le chargement conditionnel des scripts
    // Exemple : scripts marqués data-cookie-category="analytics"
    const categories = ["preferences", "analytics", "marketing"];

    categories.forEach((cat) => {
      const allowed = !!consent?.[cat];
      document.querySelectorAll(`script[data-cookie-category="${cat}"][data-cookie-src]`).forEach((s) => {
        if (allowed && !s.dataset.loaded) {
          const realSrc = s.dataset.cookieSrc;
          const newScript = document.createElement("script");
          newScript.src = realSrc;
          newScript.async = true;
          s.dataset.loaded = "1";
          s.parentNode.insertBefore(newScript, s.nextSibling);
        }
      });
    });
  }

  function showBannerIfNeeded() {
    if (!els.banner) return;
    const consent = parseConsent();
    if (!consent) {
      els.banner.hidden = false;
    } else {
      els.banner.hidden = true;
      applyConsent(consent);
    }
  }

  function openModal() {
    if (!els.modal || !els.backdrop) return;
    // sync toggles from cookie
    const consent = parseConsent();
    const prefs = consent ? consent.preferences : false;
    const analytics = consent ? consent.analytics : false;
    const marketing = consent ? consent.marketing : false;

    document.querySelector("[data-cookie-toggle='preferences']")?.toggleAttribute("checked", prefs);
    document.querySelector("[data-cookie-toggle='analytics']")?.toggleAttribute("checked", analytics);
    document.querySelector("[data-cookie-toggle='marketing']")?.toggleAttribute("checked", marketing);

    els.backdrop.hidden = false;
    els.modal.hidden = false;

    // focus first actionable element
    const closeBtn = els.modal.querySelector("[data-cookie-close='modal']");
    closeBtn && closeBtn.focus();
  }

  function closeModal() {
    if (!els.modal || !els.backdrop) return;
    els.modal.hidden = true;
    els.backdrop.hidden = true;
  }

  function saveConsent(consent) {
    setCookie(COOKIE_NAME, JSON.stringify(consent), COOKIE_MAX_DAYS);
    if (els.banner) els.banner.hidden = true;
    closeModal();
    applyConsent(consent);
  }

  function acceptAll() {
    saveConsent(buildConsent({ preferences: true, analytics: true, marketing: true }));
  }

  function rejectAll() {
    saveConsent(buildConsent({ preferences: false, analytics: false, marketing: false }));
  }

  function savePreferencesFromUI() {
    const preferences = !!document.querySelector("[data-cookie-toggle='preferences']")?.checked;
    const analytics = !!document.querySelector("[data-cookie-toggle='analytics']")?.checked;
    const marketing = !!document.querySelector("[data-cookie-toggle='marketing']")?.checked;
    saveConsent(buildConsent({ preferences, analytics, marketing }));
  }

  // Click handlers (banner + page + modal)
  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-cookie-action],[data-cookie-open],[data-cookie-close]");
    if (!t) return;

    const action = t.getAttribute("data-cookie-action");
    const open = t.getAttribute("data-cookie-open");
    const close = t.getAttribute("data-cookie-close");

    if (open === "preferences") {
      e.preventDefault();
      openModal();
      return;
    }
    if (close === "modal") {
      e.preventDefault();
      closeModal();
      return;
    }

    if (action === "accept_all") {
      e.preventDefault();
      acceptAll();
      return;
    }
    if (action === "reject_all") {
      e.preventDefault();
      rejectAll();
      return;
    }
    if (action === "save_preferences") {
      e.preventDefault();
      savePreferencesFromUI();
      return;
    }
  });

  // close modal on backdrop
  els.backdrop?.addEventListener("click", closeModal);

  // ESC to close
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });

  // Init
  showBannerIfNeeded();
})();
