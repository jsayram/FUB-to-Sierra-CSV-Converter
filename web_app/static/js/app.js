// FUB to Sierra Converter - Main JavaScript
// Professional UI Implementation with Dark/Light Mode

// =====================
// Theme Management
// =====================

// Initialize theme from localStorage or default to light
const initTheme = () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
};

// Toggle between light and dark mode
const toggleTheme = () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
};

// Update theme toggle icon
const updateThemeIcon = (theme) => {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.textContent = theme === 'light' ? '🌙' : '☀️';
    }
};

// Initialize theme on page load
initTheme();

// DOM Elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const mappingSection = document.getElementById('mappingSection');
const convertBtn = document.getElementById('convertBtn');
const consoleSection = document.getElementById('consoleSection');
const consoleOutput = document.getElementById('consoleOutput');
const downloadSection = document.getElementById('downloadSection');
const downloadFiles = document.getElementById('downloadFiles');
const errorMessage = document.getElementById('errorMessage');
const loading = document.getElementById('loading');
const previewSection = document.getElementById('previewSection');
const previewTable = document.getElementById('previewTable');
const paymentNoticeInline = document.getElementById('paymentNoticeInline');
const convertAnotherBtn = document.getElementById('convertAnotherBtn');
const warningModal = document.getElementById('warningModal');
const confirmModal = document.getElementById('confirmModal');
const cancelWarningBtn = document.getElementById('cancelWarningBtn');
const confirmWarningBtn = document.getElementById('confirmWarningBtn');
const cancelConfirmBtn = document.getElementById('cancelConfirmBtn');
const finalConfirmBtn = document.getElementById('finalConfirmBtn');
const paymentCard = document.getElementById('paymentCard');

// State
let currentFile = null;
let detectedColumns = [];
let convertedFiles = null;
let isPaymentComplete = false;

// Column Groups Configuration
const columnGroups = {
    contact: ['first_name', 'last_name', 'email', 'secondary_email', 'phone', 'secondary_phone', 'source', 'assigned_to', 'stage', 'status'],
    location: ['street', 'city', 'state', 'zip', 'county', 'country'],
    notes: ['tags', 'notes', 'search_criteria'],
    dates: ['created_date', 'modified_date', 'last_activity', 'birthday', 'anniversary'],
    professional: ['company', 'title', 'website', 'spouse_name', 'occupation', 'employer'],
    social: ['facebook', 'linkedin', 'twitter', 'instagram'],
    property: ['home_price', 'price_min', 'price_max', 'beds_min', 'beds_max', 'baths_min', 'baths_max', 'property_type', 'square_feet', 'lot_size', 'year_built'],
    mls: ['listing_id', 'mls_number'],
    custom: ['custom_field_1', 'custom_field_2', 'custom_field_3']
};

// ====================
// File Upload Handlers
// ====================

uploadZone.addEventListener('click', () => fileInput.click());

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

async function handleFileSelect(file) {
    if (!file.name.endsWith('.csv')) {
        showError('Please select a CSV file');
        return;
    }

    currentFile = file;
    hideError();

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/detect_columns', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        
        if (result.success) {
            detectedColumns = result.columns;
            buildMappingUI();
            mappingSection.classList.remove('hidden');
            uploadZone.querySelector('h2').textContent = `File loaded: ${file.name}`;
            uploadZone.querySelector('p').textContent = 'Click to select a different file';
        } else {
            showError(result.error);
        }
    } catch (error) {
        showError('Error reading file: ' + error.message);
    }
}

// ====================
// Mapping UI
// ====================

function buildMappingUI() {
    const containers = {
        contact: document.getElementById('contactMappings'),
        location: document.getElementById('locationMappings'),
        notes: document.getElementById('notesMappings'),
        dates: document.getElementById('datesMappings'),
        professional: document.getElementById('professionalMappings'),
        social: document.getElementById('socialMappings'),
        property: document.getElementById('propertyMappings'),
        mls: document.getElementById('mlsMappings'),
        custom: document.getElementById('customMappings')
    };

    // Clear all containers
    Object.values(containers).forEach(container => container.innerHTML = '');

    // Build mapping rows - only for columns detected in the CSV
    for (const [key, defaultValue] of Object.entries(window.defaultMapping)) {
        const found = detectedColumns.includes(defaultValue);
        
        // Only show this mapping if the column was detected in the CSV
        if (!found) continue;
        
        const row = document.createElement('div');
        row.className = 'mapping-row';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `map_${key}`;
        checkbox.checked = true; // Auto-check since it was found
        
        const label = document.createElement('label');
        label.textContent = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        label.setAttribute('for', `map_${key}`);
        
        const input = document.createElement('input');
        input.type = 'text';
        input.id = `val_${key}`;
        input.value = defaultValue;
        input.placeholder = 'Column name in CSV';
        
        row.appendChild(checkbox);
        row.appendChild(label);
        row.appendChild(input);
        
        // Add to appropriate category
        for (const [groupName, groupKeys] of Object.entries(columnGroups)) {
            if (groupKeys.includes(key) && containers[groupName]) {
                containers[groupName].appendChild(row);
                break;
            }
        }
    }
}

// ====================
// Conversion Process
// ====================

convertBtn.addEventListener('click', async () => {
    if (!currentFile) {
        showError('Please select a file first');
        return;
    }
    await processConversion();
});

async function processConversion() {
    try {
        loading.classList.add('active');
        consoleSection.classList.remove('hidden');
        downloadSection.classList.remove('active');
        paymentNoticeInline.style.display = 'none';
        previewSection.classList.remove('active');
        consoleOutput.innerHTML = '';
        convertBtn.disabled = true;

        const columnMapping = {};
        for (const [key] of Object.entries(window.defaultMapping)) {
            const checkbox = document.getElementById(`map_${key}`);
            const input = document.getElementById(`val_${key}`);
            if (checkbox && checkbox.checked && input) {
                columnMapping[key] = input.value;
            }
        }

        const formData = new FormData();
        formData.append('file', currentFile);
        formData.append('column_mapping', JSON.stringify(columnMapping));

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            if (result.logs) {
                result.logs.forEach(log => addConsoleLog(log, 'info'));
            }

            if (result.preview && result.preview.length > 0) {
                displayPreview(result.preview, result.preview_note);
            }

            convertedFiles = result.files;
            sessionStorage.setItem('convertedFiles', JSON.stringify(result.files));
            
            addConsoleLog('', 'info');
            addConsoleLog('✅ Conversion complete!', 'success');
            addConsoleLog('💳 Review the preview below, then complete payment to download your files', 'info');
            
            paymentNoticeInline.style.display = 'block';
            previewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            showError(result.error + (result.details ? '\n\n' + result.details : ''));
            if (result.logs) {
                result.logs.forEach(log => addConsoleLog(log, 'error'));
            }
        }
    } catch (error) {
        showError('Conversion failed: ' + error.message);
        addConsoleLog('Error: ' + error.message, 'error');
    } finally {
        loading.classList.remove('active');
        convertBtn.disabled = false;
    }
}

// ====================
// Console & Preview
// ====================

function addConsoleLog(message, type = 'info') {
    const line = document.createElement('div');
    line.className = `console-line ${type}`;
    line.textContent = message;
    consoleOutput.appendChild(line);
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
}

function displayPreview(previewData, note) {
    if (!previewData || previewData.length === 0) return;

    previewTable.innerHTML = '';

    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    const columns = Object.keys(previewData[0]);
    
    columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    previewTable.appendChild(thead);

    const tbody = document.createElement('tbody');
    previewData.forEach((row) => {
        const tr = document.createElement('tr');
        columns.forEach(col => {
            const td = document.createElement('td');
            td.textContent = row[col] || '';
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    previewTable.appendChild(tbody);

    previewSection.classList.add('active');
    
    previewSection.addEventListener('contextmenu', e => e.preventDefault());
    previewSection.addEventListener('copy', e => e.preventDefault());
    previewSection.addEventListener('cut', e => e.preventDefault());
}

// ====================
// Download Management
// ====================

function displayDownloads(files) {
    downloadFiles.innerHTML = '';
    
    // Show download section and payment card when files are ready
    downloadSection.classList.remove('hidden');
    downloadSection.classList.add('active');
    if (paymentCard) {
        paymentCard.style.display = 'block';
    }
    
    // ZIP download for multiple files
    if (files.length > 1) {
        const zipDiv = document.createElement('div');
        zipDiv.className = 'download-file';
        zipDiv.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        zipDiv.style.color = 'white';
        zipDiv.style.border = 'none';
        
        const info = document.createElement('div');
        info.className = 'file-info';
        
        const name = document.createElement('div');
        name.className = 'file-name';
        name.textContent = '📦 All Files (ZIP Archive)';
        name.style.color = 'white';
        
        const size = document.createElement('div');
        size.className = 'file-size';
        const totalRows = files.reduce((sum, f) => sum + f.rows, 0);
        size.textContent = `${files.length} files • ${totalRows.toLocaleString()} total rows`;
        size.style.color = '#e0e7ff';
        
        info.appendChild(name);
        info.appendChild(size);
        
        const btn = document.createElement('button');
        btn.className = 'download-btn';
        btn.textContent = '⬇ Download ZIP';
        btn.style.background = 'white';
        btn.style.color = '#667eea';
        btn.onclick = () => {
            downloadZip();
            btn.textContent = '✓ Downloaded';
            btn.style.background = '#d1fae5';
            btn.style.color = '#065f46';
            setTimeout(() => {
                btn.textContent = '⬇ Download Again';
                btn.style.background = 'white';
                btn.style.color = '#667eea';
            }, 2000);
        };
        
        zipDiv.appendChild(info);
        zipDiv.appendChild(btn);
        downloadFiles.appendChild(zipDiv);
        
        const separator = document.createElement('div');
        separator.style.textAlign = 'center';
        separator.style.margin = '15px 0';
        separator.style.color = '#9ca3af';
        separator.style.fontSize = '14px';
        separator.textContent = '─── or download individually ───';
        downloadFiles.appendChild(separator);
    }
    
    // Individual file downloads
    files.forEach(file => {
        const fileDiv = document.createElement('div');
        fileDiv.className = 'download-file';
        
        const info = document.createElement('div');
        info.className = 'file-info';
        
        const name = document.createElement('div');
        name.className = 'file-name';
        name.textContent = '📄 ' + file.filename;
        
        const size = document.createElement('div');
        size.className = 'file-size';
        size.textContent = `${file.rows.toLocaleString()} rows • Sierra CRM format`;
        
        info.appendChild(name);
        info.appendChild(size);
        
        const btn = document.createElement('button');
        btn.className = 'download-btn';
        btn.textContent = '⬇ Download CSV';
        btn.onclick = () => {
            downloadFile(file.path);
            btn.textContent = '✓ Downloaded';
            btn.style.background = '#218838';
            setTimeout(() => {
                btn.textContent = '⬇ Download Again';
                btn.style.background = '#4caf50';
            }, 2000);
        };
        
        fileDiv.appendChild(info);
        fileDiv.appendChild(btn);
        downloadFiles.appendChild(fileDiv);
    });
}

function downloadFile(path) {
    window.location.href = `/download/${path}`;
}

function downloadZip() {
    window.location.href = '/download_zip';
}

// ====================
// UI State Management
// ====================

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('active');
}

function hideError() {
    errorMessage.classList.remove('active');
}

function disableUpload() {
    uploadZone.classList.add('disabled');
    uploadZone.style.position = 'relative';
    fileInput.disabled = true;
    isPaymentComplete = true;
}

function enableUpload() {
    uploadZone.classList.remove('disabled');
    fileInput.disabled = false;
    isPaymentComplete = false;
}

function resetToInitialState() {
    enableUpload();
    mappingSection.classList.add('hidden');
    consoleSection.classList.add('hidden');
    previewSection.classList.remove('active');
    downloadSection.classList.remove('active');
    downloadSection.classList.add('hidden');
    paymentNoticeInline.style.display = 'none';
    if (paymentCard) {
        paymentCard.style.display = 'none';
    }
    consoleOutput.innerHTML = '';
    previewTable.innerHTML = '';
    downloadFiles.innerHTML = '';
    
    currentFile = null;
    detectedColumns = [];
    convertedFiles = null;
    
    uploadZone.querySelector('h2').textContent = 'Drop your FUB CSV file here';
    uploadZone.querySelector('p').textContent = 'or click to browse';
    
    fetch('/reset_session')
        .then(() => console.log('Session reset complete'))
        .catch(error => console.error('Error resetting session:', error));
}

// ====================
// Modal Workflow
// ====================

convertAnotherBtn.addEventListener('click', () => {
    warningModal.style.display = 'flex';
});

cancelWarningBtn.addEventListener('click', () => {
    warningModal.style.display = 'none';
});

confirmWarningBtn.addEventListener('click', () => {
    warningModal.style.display = 'none';
    confirmModal.style.display = 'flex';
});

cancelConfirmBtn.addEventListener('click', () => {
    confirmModal.style.display = 'none';
});

finalConfirmBtn.addEventListener('click', () => {
    confirmModal.style.display = 'none';
    resetToInitialState();
    window.scrollTo({ top: 0, behavior: 'smooth' });
    addConsoleLog('✅ Ready for new conversion! Upload your FUB CSV file above.', 'success');
    consoleSection.classList.remove('hidden');
});

// ====================
// Payment Verification
// ====================

const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('payment_success') === 'true') {
    fetch('/mark_payment_complete?payment_success=true')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addConsoleLog('✅ Payment verified! Loading your downloads...', 'success');
                consoleSection.classList.remove('hidden');
                return fetch('/verify_payment');
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.payment_completed && data.has_files) {
                displayDownloads(data.files);
                downloadSection.classList.add('active');
                paymentNoticeInline.style.display = 'none';
                if (paymentCard) {
                    paymentCard.style.display = 'none';
                }
                disableUpload();
                downloadSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                addConsoleLog('⚠️ No files found. Please upload and convert a file first.', 'error');
            }
        })
        .catch(error => {
            addConsoleLog('❌ Error verifying payment: ' + error.message, 'error');
        });
    
    window.history.replaceState({}, document.title, window.location.pathname);
} else {
    fetch('/verify_payment')
        .then(response => response.json())
        .then(data => {
            if (data.payment_completed && data.has_files) {
                displayDownloads(data.files);
                downloadSection.classList.add('active');
                addConsoleLog('👋 Welcome back! Your files are ready to download.', 'success');
                consoleSection.classList.remove('hidden');
                if (paymentCard) {
                    paymentCard.style.display = 'none';
                }
                disableUpload();
            }
        })
        .catch(error => {
            console.log('No existing session');
        });
}
