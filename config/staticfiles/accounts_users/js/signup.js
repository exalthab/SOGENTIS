// static/accounts_users/js/signup.js
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form[method='post']");
  if (!form) return;

  // ============================
  // CSRF (hidden input + cookie fallback)
  // ============================
  const csrfInput = form.querySelector("input[name='csrfmiddlewaretoken']");
  let csrfToken = csrfInput ? csrfInput.value : "";

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return "";
  }
  if (!csrfToken) csrfToken = getCookie("csrftoken");

  // ============================
  // Toggle password
  // ============================
  document.querySelectorAll(".toggle-password").forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-target");
      const input = targetId ? document.getElementById(targetId) : null;
      if (!input) return;

      const show = input.type === "password";
      input.type = show ? "text" : "password";
      btn.textContent = show ? "🙈" : "👁️";
    });
  });

  // ============================
  // PDF preview (optionnel) - casier judiciaire
  // ============================
  const pdfInput =
    document.getElementById("id_judicial_record") ||
    form.querySelector("input[type='file'][name$='judicial_record']");
  const pdfPreview = document.getElementById("pdf-preview");

  if (pdfInput && pdfPreview) {
    pdfInput.addEventListener("change", () => {
      const file = pdfInput.files && pdfInput.files[0];
      if (!file) {
        pdfPreview.innerHTML = "";
        return;
      }

      if (file.type === "application/pdf") {
        const reader = new FileReader();
        reader.onload = (e) => {
          pdfPreview.innerHTML = `
            <embed src="${e.target.result}" type="application/pdf"
                   width="100%" height="300px" class="rounded border" />
          `;
        };
        reader.readAsDataURL(file);
      } else {
        pdfPreview.innerHTML = `
          <p class="text-danger fw-semibold">
            Format non pris en charge. Le fichier doit être en PDF.
          </p>
        `;
      }
    });
  }

  // ============================
  // OTP (Email) - éléments
  // ============================
  const sendBtn = document.getElementById("send-otp-btn");
  if (!sendBtn) return; // page sans OTP

  const verifyBtn = document.getElementById("verify-otp-btn");
  const emailFieldId = sendBtn.getAttribute("data-email-field") || "id_email";

  // Récupère URLs (priorité: sendBtn puis verifyBtn)
  const sendUrl = (sendBtn.getAttribute("data-url") || "").trim();
  const verifyUrl =
    (sendBtn.getAttribute("data-verify-url") || "").trim() ||
    (verifyBtn ? (verifyBtn.getAttribute("data-verify-url") || "").trim() : "");

  const emailInput =
    document.getElementById(emailFieldId) ||
    form.querySelector("input[name='email']");

  const otpInput =
    document.getElementById("id_email_otp_code") ||
    form.querySelector("input[name$='email_otp_code']");

  const submitBtn =
    document.getElementById("signup-submit-btn") ||
    form.querySelector("button[type='submit']");

  const termsCheckbox =
    form.querySelector("input[type='checkbox'][name$='terms']") ||
    document.getElementById("id_terms");

  const statusBox = document.getElementById("otp-status");

  // ============================
  // Helpers UI
  // ============================
  const setStatus = (type, text) => {
    if (!statusBox) return;
    if (!text) {
      statusBox.className = "";
      statusBox.textContent = "";
      return;
    }
    const cls =
      type === "success"
        ? "alert alert-success py-2"
        : type === "error"
        ? "alert alert-danger py-2"
        : "alert alert-info py-2";
    statusBox.className = cls;
    statusBox.textContent = text;
  };

  const setButtonBusy = (btn, isBusy, text) => {
    if (!btn) return;
    btn.disabled = isBusy;
    btn.setAttribute("aria-busy", isBusy ? "true" : "false");
    if (text) btn.textContent = text;
  };

  const normalizeEmail = (v) => (v || "").trim().toLowerCase();
  const normalizeCode = (v) => (v || "").replace(/\D/g, "").slice(0, 6);

  const isValidEmail = (v) => {
    const s = normalizeEmail(v);
    // léger: côté serveur fait la validation forte
    return s.includes("@") && s.includes(".");
  };

  function termsOk() {
    return termsCheckbox ? !!termsCheckbox.checked : true;
  }

  // ============================
  // State
  // ============================
  let otpSentForEmail = "";
  let otpVerifiedForEmail = "";
  let sendBusy = false;
  let verifyBusy = false;

  const originalSendText = sendBtn.textContent || "Envoyer le code";
  const originalVerifyText = verifyBtn ? (verifyBtn.textContent || "Vérifier") : "Vérifier";

  function updateSubmitState() {
    if (!submitBtn) return;
    // submit activé seulement si OTP vérifié + CGU cochées
    submitBtn.disabled = !(otpVerifiedForEmail && termsOk());
  }

  // IMPORTANT:
  // - Avant vérification: otpInput est disabled (empêche saisie)
  // - Après vérif OK: otpInput DOIT RESTER ENABLED pour être envoyé au POST
  function lockOtpUIAfterSuccess() {
    if (otpInput) {
      otpInput.readOnly = true;          // ✅ reste envoyé au POST
      otpInput.classList.add("is-valid");
    }
    if (verifyBtn) verifyBtn.disabled = true;
  }

  function enableOtpEntry() {
    if (!otpInput) return;
    otpInput.disabled = false;
    otpInput.removeAttribute("disabled");
    otpInput.readOnly = false;
    otpInput.classList.remove("is-valid");
    otpInput.focus();
  }

  function resetOtpState({ keepStatus = false } = {}) {
    otpSentForEmail = "";
    otpVerifiedForEmail = "";

    if (otpInput) {
      otpInput.value = "";
      otpInput.readOnly = false;
      otpInput.classList.remove("is-valid");
      otpInput.disabled = true;
      otpInput.setAttribute("disabled", "disabled");
    }

    if (verifyBtn) {
      verifyBtn.disabled = true;
      verifyBtn.textContent = originalVerifyText;
    }

    updateSubmitState();
    if (!keepStatus) setStatus("info", "");
  }

  // ============================
  // Init
  // ============================
  if (submitBtn) submitBtn.disabled = true;

  if (otpInput) {
    otpInput.disabled = true;
    otpInput.setAttribute("disabled", "disabled");
    otpInput.addEventListener("input", () => {
      otpInput.value = normalizeCode(otpInput.value);

      // Dès que l'utilisateur modifie -> on rebloque submit tant que pas "Vérifié"
      otpVerifiedForEmail = "";
      updateSubmitState();

      // Active "Vérifier" uniquement si 6 chiffres + OTP envoyé
      const ok = /^\d{6}$/.test(otpInput.value) && !!otpSentForEmail;
      if (verifyBtn) verifyBtn.disabled = !ok;
    });
  }

  if (termsCheckbox) {
    termsCheckbox.addEventListener("change", () => {
      updateSubmitState();
    });
  }

  if (emailInput) {
    emailInput.addEventListener("input", () => {
      const current = normalizeEmail(emailInput.value);

      // Si l'email change après envoi OTP -> invalide OTP
      if (otpSentForEmail && current !== otpSentForEmail) {
        resetOtpState({ keepStatus: true });
        setStatus("info", "Email modifié : veuillez renvoyer un code OTP.");
      }
    });
  }

  // ============================
  // Cooldown resend (429 retry_after)
  // ============================
  function cooldown(seconds) {
    let s = parseInt(seconds, 10) || 0;
    const timer = setInterval(() => {
      if (s <= 0) {
        clearInterval(timer);
        setButtonBusy(sendBtn, false, originalSendText);
        sendBusy = false;
        return;
      }
      setButtonBusy(sendBtn, true, `Réessayer (${s}s)`);
      s -= 1;
    }, 1000);
  }

  // ============================
  // Send OTP
  // ============================
  sendBtn.addEventListener("click", async () => {
    if (sendBusy) return;

    if (!emailInput) {
      setStatus("error", "Champ email introuvable.");
      return;
    }

    const email = normalizeEmail(emailInput.value);

    if (!email || !isValidEmail(email)) {
      setStatus("error", "Veuillez saisir un email valide d’abord.");
      emailInput.focus();
      return;
    }

    if (!sendUrl) {
      setStatus("error", "URL OTP manquante (data-url).");
      return;
    }

    // reset état OTP précédent
    otpVerifiedForEmail = "";
    updateSubmitState();

    sendBusy = true;
    setButtonBusy(sendBtn, true, "Envoi…");
    setStatus("info", "Envoi du code en cours…");

    try {
      const res = await fetch(sendUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ email }),
      });

      const data = await res.json().catch(() => ({}));

      if (data.retry_after) {
        setStatus("error", data.error || "Veuillez patienter avant de réessayer.");
        cooldown(data.retry_after);
        return;
      }

      if (data.ok) {
        otpSentForEmail = email;

        setStatus("success", data.message || "Code envoyé. Vérifiez votre email.");
        setButtonBusy(sendBtn, false, originalSendText);
        sendBusy = false;

        enableOtpEntry();
        if (otpInput) otpInput.value = "";

        if (verifyBtn) {
          verifyBtn.disabled = true; // activé quand 6 chiffres
          verifyBtn.textContent = originalVerifyText;
        }
      } else {
        setStatus("error", data.error || "Échec d’envoi du code.");
        setButtonBusy(sendBtn, false, originalSendText);
        sendBusy = false;
      }
    } catch (e) {
      setStatus("error", "Erreur réseau lors de l’envoi du code.");
      setButtonBusy(sendBtn, false, originalSendText);
      sendBusy = false;
    }
  });

  // ============================
  // Verify OTP (bouton)
  // ============================
  async function verifyOtp() {
    if (verifyBusy) return;

    if (!emailInput) {
      setStatus("error", "Champ email introuvable.");
      return;
    }
    if (!otpInput) {
      setStatus("error", "Champ OTP introuvable.");
      return;
    }

    const email = normalizeEmail(emailInput.value);
    const code = normalizeCode(otpInput.value);

    if (!otpSentForEmail) {
      setStatus("error", "Veuillez d’abord envoyer un code OTP.");
      return;
    }
    if (email !== otpSentForEmail) {
      setStatus("error", "Email différent : renvoyez un nouveau code OTP.");
      resetOtpState({ keepStatus: true });
      return;
    }
    if (!/^\d{6}$/.test(code)) {
      setStatus("error", "Veuillez saisir un code à 6 chiffres.");
      otpInput.focus();
      return;
    }

    // Si verifyUrl absent: fallback -> on laisse le serveur revalider au submit
    if (!verifyUrl) {
      otpVerifiedForEmail = email;
      setStatus("success", "Code saisi. Vous pouvez créer le compte (validation serveur).");
      updateSubmitState();
      return;
    }

    verifyBusy = true;
    if (verifyBtn) setButtonBusy(verifyBtn, true, "Vérification…");
    setStatus("info", "Vérification du code…");
    updateSubmitState();

    try {
      const res = await fetch(verifyUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ email, code }),
      });

      const data = await res.json().catch(() => ({}));

      if (data.ok) {
        otpVerifiedForEmail = email;
        setStatus("success", data.message || "Email vérifié avec succès.");

        // ✅ On verrouille sans désactiver (sinon code non envoyé au POST)
        lockOtpUIAfterSuccess();

        updateSubmitState();
      } else {
        otpVerifiedForEmail = "";
        setStatus("error", data.error || "Code incorrect.");
        updateSubmitState();

        // Laisse corriger
        otpInput.readOnly = false;
        otpInput.focus();
        if (verifyBtn) {
          verifyBtn.disabled = !/^\d{6}$/.test(normalizeCode(otpInput.value));
          setButtonBusy(verifyBtn, false, originalVerifyText);
        }
      }
    } catch (e) {
      otpVerifiedForEmail = "";
      setStatus("error", "Erreur réseau lors de la vérification.");
      updateSubmitState();
      if (verifyBtn) setButtonBusy(verifyBtn, false, originalVerifyText);
    } finally {
      verifyBusy = false;
      if (verifyBtn && !verifyBtn.disabled) verifyBtn.textContent = originalVerifyText;
    }
  }

  if (verifyBtn) {
    verifyBtn.addEventListener("click", verifyOtp);
  }

  // ============================
  // Sécurité UX : empêche submit si conditions pas remplies
  // ============================
  form.addEventListener("submit", (e) => {
    const ok = otpVerifiedForEmail && termsOk();
    if (!ok) {
      e.preventDefault();

      if (!termsOk()) {
        setStatus("error", "Veuillez accepter les conditions générales.");
        termsCheckbox?.focus();
        return;
      }

      setStatus("error", "Veuillez vérifier votre email via le code OTP avant de créer le compte.");
      otpInput?.focus();
    }
  });
});
