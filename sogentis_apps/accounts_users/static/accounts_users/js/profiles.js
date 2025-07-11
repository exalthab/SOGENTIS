// profile.js

document.addEventListener("DOMContentLoaded", () => {
  console.log("Profile page loaded");

  const avatar = document.querySelector(".profile-avatar");
  if (avatar) {
    avatar.addEventListener("mouseenter", () => {
      avatar.style.borderColor = "#007bff";
    });
    avatar.addEventListener("mouseleave", () => {
      avatar.style.borderColor = "#dee2e6";
    });
  }
});
