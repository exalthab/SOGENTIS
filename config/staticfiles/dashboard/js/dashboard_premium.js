// premium_dashboard.js (production)
(function () {
  'use strict';

  function onReady(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  onReady(function () {
    const body = document.body;
    const sidebar = document.querySelector('.db-sidebar');
    if (!sidebar) return;

    const KEY_COLLAPSED = 'db_sidebar_collapsed';

    // ----- overlay -----
    function ensureOverlay() {
      let overlay = document.querySelector('.db-overlay');
      if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'db-overlay';
        overlay.hidden = true;
        document.body.appendChild(overlay);
      }
      return overlay;
    }
    const overlay = ensureOverlay();

    function isMobile() {
      return window.matchMedia('(max-width: 991.98px)').matches;
    }
    function isDesktop() {
      return window.matchMedia('(min-width: 992px)').matches;
    }

    function openSidebarMobile() {
      body.classList.add('db-sidebar-open');
      overlay.hidden = false;
      body.style.overflow = 'hidden';
    }

    function closeSidebarMobile() {
      body.classList.remove('db-sidebar-open');
      overlay.hidden = true;
      body.style.overflow = '';
    }

    function toggleSidebarMobile() {
      if (body.classList.contains('db-sidebar-open')) closeSidebarMobile();
      else openSidebarMobile();
    }

    // ----- desktop collapse (optional) -----
    function getCollapsedDesktop() {
      try { return localStorage.getItem(KEY_COLLAPSED) === '1'; } catch (e) { return false; }
    }

    function setCollapsedDesktop(collapsed) {
      if (!isDesktop()) return;
      body.classList.toggle('db-sidebar-collapsed', collapsed);
      try { localStorage.setItem(KEY_COLLAPSED, collapsed ? '1' : '0'); } catch (e) {}
    }

    // ----- buttons -----
    const openBtn = document.querySelector('[data-db-open="sidebar"]');
    if (openBtn) {
      openBtn.addEventListener('click', function (e) {
        e.preventDefault();

        // si tu veux permettre un collapse desktop, laisse ce comportement
        if (isDesktop()) {
          setCollapsedDesktop(!body.classList.contains('db-sidebar-collapsed'));
          return;
        }

        toggleSidebarMobile();
      });
    }

    const closeBtn = sidebar.querySelector('[data-db-toggle="sidebar"]');
    if (closeBtn) {
      closeBtn.addEventListener('click', function (e) {
        e.preventDefault();
        closeSidebarMobile();
      });
    }

    // close on overlay click
    overlay.addEventListener('click', closeSidebarMobile);

    // close on ESC
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeSidebarMobile();
    });

    // close on nav link click (mobile only)
    sidebar.addEventListener('click', function (e) {
      const a = e.target.closest('a');
      if (a && isMobile()) closeSidebarMobile();
    });

    // sync on resize
    function sync() {
      if (isDesktop()) {
        closeSidebarMobile();
        overlay.hidden = true;
        body.style.overflow = '';
        setCollapsedDesktop(getCollapsedDesktop());
      } else {
        // évite des états bizarres sur mobile
        body.classList.remove('db-sidebar-collapsed');
      }
    }

    sync();
    window.addEventListener('resize', sync);
  });
})();









// // premium_dashboard.js
// (function () {
//   'use strict';

//   function onReady(fn) {
//     if (document.readyState === 'loading') {
//       document.addEventListener('DOMContentLoaded', fn);
//     } else {
//       fn();
//     }
//   }

//   onReady(function () {
//     const body = document.body;
//     const sidebar = document.querySelector('.db-sidebar');
//     if (!sidebar) return;

//     const KEY_GROUPS = 'db_sidebar_groups';
//     const KEY_COLLAPSED = 'db_sidebar_collapsed';

//     // ---------- overlay ----------
//     function ensureOverlay() {
//       let overlay = document.querySelector('.db-overlay');
//       if (!overlay) {
//         overlay = document.createElement('div');
//         overlay.className = 'db-overlay';
//         overlay.hidden = true;
//         document.body.appendChild(overlay);
//       }
//       return overlay;
//     }
//     const overlay = ensureOverlay();

//     function isMobile() {
//       return window.matchMedia('(max-width: 991.98px)').matches;
//     }
//     function isDesktop() {
//       return window.matchMedia('(min-width: 992px)').matches;
//     }

//     function openSidebarMobile() {
//       body.classList.add('db-sidebar-open');
//       overlay.hidden = false;
//       body.style.overflow = 'hidden';
//     }

//     function closeSidebarMobile() {
//       body.classList.remove('db-sidebar-open');
//       overlay.hidden = true;
//       body.style.overflow = '';
//     }

//     function toggleSidebarMobile() {
//       if (body.classList.contains('db-sidebar-open')) closeSidebarMobile();
//       else openSidebarMobile();
//     }

//     // ---------- desktop collapse ----------
//     function getCollapsedDesktop() {
//       try { return localStorage.getItem(KEY_COLLAPSED) === '1'; } catch (e) { return false; }
//     }
//     function setCollapsedDesktop(collapsed) {
//       if (!isDesktop()) return;
//       body.classList.toggle('db-sidebar-collapsed', collapsed);
//       try { localStorage.setItem(KEY_COLLAPSED, collapsed ? '1' : '0'); } catch (e) {}
//     }

//     // ---------- groups state ----------
//     function readGroups() {
//       try {
//         const raw = localStorage.getItem(KEY_GROUPS);
//         return raw ? JSON.parse(raw) : {};
//       } catch (e) {
//         return {};
//       }
//     }

//     function writeGroups(obj) {
//       try { localStorage.setItem(KEY_GROUPS, JSON.stringify(obj || {})); } catch (e) {}
//     }

//     function applyGroupsState() {
//       const state = readGroups();
//       const toggles = sidebar.querySelectorAll('[data-db-collapse]');

//       toggles.forEach((btn) => {
//         const key = btn.getAttribute('data-db-collapse');
//         const group = sidebar.querySelector('[data-db-collapsible="' + key + '"]');
//         if (!key || !group) return;

//         const open = (key in state) ? !!state[key] : (btn.getAttribute('aria-expanded') !== 'false');
//         btn.setAttribute('aria-expanded', open ? 'true' : 'false');
//         group.hidden = !open;
//       });
//     }

//     function toggleGroup(btn) {
//       const key = btn.getAttribute('data-db-collapse');
//       const group = sidebar.querySelector('[data-db-collapsible="' + key + '"]');
//       if (!key || !group) return;

//       const nextOpen = group.hidden; // if hidden => open
//       group.hidden = !nextOpen;
//       btn.setAttribute('aria-expanded', nextOpen ? 'true' : 'false');

//       const state = readGroups();
//       state[key] = nextOpen;
//       writeGroups(state);
//     }

//     // ---------- wire group buttons ----------
//     sidebar.querySelectorAll('[data-db-collapse]').forEach((btn) => {
//       btn.addEventListener('click', function (e) {
//         e.preventDefault();
//         toggleGroup(btn);
//       });
//     });

//     // ---------- wire open/close sidebar ----------
//     const openBtn = document.querySelector('[data-db-open="sidebar"]');
//     if (openBtn) {
//       openBtn.addEventListener('click', function (e) {
//         e.preventDefault();
//         if (isDesktop()) {
//           setCollapsedDesktop(!body.classList.contains('db-sidebar-collapsed'));
//         } else {
//           toggleSidebarMobile();
//         }
//       });
//     }

//     const closeBtn = sidebar.querySelector('[data-db-toggle="sidebar"]');
//     if (closeBtn) {
//       closeBtn.addEventListener('click', function (e) {
//         e.preventDefault();
//         closeSidebarMobile();
//       });
//     }

//     overlay.addEventListener('click', closeSidebarMobile);

//     document.addEventListener('keydown', function (e) {
//       if (e.key === 'Escape') closeSidebarMobile();
//     });

//     // close on link click (mobile)
//     sidebar.addEventListener('click', function (e) {
//       const a = e.target.closest('a');
//       if (a && isMobile()) closeSidebarMobile();
//     });

//     // responsive sync
//     function sync() {
//       if (isDesktop()) {
//         closeSidebarMobile();
//         overlay.hidden = true;
//         body.style.overflow = '';
//         setCollapsedDesktop(getCollapsedDesktop());
//       } else {
//         body.classList.remove('db-sidebar-collapsed');
//       }
//     }

//     applyGroupsState();
//     sync();
//     window.addEventListener('resize', sync);
//   });
// })();
