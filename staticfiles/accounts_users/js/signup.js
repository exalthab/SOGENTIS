document.addEventListener("DOMContentLoaded", function () {

  const form = document.querySelector("form[method='post']");
  if (!form) return;

  const submitBtn = form.querySelector("button[type='submit']");

  const password1 = form.querySelector(".password-strong");
  const password2 = form.querySelector(".password-confirm");
  const toggleBtn = document.getElementById("togglePassword");
  const toggleIcon = document.getElementById("togglePasswordIcon");
  const capsHint = document.getElementById("capsLockHint");

  const profileInput = form.querySelector('input[name="profile_picture"]');
  const profilePreview = document.getElementById("profile_picture");

  const judicialInput = document.getElementById("id_judicial_record");
  const pdfPreview = document.getElementById("pdf-preview");

  const countrySelect = document.getElementById("id_country_of_residence");
  const phoneInput = document.getElementById("id_phone_number");

  const MAX_PDF_SIZE = 2 * 1024 * 1024;

  const countryDialCodes = {
    SN: "+221",
    FR: "+33",
    BE: "+32",
    CI: "+225",
    US: "+1",
    GB: "+44"
  };

  let currentDialCode = "";

  /* =======================
     RÈGLES DE VALIDATION
  ======================= */
  const strongPassword = v =>
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/.test(v);

  const validPhone = v =>
    /^\+[0-9]{8,15}$/.test(v);

  const validateField = (field) => {
    let valid = true;

    if (field === phoneInput) {
      const fullPhone = currentDialCode + field.value.replace(/\s+/g, "");
      valid = validPhone(fullPhone);
    } else if (field.type === "password") {
      valid = strongPassword(field.value);
    } else if (field.type === "email") {
      valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value);
    } else if (field.type === "checkbox") {
      valid = field.checked;
    } else if (field.type === "file" && field.required) {
      valid = field.files.length > 0;
    } else {
      valid = field.value.trim() !== "";
    }

    field.classList.toggle("is-valid", valid);
    field.classList.toggle("is-invalid", !valid);
    return valid;
  };

  const validateForm = () => {
    let ok = true;

    form.querySelectorAll(".form-control, .form-check-input").forEach(field => {
      if (!validateField(field)) ok = false;
    });

    // mots de passe identiques
    if (password1 && password2 && password1.value !== password2.value) {
      password2.setCustomValidity("Les mots de passe ne sont pas identiques.");
      password2.classList.add("is-invalid");
      ok = false;
    } else if (password2) {
      password2.setCustomValidity("");
    }

    // casier judiciaire
    if (judicialInput) {
      const f = judicialInput.files[0];
      if (!f || f.type !== "application/pdf" || f.size > MAX_PDF_SIZE) {
        ok = false;
        judicialInput.classList.add("is-invalid");
      } else {
        judicialInput.classList.add("is-valid");
      }
    }

    submitBtn.disabled = !ok;
    return ok;
  };

  /* =======================
     PDF – CASIER JUDICIAIRE
  ======================= */
  if (judicialInput) {
    judicialInput.required = true;
    judicialInput.addEventListener("change", () => {
      pdfPreview.innerHTML = "";
      const file = judicialInput.files[0];
      if (!file) return;

      if (file.type === "application/pdf" && file.size <= MAX_PDF_SIZE) {
        pdfPreview.innerHTML =
          `<iframe src="${URL.createObjectURL(file)}" width="100%" height="300"></iframe>`;
      }
      validateForm();
    });
  }

  /* =======================
     PHOTO DE PROFIL
  ======================= */
  if (profileInput && profilePreview) {
    profileInput.addEventListener("change", () => {
      if (profileInput.files[0]) {
        const reader = new FileReader();
        reader.onload = e => {
          profilePreview.src = e.target.result;
          profilePreview.style.display = "block";
        };
        reader.readAsDataURL(profileInput.files[0]);
      } else {
        profilePreview.style.display = "none";
      }
      validateForm();
    });
  }

  /* =======================
     TÉLÉPHONE + INDICATIF (SANS RÉÉCRITURE)
  ======================= */
  if (countrySelect && phoneInput) {

    const applyDialCode = () => {
      currentDialCode = countryDialCodes[countrySelect.value] || "";
      phoneInput.placeholder = currentDialCode
        ? `${currentDialCode} XXXXXXXX`
        : "XXXXXXXX";
    };

    countrySelect.addEventListener("change", applyDialCode);
    applyDialCode();

    // empêcher l'utilisateur de saisir +
    phoneInput.addEventListener("input", () => {
      phoneInput.value = phoneInput.value.replace(/\+/g, "");
      validateForm();
    });
  }

  /* =======================
     TOGGLE MOT DE PASSE
  ======================= */
  if (toggleBtn && toggleIcon && password1) {
    toggleBtn.addEventListener("click", () => {
      const show = password1.type === "password";
      password1.type = show ? "text" : "password";
      if (password2) password2.type = show ? "text" : "password";
      toggleIcon.textContent = show ? "🙈" : "👁️";
    });
  }

  /* =======================
     CAPS LOCK
  ======================= */
  if (password1 && capsHint) {
    ["keydown", "keyup", "focus"].forEach(evt =>
      password1.addEventListener(evt, e =>
        capsHint.classList.toggle("d-none", !e.getModifierState("CapsLock"))
      )
    );
    password1.addEventListener("blur", () => capsHint.classList.add("d-none"));
  }

  /* =======================
     SUBMIT
  ======================= */
  form.addEventListener("input", validateForm);

  form.addEventListener("submit", e => {
    e.preventDefault();
    if (!validateForm()) return;

    // recomposer le numéro final avant envoi
    if (phoneInput && currentDialCode) {
      phoneInput.value =
        currentDialCode + phoneInput.value.replace(/\s+/g, "");
    }

    submitBtn.disabled = true;
    submitBtn.setAttribute("aria-busy", "true");
    form.submit();
  });

  validateForm();
});










// // static/accounts_users/js/signup.js
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

//   /* =======================
//      RÈGLES DE VALIDATION
//   ======================= */
//   const strongPassword = (v) =>
//     /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/.test(v);

//   const validPhone = (v) =>
//     /^\+[0-9]{8,15}$/.test(v);

//   const validateField = (field) => {
//     let valid = true;

//     if (field === phoneInput) {
//       valid = validPhone(field.value);
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

//     // mot de passe identique
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
//      TÉLÉPHONE + INDICATIF
//   ======================= */
//   if (countrySelect && phoneInput) {
//     countrySelect.addEventListener("change", () => {
//       const code = countryDialCodes[countrySelect.value];
//       if (code && !phoneInput.value.startsWith("+")) {
//         phoneInput.value = code + " ";
//       }
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

//     submitBtn.disabled = true;
//     submitBtn.setAttribute("aria-busy", "true");
//     form.submit();
//   });

//   validateForm();
// });






// document.addEventListener("DOMContentLoaded", function () {

//   const form = document.querySelector("form[method='post']");
//   if (!form) return;

//   const submitBtn = form.querySelector("button[type='submit']");
//   const passwordInput = form.querySelector("input[type='password']");
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
//     "SN": "+221",
//     "FR": "+33",
//     "BE": "+32",
//     "CI": "+225",
//     "US": "+1",
//     "GB": "+44"
//   };

//   const errorMessages = {
//     text: "Ce champ est requis.",
//     email: "Entrez une adresse email valide.",
//     password: "Le mot de passe doit contenir au moins 6 caractères.",
//     checkbox: "Vous devez accepter les conditions générales.",
//     file: "Vous devez sélectionner un fichier.",
//     pdf: "Le fichier doit être au format PDF.",
//     pdfSize: "Le fichier ne doit pas dépasser 2 Mo."
//   };

//   const validateField = (field) => {
//     let valid = true;
//     let message = "";

//     if (field.type === "checkbox") {
//       valid = field.checked;
//       message = errorMessages.checkbox;
//     } else if (field.type === "file" && field.required) {
//       valid = field.files.length > 0;
//       message = errorMessages.file;
//     } else if (field.type === "email") {
//       valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value);
//       message = errorMessages.email;
//     } else if (field.type === "password") {
//       valid = field.value.trim().length >= 6;
//       message = errorMessages.password;
//     } else {
//       valid = field.value.trim() !== "";
//       message = errorMessages.text;
//     }

//     field.classList.toggle("is-valid", valid);
//     field.classList.toggle("is-invalid", !valid);

//     const errorDiv = field.closest(".mb-3, .form-check")?.querySelector(".text-danger");
//     if (errorDiv) errorDiv.textContent = valid ? "" : message;

//     return valid;
//   };

//   const validateForm = () => {
//     let allValid = true;
//     form.querySelectorAll(".form-control, .form-check-input").forEach(field => {
//       if (!validateField(field)) allValid = false;
//     });
//     submitBtn.disabled = !allValid;
//   };

//   // PDF preview + validation
//   if (judicialInput) {
//     judicialInput.required = true;
//     judicialInput.addEventListener("change", () => {
//       pdfPreview.innerHTML = "";
//       const file = judicialInput.files[0];
//       if (!file) return;

//       if (file.type !== "application/pdf") {
//         pdfPreview.innerHTML = `<p class="text-danger">${errorMessages.pdf}</p>`;
//         judicialInput.classList.add("is-invalid");
//         return;
//       }

//       if (file.size > MAX_PDF_SIZE) {
//         pdfPreview.innerHTML = `<p class="text-danger">${errorMessages.pdfSize}</p>`;
//         judicialInput.classList.add("is-invalid");
//         return;
//       }

//       judicialInput.classList.add("is-valid");
//       const url = URL.createObjectURL(file);
//       pdfPreview.innerHTML = `<iframe src="${url}" width="100%" height="300" style="border:1px solid #ddd;"></iframe>`;
//       validateForm();
//     });
//   }

//   // Profile picture preview
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

//   // Phone prefix by country
//   if (countrySelect && phoneInput) {
//     countrySelect.addEventListener("change", function () {
//       const code = countryDialCodes[this.value];
//       if (code && !phoneInput.value.startsWith("+")) {
//         phoneInput.value = code + " ";
//       }
//     });
//   }

//   // Password toggle
//   if (toggleBtn && toggleIcon && passwordInput) {
//     toggleBtn.addEventListener("click", () => {
//       const show = passwordInput.type === "password";
//       passwordInput.type = show ? "text" : "password";
//       toggleIcon.textContent = show ? "🙈" : "👁️";
//     });
//   }

//   // Caps lock hint
//   if (passwordInput && capsHint) {
//     ["keydown", "keyup", "focus"].forEach(evt =>
//       passwordInput.addEventListener(evt, e =>
//         capsHint.classList.toggle("d-none", !e.getModifierState("CapsLock"))
//       )
//     );
//     passwordInput.addEventListener("blur", () => capsHint.classList.add("d-none"));
//   }

//   // Submit anti double-click
//   form.addEventListener("submit", e => {
//     e.preventDefault();
//     validateForm();
//     if (submitBtn.disabled) return;

//     submitBtn.disabled = true;
//     submitBtn.setAttribute("aria-busy", "true");

//     if (!submitBtn.querySelector(".spinner-border")) {
//       const spinner = document.createElement("span");
//       spinner.className = "spinner-border spinner-border-sm ms-2";
//       submitBtn.appendChild(spinner);
//     }

//     form.submit();
//   });

//   validateForm();
// });

// document.addEventListener("DOMContentLoaded", function () {
//   const p1 = document.querySelector(".password-strong");
//   const p2 = document.querySelector(".password-confirm");

//   if (p1 && p2) {
//     p2.addEventListener("input", () => {
//       if (p2.value && p1.value !== p2.value) {
//         p2.setCustomValidity("Les mots de passe ne sont pas identiques.");
//       } else {
//         p2.setCustomValidity("");
//       }
//     });
//   }
// });







// document.addEventListener("DOMContentLoaded", () => {

//   /* ---------------------------------------------------------
//      ELEMENTS
//   --------------------------------------------------------- */
//   const form = document.getElementById("economic-form");
//   const submitBtn = document.getElementById("submit-btn");
//   const termsCheckbox = document.getElementById("id_terms");
//   const inputs = form.querySelectorAll(".form-control, .form-check-input");

//   const passwordInput =
//     form.querySelector("input[type='password']") ||
//     form.querySelector("input[name='password']");
//   const toggleBtn = form.querySelector("#togglePassword");
//   const toggleIcon = form.querySelector("#togglePasswordIcon");
//   const capsHint = form.querySelector("#capsLockHint");

//   /* ---------------------------------------------------------
//      FOCUS AUTOMATIQUE SUR LE PREMIER CHAMP
//   --------------------------------------------------------- */
//   if (inputs.length) {
//     setTimeout(() => inputs[0].focus(), 80);
//   }

//   /* ---------------------------------------------------------
//      CAPS LOCK DETECTOR
//   --------------------------------------------------------- */
//   if (passwordInput && capsHint) {
//     const detectCaps = (e) => {
//       const active = e.getModifierState?.("CapsLock");
//       capsHint.classList.toggle("d-none", !active);
//     };
//     ["keyup", "keydown", "focus"].forEach(evt =>
//       passwordInput.addEventListener(evt, detectCaps)
//     );
//     passwordInput.addEventListener("blur", () =>
//       capsHint.classList.add("d-none")
//     );
//   }

//   /* ---------------------------------------------------------
//      TOGGLE PASSWORD VISIBILITY
//   --------------------------------------------------------- */
//   if (toggleBtn && passwordInput && toggleIcon) {
//     toggleBtn.addEventListener("click", () => {
//       const show = passwordInput.type === "password";
//       passwordInput.type = show ? "text" : "password";
//       toggleIcon.textContent = show ? "🙈" : "👁️";
//       toggleBtn.setAttribute(
//         "aria-label",
//         show ? "Masquer le mot de passe" : "Afficher le mot de passe"
//       );
//       passwordInput.focus({ preventScroll: true });
//     });
//   }

//   /* ---------------------------------------------------------
//      VALIDATION INSTANTANEE
//   --------------------------------------------------------- */
//   const validateField = (field) => {
//     let valid = true;

//     if (field.type === "checkbox") {
//       valid = field.checked;
//     } else if (field.type === "file") {
//       valid = field.files.length > 0 || !field.required;
//     } else if (field.type === "email") {
//       valid = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(field.value);
//     } else if (field.type === "password") {
//       valid = field.value.trim().length >= 6; // exemple: password >=6 caractères
//     } else {
//       valid = field.value.trim() !== "";
//     }

//     field.classList.toggle("is-valid", valid);
//     field.classList.toggle("is-invalid", !valid);

//     return valid;
//   };

//   const validateForm = () => {
//     let allValid = true;
//     inputs.forEach(field => {
//       if (!validateField(field)) allValid = false;
//     });
//     submitBtn.disabled = !allValid;
//   };

//   inputs.forEach(field => {
//     field.addEventListener("input", validateForm);
//     field.addEventListener("change", validateForm);
//   });

//   /* ---------------------------------------------------------
//      APERCU DES FICHIERS
//   --------------------------------------------------------- */
//   const profilePreview = document.getElementById("profile_picture");
//   const profileInput = form.querySelector('input[name="profile_picture"]');
//   if (profileInput) {
//     profileInput.addEventListener("change", () => {
//       if (profileInput.files && profileInput.files[0]) {
//         const reader = new FileReader();
//         reader.onload = (e) => {
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

//   const tradePreview = document.getElementById("trade_register_document");
//   const tradeInput = form.querySelector('input[name="trade_register_document"]');
//   if (tradeInput) {
//     tradeInput.addEventListener("change", () => {
//       tradePreview.textContent = tradeInput.files.length ? tradeInput.files[0].name : "Aucun fichier sélectionné";
//       validateForm();
//     });
//   }

//   /* ---------------------------------------------------------
//      ANTI DOUBLE-SUBMIT + SPINNER
//   --------------------------------------------------------- */
//   form.addEventListener("submit", () => {
//     if (submitBtn.disabled) return;
//     submitBtn.disabled = true;
//     submitBtn.setAttribute("aria-busy", "true");

//     if (!submitBtn.querySelector(".spinner-border")) {
//       const spinner = document.createElement("span");
//       spinner.className = "spinner-border spinner-border-sm ms-2";
//       spinner.setAttribute("role", "status");
//       spinner.setAttribute("aria-hidden", "true");
//       submitBtn.appendChild(spinner);
//     }
//   });

//   /* ---------------------------------------------------------
//      VALIDATION INITIAL
//   --------------------------------------------------------- */
//   validateForm();

// });











// document.addEventListener("DOMContentLoaded", function () {
//   const form = document.querySelector("form");
//   const password1 = document.querySelector('input[name="password1"], input[name="password"]');
//   const password2 = document.querySelector('input[name="password2"], input[name="password_confirm"]');

//   if (form && password1 && password2) {
//     form.addEventListener("submit", function (e) {
//       if (password1.value !== password2.value) {
//         e.preventDefault();
//         alert("⚠️ Les mots de passe ne correspondent pas.");
//         password2.focus();
//         password2.classList.add("is-invalid");
//       } else {
//         password2.classList.remove("is-invalid");
//       }
//     });
//   }

//   // Amélioration UX pour les fichiers choisis
//   const fileInputs = document.querySelectorAll('input[type="file"]');
//   fileInputs.forEach(input => {
//     input.addEventListener("change", function () {
//       const label = this.nextElementSibling;
//       if (label && this.files.length > 0) {
//         label.textContent = this.files[0].name;
//       }
//     });
//   });
// });



// // signup.js

// document.addEventListener("DOMContentLoaded", () => {
//   const form = document.querySelector("form");

//   if (form) {
//     console.log("Signup form ready.");

//     // Simple client-side UX improvement
//     const inputs = form.querySelectorAll("input, select, textarea");
//     inputs.forEach(input => {
//       input.addEventListener("focus", () => {
//         input.style.borderColor = "#007bff";
//       });
//       input.addEventListener("blur", () => {
//         input.style.borderColor = "#ced4da";
//       });
//     });

//     form.addEventListener("submit", () => {
//       console.log("Submitting signup form...");
//     });
//   }
// });
