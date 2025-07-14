document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const password1 = document.querySelector('input[name="password1"], input[name="password"]');
  const password2 = document.querySelector('input[name="password2"], input[name="password_confirm"]');

  if (form && password1 && password2) {
    form.addEventListener("submit", function (e) {
      if (password1.value !== password2.value) {
        e.preventDefault();
        alert("⚠️ Les mots de passe ne correspondent pas.");
        password2.focus();
        password2.classList.add("is-invalid");
      } else {
        password2.classList.remove("is-invalid");
      }
    });
  }

  // Amélioration UX pour les fichiers choisis
  const fileInputs = document.querySelectorAll('input[type="file"]');
  fileInputs.forEach(input => {
    input.addEventListener("change", function () {
      const label = this.nextElementSibling;
      if (label && this.files.length > 0) {
        label.textContent = this.files[0].name;
      }
    });
  });
});



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
