document.addEventListener("DOMContentLoaded", function() {
  const btn = document.getElementById("org-toggle-btn");
  const wrapper = document.getElementById("org-wrapper");
  const arrow = document.getElementById("org-arrow");

  btn.addEventListener("click", () => {
    wrapper.classList.toggle("hidden");
    arrow.style.transform = wrapper.classList.contains("hidden")
      ? "rotate(0deg)"
      : "rotate(180deg)";
  });
});





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
