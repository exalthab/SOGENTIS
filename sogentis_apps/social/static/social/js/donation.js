document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  if (form) {
    form.addEventListener("submit", () => {
      console.log("Don en cours de traitement...");
    });
  }
});
