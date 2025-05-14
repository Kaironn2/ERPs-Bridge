document.addEventListener('DOMContentLoaded', function () {
  const dropArea = document.getElementById('drop-area');
  const fileInput = document.getElementById('fileElem');
  const fileList = document.getElementById('file-list');

  if (!dropArea || !fileInput || !fileList) return;

  dropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropArea.style.background = '#f8f9fa';
  });
  dropArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropArea.style.background = '';
  });
  dropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    dropArea.style.background = '';
    fileInput.files = e.dataTransfer.files;
    updateFileList();
  });
  fileInput.addEventListener('change', updateFileList);

  function updateFileList() {
    fileList.innerHTML = '';
    for (let file of fileInput.files) {
      let div = document.createElement('div');
      div.textContent = file.name;
      fileList.appendChild(div);
    }
  }
});