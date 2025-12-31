// static/accounts_users/js/login.js

document.addEventListener("DOMContentLoaded", () => {

  /* ---------------------------------------------------------
     ELEMENTS
  --------------------------------------------------------- */
  const form = document.querySelector("form[method='post']");
  const usernameInput = document.querySelector("#id_username");

  // Champ password (sélection robuste même si ID différent)
  const passwordInput =
    document.querySelector("input[type='password']") ||
    document.querySelector("input[name='password']");

  const toggleBtn = document.querySelector("#togglePassword");
  const toggleIcon = document.querySelector("#togglePasswordIcon");
  const capsHint = document.querySelector("#capsLockHint");

  /* ---------------------------------------------------------
     FOCUS AUTOMATIQUE SUR LE CHAMP IDENTIFIANT
  --------------------------------------------------------- */
  if (usernameInput) {
    setTimeout(() => usernameInput.focus(), 80); // évite le jump mobile
  }

  /* ---------------------------------------------------------
     CAPS LOCK DETECTOR
  --------------------------------------------------------- */
  if (passwordInput && capsHint) {
    const detectCaps = (e) => {
      const active = e.getModifierState?.("CapsLock");
      capsHint.classList.toggle("d-none", !active);
    };

    ["keyup", "keydown", "focus"].forEach(evt =>
      passwordInput.addEventListener(evt, detectCaps)
    );

    passwordInput.addEventListener("blur", () =>
      capsHint.classList.add("d-none")
    );
  }

  /* ---------------------------------------------------------
     TOGGLE PASSWORD VISIBILITY
  --------------------------------------------------------- */
  if (toggleBtn && passwordInput && toggleIcon) {
    toggleBtn.addEventListener("click", () => {

      const show = passwordInput.type === "password";
      passwordInput.type = show ? "text" : "password";

      // Icône dynamique + compatibilité texte screen-readers
      toggleIcon.textContent = show ? "🙈" : "👁️";
      toggleBtn.setAttribute(
        "aria-label",
        show
          ? "Masquer le mot de passe"
          : "Afficher le mot de passe"
      );

      // Re-focus sans scroll
      passwordInput.focus({ preventScroll: true });
    });
  }

  /* ---------------------------------------------------------
     ANTI DOUBLE-SUBMIT + SPINNER VISUEL + ARIA
  --------------------------------------------------------- */
  if (form) {
    form.addEventListener("submit", () => {

      const submitBtn = form.querySelector('button[type="submit"]');
      if (!submitBtn || submitBtn.disabled) return;

      // Désactivation sécurisée
      submitBtn.disabled = true;
      submitBtn.setAttribute("aria-busy", "true");

      // Ajout spinner si pas déjà présent
      if (!submitBtn.querySelector(".spinner-border")) {
        const spinner = document.createElement("span");
        spinner.className = "spinner-border spinner-border-sm ms-2";
        spinner.setAttribute("role", "status");
        spinner.setAttribute("aria-hidden", "true");
        submitBtn.appendChild(spinner);
      }
    });
  }

});






// // static/accounts_users/js/login.js

// document.addEventListener("DOMContentLoaded", () => {

//   const form = document.querySelector("form[method='post']");
//   const usernameInput = document.querySelector("#id_username");

//   // Password field (indestructible : capture le type password même si l’ID change)
//   const passwordInput = document.querySelector("input[type='password']");

//   const toggleBtn = document.querySelector("#togglePassword");
//   const toggleIcon = document.querySelector("#togglePasswordIcon");
//   const capsHint = document.querySelector("#capsLockHint");

//   // ---- Focus username ----
//   if (usernameInput) usernameInput.focus();

//   // ---- Caps Lock hint ----
//   if (passwordInput && capsHint) {
//     const detectCaps = (e) => {
//       const on = e.getModifierState && e.getModifierState("CapsLock");
//       capsHint.classList.toggle("d-none", !on);
//     };

//     ["keyup", "keydown", "focus"].forEach(evt =>
//       passwordInput.addEventListener(evt, detectCaps)
//     );

//     passwordInput.addEventListener("blur", () =>
//       capsHint.classList.add("d-none")
//     );
//   }

//   // ---- Toggle password visibility ----
//   if (toggleBtn && passwordInput && toggleIcon) {
//     toggleBtn.addEventListener("click", () => {
//       const show = passwordInput.type === "password";
//       passwordInput.type = show ? "text" : "password";
//       toggleIcon.textContent = show ? "🙈" : "👁️";
//       passwordInput.focus({ preventScroll: true });
//     });
//   }

//   // ---- Anti double submit + spinner ----
//   if (form) {
//     form.addEventListener("submit", () => {
//       const submitBtn = form.querySelector('button[type="submit"]');
//       if (submitBtn && !submitBtn.disabled) {
//         submitBtn.disabled = true;
//         submitBtn.setAttribute("aria-busy", "true");

//         const spinner = document.createElement("span");
//         spinner.className = "spinner-border spinner-border-sm ms-2";
//         spinner.setAttribute("aria-hidden", "true");
//         submitBtn.appendChild(spinner);
//       }
//     });
//   }
// });

