// FUB to Sierra Converter - Main JavaScript
// Professional UI Implementation with Dark/Light Mode

// =====================
// Theme Management
// =====================

// Initialize theme from localStorage or default to dark
const initTheme = () => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
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
        themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
};

// Initialize theme on page load
initTheme();

// =====================
// Session Management
// =====================

// Track if this is a fresh page load or reload
// Set a flag on initial load and check on subsequent loads
const sessionKey = 'fub_converter_session_active';
const pageLoadTime = Date.now();

// Check if there's an existing session that should be warned about
const existingSession = sessionStorage.getItem(sessionKey);
let shouldSkipSessionRestore = false; // Flag to prevent session restore after reload

if (existingSession) {
    const sessionData = JSON.parse(existingSession);
    const timeDiff = pageLoadTime - sessionData.timestamp;
    
    // If session is less than 1 hour old and page was reloaded
    if (timeDiff < 3600000 && performance.navigation && performance.navigation.type === 1) {
        // Check if user had active files
        if (sessionData.active && sessionData.hasFiles) {
            // User confirmed the reload despite the beforeunload warning - clear everything
            shouldSkipSessionRestore = true; // Skip the session restore code below
            sessionStorage.clear();
            localStorage.removeItem('convertedFiles');
            
            // Clear files on server side
            fetch('/reset_session')
                .then(() => console.log('Session and files cleared on reload'))
                .catch(error => console.error('Error clearing session:', error));
            
            // Show a notification that session was cleared
            setTimeout(() => {
                showError('⚠️ Session Cleared: Your previous files were removed because you reloaded the page. Files are NOT stored on our servers. Please upload and convert again.');
            }, 500);
        }
    }
}

// Set new session marker
function updateSessionStorage(hasFiles = false) {
    sessionStorage.setItem(sessionKey, JSON.stringify({ 
        timestamp: pageLoadTime,
        active: true,
        hasFiles: hasFiles
    }));
}
updateSessionStorage(false);

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
const previewTableInline = document.getElementById('previewTableInline');
const paymentNoticeInline = document.getElementById('paymentNoticeInline');
const convertAnotherBtn = document.getElementById('convertAnotherBtn');
const warningModal = document.getElementById('warningModal');
const confirmModal = document.getElementById('confirmModal');
const cancelWarningBtn = document.getElementById('cancelWarningBtn');
const confirmWarningBtn = document.getElementById('confirmWarningBtn');
const cancelConfirmBtn = document.getElementById('cancelConfirmBtn');
const finalConfirmBtn = document.getElementById('finalConfirmBtn');
const paymentCard = document.getElementById('paymentCard');
const previewModal = document.getElementById('previewModal');
const openFullPreviewBtn = document.getElementById('openFullPreviewBtn');
const closePreviewBtn = document.getElementById('closePreviewBtn');
const zoomInBtn = document.getElementById('zoomIn');
const zoomOutBtn = document.getElementById('zoomOut');
const zoomResetBtn = document.getElementById('zoomReset');
const fullscreenBtn = document.getElementById('fullscreenBtn');
const zoomLevelSpan = document.getElementById('zoomLevel');
const previewTableContainer = document.getElementById('previewTableContainer');

// State
let currentFile = null;
let detectedColumns = [];
let convertedFiles = null;
let isPaymentComplete = false;
let currentZoom = 1.0;

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
        
        // Create custom checkbox with material design
        const checkboxWrapper = document.createElement('label');
        checkboxWrapper.className = 'custom-checkbox';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `map_${key}`;
        checkbox.checked = true; // Auto-check since it was found
        
        const checkboxVisual = document.createElement('span');
        checkboxVisual.className = 'checkbox-visual';
        
        checkboxWrapper.appendChild(checkbox);
        checkboxWrapper.appendChild(checkboxVisual);
        
        const label = document.createElement('label');
        label.className = 'mapping-label';
        label.textContent = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        label.setAttribute('for', `map_${key}`);
        
        const inputWrapper = document.createElement('div');
        inputWrapper.className = 'input-wrapper';
        
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'mapping-input';
        input.id = `val_${key}`;
        input.value = defaultValue;
        input.placeholder = 'Column name in CSV';
        input.readOnly = true; // Make read-only since it's auto-detected
        
        inputWrapper.appendChild(input);
        
        row.appendChild(checkboxWrapper);
        row.appendChild(label);
        row.appendChild(inputWrapper);
        
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
        previewSection.style.display = 'none';
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
                displayPreview(result.preview, result.preview_note, result.total_rows);
            }

            convertedFiles = result.files;
            sessionStorage.setItem('convertedFiles', JSON.stringify(result.files));
            
            addConsoleLog('', 'info');
            addConsoleLog('✅ Conversion complete!', 'success');
            addConsoleLog('👁️ Click "View Data Preview" button below to review your converted data', 'info');
            
            // Payment notice will be shown in preview section by displayPreview
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

function displayPreview(previewData, note, totalRows) {
    if (!previewData || previewData.length === 0) return;

    // Update preview headers with dynamic row counts
    const previewCount = previewData.length;
    const totalRowsText = totalRows ? ` out of ${totalRows.toLocaleString()} Total` : '';
    
    // Update inline preview header
    const inlineHeader = document.querySelector('#previewSection h2');
    if (inlineHeader) {
        inlineHeader.innerHTML = `Data Preview (First ${previewCount} Rows${totalRowsText})`;
    }
    
    // Update modal preview header
    const modalHeader = document.querySelector('#previewModal h2');
    if (modalHeader) {
        modalHeader.innerHTML = `👁️ Data Preview (First ${previewCount} Rows${totalRowsText})`;
    }
    
    // Update modal subtitle
    const modalSubtitle = document.querySelector('#previewModal h2 + p');
    if (modalSubtitle) {
        modalSubtitle.textContent = `Showing first ${previewCount} rows of your converted Sierra CRM data`;
    }

    // Populate both inline preview and modal preview
    [previewTableInline, previewTable].forEach(table => {
        if (!table) return;
        
        table.innerHTML = '';

        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        const columns = Object.keys(previewData[0]);
        
        columns.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

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
        table.appendChild(tbody);
        
        // Disable copy/paste/cut on preview tables
        table.addEventListener('copy', e => e.preventDefault());
        table.addEventListener('cut', e => e.preventDefault());
        table.addEventListener('contextmenu', e => e.preventDefault());
        table.style.userSelect = 'none';
        table.style.webkitUserSelect = 'none';
        table.style.msUserSelect = 'none';
        
        // Make columns resizable
        makeColumnsResizable(table);
    });

    // Show the preview section
    previewSection.style.display = 'block';
    previewSection.classList.add('active');
    
    // Ensure payment notice is visible in the preview section
    if (paymentNoticeInline) {
        paymentNoticeInline.style.display = 'block';
    }
    
    // Scroll to preview section
    previewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Make table columns resizable
function makeColumnsResizable(table) {
    const headers = table.querySelectorAll('th');
    headers.forEach((th, index) => {
        const resizer = document.createElement('div');
        resizer.style.position = 'absolute';
        resizer.style.right = '0';
        resizer.style.top = '0';
        resizer.style.bottom = '0';
        resizer.style.width = '8px';
        resizer.style.cursor = 'col-resize';
        resizer.style.userSelect = 'none';
        resizer.style.zIndex = '1';
        
        th.style.position = 'relative';
        th.appendChild(resizer);
        
        let startX, startWidth;
        
        resizer.addEventListener('mousedown', (e) => {
            e.preventDefault();
            e.stopPropagation();
            startX = e.pageX;
            startWidth = th.offsetWidth;
            
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
            
            resizer.style.background = 'var(--accent-purple)';
            resizer.style.opacity = '0.5';
        });
        
        function onMouseMove(e) {
            const width = startWidth + (e.pageX - startX);
            if (width >= 50) {
                th.style.width = width + 'px';
                th.style.minWidth = width + 'px';
            }
        }
        
        function onMouseUp() {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            resizer.style.background = '';
            resizer.style.opacity = '';
        }
    });
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
        zipDiv.className = 'download-file zip-download';
        
        const info = document.createElement('div');
        info.className = 'file-info';
        
        const name = document.createElement('div');
        name.className = 'file-name';
        name.innerHTML = '<span style="font-size: 1.5rem;">📦</span> All Files (ZIP Archive)';
        
        const size = document.createElement('div');
        size.className = 'file-size';
        const totalRows = files.reduce((sum, f) => sum + f.rows, 0);
        size.textContent = `${files.length} files • ${totalRows.toLocaleString()} total rows`;
        
        info.appendChild(name);
        info.appendChild(size);
        
        const btn = document.createElement('button');
        btn.className = 'download-btn';
        btn.innerHTML = '<span style="font-size: 1.125rem;">⬇️</span> Download ZIP';
        btn.onclick = () => {
            downloadZip();
            btn.innerHTML = '<span style="font-size: 1.125rem;">✓</span> Downloaded';
            btn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
            setTimeout(() => {
                btn.innerHTML = '<span style="font-size: 1.125rem;">⬇️</span> Download Again';
                btn.style.background = '';
            }, 2000);
        };
        
        zipDiv.appendChild(info);
        zipDiv.appendChild(btn);
        downloadFiles.appendChild(zipDiv);
        
        const separator = document.createElement('div');
        separator.className = 'download-separator';
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
        name.innerHTML = '<span style="font-size: 1.25rem;">📄</span> ' + file.filename;
        
        const size = document.createElement('div');
        size.className = 'file-size';
        size.textContent = `${file.rows.toLocaleString()} rows • Sierra CRM format`;
        
        info.appendChild(name);
        info.appendChild(size);
        
        const btn = document.createElement('button');
        btn.className = 'download-btn';
        btn.innerHTML = '<span style="font-size: 1.125rem;">⬇️</span> Download CSV';
        btn.onclick = () => {
            downloadFile(file.path);
            btn.innerHTML = '<span style="font-size: 1.125rem;">✓</span> Downloaded';
            btn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
            setTimeout(() => {
                btn.innerHTML = '<span style="font-size: 1.125rem;">⬇️</span> Download Again';
                btn.style.background = '';
            }, 2000);
        };
        
        fileDiv.appendChild(info);
        fileDiv.appendChild(btn);
        downloadFiles.appendChild(fileDiv);
    });
}

function downloadFile(path) {
    isDownloading = true; // Set flag before download
    showToast('📥 Downloading file...', 'info');
    window.location.href = `/download/${path}`;
    // Reset flag after a short delay to allow download to start
    setTimeout(() => {
        isDownloading = false;
        showToast('✅ Download started! Check your downloads folder.', 'success');
    }, 500);
}

function downloadZip() {
    isDownloading = true; // Set flag before download
    showToast('📦 Preparing ZIP file...', 'info');
    window.location.href = '/download_zip';
    // Reset flag after a short delay to allow download to start
    setTimeout(() => {
        isDownloading = false;
        showToast('✅ ZIP download started! Check your downloads folder.', 'success');
    }, 500);
}

// Helper function to show toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        background: ${type === 'success' ? '#10b981' : type === 'info' ? '#3b82f6' : '#f59e0b'};
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        font-weight: 500;
        max-width: 400px;
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ====================
// UI State Management
// ====================

function showError(message) {
    errorMessage.innerHTML = `
        <span style="flex: 1;">${message}</span>
        <button onclick="hideError()" style="background: none; border: none; color: inherit; cursor: pointer; font-size: 1.25rem; padding: 0 8px; margin-left: 12px; opacity: 0.8; transition: opacity 0.2s;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.8'">✕</button>
    `;
    errorMessage.style.display = 'flex';
    errorMessage.style.alignItems = 'center';
    errorMessage.classList.add('active');
}

function hideError() {
    errorMessage.classList.remove('active');
    setTimeout(() => {
        errorMessage.innerHTML = '';
    }, 300);
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
    // Clear active files flag
    hasActiveFiles = false;
    updateSessionStorage(false);
    
    enableUpload();
    mappingSection.classList.add('hidden');
    consoleSection.classList.add('hidden');
    previewSection.style.display = 'none';
    previewSection.classList.remove('active');
    downloadSection.classList.remove('active');
    downloadSection.classList.add('hidden');
    paymentNoticeInline.style.display = 'none';
    if (previewModal) {
        previewModal.classList.remove('active');
        previewModal.style.display = 'none';
    }
    if (paymentCard) {
        paymentCard.style.display = 'none';
    }
    consoleOutput.innerHTML = '';
    previewTable.innerHTML = '';
    previewTableInline.innerHTML = '';
    downloadFiles.innerHTML = '';
    
    currentFile = null;
    detectedColumns = [];
    convertedFiles = null;
    
    uploadZone.querySelector('h2').textContent = 'Drop your FUB CSV file here';
    uploadZone.querySelector('p').textContent = 'or click to browse';
    
    fetch('/reset_session')
        .then(() => {
            console.log('Session reset complete - all files deleted');
            showToast('🗑️ All files deleted. Ready for new conversion.', 'success');
        })
        .catch(error => console.error('Error resetting session:', error));
}

// ====================
// Preview Modal Controls
// ====================

if (openFullPreviewBtn) {
    openFullPreviewBtn.addEventListener('click', () => {
        if (previewModal) {
            previewModal.style.display = 'flex';
            // Use setTimeout to ensure display:flex is applied before adding active class
            setTimeout(() => {
                previewModal.classList.add('active');
            }, 10);
            currentZoom = 1.0;
            updateZoom();
        }
    });
}

if (closePreviewBtn) {
    closePreviewBtn.addEventListener('click', () => {
        if (previewModal) {
            previewModal.classList.remove('active');
            setTimeout(() => {
                previewModal.style.display = 'none';
            }, 300); // Wait for fade out animation
        }
    });
}

if (zoomInBtn) {
    zoomInBtn.addEventListener('click', () => {
        currentZoom = Math.min(currentZoom + 0.1, 2.0);
        updateZoom();
    });
}

if (zoomOutBtn) {
    zoomOutBtn.addEventListener('click', () => {
        currentZoom = Math.max(currentZoom - 0.1, 0.5);
        updateZoom();
    });
}

if (zoomResetBtn) {
    zoomResetBtn.addEventListener('click', () => {
        currentZoom = 1.0;
        updateZoom();
    });
}

if (fullscreenBtn) {
    fullscreenBtn.addEventListener('click', () => {
        if (!document.fullscreenElement) {
            // Enter fullscreen
            const elem = previewModal;
            if (elem.requestFullscreen) {
                elem.requestFullscreen();
            } else if (elem.webkitRequestFullscreen) {
                elem.webkitRequestFullscreen();
            } else if (elem.msRequestFullscreen) {
                elem.msRequestFullscreen();
            }
        } else {
            // Exit fullscreen
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
        }
    });
}

// Listen for fullscreen changes to update button text and handle modal closure
if (document.addEventListener) {
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('mozfullscreenchange', handleFullscreenChange);
    document.addEventListener('MSFullscreenChange', handleFullscreenChange);
}

function handleFullscreenChange() {
    const isFullscreen = document.fullscreenElement || document.webkitFullscreenElement || 
                         document.mozFullScreenElement || document.msFullscreenElement;
    
    // Update button text
    if (fullscreenBtn) {
        if (isFullscreen) {
            fullscreenBtn.innerHTML = '⇲ Exit Fullscreen';
        } else {
            fullscreenBtn.innerHTML = '⇱ Fullscreen';
        }
    }
    
    // Gracefully close modal when user exits fullscreen (e.g., pressing ESC)
    if (!isFullscreen && previewModal && previewModal.style.display === 'flex') {
        // User exited fullscreen, close the modal gracefully
        setTimeout(() => {
            previewModal.classList.remove('active');
            setTimeout(() => {
                previewModal.style.display = 'none';
            }, 300); // Match CSS transition duration
        }, 100);
    }
}

function updateFullscreenButton() {
    if (fullscreenBtn) {
        if (document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement) {
            fullscreenBtn.innerHTML = '⇲ Exit Fullscreen';
        } else {
            fullscreenBtn.innerHTML = '⇱ Fullscreen';
        }
    }
}

function updateZoom() {
    if (previewTableContainer) {
        previewTableContainer.style.transform = `scale(${currentZoom})`;
        previewTableContainer.style.transformOrigin = 'top left';
    }
    if (zoomLevelSpan) {
        zoomLevelSpan.textContent = `${Math.round(currentZoom * 100)}%`;
    }
}

// Close modal when clicking outside
if (previewModal) {
    previewModal.addEventListener('click', (e) => {
        if (e.target === previewModal) {
            previewModal.classList.remove('active');
            setTimeout(() => {
                previewModal.style.display = 'none';
            }, 300);
        }
    });
}

// ====================
// Modal Workflow
// ====================

if (convertAnotherBtn) {
    convertAnotherBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (warningModal) {
            warningModal.style.display = 'flex';
            setTimeout(() => warningModal.classList.add('active'), 10);
        }
    });
}

if (cancelWarningBtn) {
    cancelWarningBtn.addEventListener('click', () => {
        warningModal.classList.remove('active');
        setTimeout(() => warningModal.style.display = 'none', 300);
    });
}

if (confirmWarningBtn) {
    confirmWarningBtn.addEventListener('click', () => {
        warningModal.classList.remove('active');
        setTimeout(() => {
            warningModal.style.display = 'none';
            confirmModal.style.display = 'flex';
            setTimeout(() => confirmModal.classList.add('active'), 10);
        }, 300);
    });
}

if (cancelConfirmBtn) {
    cancelConfirmBtn.addEventListener('click', () => {
        confirmModal.classList.remove('active');
        setTimeout(() => confirmModal.style.display = 'none', 300);
    });
}

if (finalConfirmBtn) {
    finalConfirmBtn.addEventListener('click', () => {
        confirmModal.classList.remove('active');
        setTimeout(() => {
            confirmModal.style.display = 'none';
            resetToInitialState();
            window.scrollTo({ top: 0, behavior: 'smooth' });
            addConsoleLog('✅ Ready for new conversion! Upload your FUB CSV file above.', 'success');
            consoleSection.classList.remove('hidden');
        }, 300);
    });
}

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
} else if (!shouldSkipSessionRestore) {
    // Only restore session if we didn't just clear it from a reload
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

// =====================
// Page Navigation Protection
// =====================

// Track if user has active files/preview
let hasActiveFiles = false;
let isDownloading = false; // Flag to track intentional downloads

// Warn user before leaving page if they have converted files
window.addEventListener('beforeunload', (event) => {
    // Don't warn if user is downloading files
    if (isDownloading) {
        isDownloading = false; // Reset flag
        return;
    }
    
    // Check if user has files in download section or preview visible
    const downloadVisible = downloadSection && !downloadSection.classList.contains('hidden');
    const previewVisible = previewSection && previewSection.style.display !== 'none';
    
    if (downloadVisible || previewVisible || hasActiveFiles) {
        event.preventDefault();
        event.returnValue = 'You have converted files that will be lost if you leave this page. Files are NOT stored on our servers. Have you downloaded everything?';
        return 'You have converted files that will be lost if you leave this page. Files are NOT stored on our servers. Have you downloaded everything?';
    }
});

// Prevent accidental back navigation loss
window.addEventListener('popstate', (event) => {
    const downloadVisible = downloadSection && !downloadSection.classList.contains('hidden');
    const previewVisible = previewSection && previewSection.style.display !== 'none';
    
    if (downloadVisible || previewVisible || hasActiveFiles) {
        const confirmLeave = confirm(
            '⚠️ WARNING: Going back will cause you to lose your converted files!\n\n' +
            'Your files are only available during this session and are NOT stored on our servers.\n\n' +
            'Have you downloaded all your files?\n\n' +
            'Click "Cancel" to stay on this page.\n' +
            'Click "OK" only if you have downloaded everything.'
        );
        
        if (!confirmLeave) {
            // Push state back to prevent navigation
            window.history.pushState(null, document.title, window.location.href);
        }
    }
});

// Push initial state to enable popstate detection
window.history.pushState(null, document.title, window.location.href);

// Mark files as active when preview or downloads are shown
const originalDisplayPreview = displayPreview;
displayPreview = function(data, note, totalRows) {
    hasActiveFiles = true;
    updateSessionStorage(true);
    return originalDisplayPreview.call(this, data, note, totalRows);
};

const originalDisplayDownloads = displayDownloads;
displayDownloads = function(files) {
    hasActiveFiles = true;
    updateSessionStorage(true);
    return originalDisplayDownloads.call(this, files);
};
