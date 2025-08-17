// =============================================================================
// ADMIN IMPORT/EXPORT JAVASCRIPT
// =============================================================================
// Veri aktarımı sayfası için JavaScript fonksiyonları
// =============================================================================

class AdminImportExport {
    constructor() {
        this.currentJsonFile = null;
        this.currentJsonContent = null;
        this.init();
    }

    async init() {
        await this.loadJsonFiles();
        await this.loadGrades();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // File upload change event
        const fileUpload = document.getElementById('fileUpload');
        if (fileUpload) {
            fileUpload.addEventListener('change', this.handleFileSelect.bind(this));
        }
    }

    async loadJsonFiles() {
        try {
            const response = await adminBase.apiRequest('/curriculum/json-files');
            
            if (response.success) {
                this.updateJsonFilesTable(response.data);
                this.updateImportFileSelect(response.data);
            } else {
                adminBase.showError('JSON dosyaları yüklenirken hata oluştu');
            }
        } catch (error) {
            console.error('JSON files loading error:', error);
            adminBase.showError('JSON dosyaları yüklenirken hata oluştu: ' + error.message);
        }
    }

    async loadGrades() {
        try {
            const response = await adminBase.getGrades();
            
            if (response.success) {
                this.updateExportGradeSelect(response.data);
            } else {
                adminBase.showError('Sınıflar yüklenirken hata oluştu');
            }
        } catch (error) {
            console.error('Grades loading error:', error);
            adminBase.showError('Sınıflar yüklenirken hata oluştu: ' + error.message);
        }
    }

    updateJsonFilesTable(files) {
        const tableColumns = [
            { 
                field: 'filename', 
                render: (filename) => `
                    <i class="fas fa-file-code text-primary me-2"></i>
                    <strong>${filename}</strong>
                `
            },
            { 
                field: 'actions', 
                render: (filename) => `
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="viewJsonContent('${filename}')" title="İçeriği Görüntüle">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-success" onclick="importFromJsonFile('${filename}')" title="Veritabanına Aktar">
                            <i class="fas fa-upload"></i>
                        </button>
                        <button class="btn btn-outline-info" onclick="downloadJsonFile('${filename}')" title="İndir">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="deleteJsonFile('${filename}')" title="Sil">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                `
            }
        ];

        const tableData = files.map(filename => ({ filename }));
        adminBase.updateTable('jsonFilesTable', tableData, tableColumns);
    }

    updateImportFileSelect(files) {
        const select = document.getElementById('importFileSelect');
        if (!select) return;

        select.innerHTML = '<option value="">Dosya seçiniz...</option>';
        files.forEach(filename => {
            select.innerHTML += `<option value="${filename}">${filename}</option>`;
        });
    }

    updateExportGradeSelect(grades) {
        const select = document.getElementById('exportGradeSelect');
        if (!select) return;

        select.innerHTML = '<option value="">Sınıf seçiniz...</option>';
        grades.forEach(grade => {
            select.innerHTML += `<option value="${grade.grade_id}">${grade.grade_name}</option>`;
        });
    }

    async viewJsonContent(filename) {
        try {
            adminBase.showLoading();
            
            const response = await adminBase.apiRequest(`/curriculum/json/${filename}`);
            
            if (response.success) {
                this.currentJsonFile = filename;
                this.currentJsonContent = response.data;
                
                const jsonContent = document.getElementById('jsonContent');
                if (jsonContent) {
                    jsonContent.textContent = JSON.stringify(response.data, null, 2);
                }
                
                const modal = new bootstrap.Modal(document.getElementById('jsonViewerModal'));
                modal.show();
            } else {
                adminBase.showError('JSON içeriği yüklenirken hata oluştu');
            }
        } catch (error) {
            console.error('JSON content loading error:', error);
            adminBase.showError('JSON içeriği yüklenirken hata oluştu: ' + error.message);
        } finally {
            adminBase.hideLoading();
        }
    }

    async importFromJson() {
        const filename = document.getElementById('importFileSelect').value;
        if (!filename) {
            adminBase.showWarning('Lütfen bir JSON dosyası seçiniz');
            return;
        }

        await this.importFromJsonFile(filename);
    }

    async importFromJsonFile(filename) {
        if (!confirm(`${filename} dosyasını veritabanına aktarmak istediğinizden emin misiniz?`)) {
            return;
        }

        try {
            // Show progress modal
            const progressModal = new bootstrap.Modal(document.getElementById('importProgressModal'));
            progressModal.show();
            
            const response = await adminBase.apiRequest(`/curriculum/import/${filename}`, 'POST');
            
            // Hide progress modal
            progressModal.hide();
            
            if (response.success) {
                this.showImportResults(response.data, response.message);
            } else {
                adminBase.showError('Aktarım işlemi başarısız: ' + response.message);
            }
        } catch (error) {
            // Hide progress modal
            const progressModal = bootstrap.Modal.getInstance(document.getElementById('importProgressModal'));
            if (progressModal) {
                progressModal.hide();
            }
            
            console.error('Import error:', error);
            adminBase.showError('Aktarım işlemi sırasında hata oluştu: ' + error.message);
        }
    }

    showImportResults(importData, message) {
        const resultsContent = document.getElementById('importResultsContent');
        if (!resultsContent) return;

        resultsContent.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                ${message}
            </div>
            
            <h6>Aktarım Detayları:</h6>
            <div class="row">
                <div class="col-6 col-md-3">
                    <div class="text-center p-3 bg-light rounded">
                        <div class="h4 text-primary mb-1">${importData.grades || 0}</div>
                        <small class="text-muted">Sınıf</small>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="text-center p-3 bg-light rounded">
                        <div class="h4 text-success mb-1">${importData.subjects || 0}</div>
                        <small class="text-muted">Ders</small>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="text-center p-3 bg-light rounded">
                        <div class="h4 text-warning mb-1">${importData.units || 0}</div>
                        <small class="text-muted">Ünite</small>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="text-center p-3 bg-light rounded">
                        <div class="h4 text-info mb-1">${importData.topics || 0}</div>
                        <small class="text-muted">Konu</small>
                    </div>
                </div>
            </div>
        `;

        const modal = new bootstrap.Modal(document.getElementById('importResultsModal'));
        modal.show();
    }

    async exportToJson() {
        const gradeId = document.getElementById('exportGradeSelect').value;
        if (!gradeId) {
            adminBase.showWarning('Lütfen bir sınıf seçiniz');
            return;
        }

        try {
            adminBase.showLoading();
            
            const response = await adminBase.apiRequest(`/curriculum/export/${gradeId}`);
            
            if (response.success) {
                // Create and download JSON file
                const dataStr = JSON.stringify(response.data, null, 2);
                const dataBlob = new Blob([dataStr], {type: 'application/json'});
                
                const link = document.createElement('a');
                link.href = URL.createObjectURL(dataBlob);
                link.download = `grade_${gradeId}_curriculum_${new Date().toISOString().split('T')[0]}.json`;
                link.click();
                
                adminBase.showSuccess('Müfredat başarıyla export edildi');
            } else {
                adminBase.showError('Export işlemi başarısız: ' + response.message);
            }
        } catch (error) {
            console.error('Export error:', error);
            adminBase.showError('Export işlemi sırasında hata oluştu: ' + error.message);
        } finally {
            adminBase.hideLoading();
        }
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (!file.name.endsWith('.json')) {
            adminBase.showError('Lütfen geçerli bir JSON dosyası seçiniz');
            event.target.value = '';
            return;
        }

        if (file.size > 5 * 1024 * 1024) { // 5MB limit
            adminBase.showError('Dosya boyutu 5MB\'dan büyük olamaz');
            event.target.value = '';
            return;
        }
    }

    async uploadJsonFile() {
        const fileInput = document.getElementById('fileUpload');
        const file = fileInput.files[0];
        
        if (!file) {
            adminBase.showWarning('Lütfen bir dosya seçiniz');
            return;
        }

        try {
            adminBase.showLoading();
            
            // Read file content
            const fileContent = await this.readFileAsText(file);
            
            // Validate JSON
            let jsonData;
            try {
                jsonData = JSON.parse(fileContent);
            } catch (e) {
                throw new Error('Geçersiz JSON formatı');
            }
            
            // Save to server
            const response = await adminBase.apiRequest('/curriculum/save-json', 'POST', {
                filename: file.name,
                content: jsonData
            });
            
            if (response.success) {
                adminBase.showSuccess('JSON dosyası başarıyla yüklendi');
                fileInput.value = '';
                await this.loadJsonFiles();
            } else {
                adminBase.showError('Dosya yükleme başarısız: ' + response.message);
            }
        } catch (error) {
            console.error('File upload error:', error);
            adminBase.showError('Dosya yükleme sırasında hata oluştu: ' + error.message);
        } finally {
            adminBase.hideLoading();
        }
    }

    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('Dosya okuma hatası'));
            reader.readAsText(file, 'UTF-8');
        });
    }

    downloadCurrentJson() {
        if (!this.currentJsonContent || !this.currentJsonFile) {
            adminBase.showError('İndirilecek JSON içeriği bulunamadı');
            return;
        }

        const dataStr = JSON.stringify(this.currentJsonContent, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = this.currentJsonFile;
        link.click();
    }

    async deleteJsonFile(filename) {
        if (!confirm(`${filename} dosyasını silmek istediğinizden emin misiniz?`)) {
            return;
        }

        try {
            adminBase.showLoading();
            
            // Note: This would need to be implemented in the backend
            // const response = await adminBase.apiRequest(`/curriculum/json/${filename}`, 'DELETE');
            
            adminBase.showWarning('Dosya silme özelliği henüz implementasyonda');
            
        } catch (error) {
            console.error('Delete error:', error);
            adminBase.showError('Dosya silme sırasında hata oluştu: ' + error.message);
        } finally {
            adminBase.hideLoading();
        }
    }

    async downloadJsonFile(filename) {
        try {
            adminBase.showLoading();
            
            const response = await adminBase.apiRequest(`/curriculum/json/${filename}`);
            
            if (response.success) {
                const dataStr = JSON.stringify(response.data, null, 2);
                const dataBlob = new Blob([dataStr], {type: 'application/json'});
                
                const link = document.createElement('a');
                link.href = URL.createObjectURL(dataBlob);
                link.download = filename;
                link.click();
                
                adminBase.showSuccess('Dosya başarıyla indirildi');
            } else {
                adminBase.showError('Dosya indirme başarısız');
            }
        } catch (error) {
            console.error('Download error:', error);
            adminBase.showError('Dosya indirme sırasında hata oluştu: ' + error.message);
        } finally {
            adminBase.hideLoading();
        }
    }
}

// Global functions for template usage
window.loadJsonFiles = function() {
    window.adminImportExport.loadJsonFiles();
};

window.viewJsonContent = function(filename) {
    window.adminImportExport.viewJsonContent(filename);
};

window.importFromJson = function() {
    window.adminImportExport.importFromJson();
};

window.importFromJsonFile = function(filename) {
    window.adminImportExport.importFromJsonFile(filename);
};

window.exportToJson = function() {
    window.adminImportExport.exportToJson();
};

window.uploadJsonFile = function() {
    window.adminImportExport.uploadJsonFile();
};

window.downloadCurrentJson = function() {
    window.adminImportExport.downloadCurrentJson();
};

window.deleteJsonFile = function(filename) {
    window.adminImportExport.deleteJsonFile(filename);
};

window.downloadJsonFile = function(filename) {
    window.adminImportExport.downloadJsonFile(filename);
};

// Initialize import/export when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.adminImportExport = new AdminImportExport();
});
