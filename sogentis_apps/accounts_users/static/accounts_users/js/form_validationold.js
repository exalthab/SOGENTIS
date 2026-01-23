document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form[method='post']");
  if (!form) return;

  const submitBtn = form.querySelector("button[type='submit']");

  // =====================================================
  // 🎯 IDS DJANGO
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
  const MAX_PDF_SIZE = 2 * 1024 * 1024; // 2 Mo
  const MAX_IMAGE_SIZE = 5 * 1024 * 1024;

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

  let currentPhonePrefix = "";
  let otpValidated = false;
  let submitting = false;

  // =====================================================
  // 🧩 UTILS
  // =====================================================
  const setValidity = (field, valid) => {
    if (!field) return;
    field.classList.toggle("is-valid", valid);
    field.classList.toggle("is-invalid", !valid);
  };

  // =====================================================
  // 📧 EMAIL
  // =====================================================
  const validateEmail = () => {
    if (!emailInput) return true;
    const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value.trim());
    setValidity(emailInput, ok);
    return ok;
  };

  // =====================================================
  // 📱 TÉLÉPHONE
  // =====================================================
  const validatePhone = () => {
    if (!phoneInput) return true;

    const raw = phoneInput.value.replace(/\s+/g, "");

    if (!raw.startsWith("+") || raw.length < 11) {
      setValidity(phoneInput, false);
      return false;
    }

    if (countrySelect?.value === "SN") {
      const national = raw.replace("+221", "");
      if (!/^(70|75|76|77|78)\d{7}$/.test(national)) {
        setValidity(phoneInput, false);
        return false;
      }
    }

    setValidity(phoneInput, true);
    return true;
  };

  // =====================================================
  // 🔐 MOTS DE PASSE
  // =====================================================
  const validatePasswords = () => {
    if (!password1Input || !password2Input) return true;
    const ok = password1Input.value === password2Input.value;
    setValidity(password2Input, ok);
    return ok;
  };

  // =====================================================
  // 🎂 ÂGE (>= 18)
  // =====================================================
  const validateAge = () => {
    if (!birthDateInput || !membershipDateInput) return true;
    if (!birthDateInput.value || !membershipDateInput.value) return true;

    const age =
      (new Date(membershipDateInput.value) -
        new Date(birthDateInput.value)) /
      (1000 * 60 * 60 * 24 * 365.25);

    const ok = age >= 18;
    setValidity(membershipDateInput, ok);
    return ok;
  };

  // =====================================================
  // 📄 CASIER JUDICIAIRE (VALIDATION SEULE)
  // =====================================================
  const validateJudicialRecord = () => {
    if (!judicialInput) return true;

    // optionnel : vide = OK
    if (!judicialInput.files.length) {
      setValidity(judicialInput, true);
      return true;
    }

    const file = judicialInput.files[0];
    const ok =
      file.type === "application/pdf" &&
      file.size <= MAX_PDF_SIZE;

    setValidity(judicialInput, ok);
    return ok;
  };

  // =====================================================
  // 📄 PDF PREVIEW (UNIQUEMENT SUR CHANGE)
  // =====================================================
  judicialInput?.addEventListener("change", () => {
    if (!judicialInput.files.length) {
      pdfPreview.innerHTML = "";
      return;
    }

    const file = judicialInput.files[0];

    if (file.type === "application/pdf" && file.size <= MAX_PDF_SIZE) {
      pdfPreview.innerHTML = `
        <iframe
          src="${URL.createObjectURL(file)}"
          width="100%"
          height="300"
          style="border:1px solid #ccc;"
        ></iframe>
      `;
    } else {
      pdfPreview.innerHTML = "";
    }
  });

  // =====================================================
  // 🖼️ PHOTO DE PROFIL
  // =====================================================
  const validateProfilePicture = () => {
    if (!profilePictureInput || !profilePictureInput.files.length)
      return true;

    const file = profilePictureInput.files[0];
    const ok =
      file.type.startsWith("image/") &&
      file.size <= MAX_IMAGE_SIZE;

    setValidity(profilePictureInput, ok);
    return ok;
  };

  // =====================================================
  // 🌍 PAYS → PRÉFIXE
  // =====================================================
  const syncCountryToPhone = () => {
    if (!countrySelect || !phoneInput) return;

    const prefix = COUNTRY_PHONE_PREFIX[countrySelect.value];
    if (!prefix) return;

    currentPhonePrefix = `${prefix} `;
    if (!phoneInput.value.trim()) {
      phoneInput.value = currentPhonePrefix;
    }

    phoneInput.focus();
    phoneInput.setSelectionRange(
      currentPhonePrefix.length,
      currentPhonePrefix.length
    );
  };

  phoneInput?.addEventListener("input", () => {
    if (!currentPhonePrefix) return;

    if (!phoneInput.value.startsWith(currentPhonePrefix)) {
      phoneInput.value = currentPhonePrefix;
      return;
    }

    const numberPart = phoneInput.value
      .slice(currentPhonePrefix.length)
      .replace(/\D/g, "");

    phoneInput.value = currentPhonePrefix + numberPart;
  });

  // =====================================================
  // 🧪 VALIDATION GLOBALE
  // =====================================================
  const validateForm = () =>
    validateEmail() &&
    validatePhone() &&
    validatePasswords() &&
    validateAge() &&
    validateJudicialRecord() &&
    validateProfilePicture();

  form.addEventListener("input", validateForm);
  form.addEventListener("change", validateForm);

  countrySelect?.addEventListener("change", syncCountryToPhone);
  syncCountryToPhone();

  // =====================================================
  // 🚀 SUBMIT FINAL
  // =====================================================
  form.addEventListener("submit", (e) => {
    if (submitting || !validateForm()) {
      e.preventDefault();
      return;
    }

    phoneInput.value = phoneInput.value.replace(/\s+/g, "");

    submitting = true;
    submitBtn && (submitBtn.disabled = true);
    submitBtn?.setAttribute("aria-busy", "true");
  });

  // état initial
  validateForm();
});
