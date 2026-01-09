// static/core/js/contact.js
(() => {
  const form = document.querySelector(".contact-form");
  if (!form) return;

  const btn = document.getElementById("contactSubmit");
  const captchaHint = form.querySelector(".captcha-hint");

  const getHCaptchaValue = () => {
    const el = form.querySelector('textarea[name="h-captcha-response"], input[name="h-captcha-response"]');
    return (el && el.value ? el.value.trim() : "");
  };

  form.addEventListener("submit", (e) => {
    // UX: disable double submit
    if (btn) {
      btn.disabled = true;
      btn.classList.add("is-loading");
      btn.setAttribute("aria-busy", "true");
    }

    // Soft-check hCaptcha (n’empêche pas si widget absent)
    const widgetExists = !!form.querySelector(".h-captcha");
    if (widgetExists) {
      const token = getHCaptchaValue();
      if (!token) {
        e.preventDefault();

        if (captchaHint) {
          captchaHint.style.color = "#b91c1c";
          captchaHint.style.fontWeight = "700";
          captchaHint.textContent = captchaHint.textContent || "Veuillez compléter le captcha avant d’envoyer.";
        }

        if (btn) {
          btn.disabled = false;
          btn.classList.remove("is-loading");
          btn.removeAttribute("aria-busy");
        }
        return;
      }
    }
  });
})();

