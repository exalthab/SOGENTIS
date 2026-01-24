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
  // PDF preview (optionnel)
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
  if (!sendBtn) return; // pages sans OTP: on garde juste toggle password + pdf preview

  const sendUrl = sendBtn.getAttribute("data-url") || "";
  const verifyUrl = sendBtn.getAttribute("data-verify-url") || ""; // recommandé
  const emailFieldId = sendBtn.getAttribute("data-email-field") || "id_email";

  const emailInput = document.getElementById(emailFieldId) || form.querySelector("input[name='email']");
  const otpInput =
    document.getElementById("id_email_otp_code") ||
    form.querySelector("input[name$='email_otp_code']");
  const verifyBtn = document.getElementById("verify-otp-btn"); // présent dans tes templates finaux
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
      type === "success" ? "alert alert-success py-2" :
      type === "error" ? "alert alert-danger py-2" :
      "alert alert-info py-2";
    statusBox.className = cls;
    statusBox.textContent = text;
  };

  const setButtonBusy = (btn, isBusy, text) => {
    if (!btn) return;
    btn.disabled = isBusy;
    btn.setAttribute("aria-busy", isBusy ? "true" : "false");
    if (text) btn.textContent = text;
  };

  const isValidEmail = (v) => (v || "").includes("@"); // léger, validation forte côté serveur
  const normalizeEmail = (v) => (v || "").trim().toLowerCase();
  const normalizeCode = (v) => (v || "").replace(/\D/g, "").slice(0, 6);

  // ============================
  // State
  // ============================
  let otpSentForEmail = "";
  let otpVerifiedForEmail = "";
  let sendBusy = false;
  let verifyBusy = false;

  const originalSendText = sendBtn.textContent || "Envoyer le code";
  const originalVerifyText = verifyBtn ? (verifyBtn.textContent || "Vérifier") : "Vérifier";

  function termsOk() {
    return termsCheckbox ? !!termsCheckbox.checked : true;
  }

  function updateSubmitState() {
    if (!submitBtn) return;
    // submit activé seulement si OTP validé + terms cochées
    submitBtn.disabled = !(otpVerifiedForEmail && termsOk());
  }

  function lockOtpUI() {
    if (otpInput) {
      otpInput.disabled = true;
      otpInput.setAttribute("disabled", "disabled");
      otpInput.readOnly = true;
    }
    if (verifyBtn) verifyBtn.disabled = true;
  }

  function enableOtpUI() {
    if (otpInput) {
      otpInput.disabled = false;
      otpInput.removeAttribute("disabled");
      otpInput.readOnly = false;
    }
    if (verifyBtn) verifyBtn.disabled = false;
  }

  function resetOtpState({ keepStatus = false } = {}) {
    otpSentForEmail = "";
    otpVerifiedForEmail = "";
    if (otpInput) {
      otpInput.value = "";
      otpInput.disabled = true;
      otpInput.setAttribute("disabled", "disabled");
      otpInput.readOnly = false;
    }
    if (verifyBtn) {
      verifyBtn.disabled = true;
      verifyBtn.textContent = originalVerifyText;
    }
    updateSubmitState();
    if (!keepStatus) setStatus("info", "");
  }

  // Au chargement : on force le submit disabled tant que l'OTP n'est pas validé
  if (submitBtn) submitBtn.disabled = true;
  if (otpInput) {
    otpInput.disabled = true;
    otpInput.setAttribute("disabled", "disabled");
  }
  if (verifyBtn) verifyBtn.disabled = true;

  // Terms -> recheck submit
  if (termsCheckbox) {
    termsCheckbox.addEventListener("change", () => {
      updateSubmitState();
    });
  }

  // Email change -> on invalide OTP (pour éviter mismatch)
  if (emailInput) {
    emailInput.addEventListener("input", () => {
      const current = normalizeEmail(emailInput.value);
      if (otpSentForEmail && current !== otpSentForEmail) {
        resetOtpState({ keepStatus: true });
        setStatus("info", "Email modifié : veuillez renvoyer un code OTP.");
      }
    });
  }

  // OTP input -> digits only
  if (otpInput) {
    otpInput.addEventListener("input", () => {
      otpInput.value = normalizeCode(otpInput.value);
      // Active le bouton vérifier quand 6 chiffres
      if (verifyBtn) verifyBtn.disabled = !/^\d{6}$/.test(otpInput.value);
      // Fallback si pas de bouton vérifier (ancien template)
      if (!verifyBtn && /^\d{6}$/.test(otpInput.value) && !verifyUrl) {
        // Sans verify ajax, on permet submit (le serveur revalidera)
        otpVerifiedForEmail = otpSentForEmail || normalizeEmail(emailInput?.value || "");
        updateSubmitState();
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
    const email = normalizeEmail(emailInput ? emailInput.value : "");

    if (!emailInput) {
      setStatus("error", "Champ email introuvable.");
      return;
    }
    if (!email || !isValidEmail(email)) {
      setStatus("error", "Veuillez saisir un email valide d’abord.");
      emailInput.focus();
      return;
    }
    if (!sendUrl) {
      setStatus("error", "URL OTP manquante (data-url).");
      return;
    }

    // reset état précédent (mais on ne touche pas aux autres champs)
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

        enableOtpUI();

        if (otpInput) {
          otpInput.value = "";
          otpInput.focus();
        }

        if (verifyBtn) {
          verifyBtn.disabled = true; // restera false quand 6 chiffres
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

    const email = normalizeEmail(emailInput ? emailInput.value : "");
    const code = normalizeCode(otpInput ? otpInput.value : "");

    if (!emailInput) {
      setStatus("error", "Champ email introuvable.");
      return;
    }
    if (!otpInput) {
      setStatus("error", "Champ OTP introuvable.");
      return;
    }
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

    // Fallback si pas de verifyUrl: on laisse le serveur revalider au submit
    if (!verifyUrl) {
      otpVerifiedForEmail = email;
      setStatus("success", "Code saisi. Vous pouvez créer le compte (validation serveur).");
      updateSubmitState();
      return;
    }

    verifyBusy = true;
    if (verifyBtn) setButtonBusy(verifyBtn, true, "Vérification…");
    setStatus("info", "Vérification du code…");
    updateSubmitState(); // reste disabled tant que pas ok

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

        // Option: on verrouille l'OTP après succès (évite changement)
        lockOtpUI();

        updateSubmitState();
      } else {
        otpVerifiedForEmail = "";
        setStatus("error", data.error || "Code incorrect.");
        updateSubmitState();

        // On laisse l'utilisateur corriger
        if (otpInput) otpInput.focus();
        if (verifyBtn) {
          verifyBtn.disabled = !/^\d{6}$/.test(otpInput.value);
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
  } else if (otpInput) {
    // compat ancien template : auto-verify quand 6 chiffres (si verifyUrl dispo)
    otpInput.addEventListener("keyup", () => {
      if (/^\d{6}$/.test(normalizeCode(otpInput.value)) && verifyUrl) verifyOtp();
    });
  }

  // Empêche submit si OTP pas validé ou terms pas cochées (sécurité UX)
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
      if (otpInput) otpInput.focus();
    }
  });
});








// // static/accounts_users/js/signup.js
// document.addEventListener("DOMContentLoaded", () => {
//   const form = document.querySelector("form[method='post']");
//   if (!form) return;

//   // ============================
//   // CSRF (hidden input + cookie fallback)
//   // ============================
//   const csrfInput = form.querySelector("input[name='csrfmiddlewaretoken']");
//   let csrfToken = csrfInput ? csrfInput.value : "";

//   function getCookie(name) {
//     const value = `; ${document.cookie}`;
//     const parts = value.split(`; ${name}=`);
//     if (parts.length === 2) return parts.pop().split(";").shift();
//     return "";
//   }
//   if (!csrfToken) csrfToken = getCookie("csrftoken");

//   // ============================
//   // Toggle password
//   // ============================
//   document.querySelectorAll(".toggle-password").forEach((btn) => {
//     btn.addEventListener("click", () => {
//       const targetId = btn.getAttribute("data-target");
//       const input = targetId ? document.getElementById(targetId) : null;
//       if (!input) return;

//       const show = input.type === "password";
//       input.type = show ? "text" : "password";
//       btn.textContent = show ? "🙈" : "👁️";
//     });
//   });

//   // ============================
//   // OTP elements
//   // ============================
//   const sendBtn = document.getElementById("send-otp-btn");
//   if (!sendBtn) return;

//   const sendUrl = sendBtn.getAttribute("data-url");
//   const verifyUrl = sendBtn.getAttribute("data-verify-url"); // ✅ optionnel
//   const emailFieldId = sendBtn.getAttribute("data-email-field") || "id_email";

//   const otpInput = document.getElementById("id_email_otp_code");
//   const submitBtn = document.getElementById("signup-submit-btn") || form.querySelector("button[type='submit']");
//   const statusBox = document.getElementById("otp-status");

//   const setStatus = (type, text) => {
//     if (!statusBox) return;
//     const cls =
//       type === "success" ? "alert alert-success py-2" :
//       type === "error" ? "alert alert-danger py-2" :
//       "alert alert-info py-2";
//     statusBox.className = cls;
//     statusBox.textContent = text || "";
//   };

//   const setBusy = (isBusy, text) => {
//     sendBtn.disabled = isBusy;
//     sendBtn.setAttribute("aria-busy", isBusy ? "true" : "false");
//     if (text) sendBtn.textContent = text;
//   };

//   const originalSendText = sendBtn.textContent;

//   const getEmail = () => {
//     const emailInput = document.getElementById(emailFieldId);
//     return {
//       el: emailInput,
//       value: emailInput ? (emailInput.value || "").trim() : "",
//     };
//   };

//   const enableOtpEntry = () => {
//     if (!otpInput) return;
//     otpInput.disabled = false;
//     otpInput.removeAttribute("disabled");
//     otpInput.focus();
//   };

//   const disableSubmit = () => {
//     if (submitBtn) submitBtn.disabled = true;
//   };

//   const enableSubmit = () => {
//     if (submitBtn) submitBtn.disabled = false;
//   };

//   // Au chargement : si ton template met submit disabled, on respecte
//   // (on activera uniquement après OTP validé)
//   disableSubmit();

//   // Nettoyage OTP -> digits only, max 6
//   otpInput?.addEventListener("input", () => {
//     otpInput.value = (otpInput.value || "").replace(/\D/g, "").slice(0, 6);
//   });

//   async function verifyOtpIfPossible() {
//     if (!verifyUrl) {
//       // Pas de vérif AJAX: on autorise submit quand 6 chiffres (le serveur revalidera)
//       const ok = otpInput && /^[0-9]{6}$/.test((otpInput.value || "").trim());
//       if (ok) enableSubmit();
//       else disableSubmit();
//       return;
//     }

//     // Vérif AJAX: on n'active submit qu'après validation serveur
//     const code = otpInput ? (otpInput.value || "").trim() : "";
//     const { el: emailEl, value: email } = getEmail();

//     if (!email) {
//       setStatus("error", "Veuillez saisir votre email d’abord.");
//       disableSubmit();
//       emailEl?.focus();
//       return;
//     }
//     if (!/^[0-9]{6}$/.test(code)) {
//       disableSubmit();
//       return;
//     }

//     disableSubmit();
//     setStatus("info", "Vérification du code…");

//     try {
//       const res = await fetch(verifyUrl, {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//           "X-CSRFToken": csrfToken,
//         },
//         body: JSON.stringify({ email, code }),
//       });

//       const data = await res.json().catch(() => ({}));

//       if (data.ok) {
//         setStatus("success", data.message || "Email vérifié avec succès.");
//         enableSubmit();
//       } else {
//         setStatus("error", data.error || "Code incorrect.");
//         disableSubmit();
//       }
//     } catch (e) {
//       setStatus("error", "Erreur réseau lors de la vérification.");
//       disableSubmit();
//     }
//   }

//   otpInput?.addEventListener("keyup", () => {
//     // quand 6 chiffres, on vérifie / ou on autorise
//     verifyOtpIfPossible();
//   });

//   // ============================
//   // Send OTP
//   // ============================
//   sendBtn.addEventListener("click", async () => {
//     const { el: emailEl, value: email } = getEmail();

//     if (!email) {
//       setStatus("error", "Veuillez saisir votre email d’abord.");
//       emailEl?.focus();
//       return;
//     }
//     if (!sendUrl) {
//       setStatus("error", "URL OTP manquante (data-url).");
//       return;
//     }

//     setBusy(true, "Envoi…");
//     setStatus("info", "Envoi du code en cours…");

//     try {
//       const res = await fetch(sendUrl, {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//           "X-CSRFToken": csrfToken,
//         },
//         body: JSON.stringify({ email }),
//       });

//       const data = await res.json().catch(() => ({}));

//       // Ton endpoint renvoie retry_after en cas de 429 (OK)
//       if (data.retry_after) {
//         setStatus("error", data.error || "Veuillez patienter avant de réessayer.");
//         // on réactive le bouton après attente côté serveur
//         let s = parseInt(data.retry_after, 10) || 0;
//         const timer = setInterval(() => {
//           if (s <= 0) {
//             clearInterval(timer);
//             setBusy(false, originalSendText);
//             return;
//           }
//           sendBtn.textContent = `Réessayer (${s}s)`;
//           s -= 1;
//         }, 1000);
//         return;
//       }

//       if (data.ok) {
//         setStatus("success", data.message || "Code envoyé. Vérifiez votre email.");
//         setBusy(false, originalSendText);

//         enableOtpEntry();
//         disableSubmit(); // on attend OTP valide
//       } else {
//         setStatus("error", data.error || "Échec d’envoi du code.");
//         setBusy(false, originalSendText);
//       }
//     } catch (e) {
//       setStatus("error", "Erreur réseau lors de l’envoi du code.");
//       setBusy(false, originalSendText);
//     }
//   });
// });




// // static/accounts_users/js/signup.js
// document.addEventListener("DOMContentLoaded", () => {
//   const form = document.querySelector("form[method='post']");
//   if (!form) return;

//   // ============================
//   // CSRF (Django) : input hidden + fallback cookie
//   // ============================
//   const csrfInput = form.querySelector("input[name='csrfmiddlewaretoken']");
//   let csrfToken = csrfInput ? csrfInput.value : "";

//   function getCookie(name) {
//     const value = `; ${document.cookie}`;
//     const parts = value.split(`; ${name}=`);
//     if (parts.length === 2) return parts.pop().split(";").shift();
//     return "";
//   }
//   if (!csrfToken) csrfToken = getCookie("csrftoken");

//   // ============================
//   // Toggle password (multi champs)
//   // ============================
//   document.querySelectorAll(".toggle-password").forEach((btn) => {
//     btn.addEventListener("click", () => {
//       const targetId = btn.getAttribute("data-target");
//       if (!targetId) return;

//       const input = document.getElementById(targetId);
//       if (!input) return;

//       const show = input.type === "password";
//       input.type = show ? "text" : "password";
//       btn.textContent = show ? "🙈" : "👁️";
//     });
//   });

//   // ============================
//   // OTP EMAIL
//   // ============================
//   const sendBtn = document.getElementById("send-otp-btn");
//   if (!sendBtn) return;

//   const url = sendBtn.getAttribute("data-url");
//   const emailFieldId = sendBtn.getAttribute("data-email-field") || "id_email";

//   const otpInput =
//     document.getElementById("id_email_otp_code") ||
//     document.querySelector("input[name$='email_otp_code']");

//   const submitBtn =
//     document.getElementById("signup-submit-btn") ||
//     form.querySelector("button[type='submit']");

//   const statusBox = document.getElementById("otp-status");

//   const setStatus = (type, text) => {
//     if (!statusBox) return;
//     const cls =
//       type === "success"
//         ? "alert alert-success py-2"
//         : type === "error"
//         ? "alert alert-danger py-2"
//         : "alert alert-info py-2";
//     statusBox.className = cls;
//     statusBox.textContent = text || "";
//   };

//   function setBusy(isBusy, text) {
//     sendBtn.disabled = isBusy;
//     sendBtn.setAttribute("aria-busy", isBusy ? "true" : "false");
//     if (text) sendBtn.textContent = text;
//   }

//   function cooldown(seconds) {
//     let s = parseInt(seconds, 10) || 0;
//     const originalText =
//       sendBtn.getAttribute("data-original-text") || sendBtn.textContent;

//     sendBtn.setAttribute("data-original-text", originalText);

//     const timer = setInterval(() => {
//       if (s <= 0) {
//         clearInterval(timer);
//         setBusy(false, originalText);
//         return;
//       }
//       setBusy(true, `Réessayer (${s}s)`);
//       s -= 1;
//     }, 1000);
//   }

//   const enableOtpEntry = () => {
//     if (!otpInput) return;
//     otpInput.removeAttribute("disabled");
//     otpInput.disabled = false;
//     otpInput.focus();
//   };

//   const updateSubmitState = () => {
//     if (!submitBtn) return;
//     // Si pas d'OTP input, on ne bloque pas
//     if (!otpInput) {
//       submitBtn.disabled = false;
//       return;
//     }
//     const val = (otpInput.value || "").trim();
//     const ok = /^[0-9]{6}$/.test(val);
//     submitBtn.disabled = !ok;
//   };

//   // Init : si OTP est disabled et vide -> submit disabled (comme ton template)
//   updateSubmitState();

//   // Enable submit automatiquement quand OTP valide
//   otpInput?.addEventListener("input", updateSubmitState);

//   sendBtn.addEventListener("click", async () => {
//     const emailInput = document.getElementById(emailFieldId);
//     const email = emailInput ? (emailInput.value || "").trim() : "";

//     if (!email) {
//       setStatus("error", "Veuillez saisir votre email d’abord.");
//       if (emailInput) emailInput.focus();
//       return;
//     }
//     if (!url) {
//       setStatus("error", "URL OTP manquante (data-url).");
//       return;
//     }

//     setBusy(true, "Envoi...");
//     setStatus("info", "Envoi du code en cours…");

//     try {
//       const res = await fetch(url, {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//           "X-CSRFToken": csrfToken,
//         },
//         body: JSON.stringify({ email }),
//       });

//       const data = await res.json().catch(() => ({}));

//       if (data.retry_after) {
//         setStatus(
//           "error",
//           data.error || data.message || "Veuillez patienter avant de réessayer."
//         );
//         cooldown(data.retry_after);
//         return;
//       }

//       if (data.ok) {
//         setStatus("success", data.message || "Code envoyé. Vérifiez votre email.");
//         enableOtpEntry();
//         // on garde submit désactivé tant que l'OTP n'est pas 6 chiffres
//         updateSubmitState();
//       } else {
//         setStatus("error", data.error || "Échec d’envoi du code.");
//         setBusy(false, sendBtn.getAttribute("data-original-text") || "Envoyer le code");
//       }
//     } catch (e) {
//       setStatus("error", "Erreur réseau lors de l’envoi du code.");
//       setBusy(false, sendBtn.getAttribute("data-original-text") || "Envoyer le code");
//     }
//   });
// });







// // static/accounts_users/js/signup.js
// document.addEventListener("DOMContentLoaded", () => {
//   const form = document.querySelector("form[method='post']");
//   if (!form) return;

//   // CSRF (Django) : input hidden en priorité + fallback cookie
//   const csrfInput = form.querySelector("input[name='csrfmiddlewaretoken']");
//   let csrfToken = csrfInput ? csrfInput.value : "";

//   function getCookie(name) {
//     const value = `; ${document.cookie}`;
//     const parts = value.split(`; ${name}=`);
//     if (parts.length === 2) return parts.pop().split(";").shift();
//     return "";
//   }
//   if (!csrfToken) csrfToken = getCookie("csrftoken");

//   // ============================
//   // Toggle password (multi champs)
//   // ============================
//   document.querySelectorAll(".toggle-password").forEach((btn) => {
//     btn.addEventListener("click", () => {
//       const targetId = btn.getAttribute("data-target");
//       if (!targetId) return;

//       const input = document.getElementById(targetId);
//       if (!input) return;

//       const show = input.type === "password";
//       input.type = show ? "text" : "password";
//       btn.textContent = show ? "🙈" : "👁️";
//     });
//   });

//   // ============================
//   // OTP - envoyer code
//   // ============================
//   const sendBtn = document.getElementById("send-otp-btn");
//   if (!sendBtn) return;

//   const url = sendBtn.getAttribute("data-url");
//   const emailFieldId = sendBtn.getAttribute("data-email-field") || "id_email";

//   function setBusy(isBusy, text) {
//     sendBtn.disabled = isBusy;
//     sendBtn.setAttribute("aria-busy", isBusy ? "true" : "false");
//     if (text) sendBtn.textContent = text;
//   }

//   function cooldown(seconds) {
//     let s = parseInt(seconds, 10) || 0;
//     const originalText = sendBtn.getAttribute("data-original-text") || sendBtn.textContent;

//     sendBtn.setAttribute("data-original-text", originalText);

//     const timer = setInterval(() => {
//       if (s <= 0) {
//         clearInterval(timer);
//         setBusy(false, originalText);
//         return;
//       }
//       setBusy(true, `Réessayer (${s}s)`);
//       s -= 1;
//     }, 1000);
//   }

//   sendBtn.addEventListener("click", async () => {
//     const emailInput = document.getElementById(emailFieldId);
//     const email = emailInput ? (emailInput.value || "").trim() : "";

//     if (!email) {
//       alert("Veuillez saisir votre email d’abord.");
//       if (emailInput) emailInput.focus();
//       return;
//     }
//     if (!url) {
//       alert("URL OTP manquante (data-url).");
//       return;
//     }

//     setBusy(true, "Envoi...");

//     try {
//       const res = await fetch(url, {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//           "X-CSRFToken": csrfToken,
//         },
//         body: JSON.stringify({ email }),
//       });

//       const data = await res.json().catch(() => ({}));

//       if (data.retry_after) {
//         alert(data.error || data.message || "Veuillez patienter avant de réessayer.");
//         cooldown(data.retry_after);
//         return;
//       }

//       if (data.ok) {
//         alert(data.message || "Code envoyé. Vérifiez votre email.");
//         // focus OTP input après envoi
//         const otpInput = document.getElementById("id_email_otp_code");
//         if (otpInput) otpInput.focus();
//       } else {
//         alert(data.error || "Échec d’envoi du code.");
//         setBusy(false, sendBtn.getAttribute("data-original-text") || "Envoyer le code");
//       }
//     } catch (e) {
//       alert("Erreur réseau lors de l’envoi du code.");
//       setBusy(false, sendBtn.getAttribute("data-original-text") || "Envoyer le code");
//     }
//   });
// });



// document.addEventListener("DOMContentLoaded", function () {

//   const form = document.querySelector("form[method='post']");
//   if (!form) return;

//   const submitBtn = form.querySelector("button[type='submit']");

//   const password1 = form.querySelector(".password-strong");
//   const password2 = form.querySelector(".password-confirm");
//   const toggleBtn = document.getElementById("togglePassword");
//   const toggleIcon = document.getElementById("togglePasswordIcon");
//   const capsHint = document.getElementById("capsLockHint");

//   const profileInput = form.querySelector('input[name="profile_picture"]');
//   const profilePreview = document.getElementById("profile_picture");

//   const judicialInput = document.getElementById("id_judicial_record");
//   const pdfPreview = document.getElementById("pdf-preview");

//   const countrySelect = document.getElementById("id_country_of_residence");
//   const phoneInput = document.getElementById("id_phone_number");

//   const MAX_PDF_SIZE = 2 * 1024 * 1024;

//   const countryDialCodes = {
//     SN: "+221",
//     FR: "+33",
//     BE: "+32",
//     CI: "+225",
//     US: "+1",
//     GB: "+44"
//   };

//   let currentDialCode = "";

//   /* =======================
//      RÈGLES DE VALIDATION
//   ======================= */
//   const strongPassword = v =>
//     /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/.test(v);

//   const validPhone = v =>
//     /^\+[0-9]{8,15}$/.test(v);

//   const validateField = (field) => {
//     let valid = true;

//     if (field === phoneInput) {
//       const fullPhone = currentDialCode + field.value.replace(/\s+/g, "");
//       valid = validPhone(fullPhone);
//     } else if (field.type === "password") {
//       valid = strongPassword(field.value);
//     } else if (field.type === "email") {
//       valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value);
//     } else if (field.type === "checkbox") {
//       valid = field.checked;
//     } else if (field.type === "file" && field.required) {
//       valid = field.files.length > 0;
//     } else {
//       valid = field.value.trim() !== "";
//     }

//     field.classList.toggle("is-valid", valid);
//     field.classList.toggle("is-invalid", !valid);
//     return valid;
//   };

//   const validateForm = () => {
//     let ok = true;

//     form.querySelectorAll(".form-control, .form-check-input").forEach(field => {
//       if (!validateField(field)) ok = false;
//     });

//     // mots de passe identiques
//     if (password1 && password2 && password1.value !== password2.value) {
//       password2.setCustomValidity("Les mots de passe ne sont pas identiques.");
//       password2.classList.add("is-invalid");
//       ok = false;
//     } else if (password2) {
//       password2.setCustomValidity("");
//     }

//     // casier judiciaire
//     if (judicialInput) {
//       const f = judicialInput.files[0];
//       if (!f || f.type !== "application/pdf" || f.size > MAX_PDF_SIZE) {
//         ok = false;
//         judicialInput.classList.add("is-invalid");
//       } else {
//         judicialInput.classList.add("is-valid");
//       }
//     }

//     submitBtn.disabled = !ok;
//     return ok;
//   };

//   /* =======================
//      PDF – CASIER JUDICIAIRE
//   ======================= */
//   if (judicialInput) {
//     judicialInput.required = true;
//     judicialInput.addEventListener("change", () => {
//       pdfPreview.innerHTML = "";
//       const file = judicialInput.files[0];
//       if (!file) return;

//       if (file.type === "application/pdf" && file.size <= MAX_PDF_SIZE) {
//         pdfPreview.innerHTML =
//           `<iframe src="${URL.createObjectURL(file)}" width="100%" height="300"></iframe>`;
//       }
//       validateForm();
//     });
//   }

//   /* =======================
//      PHOTO DE PROFIL
//   ======================= */
//   if (profileInput && profilePreview) {
//     profileInput.addEventListener("change", () => {
//       if (profileInput.files[0]) {
//         const reader = new FileReader();
//         reader.onload = e => {
//           profilePreview.src = e.target.result;
//           profilePreview.style.display = "block";
//         };
//         reader.readAsDataURL(profileInput.files[0]);
//       } else {
//         profilePreview.style.display = "none";
//       }
//       validateForm();
//     });
//   }

//   /* =======================
//      TÉLÉPHONE + INDICATIF (SANS RÉÉCRITURE)
//   ======================= */
//   if (countrySelect && phoneInput) {

//     const applyDialCode = () => {
//       currentDialCode = countryDialCodes[countrySelect.value] || "";
//       phoneInput.placeholder = currentDialCode
//         ? `${currentDialCode} XXXXXXXX`
//         : "XXXXXXXX";
//     };

//     countrySelect.addEventListener("change", applyDialCode);
//     applyDialCode();

//     // empêcher l'utilisateur de saisir +
//     phoneInput.addEventListener("input", () => {
//       phoneInput.value = phoneInput.value.replace(/\+/g, "");
//       validateForm();
//     });
//   }

//   /* =======================
//      TOGGLE MOT DE PASSE
//   ======================= */
//   if (toggleBtn && toggleIcon && password1) {
//     toggleBtn.addEventListener("click", () => {
//       const show = password1.type === "password";
//       password1.type = show ? "text" : "password";
//       if (password2) password2.type = show ? "text" : "password";
//       toggleIcon.textContent = show ? "🙈" : "👁️";
//     });
//   }

//   /* =======================
//      CAPS LOCK
//   ======================= */
//   if (password1 && capsHint) {
//     ["keydown", "keyup", "focus"].forEach(evt =>
//       password1.addEventListener(evt, e =>
//         capsHint.classList.toggle("d-none", !e.getModifierState("CapsLock"))
//       )
//     );
//     password1.addEventListener("blur", () => capsHint.classList.add("d-none"));
//   }

//   /* =======================
//      SUBMIT
//   ======================= */
//   form.addEventListener("input", validateForm);

//   form.addEventListener("submit", e => {
//     e.preventDefault();
//     if (!validateForm()) return;

//     // recomposer le numéro final avant envoi
//     if (phoneInput && currentDialCode) {
//       phoneInput.value =
//         currentDialCode + phoneInput.value.replace(/\s+/g, "");
//     }

//     submitBtn.disabled = true;
//     submitBtn.setAttribute("aria-busy", "true");
//     form.submit();
//   });

//   validateForm();
// });










// // // static/accounts_users/js/signup.js
// // document.addEventListener("DOMContentLoaded", function () {

// //   const form = document.querySelector("form[method='post']");
// //   if (!form) return;

// //   const submitBtn = form.querySelector("button[type='submit']");

// //   const password1 = form.querySelector(".password-strong");
// //   const password2 = form.querySelector(".password-confirm");
// //   const toggleBtn = document.getElementById("togglePassword");
// //   const toggleIcon = document.getElementById("togglePasswordIcon");
// //   const capsHint = document.getElementById("capsLockHint");

// //   const profileInput = form.querySelector('input[name="profile_picture"]');
// //   const profilePreview = document.getElementById("profile_picture");

// //   const judicialInput = document.getElementById("id_judicial_record");
// //   const pdfPreview = document.getElementById("pdf-preview");

// //   const countrySelect = document.getElementById("id_country_of_residence");
// //   const phoneInput = document.getElementById("id_phone_number");

// //   const MAX_PDF_SIZE = 2 * 1024 * 1024;

// //   const countryDialCodes = {
// //     SN: "+221",
// //     FR: "+33",
// //     BE: "+32",
// //     CI: "+225",
// //     US: "+1",
// //     GB: "+44"
// //   };

// //   /* =======================
// //      RÈGLES DE VALIDATION
// //   ======================= */
// //   const strongPassword = (v) =>
// //     /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/.test(v);

// //   const validPhone = (v) =>
// //     /^\+[0-9]{8,15}$/.test(v);

// //   const validateField = (field) => {
// //     let valid = true;

// //     if (field === phoneInput) {
// //       valid = validPhone(field.value);
// //     } else if (field.type === "password") {
// //       valid = strongPassword(field.value);
// //     } else if (field.type === "email") {
// //       valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value);
// //     } else if (field.type === "checkbox") {
// //       valid = field.checked;
// //     } else if (field.type === "file" && field.required) {
// //       valid = field.files.length > 0;
// //     } else {
// //       valid = field.value.trim() !== "";
// //     }

// //     field.classList.toggle("is-valid", valid);
// //     field.classList.toggle("is-invalid", !valid);
// //     return valid;
// //   };

// //   const validateForm = () => {
// //     let ok = true;

// //     form.querySelectorAll(".form-control, .form-check-input").forEach(field => {
// //       if (!validateField(field)) ok = false;
// //     });

// //     // mot de passe identique
// //     if (password1 && password2 && password1.value !== password2.value) {
// //       password2.setCustomValidity("Les mots de passe ne sont pas identiques.");
// //       password2.classList.add("is-invalid");
// //       ok = false;
// //     } else if (password2) {
// //       password2.setCustomValidity("");
// //     }

// //     // casier judiciaire
// //     if (judicialInput) {
// //       const f = judicialInput.files[0];
// //       if (!f || f.type !== "application/pdf" || f.size > MAX_PDF_SIZE) {
// //         ok = false;
// //         judicialInput.classList.add("is-invalid");
// //       } else {
// //         judicialInput.classList.add("is-valid");
// //       }
// //     }

// //     submitBtn.disabled = !ok;
// //     return ok;
// //   };

// //   /* =======================
// //      PDF – CASIER JUDICIAIRE
// //   ======================= */
// //   if (judicialInput) {
// //     judicialInput.required = true;
// //     judicialInput.addEventListener("change", () => {
// //       pdfPreview.innerHTML = "";
// //       const file = judicialInput.files[0];
// //       if (!file) return;

// //       if (file.type === "application/pdf" && file.size <= MAX_PDF_SIZE) {
// //         pdfPreview.innerHTML =
// //           `<iframe src="${URL.createObjectURL(file)}" width="100%" height="300"></iframe>`;
// //       }
// //       validateForm();
// //     });
// //   }

// //   /* =======================
// //      PHOTO DE PROFIL
// //   ======================= */
// //   if (profileInput && profilePreview) {
// //     profileInput.addEventListener("change", () => {
// //       if (profileInput.files[0]) {
// //         const reader = new FileReader();
// //         reader.onload = e => {
// //           profilePreview.src = e.target.result;
// //           profilePreview.style.display = "block";
// //         };
// //         reader.readAsDataURL(profileInput.files[0]);
// //       } else {
// //         profilePreview.style.display = "none";
// //       }
// //       validateForm();
// //     });
// //   }

// //   /* =======================
// //      TÉLÉPHONE + INDICATIF
// //   ======================= */
// //   if (countrySelect && phoneInput) {
// //     countrySelect.addEventListener("change", () => {
// //       const code = countryDialCodes[countrySelect.value];
// //       if (code && !phoneInput.value.startsWith("+")) {
// //         phoneInput.value = code + " ";
// //       }
// //       validateForm();
// //     });
// //   }

// //   /* =======================
// //      TOGGLE MOT DE PASSE
// //   ======================= */
// //   if (toggleBtn && toggleIcon && password1) {
// //     toggleBtn.addEventListener("click", () => {
// //       const show = password1.type === "password";
// //       password1.type = show ? "text" : "password";
// //       if (password2) password2.type = show ? "text" : "password";
// //       toggleIcon.textContent = show ? "🙈" : "👁️";
// //     });
// //   }

// //   /* =======================
// //      CAPS LOCK
// //   ======================= */
// //   if (password1 && capsHint) {
// //     ["keydown", "keyup", "focus"].forEach(evt =>
// //       password1.addEventListener(evt, e =>
// //         capsHint.classList.toggle("d-none", !e.getModifierState("CapsLock"))
// //       )
// //     );
// //     password1.addEventListener("blur", () => capsHint.classList.add("d-none"));
// //   }

// //   /* =======================
// //      SUBMIT
// //   ======================= */
// //   form.addEventListener("input", validateForm);

// //   form.addEventListener("submit", e => {
// //     e.preventDefault();
// //     if (!validateForm()) return;

// //     submitBtn.disabled = true;
// //     submitBtn.setAttribute("aria-busy", "true");
// //     form.submit();
// //   });

// //   validateForm();
// // });






// // document.addEventListener("DOMContentLoaded", function () {

// //   const form = document.querySelector("form[method='post']");
// //   if (!form) return;

// //   const submitBtn = form.querySelector("button[type='submit']");
// //   const passwordInput = form.querySelector("input[type='password']");
// //   const toggleBtn = document.getElementById("togglePassword");
// //   const toggleIcon = document.getElementById("togglePasswordIcon");
// //   const capsHint = document.getElementById("capsLockHint");

// //   const profileInput = form.querySelector('input[name="profile_picture"]');
// //   const profilePreview = document.getElementById("profile_picture");

// //   const judicialInput = document.getElementById("id_judicial_record");
// //   const pdfPreview = document.getElementById("pdf-preview");

// //   const countrySelect = document.getElementById("id_country_of_residence");
// //   const phoneInput = document.getElementById("id_phone_number");

// //   const MAX_PDF_SIZE = 2 * 1024 * 1024;

// //   const countryDialCodes = {
// //     "SN": "+221",
// //     "FR": "+33",
// //     "BE": "+32",
// //     "CI": "+225",
// //     "US": "+1",
// //     "GB": "+44"
// //   };

// //   const errorMessages = {
// //     text: "Ce champ est requis.",
// //     email: "Entrez une adresse email valide.",
// //     password: "Le mot de passe doit contenir au moins 6 caractères.",
// //     checkbox: "Vous devez accepter les conditions générales.",
// //     file: "Vous devez sélectionner un fichier.",
// //     pdf: "Le fichier doit être au format PDF.",
// //     pdfSize: "Le fichier ne doit pas dépasser 2 Mo."
// //   };

// //   const validateField = (field) => {
// //     let valid = true;
// //     let message = "";

// //     if (field.type === "checkbox") {
// //       valid = field.checked;
// //       message = errorMessages.checkbox;
// //     } else if (field.type === "file" && field.required) {
// //       valid = field.files.length > 0;
// //       message = errorMessages.file;
// //     } else if (field.type === "email") {
// //       valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value);
// //       message = errorMessages.email;
// //     } else if (field.type === "password") {
// //       valid = field.value.trim().length >= 6;
// //       message = errorMessages.password;
// //     } else {
// //       valid = field.value.trim() !== "";
// //       message = errorMessages.text;
// //     }

// //     field.classList.toggle("is-valid", valid);
// //     field.classList.toggle("is-invalid", !valid);

// //     const errorDiv = field.closest(".mb-3, .form-check")?.querySelector(".text-danger");
// //     if (errorDiv) errorDiv.textContent = valid ? "" : message;

// //     return valid;
// //   };

// //   const validateForm = () => {
// //     let allValid = true;
// //     form.querySelectorAll(".form-control, .form-check-input").forEach(field => {
// //       if (!validateField(field)) allValid = false;
// //     });
// //     submitBtn.disabled = !allValid;
// //   };

// //   // PDF preview + validation
// //   if (judicialInput) {
// //     judicialInput.required = true;
// //     judicialInput.addEventListener("change", () => {
// //       pdfPreview.innerHTML = "";
// //       const file = judicialInput.files[0];
// //       if (!file) return;

// //       if (file.type !== "application/pdf") {
// //         pdfPreview.innerHTML = `<p class="text-danger">${errorMessages.pdf}</p>`;
// //         judicialInput.classList.add("is-invalid");
// //         return;
// //       }

// //       if (file.size > MAX_PDF_SIZE) {
// //         pdfPreview.innerHTML = `<p class="text-danger">${errorMessages.pdfSize}</p>`;
// //         judicialInput.classList.add("is-invalid");
// //         return;
// //       }

// //       judicialInput.classList.add("is-valid");
// //       const url = URL.createObjectURL(file);
// //       pdfPreview.innerHTML = `<iframe src="${url}" width="100%" height="300" style="border:1px solid #ddd;"></iframe>`;
// //       validateForm();
// //     });
// //   }

// //   // Profile picture preview
// //   if (profileInput && profilePreview) {
// //     profileInput.addEventListener("change", () => {
// //       if (profileInput.files[0]) {
// //         const reader = new FileReader();
// //         reader.onload = e => {
// //           profilePreview.src = e.target.result;
// //           profilePreview.style.display = "block";
// //         };
// //         reader.readAsDataURL(profileInput.files[0]);
// //       } else {
// //         profilePreview.style.display = "none";
// //       }
// //       validateForm();
// //     });
// //   }

// //   // Phone prefix by country
// //   if (countrySelect && phoneInput) {
// //     countrySelect.addEventListener("change", function () {
// //       const code = countryDialCodes[this.value];
// //       if (code && !phoneInput.value.startsWith("+")) {
// //         phoneInput.value = code + " ";
// //       }
// //     });
// //   }

// //   // Password toggle
// //   if (toggleBtn && toggleIcon && passwordInput) {
// //     toggleBtn.addEventListener("click", () => {
// //       const show = passwordInput.type === "password";
// //       passwordInput.type = show ? "text" : "password";
// //       toggleIcon.textContent = show ? "🙈" : "👁️";
// //     });
// //   }

// //   // Caps lock hint
// //   if (passwordInput && capsHint) {
// //     ["keydown", "keyup", "focus"].forEach(evt =>
// //       passwordInput.addEventListener(evt, e =>
// //         capsHint.classList.toggle("d-none", !e.getModifierState("CapsLock"))
// //       )
// //     );
// //     passwordInput.addEventListener("blur", () => capsHint.classList.add("d-none"));
// //   }

// //   // Submit anti double-click
// //   form.addEventListener("submit", e => {
// //     e.preventDefault();
// //     validateForm();
// //     if (submitBtn.disabled) return;

// //     submitBtn.disabled = true;
// //     submitBtn.setAttribute("aria-busy", "true");

// //     if (!submitBtn.querySelector(".spinner-border")) {
// //       const spinner = document.createElement("span");
// //       spinner.className = "spinner-border spinner-border-sm ms-2";
// //       submitBtn.appendChild(spinner);
// //     }

// //     form.submit();
// //   });

// //   validateForm();
// // });

// // document.addEventListener("DOMContentLoaded", function () {
// //   const p1 = document.querySelector(".password-strong");
// //   const p2 = document.querySelector(".password-confirm");

// //   if (p1 && p2) {
// //     p2.addEventListener("input", () => {
// //       if (p2.value && p1.value !== p2.value) {
// //         p2.setCustomValidity("Les mots de passe ne sont pas identiques.");
// //       } else {
// //         p2.setCustomValidity("");
// //       }
// //     });
// //   }
// // });







// // document.addEventListener("DOMContentLoaded", () => {

// //   /* ---------------------------------------------------------
// //      ELEMENTS
// //   --------------------------------------------------------- */
// //   const form = document.getElementById("economic-form");
// //   const submitBtn = document.getElementById("submit-btn");
// //   const termsCheckbox = document.getElementById("id_terms");
// //   const inputs = form.querySelectorAll(".form-control, .form-check-input");

// //   const passwordInput =
// //     form.querySelector("input[type='password']") ||
// //     form.querySelector("input[name='password']");
// //   const toggleBtn = form.querySelector("#togglePassword");
// //   const toggleIcon = form.querySelector("#togglePasswordIcon");
// //   const capsHint = form.querySelector("#capsLockHint");

// //   /* ---------------------------------------------------------
// //      FOCUS AUTOMATIQUE SUR LE PREMIER CHAMP
// //   --------------------------------------------------------- */
// //   if (inputs.length) {
// //     setTimeout(() => inputs[0].focus(), 80);
// //   }

// //   /* ---------------------------------------------------------
// //      CAPS LOCK DETECTOR
// //   --------------------------------------------------------- */
// //   if (passwordInput && capsHint) {
// //     const detectCaps = (e) => {
// //       const active = e.getModifierState?.("CapsLock");
// //       capsHint.classList.toggle("d-none", !active);
// //     };
// //     ["keyup", "keydown", "focus"].forEach(evt =>
// //       passwordInput.addEventListener(evt, detectCaps)
// //     );
// //     passwordInput.addEventListener("blur", () =>
// //       capsHint.classList.add("d-none")
// //     );
// //   }

// //   /* ---------------------------------------------------------
// //      TOGGLE PASSWORD VISIBILITY
// //   --------------------------------------------------------- */
// //   if (toggleBtn && passwordInput && toggleIcon) {
// //     toggleBtn.addEventListener("click", () => {
// //       const show = passwordInput.type === "password";
// //       passwordInput.type = show ? "text" : "password";
// //       toggleIcon.textContent = show ? "🙈" : "👁️";
// //       toggleBtn.setAttribute(
// //         "aria-label",
// //         show ? "Masquer le mot de passe" : "Afficher le mot de passe"
// //       );
// //       passwordInput.focus({ preventScroll: true });
// //     });
// //   }

// //   /* ---------------------------------------------------------
// //      VALIDATION INSTANTANEE
// //   --------------------------------------------------------- */
// //   const validateField = (field) => {
// //     let valid = true;

// //     if (field.type === "checkbox") {
// //       valid = field.checked;
// //     } else if (field.type === "file") {
// //       valid = field.files.length > 0 || !field.required;
// //     } else if (field.type === "email") {
// //       valid = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(field.value);
// //     } else if (field.type === "password") {
// //       valid = field.value.trim().length >= 6; // exemple: password >=6 caractères
// //     } else {
// //       valid = field.value.trim() !== "";
// //     }

// //     field.classList.toggle("is-valid", valid);
// //     field.classList.toggle("is-invalid", !valid);

// //     return valid;
// //   };

// //   const validateForm = () => {
// //     let allValid = true;
// //     inputs.forEach(field => {
// //       if (!validateField(field)) allValid = false;
// //     });
// //     submitBtn.disabled = !allValid;
// //   };

// //   inputs.forEach(field => {
// //     field.addEventListener("input", validateForm);
// //     field.addEventListener("change", validateForm);
// //   });

// //   /* ---------------------------------------------------------
// //      APERCU DES FICHIERS
// //   --------------------------------------------------------- */
// //   const profilePreview = document.getElementById("profile_picture");
// //   const profileInput = form.querySelector('input[name="profile_picture"]');
// //   if (profileInput) {
// //     profileInput.addEventListener("change", () => {
// //       if (profileInput.files && profileInput.files[0]) {
// //         const reader = new FileReader();
// //         reader.onload = (e) => {
// //           profilePreview.src = e.target.result;
// //           profilePreview.style.display = "block";
// //         };
// //         reader.readAsDataURL(profileInput.files[0]);
// //       } else {
// //         profilePreview.style.display = "none";
// //       }
// //       validateForm();
// //     });
// //   }

// //   const tradePreview = document.getElementById("trade_register_document");
// //   const tradeInput = form.querySelector('input[name="trade_register_document"]');
// //   if (tradeInput) {
// //     tradeInput.addEventListener("change", () => {
// //       tradePreview.textContent = tradeInput.files.length ? tradeInput.files[0].name : "Aucun fichier sélectionné";
// //       validateForm();
// //     });
// //   }

// //   /* ---------------------------------------------------------
// //      ANTI DOUBLE-SUBMIT + SPINNER
// //   --------------------------------------------------------- */
// //   form.addEventListener("submit", () => {
// //     if (submitBtn.disabled) return;
// //     submitBtn.disabled = true;
// //     submitBtn.setAttribute("aria-busy", "true");

// //     if (!submitBtn.querySelector(".spinner-border")) {
// //       const spinner = document.createElement("span");
// //       spinner.className = "spinner-border spinner-border-sm ms-2";
// //       spinner.setAttribute("role", "status");
// //       spinner.setAttribute("aria-hidden", "true");
// //       submitBtn.appendChild(spinner);
// //     }
// //   });

// //   /* ---------------------------------------------------------
// //      VALIDATION INITIAL
// //   --------------------------------------------------------- */
// //   validateForm();

// // });











// // document.addEventListener("DOMContentLoaded", function () {
// //   const form = document.querySelector("form");
// //   const password1 = document.querySelector('input[name="password1"], input[name="password"]');
// //   const password2 = document.querySelector('input[name="password2"], input[name="password_confirm"]');

// //   if (form && password1 && password2) {
// //     form.addEventListener("submit", function (e) {
// //       if (password1.value !== password2.value) {
// //         e.preventDefault();
// //         alert("⚠️ Les mots de passe ne correspondent pas.");
// //         password2.focus();
// //         password2.classList.add("is-invalid");
// //       } else {
// //         password2.classList.remove("is-invalid");
// //       }
// //     });
// //   }

// //   // Amélioration UX pour les fichiers choisis
// //   const fileInputs = document.querySelectorAll('input[type="file"]');
// //   fileInputs.forEach(input => {
// //     input.addEventListener("change", function () {
// //       const label = this.nextElementSibling;
// //       if (label && this.files.length > 0) {
// //         label.textContent = this.files[0].name;
// //       }
// //     });
// //   });
// // });



// // // signup.js

// // document.addEventListener("DOMContentLoaded", () => {
// //   const form = document.querySelector("form");

// //   if (form) {
// //     console.log("Signup form ready.");

// //     // Simple client-side UX improvement
// //     const inputs = form.querySelectorAll("input, select, textarea");
// //     inputs.forEach(input => {
// //       input.addEventListener("focus", () => {
// //         input.style.borderColor = "#007bff";
// //       });
// //       input.addEventListener("blur", () => {
// //         input.style.borderColor = "#ced4da";
// //       });
// //     });

// //     form.addEventListener("submit", () => {
// //       console.log("Submitting signup form...");
// //     });
// //   }
// // });
