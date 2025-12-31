// Fonction pour valider un email
const validateEmail = (email) => {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // Un modèle d'email basique
  return emailPattern.test(email);
};

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form[method='post']");
  if (!form) return;

  const submitBtn = form.querySelector("button[type='submit']");
  const emailField = form.querySelector('input[type="email"]');
  
  const validateField = (field) => {
    let valid = true;

    if (field.type === "email") {
      valid = validateEmail(field.value); // Utilise la fonction validateEmail
    } else if (field.type === "checkbox") {
      valid = field.checked; // Validation des cases à cocher
    } else if (field.type === "file" && field.required) {
      valid = field.files.length > 0; // Validation des fichiers requis
    } else {
      valid = field.value.trim() !== ""; // Validation des champs texte
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

    submitBtn.disabled = !ok; // Désactive le bouton si le formulaire n'est pas valide
    return ok;
  };

  form.addEventListener("input", validateForm);

  form.addEventListener("submit", e => {
    e.preventDefault();
    if (!validateForm()) return;

    submitBtn.disabled = true;
    submitBtn.setAttribute("aria-busy", "true");
    form.submit(); // Soumettre le formulaire après validation
  });

  validateForm(); // Vérifie la validité dès le chargement de la page
});
