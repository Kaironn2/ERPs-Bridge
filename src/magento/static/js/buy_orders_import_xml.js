document.addEventListener('DOMContentLoaded', function () {
  const dropArea = document.getElementById('drop-area');
  const fileInput = document.getElementById('fileElem');
  const fileList = document.getElementById('file-list');
  const form = document.getElementById('upload-form');

  let droppedFiles = fileInput.files;

  function showFiles(files) {
    fileList.innerHTML = '';
    if (!files || files.length === 0) {
      fileList.innerHTML = '<em>Nenhum arquivo selecionado</em>';
      return;
    }
    for (const file of files) {
      const div = document.createElement('div');
      div.textContent = file.name;
      fileList.appendChild(div);
    }
  }

  dropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropArea.classList.add('dragover');
  });

  dropArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropArea.classList.remove('dragover');
  });

  dropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    dropArea.classList.remove('dragover');
    
    const newDroppedFiles = e.dataTransfer.files;
    const dataTransfer = new DataTransfer();

    if (newDroppedFiles && newDroppedFiles.length > 0) {
      for (const file of newDroppedFiles) {
        dataTransfer.items.add(file);
      }
    }
    fileInput.files = dataTransfer.files; 
    droppedFiles = fileInput.files;
    showFiles(droppedFiles);
  });

  fileInput.addEventListener('change', () => {
    droppedFiles = fileInput.files;
    showFiles(droppedFiles);
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    if (!droppedFiles || droppedFiles.length === 0) {
      alert('Selecione ou arraste arquivos XML antes de enviar.');
      return;
    }

    const formData = new FormData();
    for (const file of droppedFiles) {
      formData.append('xml_file', file);
    }

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(form.action, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
      },
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          return response.text().then(text => { 
            throw new Error(`Erro ao enviar arquivos: ${response.status} ${text || ''}`);
          });
        }
        return response.text();
      })
      .then((data) => {
        fileList.innerHTML = '<div class="text-success mt-2">✅ Arquivos enviados com sucesso.</div>';
        const dt = new DataTransfer();
        fileInput.files = dt.files;
        droppedFiles = fileInput.files;
        showFiles(droppedFiles);
      })
      .catch((error) => {
        console.error(error);
        fileList.innerHTML = `<div class="text-danger mt-2">❌ Ocorreu um erro ao enviar os arquivos. ${error.message}</div>`;
      });
  });

  showFiles(droppedFiles);
});
