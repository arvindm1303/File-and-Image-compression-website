const fileInput = document.getElementById('file-input');
const dropArea = document.getElementById('drop-area');
const fileInfo = document.getElementById('file-info');
const selectedFilename = document.getElementById('selected-filename');
const selectedFilesize = document.getElementById('selected-filesize');
const qualityRange = document.getElementById('quality-range');
const qualityValue = document.getElementById('quality-value');
const compressBtn = document.getElementById('compress-btn');
const progressContainer = document.getElementById('progress-container');
const progressFill = document.getElementById('progress-fill');
const progressStatus = document.getElementById('progress-status');
const resultSection = document.getElementById('result-section');
const resOriginalSize = document.getElementById('res-original-size');
const resCompressedSize = document.getElementById('res-compressed-size');
const resReduction = document.getElementById('res-reduction');
const downloadLink = document.getElementById('download-link');
const resetBtn = document.getElementById('reset-btn');

const API_BASE_URL = 'http://localhost:5000/api';

let currentFileId = null;

// Update quality display
qualityRange.addEventListener('input', () => {
    qualityValue.textContent = qualityRange.value;
});

// Drag and drop events
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, () => dropArea.classList.add('highlight'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, () => dropArea.classList.remove('highlight'), false);
});

dropArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
        handleFiles(files[0]);
    }
}

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFiles(e.target.files[0]);
    }
});

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

async function handleFiles(file) {
    // Basic validation
    const allowedTypes = ['.jpg', '.jpeg', '.png', '.pdf', '.docx'];
    const fileName = file.name.toLowerCase();
    const isValid = allowedTypes.some(ext => fileName.endsWith(ext));

    if (!isValid) {
        alert('Please upload a supported file type (JPEG, PNG, PDF, or DOCX)');
        return;
    }

    selectedFilename.textContent = `File Name: ${file.name}`;
    selectedFilesize.textContent = `Size: ${formatBytes(file.size)}`;
    
    // Hide upload section and show file info
    dropArea.classList.add('hidden');
    fileInfo.classList.remove('hidden');
    
    // Start upload immediately to get file_id
    await uploadFile(file);
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    progressContainer.classList.remove('hidden');
    progressStatus.textContent = 'Uploading file...';
    progressFill.style.width = '30%';

    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Upload failed');

        const data = await response.json();
        currentFileId = data.file_id;
        
        progressFill.style.width = '100%';
        progressStatus.textContent = 'Upload complete!';
        
        setTimeout(() => {
            progressContainer.classList.add('hidden');
        }, 1000);
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to upload file. Please try again.');
        resetUI();
    }
}

compressBtn.addEventListener('click', async () => {
    if (!currentFileId) return;

    fileInfo.classList.add('hidden');
    progressContainer.classList.remove('hidden');
    progressFill.style.width = '0%';
    progressStatus.textContent = 'Compressing...';

    // Simulate progress
    let progress = 0;
    const interval = setInterval(() => {
        if (progress < 90) {
            progress += 10;
            progressFill.style.width = `${progress}%`;
        }
    }, 500);

    try {
        const response = await fetch(`${API_BASE_URL}/compress`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_id: currentFileId,
                quality: parseInt(qualityRange.value)
            })
        });

        clearInterval(interval);

        if (!response.ok) throw new Error('Compression failed');

        const data = await response.json();
        
        progressFill.style.width = '100%';
        progressStatus.textContent = 'Compression complete!';
        
        showResults(data);
    } catch (error) {
        clearInterval(interval);
        console.error('Error:', error);
        alert('An error occurred during compression.');
        resetUI();
    }
});

function showResults(data) {
    progressContainer.classList.add('hidden');
    resultSection.classList.remove('hidden');
    
    resOriginalSize.textContent = formatBytes(data.original_size);
    resCompressedSize.textContent = formatBytes(data.compressed_size);
    resReduction.textContent = `${data.reduction_percentage}%`;
    downloadLink.href = data.download_url;
}

resetBtn.addEventListener('click', resetUI);

function resetUI() {
    currentFileId = null;
    fileInput.value = '';
    dropArea.classList.remove('hidden');
    fileInfo.classList.add('hidden');
    progressContainer.classList.add('hidden');
    resultSection.classList.add('hidden');
}
