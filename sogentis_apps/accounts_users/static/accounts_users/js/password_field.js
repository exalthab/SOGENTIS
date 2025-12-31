document.addEventListener("DOMContentLoaded", function () {

  const form = document.querySelector("form[method='post']");
  if (!form) return;

  const password1 = form.querySelector(".password-strong");
  const password2 = form.querySelector(".password-confirm");
  const toggleBtn = document.getElementById("togglePassword");
  const toggleIcon = document.getElementById("togglePasswordIcon");
  const capsHint = document.getElementById("capsLockHint");

  /* =======================
     RÈGLES DE VALIDATION MOT DE PASSE
  ======================= */
  const strongPassword = v =>
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/.test(v);

  const validatePassword = (passwordField) => {
    const valid = strongPassword(passwordField.value);
    passwordField.classList.toggle("is-valid", valid);
    passwordField.classList.toggle("is-invalid", !valid);
    return valid;
  };

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
     MISE À JOUR À CHAQUE SAISIE
  ======================= */
  if (password1) {
    password1.addEventListener("input", () => validatePassword(password1));
  }

  if (password2) {
    password2.addEventListener("input", () => {
      if (password1 && password2 && password1.value !== password2.value) {
        password2.setCustomValidity("Les mots de passe ne sont pas identiques.");
        password2.classList.add("is-invalid");
      } else {
        password2.setCustomValidity("");
        validatePassword(password2);
      }
    });
  }

});
