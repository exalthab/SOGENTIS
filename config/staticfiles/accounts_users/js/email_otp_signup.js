document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form[method='post']");
  if (!form) return;

  const csrf = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";

  const emailInput = document.getElementById("id_email");
  const otpInput = document.getElementById("id_email_otp_code");
  const sendBtn = document.getElementById("send-otp-btn");
  const statusBox = document.getElementById("otp-status");
  const submitBtn = form.querySelector("button[type='submit']");

  if (!emailInput || !otpInput || !sendBtn) return;

  // Etat initial
  otpInput.disabled = true;

  let otpSentForEmail = "";
  let otpVerified = false;
  let bypassNextSubmit = false;

  const isValidEmail = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test((v || "").trim());

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

  const normalizeOtp = () => {
    let v = (otpInput.value || "").replace(/\D/g, "").slice(0, 6);
    if (otpInput.value !== v) otpInput.value = v;
    return v;
  };

  otpInput.addEventListener("input", normalizeOtp);
  otpInput.addEventListener("paste", () => setTimeout(normalizeOtp, 0));

  // Si l'email change après envoi => reset
  emailInput.addEventListener("input", () => {
    const email = (emailInput.value || "").trim().toLowerCase();
    if (otpSentForEmail && email !== otpSentForEmail) {
      otpSentForEmail = "";
      otpVerified = false;
      otpInput.value = "";
      otpInput.disabled = true;
      setStatus("warning", "Email modifié : veuillez renvoyer un nouveau code.");
    }
  });

  const startCooldown = (seconds) => {
    let s = Number(seconds || 0);
    if (s <= 0) return;

    const baseText = sendBtn.dataset.baseText || sendBtn.textContent.trim();
    sendBtn.dataset.baseText = baseText;

    sendBtn.disabled = true;
    const tick = () => {
      if (s <= 0) {
        sendBtn.disabled = false;
        sendBtn.textContent = baseText;
        return;
      }
      sendBtn.textContent = `${baseText} (${s}s)`;
      s -= 1;
      setTimeout(tick, 1000);
    };
    tick();
  };

  // Envoi OTP
  sendBtn.addEventListener("click", async () => {
    const email = (emailInput.value || "").trim().toLowerCase();
    if (!isValidEmail(email)) {
      emailInput.classList.add("is-invalid");
      setStatus("warning", "Veuillez saisir un email valide puis envoyer le code.");
      return;
    }
    emailInput.classList.remove("is-invalid");
    setStatus("", "");

    const sendUrl = sendBtn.getAttribute("data-send-url");
    if (!sendUrl) {
      setStatus("danger", "URL send OTP manquante.");
      return;
    }

    sendBtn.disabled = true;

    try {
      const res = await fetch(sendUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrf,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok || !data.ok) {
        // 429 => retry_after
        if (res.status === 429 && data.retry_after) {
          setStatus("warning", data.error || "Veuillez patienter avant de renvoyer un code.");
          startCooldown(data.retry_after);
          return;
        }

        setStatus("danger", data.error || "Impossible d’envoyer le code. Réessayez.");
        sendBtn.disabled = false;
        return;
      }

      otpSentForEmail = email;
      otpVerified = false;

      otpInput.disabled = false;
      otpInput.value = "";
      otpInput.focus();

      setStatus("success", data.message || "Code envoyé. Vérifiez votre email puis saisissez les 6 chiffres.");
      startCooldown(60);
    } catch (e) {
      setStatus("danger", "Erreur réseau. Réessayez.");
      sendBtn.disabled = false;
    }
  });

  // Vérification OTP (AJAX) puis submit
  const verifyOtpThenSubmit = async () => {
    const email = (emailInput.value || "").trim().toLowerCase();
    const code = normalizeOtp();

    if (!otpSentForEmail || otpInput.disabled) {
      setStatus("warning", "Cliquez d’abord sur “Envoyer le code”, puis saisissez le code reçu.");
      return;
    }

    if (email !== otpSentForEmail) {
      setStatus("warning", "Email modifié : renvoyez un nouveau code.");
      otpInput.disabled = true;
      otpInput.value = "";
      otpSentForEmail = "";
      return;
    }

    if (code.length !== 6) {
      setStatus("warning", "Saisissez les 6 chiffres reçus par email.");
      otpInput.focus();
      return;
    }

    if (otpVerified) {
      bypassNextSubmit = true;
      form.requestSubmit();
      return;
    }

    const verifyUrl = sendBtn.getAttribute("data-verify-url");
    if (!verifyUrl) {
      setStatus("danger", "URL verify OTP manquante.");
      return;
    }

    try {
      setStatus("", "");
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.setAttribute("aria-busy", "true");
      }

      const res = await fetch(verifyUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrf,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, code }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok || !data.ok) {
        setStatus("danger", data.error || "Code incorrect.");
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.removeAttribute("aria-busy");
        }
        return;
      }

      otpVerified = true;
      setStatus("success", data.message || "Email vérifié. Vous pouvez créer votre compte.");
      bypassNextSubmit = true;
      form.requestSubmit();
    } catch (e) {
      setStatus("danger", "Erreur réseau pendant la vérification. Réessayez.");
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.removeAttribute("aria-busy");
      }
    }
  };

  // Interception submit : on vérifie OTP d'abord
  form.addEventListener("submit", (e) => {
    if (bypassNextSubmit) {
      bypassNextSubmit = false;
      return; // laisser passer
    }

    // si tu veux rendre OTP obligatoire : on bloque tant qu'il n'est pas vérifié
    if (!otpVerified) {
      e.preventDefault();
      verifyOtpThenSubmit();
    }
  });
});
