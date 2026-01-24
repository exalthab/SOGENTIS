document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form[method='post']");
  if (!form) return;

  const csrf = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";

  const emailInput = document.getElementById("id_email");
  const otpInput = document.getElementById("id_email_otp_code");
  const sendOtpBtn = document.getElementById("send-otp-btn");
  const submitBtn =
    document.getElementById("signup-submit-btn") ||
    form.querySelector("button[type='submit']");

  const statusBox = document.getElementById("otp-status");

  const setStatus = (type, msg) => {
    if (!statusBox) return;
    if (!msg) {
      statusBox.innerHTML = "";
      return;
    }
    const klass =
      type === "success"
        ? "alert alert-success"
        : type === "warning"
        ? "alert alert-warning"
        : "alert alert-danger";
    statusBox.innerHTML = `<div class="${klass} py-2 mb-2">${msg}</div>`;
  };

  const isValidEmail = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test((v || "").trim());

  // 1) état initial : OTP désactivé
  if (otpInput) {
    otpInput.disabled = true;
    otpInput.value = "";
  }

  // 2) si l'utilisateur change l'email après envoi -> on reset OTP
  let lastEmailSent = "";
  if (emailInput && otpInput) {
    emailInput.addEventListener("input", () => {
      const current = (emailInput.value || "").trim().toLowerCase();
      if (lastEmailSent && current !== lastEmailSent) {
        otpInput.disabled = true;
        otpInput.value = "";
        setStatus("warning", "Email modifié : veuillez renvoyer un nouveau code.");
        lastEmailSent = "";
      }
    });
  }

  // 3) normalisation OTP => 6 chiffres
  const normalizeOtp = () => {
    if (!otpInput) return "";
    let v = (otpInput.value || "").replace(/\D/g, "").slice(0, 6);
    if (otpInput.value !== v) otpInput.value = v;
    return v;
  };

  otpInput?.addEventListener("input", normalizeOtp);
  otpInput?.addEventListener("paste", () => setTimeout(normalizeOtp, 0));

  // 4) cooldown bouton envoyer
  const startCooldown = (seconds) => {
    if (!sendOtpBtn) return;
    let s = Number(seconds || 0);
    if (s <= 0) return;

    const baseText = sendOtpBtn.dataset.baseText || sendOtpBtn.textContent.trim();
    sendOtpBtn.dataset.baseText = baseText;

    sendOtpBtn.disabled = true;
    const tick = () => {
      if (s <= 0) {
        sendOtpBtn.disabled = false;
        sendOtpBtn.textContent = baseText;
        return;
      }
      sendOtpBtn.textContent = `${baseText} (${s}s)`;
      s -= 1;
      setTimeout(tick, 1000);
    };
    tick();
  };

  // 5) click envoyer le code
  sendOtpBtn?.addEventListener("click", async () => {
    if (!emailInput) {
      setStatus("danger", "Champ email introuvable.");
      return;
    }
    const email = (emailInput.value || "").trim().toLowerCase();

    if (!isValidEmail(email)) {
      emailInput.classList.add("is-invalid");
      setStatus("warning", "Veuillez saisir un email valide puis envoyer le code.");
      return;
    }
    emailInput.classList.remove("is-invalid");
    setStatus("", "");

    const url = sendOtpBtn.getAttribute("data-url");
    if (!url) {
      setStatus("danger", "URL d’envoi OTP manquante.");
      return;
    }

    sendOtpBtn.disabled = true;

    try {
      const res = await fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrf,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok || !data.ok) {
        setStatus("danger", data.error || "Impossible d’envoyer le code. Réessayez.");
        sendOtpBtn.disabled = false;
        return;
      }

      // OK
      lastEmailSent = email;

      if (otpInput) {
        otpInput.disabled = false;
        otpInput.value = "";
        otpInput.focus();
      }

      setStatus("success", data.message || "Code envoyé. Vérifiez votre email puis saisissez les 6 chiffres.");
      startCooldown(data.cooldown || 60);
    } catch (e) {
      setStatus("danger", "Erreur réseau. Réessayez.");
      sendOtpBtn.disabled = false;
    }
  });

  // 6) submit : bloquer si OTP non envoyé / non saisi
  form.addEventListener("submit", (e) => {
    if (!emailInput || !otpInput) return; // pas d'OTP -> on ne bloque pas

    const email = (emailInput.value || "").trim().toLowerCase();
    if (!isValidEmail(email)) return; // laisser la validation serveur

    const otp = normalizeOtp();

    // OTP pas envoyé -> champ toujours disabled
    if (otpInput.disabled) {
      e.preventDefault();
      setStatus("warning", "Cliquez d’abord sur “Envoyer le code”, puis saisissez le code reçu.");
      otpInput.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }

    // OTP envoyé mais pas 6 chiffres
    if (otp.length !== 6) {
      e.preventDefault();
      setStatus("warning", "Saisissez les 6 chiffres reçus par email.");
      otpInput.focus();
      return;
    }

    // OK -> laisser passer, backend vérifiera réellement
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.setAttribute("aria-busy", "true");
    }
  });
});
