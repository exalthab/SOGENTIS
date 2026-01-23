/*!
 * dashboard/js/premium_dashboard.js
 * - Sidebar toggle (mobile) + overlay + ESC close
 * - Optional chart init (reads json_script ids: dbChartLabels / dbChartValues)
 * - Small UX helpers (safe no-op if elements absent)
 */
(function () {
  "use strict";

  // -------------------------
  // Helpers
  // -------------------------
  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }
  function qsa(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function readJsonScript(id) {
    var el = document.getElementById(id);
    if (!el) return null;
    try {
      var txt = (el.textContent || "").trim();
      if (!txt) return null;
      return JSON.parse(txt);
    } catch (e) {
      return null;
    }
  }

  function boolish(v, fallback) {
    if (v === true || v === false) return v;
    if (typeof v === "string") {
      var s = v.trim().toLowerCase();
      if (s === "1" || s === "true" || s === "yes") return true;
      if (s === "0" || s === "false" || s === "no") return false;
    }
    return !!fallback;
  }

  // -------------------------
  // Sidebar
  // -------------------------
  function setupSidebar() {
    var sidebar = qs("[data-db-sidebar]");
    if (!sidebar) return;

    // Overlay (created once)
    var overlay = qs("[data-db-overlay='sidebar']");
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.setAttribute("data-db-overlay", "sidebar");
      overlay.style.position = "fixed";
      overlay.style.inset = "0";
      overlay.style.background = "rgba(15,23,42,.45)";
      overlay.style.backdropFilter = "blur(2px)";
      overlay.style.zIndex = "1040";
      overlay.style.display = "none";
      document.body.appendChild(overlay);
    }

    function openSidebar() {
      sidebar.classList.add("is-open");
      overlay.style.display = "block";
      document.documentElement.classList.add("db-sidebar-open");
    }

    function closeSidebar() {
      sidebar.classList.remove("is-open");
      overlay.style.display = "none";
      document.documentElement.classList.remove("db-sidebar-open");
    }

    // Open buttons
    qsa("[data-db-open='sidebar']").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        openSidebar();
      });
    });

    // Close buttons (in sidebar)
    qsa("[data-db-toggle='sidebar']").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        closeSidebar();
      });
    });

    // Click overlay closes
    overlay.addEventListener("click", function () {
      closeSidebar();
    });

    // ESC closes
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeSidebar();
    });

    // If screen becomes large, ensure overlay closes
    window.addEventListener("resize", function () {
      if (window.matchMedia("(min-width: 992px)").matches) {
        closeSidebar();
      }
    });
  }

  // -------------------------
  // Charts (optional)
  // -------------------------
  function setupCharts() {
    // Canvas: accept multiple conventions
    var canvas =
      qs("#dbChart") ||
      qs("#dashboardChart") ||
      qs("canvas[data-db-chart]");

    if (!canvas) return;

    // Data: json_script recommended
    var labels = readJsonScript("dbChartLabels");
    var values = readJsonScript("dbChartValues");

    // Fallback: data attributes (CSV)
    if (!labels) {
      var rawLabels = canvas.getAttribute("data-labels");
      if (rawLabels) labels = rawLabels.split(",").map(function (s) { return s.trim(); });
    }
    if (!values) {
      var rawValues = canvas.getAttribute("data-values");
      if (rawValues) values = rawValues.split(",").map(function (s) { return Number(s.trim()) || 0; });
    }

    if (!labels || !values || !labels.length) return;
    if (!window.Chart) {
      // Chart engine missing => skip quietly
      return;
    }

    // Avoid double init
    if (canvas._dbChartInstance && typeof canvas._dbChartInstance.destroy === "function") {
      try { canvas._dbChartInstance.destroy(); } catch (e) {}
    }

    var ctx = canvas.getContext("2d");

    // Locale optional from html lang
    var locale = document.documentElement.lang || undefined;

    canvas._dbChartInstance = new window.Chart(ctx, {
      type: canvas.getAttribute("data-chart-type") || "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: canvas.getAttribute("data-chart-label") || "Activité",
            data: values,
            borderWidth: 2
          }
        ]
      },
      options: {
        locale: locale,
        plugins: {
          legend: { display: boolish(canvas.getAttribute("data-legend"), false) }
        },
        scales: {
          y: { beginAtZero: true }
        }
      }
    });
  }

  // -------------------------
  // Small UX: auto-dismiss bootstrap toasts/alerts if desired
  // -------------------------
  function setupAutoDismiss() {
    qsa("[data-db-autodismiss]").forEach(function (el) {
      var ms = Number(el.getAttribute("data-db-autodismiss")) || 0;
      if (ms <= 0) return;
      setTimeout(function () {
        el.classList.add("fade");
        el.classList.remove("show");
        setTimeout(function () {
          if (el && el.parentNode) el.parentNode.removeChild(el);
        }, 250);
      }, ms);
    });
  }

  // -------------------------
  // Boot
  // -------------------------
  document.addEventListener("DOMContentLoaded", function () {
    setupSidebar();
    setupCharts();
    setupAutoDismiss();
  });
})();
