// password_reset.js

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const emailField = form?.querySelector("input[type='email']");

  if (emailField) {
    emailField.focus();
    emailField.addEventListener("blur", () => {
      if (!emailField.value.includes("@")) {
        console.warn("Invalid email format");
        // For production: display a message or validation indicator
      }
    });
  }

  form?.addEventListener("submit", () => {
    console.log("Password reset request submitted");
  });
});
