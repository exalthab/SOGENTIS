// Petit helper UX (safe, minimal)
document.addEventListener("DOMContentLoaded", () => {
  // auto-focus sur textarea si présent
  const ta = document.querySelector("textarea");
  if (ta && ta.offsetParent !== null) ta.focus();
});
