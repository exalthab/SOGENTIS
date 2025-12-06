// ===============================
// Toggle thème clair / sombre
// ===============================
const html = document.documentElement;

document.getElementById("themeToggle")?.addEventListener("click", () => {
    html.classList.toggle("light-theme");
    localStorage.setItem("theme", html.classList.contains("light-theme") ? "light" : "dark");
});

document.getElementById("themeToggleMobile")?.addEventListener("click", () => {
    html.classList.toggle("light-theme");
    localStorage.setItem("theme", html.classList.contains("light-theme") ? "light" : "dark");
});

// ===============================
// Charger le thème sauvegardé
// ===============================
if (localStorage.getItem("theme") === "light") {
    html.classList.add("light-theme");
}
