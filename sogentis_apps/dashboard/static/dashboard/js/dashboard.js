(() => {
  const shell = document.querySelector("[data-dashboard-shell]");
  if (!shell) return;

  const sidebar = shell.querySelector("[data-dashboard-sidebar]");
  const overlay = shell.querySelector("[data-dashboard-overlay]");
  const toggleBtn = document.querySelector("[data-dashboard-toggle='sidebar']");

  const open = () => {
    shell.classList.add("is-sidebar-open");
    if (overlay) overlay.hidden = false;
  };

  const close = () => {
    shell.classList.remove("is-sidebar-open");
    if (overlay) overlay.hidden = true;
  };

  const isMobile = () => window.matchMedia("(max-width: 991.98px)").matches;

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      if (shell.classList.contains("is-sidebar-open")) close();
      else open();
    });
  }

  if (overlay) overlay.addEventListener("click", close);

  // Close on ESC
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && shell.classList.contains("is-sidebar-open")) close();
  });

  // If resizing to desktop, ensure overlay hidden
  window.addEventListener("resize", () => {
    if (!isMobile()) {
      close();
    }
  });

  // Init overlay state
  close();
})();
