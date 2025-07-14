document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll(".desc-toggle").forEach(function(link) {
    link.addEventListener("click", function(e) {
      e.preventDefault();
      let target = document.querySelector(this.dataset.target);
      if (!target) return;
      if (target.style.display === "block") {
        target.style.display = "none";
        this.textContent = "Voir plus";
      } else {
        target.style.display = "block";
        this.textContent = "Voir moins";
      }
    });
  });
});
