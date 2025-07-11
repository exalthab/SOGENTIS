  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.desc-toggle').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        var target = document.querySelector(this.getAttribute('data-target'));
        if (!target) return;
        if (target.classList.contains('collapse')) {
          // Affiche la description complète et masque le court
          target.classList.remove('collapse');
          this.closest('.desc-short')?.classList?.add('collapse');
        } else {
          // Cache la description complète et montre le court
          target.classList.add('collapse');
          document.getElementById('desc-short-' + target.id.split('-').pop())?.classList?.remove('collapse');
        }
      });
    });
  });
