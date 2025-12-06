document.addEventListener("DOMContentLoaded", function () {
    const body = document.body;
    const toggleBtn = document.getElementById("themeToggle");
    const themeIcon = document.getElementById("themeIcon");

    // Récupération du thème sauvegardé
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
      body.classList.add("dark-mode");
      themeIcon.textContent = "☀️";
    }

    // Bascule entre sombre et clair
    toggleBtn?.addEventListener("click", () => {
      body.classList.toggle("dark-mode");
      const isDark = body.classList.contains("dark-mode");
      themeIcon.textContent = isDark ? "☀️" : "🌙";
      localStorage.setItem("theme", isDark ? "dark" : "light");
    });
  });




  
// document.addEventListener("DOMContentLoaded", function () {
//   const body = document.body;
//   const toggleBtn = document.getElementById("themeToggle");
//   const themeIcon = document.getElementById("themeIcon");

//   // Fonction pour appliquer le thème
//   function applyTheme(theme) {
//     if (theme === "dark") {
//       body.classList.add("dark-mode");
//       themeIcon.textContent = "☀️";
//     } else {
//       body.classList.remove("dark-mode");
//       themeIcon.textContent = "🌙";
//     }
//   }

//   // Récupération du thème sauvegardé
//   const savedTheme = localStorage.getItem("theme") || "light";
//   applyTheme(savedTheme);

//   // Bascule entre sombre et clair
//   toggleBtn?.addEventListener("click", () => {
//     const isDark = body.classList.toggle("dark-mode");
//     const newTheme = isDark ? "dark" : "light";
//     themeIcon.textContent = isDark ? "☀️" : "🌙";
//     localStorage.setItem("theme", newTheme);
//   });
// });
