// 🔄 Barre de progression simple pendant le chargement de la page
document.onreadystatechange = () => {
  const progress = document.getElementById('progress-bar');
  if (!progress) return;

  if (document.readyState === "interactive") {
    progress.style.width = "50%";
  } else if (document.readyState === "complete") {
    progress.style.width = "100%";
    setTimeout(() => {
      progress.style.display = "none";
    }, 500);
  }
};

// 🍪 Gestion de la bannière de consentement aux cookies
window.addEventListener("DOMContentLoaded", function () {
  const cookieBanner = document.getElementById("cookie-banner");
  const acceptBtn = document.getElementById("accept-cookies");

  if (!cookieBanner || !acceptBtn) return;

  // Vérifie si le cookie 'cookies_accepted' est déjà présent
  const cookiesAccepted = document.cookie
    .split("; ")
    .find(row => row.startsWith("cookies_accepted="));

  // Si le cookie n'existe pas, affiche la bannière
  if (!cookiesAccepted) {
    cookieBanner.style.display = "block";
  }

  // Au clic sur "Accepter", crée un cookie valable 1 an
  acceptBtn.addEventListener("click", function () {
    const oneYear = 60 * 60 * 24 * 365; // en secondes
    document.cookie = "cookies_accepted=true; path=/; max-age=" + oneYear;
    cookieBanner.style.display = "none";
  });
});
