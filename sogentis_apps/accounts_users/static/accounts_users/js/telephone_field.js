document.addEventListener("DOMContentLoaded", function () {

  const phoneInput = document.getElementById("id_phone_number");
  const countrySelect = document.getElementById("id_country_of_residence");

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
     VALIDATION TÉLÉPHONE
  ======================= */
  const validPhone = v =>
    /^\+[0-9]{8,15}$/.test(v);  // Vérification du format du téléphone avec indicatif

  const validatePhone = (phoneField) => {
    const fullPhone = currentDialCode + phoneField.value.replace(/\s+/g, "");
    const valid = validPhone(fullPhone);
    phoneField.classList.toggle("is-valid", valid);
    phoneField.classList.toggle("is-invalid", !valid);
    return valid;
  };

  /* =======================
     APPLICATION DE L'INDICATIF
  ======================= */
  const applyDialCode = () => {
    currentDialCode = countryDialCodes[countrySelect.value] || "";
    phoneInput.placeholder = currentDialCode
      ? `${currentDialCode} XXXXXXXX`
      : "XXXXXXXX";
  };

  if (countrySelect && phoneInput) {
    countrySelect.addEventListener("change", applyDialCode);
    applyDialCode(); // Appliquer l'indicatif dès le chargement

    phoneInput.addEventListener("input", () => {
      // Empêcher la saisie du symbole "+"
      phoneInput.value = phoneInput.value.replace(/\+/g, "");
      validatePhone(phoneInput);
    });
  }

});
