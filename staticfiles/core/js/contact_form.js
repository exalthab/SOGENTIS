// static/core/js/contact_form.js
(() => {
  const form = document.querySelector(".contact-form");
  if (!form) return;

  const card = form.closest(".contact-card");
  const btn = document.getElementById("contactSubmit");
  const captchaWrap = form.querySelector(".captcha-wrap");
  const captchaHint = form.querySelector(".captcha-hint");

  let isSubmitting = false;

  // Messages i18n pour le captcha (depuis les data-attributes)
  const captchaErrorMsg = captchaWrap?.dataset.hcaptchaErrorMsg || "Veuillez compléter le captcha avant d’envoyer.";
  const captchaLoadErrorMsg = captchaWrap?.dataset.hcaptchaLoadErrorMsg || "Le captcha n’a pas pu se charger. Désactivez un bloqueur puis rechargez la page.";

  const setLoading = (loading) => {
    if (btn) {
      btn.disabled = loading;
      btn.classList.toggle("is-loading", loading);
      if (loading) btn.setAttribute("aria-busy", "true");
      else btn.removeAttribute("aria-busy");
    }
    if (card) card.classList.toggle("is-submitting", loading);
  };

  const setCaptchaHint = (msg, isError = false) => {
    if (!captchaHint) return;
    if (captchaWrap) captchaWrap.classList.toggle("is-error", isError);

    captchaHint.textContent = msg;
    captchaHint.setAttribute("role", "alert");
    captchaHint.setAttribute("aria-live", "polite");
  };

  const resetCaptchaHint = () => {
    if (!captchaHint) return;
    if (captchaWrap) captchaWrap.classList.remove("is-error");
    captchaHint.textContent = captchaErrorMsg;
  };

  const getHCaptchaValue = () => {
    const el = form.querySelector(
      'textarea[name="h-captcha-response"], input[name="h-captcha-response"]'
    );
    return (el && el.value ? el.value.trim() : "");
  };

  const scrollToWidget = () => {
    const widgetHost = form.querySelector(".h-captcha");
    if (widgetHost) widgetHost.scrollIntoView({ behavior: "smooth", block: "center" });
  };

  form.addEventListener("submit", (e) => {
    if (isSubmitting) {
      e.preventDefault();
      return;
    }

    setLoading(true);

    const widgetHost = form.querySelector(".h-captcha");

    // Pas de captcha => submit normal
    if (!widgetHost) {
      isSubmitting = true;
      return;
    }

    // hCaptcha non chargé
    if (typeof window.hcaptcha === "undefined") {
      e.preventDefault();
      setCaptchaHint(captchaLoadErrorMsg, true);
      setLoading(false);
      isSubmitting = false;
      scrollToWidget();
      widgetHost.querySelector("iframe")?.focus();
      return;
    }

    const token = getHCaptchaValue();
    if (!token) {
      e.preventDefault();
      setCaptchaHint(captchaErrorMsg, true);
      setLoading(false);
      isSubmitting = false;
      scrollToWidget();
      widgetHost.querySelector("iframe")?.focus();
      return;
    }

    // OK
    resetCaptchaHint();
    isSubmitting = true;
  });

  // Observer pour reset l'erreur quand l'utilisateur complète le captcha
  const tokenObserver = () => {
    if (!captchaWrap) return;
    const token = getHCaptchaValue();
    if (token) captchaWrap.classList.remove("is-error");
  };

  form.addEventListener("input", tokenObserver);
  form.addEventListener("change", tokenObserver);
})();





// // static/core/js/contact_form.js
// (() => {
//   "use strict";

//   // =========================================================
//   //  SELECTEURS / CONTEXTE
//   // =========================================================
//   const form = document.querySelector(".contact-form");
//   if (!form) return;

//   const card = form.closest(".contact-card");
//   const btn = document.getElementById("contactSubmit");

//   // Captcha wrapper + hint (optionnels)
//   const captchaWrap = form.querySelector(".captcha-wrap");
//   const captchaHint = form.querySelector(".captcha-hint");
//   const widgetHost = form.querySelector(".h-captcha");

//   // =========================================================
//   //  TEXTES (tu peux override via data-attrs si tu veux)
//   //  ex: <form ... data-captcha-required="..." data-captcha-blocked="...">
//   // =========================================================
//   const TXT = {
//     captchaRequired:
//       form.dataset.captchaRequired ||
//       "Veuillez compléter le captcha avant d’envoyer.",
//     captchaBlocked:
//       form.dataset.captchaBlocked ||
//       "Le captcha n’a pas pu se charger. Désactivez un bloqueur (adblock) puis rechargez la page.",
//   };

//   // =========================================================
//   //  ETAT
//   // =========================================================
//   let isSubmitting = false;

//   // =========================================================
//   //  HELPERS UI
//   // =========================================================
//   const setLoading = (loading) => {
//     // Bouton
//     if (btn) {
//       btn.disabled = !!loading;
//       btn.classList.toggle("is-loading", !!loading);
//       if (loading) btn.setAttribute("aria-busy", "true");
//       else btn.removeAttribute("aria-busy");
//     }

//     // Barre de progression (via CSS .contact-card.is-submitting)
//     if (card) card.classList.toggle("is-submitting", !!loading);
//   };

//   const setCaptchaHint = (msg, isError = false) => {
//     if (!captchaHint) return;
//     if (captchaWrap) captchaWrap.classList.toggle("is-error", !!isError);
//     captchaHint.textContent = msg || "";
//   };

//   const resetCaptchaHint = () => {
//     if (!captchaHint) return;
//     if (captchaWrap) captchaWrap.classList.remove("is-error");
//     captchaHint.textContent = TXT.captchaRequired;
//   };

//   const scrollToCaptcha = () => {
//     if (!widgetHost) return;
//     try {
//       widgetHost.scrollIntoView({ behavior: "smooth", block: "center" });
//     } catch (e) {
//       // fallback silencieux
//     }
//   };

//   // =========================================================
//   //  hCAPTCHA TOKEN
//   // =========================================================
//   const getHCaptchaTokenFromField = () => {
//     // hCaptcha injecte souvent un textarea hidden nommé h-captcha-response
//     const el = form.querySelector(
//       'textarea[name="h-captcha-response"], input[name="h-captcha-response"]'
//     );
//     return el && el.value ? el.value.trim() : "";
//   };

//   const getHCaptchaToken = () => {
//     // 1) Essaye le champ (marche pour auto-render)
//     const token = getHCaptchaTokenFromField();
//     if (token) return token;

//     // 2) Si rendu explicite: on peut parfois avoir un widget id
//     //    (si tu le stockes toi-même: widgetHost.dataset.widgetId = "123")
//     //    sinon on tente getResponse() global
//     if (typeof window.hcaptcha !== "undefined") {
//       try {
//         const wid = widgetHost?.dataset?.widgetId;
//         if (wid) {
//           const t = window.hcaptcha.getResponse(wid);
//           if (t) return String(t).trim();
//         }
//         // fallback global
//         const t2 = window.hcaptcha.getResponse();
//         if (t2) return String(t2).trim();
//       } catch (e) {
//         // ignore
//       }
//     }

//     return "";
//   };

//   // =========================================================
//   //  SUBMIT HANDLER
//   // =========================================================
//   form.addEventListener("submit", (e) => {
//     // --------------------------
//     // Anti double-submit
//     // --------------------------
//     if (isSubmitting) {
//       e.preventDefault();
//       return;
//     }

//     // Active l’état loading (progress + bouton)
//     setLoading(true);

//     // --------------------------
//     // Si pas de captcha sur la page => submit normal
//     // --------------------------
//     if (!widgetHost) {
//       isSubmitting = true;
//       return;
//     }

//     // --------------------------
//     // Script hCaptcha absent (adblock / CSP / offline)
//     // --------------------------
//     if (typeof window.hcaptcha === "undefined") {
//       e.preventDefault();
//       setCaptchaHint(TXT.captchaBlocked, true);
//       setLoading(false);
//       isSubmitting = false;
//       scrollToCaptcha();
//       return;
//     }

//     // --------------------------
//     // Token absent => on bloque
//     // --------------------------
//     const token = getHCaptchaToken();
//     if (!token) {
//       e.preventDefault();
//       setCaptchaHint(TXT.captchaRequired, true);
//       setLoading(false);
//       isSubmitting = false;
//       scrollToCaptcha();
//       return;
//     }

//     // --------------------------
//     // OK => on laisse passer
//     // --------------------------
//     resetCaptchaHint();
//     isSubmitting = true;
//   });

//   // =========================================================
//   //  OBSERVATEUR TOKEN : enlève l'état d'erreur si token apparaît
//   // =========================================================
//   const tokenObserver = () => {
//     if (!captchaWrap || !widgetHost) return;
//     const token = getHCaptchaToken();
//     if (token) captchaWrap.classList.remove("is-error");
//   };

//   form.addEventListener("input", tokenObserver);
//   form.addEventListener("change", tokenObserver);

//   // =========================================================
//   //  RESET AU RETOUR NAVIGATEUR (bfcache)
//   //  évite bouton disabled/loader bloqué en revenant sur la page
//   // =========================================================
//   window.addEventListener("pageshow", () => {
//     isSubmitting = false;
//     setLoading(false);
//     resetCaptchaHint();
//   });
// })();






// // static/core/js/contact_form.js
// (() => {
//   const form = document.querySelector(".contact-form");
//   if (!form) return;

//   const card = form.closest(".contact-card");
//   const btn = document.getElementById("contactSubmit");
//   const captchaWrap = form.querySelector(".captcha-wrap");
//   const captchaHint = form.querySelector(".captcha-hint");

//   let isSubmitting = false;

//   const setLoading = (loading) => {
//     if (btn) {
//       btn.disabled = loading;
//       btn.classList.toggle("is-loading", loading);
//       if (loading) btn.setAttribute("aria-busy", "true");
//       else btn.removeAttribute("aria-busy");
//     }
//     if (card) card.classList.toggle("is-submitting", loading); // Progress bar
//   };

//   const setCaptchaHint = (msg, isError = false) => {
//     if (!captchaHint) return;
//     if (captchaWrap) captchaWrap.classList.toggle("is-error", isError);
//     captchaHint.textContent = msg;
//   };

//   const resetCaptchaHint = () => {
//     if (!captchaHint) return;
//     if (captchaWrap) captchaWrap.classList.remove("is-error");
//     captchaHint.textContent = "Veuillez compléter le captcha avant d’envoyer.";
//   };

//   const getHCaptchaValue = () => {
//     const el = form.querySelector(
//       'textarea[name="h-captcha-response"], input[name="h-captcha-response"]'
//     );
//     return (el && el.value ? el.value.trim() : "");
//   };

//   form.addEventListener("submit", (e) => {
//     // Anti double-submit
//     if (isSubmitting) {
//       e.preventDefault();
//       return;
//     }

//     setLoading(true);

//     const widgetHost = form.querySelector(".h-captcha");
//     if (!widgetHost) {
//       // Pas de captcha sur cette page => submit normal
//       isSubmitting = true;
//       return;
//     }

//     // Script hCaptcha non chargé
//     if (typeof window.hcaptcha === "undefined") {
//       e.preventDefault();
//       setCaptchaHint(
//         "Le captcha n’a pas pu se charger. Désactivez un bloqueur (adblock) puis rechargez la page.",
//         true
//       );
//       setLoading(false);
//       isSubmitting = false;
//       widgetHost.scrollIntoView({ behavior: "smooth", block: "center" });
//       return;
//     }

//     const token = getHCaptchaValue();
//     if (!token) {
//       e.preventDefault();
//       setCaptchaHint("Veuillez compléter le captcha avant d’envoyer.", true);
//       setLoading(false);
//       isSubmitting = false;
//       widgetHost.scrollIntoView({ behavior: "smooth", block: "center" });
//       return;
//     }

//     // OK
//     resetCaptchaHint();
//     isSubmitting = true;
//   });

//   // Si l’utilisateur corrige / recharge captcha, enlever l’état d’erreur quand un token apparaît
//   const tokenObserver = () => {
//     const widgetHost = form.querySelector(".h-captcha");
//     if (!widgetHost || !captchaWrap) return;

//     const token = getHCaptchaValue();
//     if (token) captchaWrap.classList.remove("is-error");
//   };

//   form.addEventListener("input", tokenObserver);
//   form.addEventListener("change", tokenObserver);
// })();










// // static/core/js/contact_form.js
// (() => {
//   const form = document.querySelector(".contact-form");
//   if (!form) return;

//   const btn = document.getElementById("contactSubmit");
//   const captchaWrap = form.querySelector(".captcha-wrap");
//   const captchaHint = form.querySelector(".captcha-hint");

//   let isSubmitting = false;

//   const setLoading = (loading) => {
//     if (!btn) return;
//     btn.disabled = loading;
//     btn.classList.toggle("is-loading", loading);
//     if (loading) btn.setAttribute("aria-busy", "true");
//     else btn.removeAttribute("aria-busy");
//   };

//   const setCaptchaHint = (msg, isError = false) => {
//     if (!captchaHint) return;
//     if (captchaWrap) captchaWrap.classList.toggle("is-error", isError);
//     captchaHint.textContent = msg;
//   };

//   const resetCaptchaHint = () => {
//     if (!captchaHint) return;
//     if (captchaWrap) captchaWrap.classList.remove("is-error");
//     // Texte par défaut (même que template)
//     captchaHint.textContent = "Veuillez compléter le captcha avant d’envoyer.";
//   };

//   const getHCaptchaValue = () => {
//     const el = form.querySelector(
//       'textarea[name="h-captcha-response"], input[name="h-captcha-response"]'
//     );
//     return (el && el.value ? el.value.trim() : "");
//   };

//   form.addEventListener("submit", (e) => {
//     // Anti double-submit
//     if (isSubmitting) {
//       e.preventDefault();
//       return;
//     }

//     setLoading(true);

//     const widgetHost = form.querySelector(".h-captcha");
//     if (!widgetHost) {
//       // Pas de captcha sur cette page => on laisse submit normal
//       isSubmitting = true;
//       return;
//     }

//     // Si le script hCaptcha n'a pas chargé
//     if (typeof window.hcaptcha === "undefined") {
//       e.preventDefault();
//       setCaptchaHint(
//         "Le captcha n’a pas pu se charger. Désactivez un bloqueur (adblock) puis rechargez la page.",
//         true
//       );
//       setLoading(false);
//       isSubmitting = false;
//       widgetHost.scrollIntoView({ behavior: "smooth", block: "center" });
//       return;
//     }

//     const token = getHCaptchaValue();
//     if (!token) {
//       e.preventDefault();
//       setCaptchaHint("Veuillez compléter le captcha avant d’envoyer.", true);
//       setLoading(false);
//       isSubmitting = false;
//       widgetHost.scrollIntoView({ behavior: "smooth", block: "center" });
//       return;
//     }

//     // OK
//     resetCaptchaHint();
//     isSubmitting = true;
//   });

//   // Si l’utilisateur corrige / recharge captcha, on enlève l’état d’erreur quand un token apparaît
//   const tokenObserver = () => {
//     const widgetHost = form.querySelector(".h-captcha");
//     if (!widgetHost || !captchaWrap) return;

//     const token = getHCaptchaValue();
//     if (token) captchaWrap.classList.remove("is-error");
//   };

//   form.addEventListener("input", tokenObserver);
//   form.addEventListener("change", tokenObserver);
// })();








// // static/core/js/contact_form.js
// (() => {
//   const form = document.querySelector(".contact-form");
//   if (!form) return;

//   const btn = document.getElementById("contactSubmit");
//   const captchaHint = form.querySelector(".captcha-hint");

//   const setLoading = (loading) => {
//     if (!btn) return;
//     btn.disabled = loading;
//     btn.classList.toggle("is-loading", loading);
//     if (loading) btn.setAttribute("aria-busy", "true");
//     else btn.removeAttribute("aria-busy");
//   };

//   const setCaptchaError = (msg) => {
//     if (!captchaHint) return;
//     captchaHint.style.color = "#b91c1c";
//     captchaHint.style.fontWeight = "700";
//     captchaHint.textContent = msg;
//   };

//   const getHCaptchaValue = () => {
//     const el = form.querySelector('textarea[name="h-captcha-response"], input[name="h-captcha-response"]');
//     return (el && el.value ? el.value.trim() : "");
//   };

//   form.addEventListener("submit", (e) => {
//     setLoading(true);

//     const widgetHost = form.querySelector(".h-captcha");
//     if (!widgetHost) return; // pas de captcha sur cette page

//     // Si le script hCaptcha n'a pas chargé => widget invisible
//     if (typeof window.hcaptcha === "undefined") {
//       e.preventDefault();
//       setCaptchaError("Le captcha n’a pas pu se charger. Désactivez un bloqueur (adblock) puis rechargez la page.");
//       setLoading(false);
//       return;
//     }

//     const token = getHCaptchaValue();
//     if (!token) {
//       e.preventDefault();
//       setCaptchaError("Veuillez compléter le captcha avant d’envoyer.");
//       setLoading(false);
//       return;
//     }
//   });
// })();





// // static/core/js/contact.js
// (() => {
//   const form = document.querySelector(".contact-form");
//   if (!form) return;

//   const btn = document.getElementById("contactSubmit");
//   const captchaHint = form.querySelector(".captcha-hint");

//   const getHCaptchaValue = () => {
//     const el = form.querySelector('textarea[name="h-captcha-response"], input[name="h-captcha-response"]');
//     return (el && el.value ? el.value.trim() : "");
//   };

//   form.addEventListener("submit", (e) => {
//     // UX: disable double submit
//     if (btn) {
//       btn.disabled = true;
//       btn.classList.add("is-loading");
//       btn.setAttribute("aria-busy", "true");
//     }

//     // Soft-check hCaptcha (n’empêche pas si widget absent)
//     const widgetExists = !!form.querySelector(".h-captcha");
//     if (widgetExists) {
//       const token = getHCaptchaValue();
//       if (!token) {
//         e.preventDefault();

//         if (captchaHint) {
//           captchaHint.style.color = "#b91c1c";
//           captchaHint.style.fontWeight = "700";
//           captchaHint.textContent = captchaHint.textContent || "Veuillez compléter le captcha avant d’envoyer.";
//         }

//         if (btn) {
//           btn.disabled = false;
//           btn.classList.remove("is-loading");
//           btn.removeAttribute("aria-busy");
//         }
//         return;
//       }
//     }
//   });
// })();

