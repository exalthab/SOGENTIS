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
  const MAX_PDF_SIZE = 2 * 1024 * 1024;
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
  // 📱 TÉLÉPHONE (E.164 + Sénégal)
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
  // 🔐 PASSWORDS
  // =====================================================
  const validatePasswords = () => {
    if (!password1Input || !password2Input) return true;
    const ok = password1Input.value === password2Input.value;
    setValidity(password2Input, ok);
    return ok;
  };

  // =====================================================
  // 🎂 AGE
  // =====================================================
  const validateAge = () => {
    if (!birthDateInput || !membershipDateInput) return true;
    if (!birthDateInput.value || !membershipDateInput.value) return true;

    const age =
      (new Date(membershipDateInput.value) - new Date(birthDateInput.value)) /
      (1000 * 60 * 60 * 24 * 365.25);

    const ok = age >= 18;
    setValidity(membershipDateInput, ok);
    return ok;
  };

  // =====================================================
  // 📄 CASIER JUDICIAIRE (OPTIONNEL + PREVIEW PROPRE)
  // =====================================================
  const validateJudicialRecord = () => {
    if (!judicialInput) return true;

    // Vide => OK (optionnel)
    if (!judicialInput.files.length) {
      setValidity(judicialInput, true);
      if (pdfPreview) pdfPreview.innerHTML = "";
      return true;
    }

    const file = judicialInput.files[0];
    const ok = file.type === "application/pdf" && file.size <= MAX_PDF_SIZE;

    setValidity(judicialInput, ok);

    if (pdfPreview) {
      pdfPreview.innerHTML = ok
        ? `<iframe src="${URL.createObjectURL(file)}" width="100%" height="300"
             style="border:1px solid #ccc;"></iframe>`
        : "";
    }

    return ok;
  };

  // =====================================================
  // 🖼️ PHOTO
  // =====================================================
  const validateProfilePicture = () => {
    if (!profilePictureInput || !profilePictureInput.files.length) return true;
    const file = profilePictureInput.files[0];
    const ok = file.type.startsWith("image/") && file.size <= MAX_IMAGE_SIZE;
    setValidity(profilePictureInput, ok);
    return ok;
  };

  // =====================================================
  // 🌍 PAYS → PRÉFIXE (FIX MOBILE: focus avant setSelectionRange)
  // =====================================================
  const syncCountryToPhone = () => {
    if (!countrySelect || !phoneInput) return;

    const prefix = COUNTRY_PHONE_PREFIX[countrySelect.value];
    if (!prefix) return;

    currentPhonePrefix = `${prefix} `;
    if (!phoneInput.value.trim()) phoneInput.value = currentPhonePrefix;

    // ✅ important mobile
    phoneInput.focus();
    phoneInput.setSelectionRange(
      currentPhonePrefix.length,
      currentPhonePrefix.length
    );
  };

  // =====================================================
  // 🔒 PROTECTION SAISIE TÉLÉPHONE
  // =====================================================
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
  // 📱 OTP FLOW
  // =====================================================
  const modalEl = document.getElementById("otpModal");
  if (!modalEl || !phoneInput) return;

  const csrf = document.querySelector("[name=csrfmiddlewaretoken]")?.value;
  const otpModal = new bootstrap.Modal(modalEl);

  const sendOTP = async () => {
    const res = await fetch("/accounts_users/ajax/phone/send-otp/", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrf,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `phone=${encodeURIComponent(phoneInput.value)}`,
    });

    const data = await res.json();
    if (data.ok) otpModal.show();
    else alert(data.error);
  };

  document
    .getElementById("verify-otp-btn")
    ?.addEventListener("click", async () => {
      const code = document.getElementById("otp-code-input")?.value;
      const errorBox = document.getElementById("otp-error");

      const res = await fetch("/accounts_users/ajax/phone/verify-otp/", {
        method: "POST",
        headers: {
          "X-CSRFToken": csrf,
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `phone=${encodeURIComponent(phoneInput.value)}&code=${code}`,
      });

      const data = await res.json();
      if (data.ok) {
        otpValidated = true;
        otpModal.hide();
        form.requestSubmit(); // ✅ déclenche submit normal
      } else {
        if (errorBox) {
          errorBox.textContent = data.error || "Code invalide";
          errorBox.classList.remove("d-none");
        } else {
          alert(data.error || "Code invalide");
        }
      }
    });

  // =====================================================
  // 🚀 SUBMIT FINAL
  // =====================================================
  form.addEventListener("submit", (e) => {
    if (submitting) {
      e.preventDefault();
      return;
    }

    if (!validateForm()) {
      e.preventDefault();
      return;
    }

    if (!otpValidated) {
      e.preventDefault();
      sendOTP();
      return;
    }

    // Nettoyage final E.164 (sans espaces)
    phoneInput.value = phoneInput.value.replace(/\s+/g, "");

    submitting = true;
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.setAttribute("aria-busy", "true");
    }
  });

  // validation initiale pour état cohérent
  validateForm();
});
