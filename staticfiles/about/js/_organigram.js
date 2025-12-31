// /static/about/js/_organigram.js

document.addEventListener("DOMContentLoaded", function () {
  const btn = document.getElementById("org-toggle-btn");
  const wrapper = document.getElementById("org-wrapper");
  const arrow = document.getElementById("org-arrow");

  if (!btn || !wrapper) return;

  // état initial (replié)
  btn.setAttribute("aria-expanded", "false");
  wrapper.setAttribute("aria-hidden", "true");
  wrapper.classList.add("is-collapsed");

  btn.addEventListener("click", () => {
    const expanded = btn.getAttribute("aria-expanded") === "true";
    const next = !expanded;

    btn.setAttribute("aria-expanded", String(next));
    wrapper.setAttribute("aria-hidden", String(!next));

    // toggle la classe dédiée
    wrapper.classList.toggle("is-collapsed", !next);

    // rotation visuelle (en plus du sélecteur CSS)
    if (arrow) arrow.style.transform = next ? "rotate(180deg)" : "rotate(0deg)";
  });
});







// document.addEventListener("DOMContentLoaded", function() {
//   const btn = document.getElementById("org-toggle-btn");
//   const wrapper = document.getElementById("org-wrapper");
//   const arrow = document.getElementById("org-arrow");

//   btn.addEventListener("click", () => {
//     wrapper.classList.toggle("hidden");
//     arrow.style.transform = wrapper.classList.contains("hidden")
//       ? "rotate(0deg)"
//       : "rotate(180deg)";
//   });
// });





// document.getElementById('org-toggle-btn').addEventListener('click', function() {
//     const wrapper = document.getElementById('org-wrapper');
//     const arrow = document.getElementById('org-arrow');

//     wrapper.classList.toggle('hidden');
//     arrow.style.transform = wrapper.classList.contains('hidden') 
//         ? 'rotate(0deg)' 
//         : 'rotate(180deg)';
// });





// document.addEventListener("DOMContentLoaded", function(){
//   const toggleBtn = document.getElementById("org-toggle-btn");
//   const wrapper = document.getElementById("org-wrapper");
//   const arrow = document.getElementById("org-arrow");

//   toggleBtn.addEventListener("click", () => {
//     wrapper.classList.toggle("hidden");
//     wrapper.classList.toggle("show");
//     arrow.textContent = wrapper.classList.contains("show") ? "▲" : "▼";
//   });
// });
