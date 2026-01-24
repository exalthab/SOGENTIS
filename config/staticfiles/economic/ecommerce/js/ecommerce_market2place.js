/* static/economic/ecommerce/js/ecommerce_market2place.js */

(function () {
  function syncRange() {
    document.querySelectorAll('[data-mk-range]').forEach((range) => {
      const wrap = range.closest('.mk-filter-card') || document;
      const out = wrap.querySelector('[data-mk-range-value]');
      if (!out) return;

      const update = () => { out.textContent = range.value; };
      range.addEventListener('input', update);
      update();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', syncRange);
  } else {
    syncRange();
  }
})();
