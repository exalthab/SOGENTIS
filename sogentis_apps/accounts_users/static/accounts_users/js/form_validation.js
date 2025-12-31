// static/accounts_users/js/form_validation.js

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form[method='post']");
  if (!form) return;

  const submitBtn = form.querySelector("button[type='submit']");

  // =====================================================
  // 🎯 IDS DJANGO (CONFORMES AUX FORMS)
  // =====================================================
  const emailInput = document.getElementById("id_email");
  const phoneInput = document.getElementById("id_phone_number");

  const password1Input = document.getElementById("id_password1");
  const password2Input = document.getElementById("id_password2");

  const birthDateInput = document.getElementById("id_date_of_birth");
  const membershipDateInput = document.getElementById("id_membership_date");

  const countrySelect =
    document.getElementById("id_country_of_residence") ||
    document.getElementById("id_country_of_birth");

  const judicialInput = document.getElementById("id_judicial_record");
  const profilePictureInput = document.getElementById("id_profile_picture");
  const pdfPreview = document.getElementById("pdf-preview");

  // =====================================================
  // ⚙️ CONSTANTES
  // =====================================================
  const MAX_PDF_SIZE = 2 * 1024 * 1024;   // 2 Mo
  const MAX_IMAGE_SIZE = 5 * 1024 * 1024; // 5 Mo

  // ISO alpha-2 → indicatif (cohérent phonenumber_field)
  const COUNTRY_PHONE_PREFIX = {
    SN: "+221",
    FR: "+33",
    BE: "+32",
    CH: "+41",
    CA: "+1",
    US: "+1",
    MA: "+212",
    CI: "+225",
    BF: "+226",
    ML: "+223",
    TG: "+228",
    BJ: "+229",
    NE: "+227",
  };

  // =====================================================
  // 🧩 UTILS
  // =====================================================
  const setValidity = (field, valid) => {
    if (!field) return;
    field.classList.toggle("is-valid", valid);
    field.classList.toggle("is-invalid", !valid);
  };

  // =====================================================
  // 📧 EMAIL (BASIQUE)
  // =====================================================
  const validateEmail = () => {
    if (!emailInput) return true;
    const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value.trim());
    setValidity(emailInput, ok);
    return ok;
  };

  // =====================================================
// ✉️ VALIDATION EMAIL ASYNCHRONE (AJAX)
// =====================================================
(function asyncEmailCheck() {
  const emailInput = document.getElementById("id_email");
  if (!emailInput) return;

  let controller = null;
  let debounceTimer = null;

  const setState = (state, message = "") => {
    emailInput.classList.remove("is-valid", "is-invalid");
    const feedbackId = "email-async-feedback";
    let fb = document.getElementById(feedbackId);

    if (!fb) {
      fb = document.createElement("div");
      fb.id = feedbackId;
      fb.className = "form-text";
      emailInput.parentNode.appendChild(fb);
    }

    if (state === "checking") {
      fb.textContent = "Vérification de l’email…";
      fb.className = "form-text text-muted";
    } else if (state === "valid") {
      emailInput.classList.add("is-valid");
      fb.textContent = "Email disponible";
      fb.className = "form-text text-success";
    } else if (state === "invalid") {
      emailInput.classList.add("is-invalid");
      fb.textContent = message || "Email déjà utilisé";
      fb.className = "form-text text-danger";
    } else {
      fb.textContent = "";
    }
  };

  const checkEmail = async (email) => {
    if (controller) controller.abort();
    controller = new AbortController();

    setState("checking");

    try {
      const res = await fetch(
        `/accounts_users/ajax/check-email/?email=${encodeURIComponent(email)}`,
        { signal: controller.signal }
      );
      const data = await res.json();

      if (data.available) {
        setState("valid");
      } else {
        setState("invalid", "Cet email est déjà utilisé");
      }
    } catch (e) {
      // silencieux : on laisse le backend décider au submit
      setState("idle");
    }
  };

  emailInput.addEventListener("input", () => {
    const email = emailInput.value.trim();
    clearTimeout(debounceTimer);

    if (!email || email.length < 5 || !email.includes("@")) {
      setState("idle");
      return;
    }

    debounceTimer = setTimeout(() => checkEmail(email), 400);
  });
})();

// =====================================================
// 📱 OTP TÉLÉPHONE (AJAX)
// =====================================================
(function phoneOTP() {
  const phoneInput = document.getElementById("id_phone_number");
  if (!phoneInput) return;

  let verified = false;

  const sendOTP = async () => {
    await fetch("/accounts_users/ajax/phone/send-otp/", {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `phone=${encodeURIComponent(phoneInput.value)}`,
    });
    alert("Code envoyé par SMS");
  };

  const verifyOTP = async (code) => {
    const res = await fetch("/accounts_users/ajax/phone/verify-otp/", {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `phone=${encodeURIComponent(phoneInput.value)}&code=${code}`,
    });
    const data = await res.json();
    verified = data.ok;
    alert(data.ok ? "Téléphone vérifié" : data.error);
  };

  // À brancher sur tes boutons UI (modal / input OTP)
})();


  // =====================================================
  // 📱 TÉLÉPHONE (SOUPLE – BACKEND FAIT FOI)
  // =====================================================
  const validatePhone = () => {
    if (!phoneInput) return true;
    const value = phoneInput.value.trim();

    // phonenumber_field gère la vraie validation côté Django
    const ok = value.length >= 7;
    setValidity(phoneInput, ok);
    return ok;
  };

  // =====================================================
  // 🔐 MOTS DE PASSE
  // =====================================================
  const validatePasswords = () => {
    if (!password1Input || !password2Input) return true;
    const ok =
      password1Input.value &&
      password1Input.value === password2Input.value;
    setValidity(password2Input, ok);
    return ok;
  };

  // =====================================================
  // 🎂 ÂGE (OPTIONNEL MAIS UTILE)
  // =====================================================
  const validateAge = () => {
    if (!birthDateInput || !membershipDateInput) return true;
    if (!birthDateInput.value || !membershipDateInput.value) return true;

    const birth = new Date(birthDateInput.value);
    const join = new Date(membershipDateInput.value);
    const age = (join - birth) / (1000 * 60 * 60 * 24 * 365.25);

    const ok = age >= 18;
    setValidity(membershipDateInput, ok);
    return ok;
  };

  // =====================================================
  // 📄 CASIER JUDICIAIRE
  // =====================================================
  const validateJudicialRecord = () => {
    if (!judicialInput || !judicialInput.files.length) return false;

    const file = judicialInput.files[0];
    const ok =
      file.type === "application/pdf" &&
      file.size <= MAX_PDF_SIZE;

    setValidity(judicialInput, ok);

    if (pdfPreview) {
      pdfPreview.innerHTML = ok
        ? `<iframe src="${URL.createObjectURL(file)}"
                    width="100%" height="300"
                    style="border:1px solid #ccc;"></iframe>`
        : "";
    }

    return ok;
  };

  // =====================================================
  // 🖼️ PHOTO (OPTIONNEL)
  // =====================================================
  const validateProfilePicture = () => {
    if (!profilePictureInput || !profilePictureInput.files.length) return true;

    const file = profilePictureInput.files[0];
    const ok =
      file.type.startsWith("image/") &&
      file.size <= MAX_IMAGE_SIZE;

    setValidity(profilePictureInput, ok);
    return ok;
  };

  // =====================================================
  // 🌍 SYNC PAYS → INDICATIF (UX SEULEMENT)
  // =====================================================
  const syncCountryToPhone = () => {
    if (!countrySelect || !phoneInput) return;

    // Ne jamais écraser une saisie existante
    if (phoneInput.value.trim()) return;

    const prefix = COUNTRY_PHONE_PREFIX[countrySelect.value];
    if (prefix) {
      phoneInput.value = prefix + " ";
      phoneInput.focus();
    }
  };

  // =====================================================
  // 🧪 VALIDATION GLOBALE
  // =====================================================
  const validateForm = () => {
    let ok = true;

    ok &= validateEmail();
    ok &= validatePhone();
    ok &= validatePasswords();
    ok &= validateAge();
    ok &= validateJudicialRecord();
    ok &= validateProfilePicture();

    submitBtn.disabled = !ok;
    return !!ok;
  };

  // =====================================================
  // 🧲 EVENTS
  // =====================================================
  form.addEventListener("input", validateForm);
  form.addEventListener("change", validateForm);

  if (countrySelect) {
    countrySelect.addEventListener("change", syncCountryToPhone);
  }

  form.addEventListener("submit", (e) => {
    if (!validateForm()) {
      e.preventDefault();
    } else {
      submitBtn.disabled = true;
      submitBtn.setAttribute("aria-busy", "true");
    }
  });

  // Init
  validateForm();
});









// document.addEventListener("DOMContentLoaded", function () {
//   const form = document.querySelector("form[method='post']");
//   const submitBtn = form.querySelector("button[type='submit']");
//   const emailInput = document.getElementById("id_email");
//   const phoneInput = document.getElementById("id_phone_number");
//   const judicialInput = document.getElementById("id_judicial_record");
//   const profilePictureInput = document.getElementById("id_profile_picture");
//   const profilePicturePreview = document.getElementById("profile_picture_preview");
//   const birthDateInput = document.getElementById("id_birth_date");
//   const joinDateInput = document.getElementById("id_join_date");
//   const ageErrorMessage = document.getElementById("age-error-message");
//   const password1Input = document.getElementById("id_password1");
//   const password2Input = document.getElementById("id_password2");

//   const MAX_PDF_SIZE = 2 * 1024 * 1024; // Taille maximale du fichier PDF (2MB)
//   const MAX_IMAGE_SIZE = 5 * 1024 * 1024; // Taille maximale du fichier image (5MB)

//   // Validation de l'email (format strict)
//   const validateEmail = (email) => {
//     const emailRegex = /^[a-zA-Z0-9]+([.#$^*-_]?[a-zA-Z0-9])*@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$/;
//     return emailRegex.test(email);
//   };

//   // Validation du téléphone : minimum 7 chiffres après l'indicatif
//   const validatePhone = (phone) => {
//     const phoneRegex = /^\+?[0-9]{7,15}$/;
//     return phoneRegex.test(phone);
//   };

//   // Validation du casier judiciaire (PDF uniquement et taille maximale)
//   const validateJudicialRecord = (file) => {
//     return file && file.type === "application/pdf" && file.size <= MAX_PDF_SIZE;
//   };

//   // Validation de la photo de profil (image seulement et taille maximale)
//   const validateProfilePicture = (file) => {
//     const fileType = file ? file.type.split("/")[0] : "";
//     const fileSize = file ? file.size : 0;
//     return fileType === "image" && fileSize <= MAX_IMAGE_SIZE;
//   };

//   // Validation de l'âge : l'utilisateur doit avoir minimum 19 ans
//   const validateAge = () => {
//     if (!birthDateInput || !joinDateInput) return true;

//     const birthDate = new Date(birthDateInput.value);
//     const joinDate = new Date(joinDateInput.value);
//     const ageDifference = (joinDate - birthDate) / (1000 * 60 * 60 * 24 * 365); // En années

//     if (ageDifference < 19) {
//       ageErrorMessage.style.display = "block";
//       joinDateInput.classList.add("is-invalid");
//       joinDateInput.classList.remove("is-valid");
//       return false;
//     } else {
//       ageErrorMessage.style.display = "none";
//       joinDateInput.classList.add("is-valid");
//       joinDateInput.classList.remove("is-invalid");
//       return true;
//     }
//   };

//   // Comparaison des mots de passe
//   const validatePasswordsMatch = () => {
//     if (password1Input && password2Input) {
//       const password1 = password1Input.value.trim();
//       const password2 = password2Input.value.trim();

//       if (password1 !== password2) {
//         password2Input.classList.add("is-invalid");
//         password2Input.classList.remove("is-valid");
//         return false;
//       } else {
//         password2Input.classList.add("is-valid");
//         password2Input.classList.remove("is-invalid");
//         return true;
//       }
//     }
//     return true;
//   };

//   // Validation générale de chaque champ
//   const validateField = (field) => {
//     let valid = true;

//     if (field.type === "email") {
//       valid = validateEmail(field.value);
//     } else if (field === phoneInput) {
//       valid = validatePhone(field.value);
//     } else if (field === judicialInput) {
//       const file = judicialInput.files[0];
//       valid = validateJudicialRecord(file);
//     } else if (field === profilePictureInput) {
//       const file = profilePictureInput.files[0];
//       valid = validateProfilePicture(file);
//     } else if (field === password2Input) {
//       valid = validatePasswordsMatch();
//     } else {
//       valid = field.value.trim() !== "";  // Vérification des autres champs
//     }

//     field.classList.toggle("is-valid", valid);
//     field.classList.toggle("is-invalid", !valid);
//     return valid;
//   };

//   // Validation du formulaire complet
//   const validateForm = () => {
//     let isValid = true;

//     // Vérification de tous les champs
//     form.querySelectorAll(".form-control, .form-check-input").forEach(field => {
//       if (!validateField(field)) isValid = false;
//     });

//     // Validation de l'âge (19 ans minimum)
//     if (!validateAge()) isValid = false;

//     submitBtn.disabled = !isValid;
//     return isValid;
//   };

//   // Validation sur chaque modification des champs
//   form.addEventListener("input", validateForm);

//   // Validation au moment de la soumission
//   form.addEventListener("submit", e => {
//     e.preventDefault();
//     if (!validateForm()) return;

//     submitBtn.disabled = true;
//     submitBtn.setAttribute("aria-busy", "true");
//     form.submit(); // Soumettre le formulaire après validation
//   });

//   // Aperçu de l'image de profil
//   if (profilePictureInput) {
//     profilePictureInput.addEventListener("change", () => {
//       const file = profilePictureInput.files[0];
//       if (file) {
//         const reader = new FileReader();
//         reader.onload = (e) => {
//           profilePicturePreview.src = e.target.result;
//           profilePicturePreview.style.display = "block";
//         };
//         reader.readAsDataURL(file);
//       } else {
//         profilePicturePreview.style.display = "none";
//       }
//       validateForm(); // Vérification après modification du fichier
//     });
//   }

//   // Aperçu et validation du fichier PDF (casier judiciaire)
//   if (judicialInput) {
//     judicialInput.addEventListener("change", () => {
//       const file = judicialInput.files[0];
//       const pdfPreview = document.getElementById("pdf-preview");

//       if (file && validateJudicialRecord(file)) {
//         pdfPreview.innerHTML = `<iframe src="${URL.createObjectURL(file)}" width="100%" height="300"></iframe>`;
//       } else {
//         pdfPreview.innerHTML = "";
//       }

//       validateForm(); // Vérification après modification du fichier PDF
//     });
//   }

//   // Validation du téléphone
//   if (phoneInput) {
//     phoneInput.addEventListener("input", () => {
//       validateField(phoneInput);
//     });
//   }

//   // Validation de l'email
//   if (emailInput) {
//     emailInput.addEventListener("input", () => {
//       validateField(emailInput);
//     });
//   }

//   // Validation des dates (naissance et adhésion)
//   if (birthDateInput && joinDateInput) {
//     joinDateInput.addEventListener("blur", validateAge);  // Vérifier quand l'adhésion est modifiée
//     birthDateInput.addEventListener("blur", validateAge);  // Vérifier si la date de naissance change
//   }

//   // Initialiser la validation au chargement
//   validateForm();
// });







// document.addEventListener("DOMContentLoaded", function () {
//   const form = document.querySelector("form[method='post']");
//   const submitBtn = form.querySelector("button[type='submit']");
//   const emailInput = document.getElementById("id_email");
//   const phoneInput = document.getElementById("id_phone_number");
//   const judicialInput = document.getElementById("id_judicial_record");
//   const profilePictureInput = document.getElementById("id_profile_picture");
//   const profilePicturePreview = document.getElementById("profile_picture_preview");
//   const birthDateInput = document.getElementById("id_birth_date");
//   const joinDateInput = document.getElementById("id_join_date");
//   const ageErrorMessage = document.getElementById("age-error-message");

//   const MAX_PDF_SIZE = 2 * 1024 * 1024; // Taille maximale du fichier PDF (2MB)
//   const MAX_IMAGE_SIZE = 5 * 1024 * 1024; // Taille maximale du fichier image (5MB)
//   let currentDialCode = "";

//   // Fonction de validation de l'email
//   const validateEmail = (email) => {
//     const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
//     return emailRegex.test(email);
//   };

//   // Validation du téléphone : minimum 7 chiffres après l'indicatif
//   const validatePhone = (phone) => {
//     const phoneRegex = /^\+?[0-9]{7,15}$/;
//     return phoneRegex.test(phone);
//   };

//   // Validation du casier judiciaire (PDF seulement)
//   const validateJudicialRecord = (file) => {
//     return file && file.type === "application/pdf" && file.size <= MAX_PDF_SIZE;
//   };

//   // Validation de la photo de profil (image uniquement et taille maximale)
//   const validateProfilePicture = (file) => {
//     const fileType = file ? file.type.split("/")[0] : "";
//     const fileSize = file ? file.size : 0;
//     return fileType === "image" && fileSize <= MAX_IMAGE_SIZE;
//   };

//   // Validation de la date d'adhésion vs date de naissance : minimum 19 ans
//   const validateAge = () => {
//     if (!birthDateInput || !joinDateInput) return true;

//     const birthDate = new Date(birthDateInput.value);
//     const joinDate = new Date(joinDateInput.value);
//     const ageDifference = (joinDate - birthDate) / (1000 * 60 * 60 * 24 * 365); // En années

//     if (ageDifference < 19) {
//       ageErrorMessage.style.display = "block";
//       joinDateInput.classList.add("is-invalid");
//       joinDateInput.classList.remove("is-valid");
//       return false;
//     } else {
//       ageErrorMessage.style.display = "none";
//       joinDateInput.classList.add("is-valid");
//       joinDateInput.classList.remove("is-invalid");
//       return true;
//     }
//   };

//   // Validation générale de chaque champ
//   const validateField = (field) => {
//     let valid = true;

//     if (field.type === "email") {
//       valid = validateEmail(field.value);
//     } else if (field === phoneInput) {
//       valid = validatePhone(field.value);
//     } else if (field === judicialInput) {
//       const file = judicialInput.files[0];
//       valid = validateJudicialRecord(file);
//     } else if (field === profilePictureInput) {
//       const file = profilePictureInput.files[0];
//       valid = validateProfilePicture(file);
//     } else {
//       valid = field.value.trim() !== "";  // Vérification des autres champs
//     }

//     field.classList.toggle("is-valid", valid);
//     field.classList.toggle("is-invalid", !valid);
//     return valid;
//   };

//   // Validation du formulaire
//   const validateForm = () => {
//     let isValid = true;

//     // Vérification de tous les champs
//     form.querySelectorAll(".form-control, .form-check-input").forEach(field => {
//       if (!validateField(field)) isValid = false;
//     });

//     // Validation de l'âge (19 ans minimum)
//     if (!validateAge()) isValid = false;

//     submitBtn.disabled = !isValid;
//     return isValid;
//   };

//   // Validation sur chaque modification des champs
//   form.addEventListener("input", validateForm);

//   // Validation au moment de la soumission
//   form.addEventListener("submit", e => {
//     e.preventDefault();
//     if (!validateForm()) return;

//     // Si le téléphone a une indicatif, recomposer l'input avant soumission
//     if (phoneInput && currentDialCode) {
//       phoneInput.value = currentDialCode + phoneInput.value.replace(/\s+/g, "");
//     }

//     submitBtn.disabled = true;
//     submitBtn.setAttribute("aria-busy", "true");
//     form.submit(); // Soumettre le formulaire après validation
//   });

//   // Aperçu de l'image de profil
//   if (profilePictureInput) {
//     profilePictureInput.addEventListener("change", () => {
//       const file = profilePictureInput.files[0];
//       if (file) {
//         const reader = new FileReader();
//         reader.onload = (e) => {
//           profilePicturePreview.src = e.target.result;
//           profilePicturePreview.style.display = "block";
//         };
//         reader.readAsDataURL(file);
//       } else {
//         profilePicturePreview.style.display = "none";
//       }
//       validateForm(); // Vérification après modification du fichier
//     });
//   }

//   // Aperçu et validation du fichier PDF (casier judiciaire)
//   if (judicialInput) {
//     judicialInput.addEventListener("change", () => {
//       const file = judicialInput.files[0];
//       const pdfPreview = document.getElementById("pdf-preview");

//       if (file && validateJudicialRecord(file)) {
//         pdfPreview.innerHTML = `<iframe src="${URL.createObjectURL(file)}" width="100%" height="300"></iframe>`;
//       } else {
//         pdfPreview.innerHTML = "";
//       }

//       validateForm(); // Vérification après modification du fichier PDF
//     });
//   }

//   // Validation du téléphone
//   if (phoneInput) {
//     phoneInput.addEventListener("input", () => {
//       validateField(phoneInput);
//     });
//   }

//   // Validation de l'email
//   if (emailInput) {
//     emailInput.addEventListener("input", () => {
//       validateField(emailInput);
//     });
//   }

//   // Validation des dates (naissance et adhésion)
//   if (birthDateInput && joinDateInput) {
//     joinDateInput.addEventListener("blur", validateAge);  // Vérifier quand l'adhésion est modifiée
//     birthDateInput.addEventListener("blur", validateAge);  // Vérifier si la date de naissance change
//   }

//   // Initialiser la validation au chargement
//   validateForm();
// });
