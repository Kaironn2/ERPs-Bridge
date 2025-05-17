document.addEventListener('DOMContentLoaded', function () {
  const collapseId = 'filtersCollapse';
  const collapseEl = document.getElementById(collapseId);

  if (localStorage.getItem('filtersCollapseOpen') === 'true') {
    collapseEl.classList.add('notransition');
    collapseEl.classList.add('show');
    void collapseEl.offsetWidth;
    collapseEl.classList.remove('notransition');
  } else {
    collapseEl.classList.remove('show');
  }

  const bsCollapse = new bootstrap.Collapse(collapseEl, {
    toggle: false
  });

  collapseEl.addEventListener('show.bs.collapse', function () {
    localStorage.setItem('filtersCollapseOpen', 'true');
  });
  collapseEl.addEventListener('hide.bs.collapse', function () {
    localStorage.setItem('filtersCollapseOpen', 'false');
  });
});