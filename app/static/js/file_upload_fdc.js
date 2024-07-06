document.addEventListener('DOMContentLoaded', () => {
    const dropzoneBox = document.querySelector('.dropzone-box');
    const fileInput = document.querySelector('input[type="file"]');
    const dropzoneArea = fileInput.closest('.dropzone-area');
    const message = dropzoneArea.querySelector('.message');
    const MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024;  // 2 GB

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            if (fileInput.files[0].size > MAX_FILE_SIZE) {
                alert('File is too large. Maximum file size is 2 GB.');
                fileInput.value = '';  // Clear the input
                message.textContent = 'No Files Selected';
            } else {
                updateDropzoneFileList(fileInput.files[0]);
            }
        }
    });

    dropzoneArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzoneArea.classList.add('dragover');
    });

    ['dragleave', 'dragend'].forEach((type) => {
        dropzoneArea.addEventListener(type, () => {
            dropzoneArea.classList.remove('dragover');
        });
    });

    dropzoneArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzoneArea.classList.remove('dragover');

        if (e.dataTransfer.files.length) {
            if (e.dataTransfer.files[0].size > MAX_FILE_SIZE) {
                alert('File is too large. Maximum file size is 2 GB.');
                e.dataTransfer.clearData();  // Clear the dragged files
                message.textContent = 'No Files Selected';
            } else {
                fileInput.files = e.dataTransfer.files;
                updateDropzoneFileList(e.dataTransfer.files[0]);
            }
        }
    });

    const updateDropzoneFileList = (file) => {
        message.textContent = `${file.name}, ${file.size} bytes`;
    };

    dropzoneBox.addEventListener('reset', () => {
        message.textContent = 'No Files Selected';
    });
});
