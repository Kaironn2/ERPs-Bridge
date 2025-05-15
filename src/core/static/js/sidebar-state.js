document.addEventListener('DOMContentLoaded', function () {
  const menus = ['magento-collapse', 'eccosys-collapse', 'account-collapse'];

  function saveSidebarState() {
    menus.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        const isShown = el.classList.contains('show');
        localStorage.setItem(id, isShown ? 'open' : 'closed');
      }
    });
  }

  function restoreSidebarState() {
    menus.forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;

      const state = localStorage.getItem(id);

      if (state === 'open') {
        el.classList.add('show');
      } else {
        el.classList.remove('show');
      }
    });
  }

  restoreSidebarState();

  menus.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('shown.bs.collapse', saveSidebarState);
      el.addEventListener('hidden.bs.collapse', saveSidebarState);
    }
  });
});
