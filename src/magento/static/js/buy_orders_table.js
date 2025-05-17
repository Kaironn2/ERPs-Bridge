document.addEventListener('DOMContentLoaded', function () {
  function loadTable(url) {
    fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}})
      .then(resp => resp.text())
      .then(html => {
        document.getElementById('buy-orders-table-container').innerHTML = html;
        attachPaginationHandlers();
      });
  }

  function attachPaginationHandlers() {
    document.querySelectorAll('.page-link.page-ajax').forEach(link => {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        loadTable(this.href);
      });
    });
  }

  attachPaginationHandlers();
});