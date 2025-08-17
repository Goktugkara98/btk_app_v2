// =============================================================================
// ADMIN GRADES JAVASCRIPT
// =============================================================================
// Sınıf yönetimi sayfası için JavaScript fonksiyonları
// =============================================================================

class AdminGrades {
    constructor() {
        this.grades = [];
        this.init();
    }

    async init() {
        await this.loadGrades();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Modal events
        const gradeModal = document.getElementById('gradeModal');
        if (gradeModal) {
            gradeModal.addEventListener('hidden.bs.modal', () => {
                adminBase.resetForm('gradeForm');
            });
        }
    }

    async loadGrades() {
        try {
            adminBase.showLoading();
            
            const response = await adminBase.getGrades();
            
            if (response.success) {
                this.grades = response.data;
                this.updateGradesTable();
            } else {
                adminBase.showError('Sınıflar yüklenirken hata oluştu');
            }
        } catch (error) {
            console.error('Grades loading error:', error);
            adminBase.showError('Sınıflar yüklenirken hata oluştu: ' + error.message);
        } finally {
            adminBase.hideLoading();
        }
    }

    updateGradesTable() {
        const tableColumns = [
            { field: 'grade_id', render: (item) => `<strong>#${item.grade_id}</strong>` },
            { field: 'grade_name', render: (item) => `<strong>${item.grade_name}</strong>` },
            { field: 'description', render: (item) => item.description || '-' },
            { 
                field: 'is_active', 
                render: (item) => `
                    <span class="badge ${item.is_active ? 'bg-success' : 'bg-danger'}">
                        ${item.is_active ? 'Aktif' : 'Pasif'}
                    </span>
                `
            },
            { field: 'created_at', render: (item) => adminBase.formatDate(item.created_at) },
            { 
                field: 'actions', 
                render: (item) => `
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-warning" onclick="editGrade(${item.grade_id})" title="Düzenle">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="deleteGrade(${item.grade_id})" title="Sil">
                            <i class="fas fa-trash"></i>
                        </button>
                        <a href="/admin/subjects?grade_id=${item.grade_id}" class="btn btn-outline-info" title="Dersleri Görüntüle">
                            <i class="fas fa-eye"></i>
                        </a>
                    </div>
                `
            }
        ];

        adminBase.updateTable('gradesTable', this.grades, tableColumns);
    }

    showAddModal() {
        const modal = new bootstrap.Modal(document.getElementById('gradeModal'));
        
        // Reset form
        adminBase.resetForm('gradeForm');
        
        // Set modal title
        document.getElementById('modalTitle').textContent = 'Yeni Sınıf Ekle';
        document.getElementById('gradeId').value = '';
        
        modal.show();
    }

    showEditModal(gradeId) {
        const grade = this.grades.find(g => g.grade_id === gradeId);
        if (!grade) {
            adminBase.showError('Sınıf bulunamadı');
            return;
        }

        const modal = new bootstrap.Modal(document.getElementById('gradeModal'));
        
        // Reset form
        adminBase.resetForm('gradeForm');
        
        // Set modal title
        document.getElementById('modalTitle').textContent = 'Sınıf Düzenle';
        
        // Fill form
        document.getElementById('gradeId').value = grade.grade_id;
        document.getElementById('gradeName').value = grade.grade_name;
        document.getElementById('gradeDescription').value = grade.description || '';
        document.getElementById('isActive').checked = grade.is_active;
        
        modal.show();
    }

    async saveGrade() {
        if (!adminBase.validateForm('gradeForm')) {
            return;
        }

        const form = document.getElementById('gradeForm');
        const formData = new FormData(form);
        const gradeId = formData.get('gradeId');
        const isEdit = gradeId && gradeId !== '';

        const data = {
            grade_name: formData.get('gradeName'),
            description: formData.get('gradeDescription'),
            is_active: formData.get('isActive') === 'on'
        };

        try {
            adminBase.showLoading();
            
            let response;
            if (isEdit) {
                response = await adminBase.updateItem('grade', gradeId, data);
            } else {
                response = await adminBase.createItem('grade', data);
            }

            if (response.success) {
                adminBase.showSuccess(`Sınıf başarıyla ${isEdit ? 'güncellendi' : 'oluşturuldu'}`);
                bootstrap.Modal.getInstance(document.getElementById('gradeModal')).hide();
                await this.loadGrades();
            } else {
                adminBase.showError(response.message);
            }
        } catch (error) {
            console.error('Save error:', error);
            adminBase.showError('Kaydetme işlemi sırasında hata oluştu: ' + error.message);
        } finally {
            adminBase.hideLoading();
        }
    }

    async deleteGrade(gradeId) {
        const grade = this.grades.find(g => g.grade_id === gradeId);
        if (!grade) {
            adminBase.showError('Sınıf bulunamadı');
            return;
        }

        if (!confirm(`"${grade.grade_name}" sınıfını silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz ve bu sınıfa bağlı tüm dersler, üniteler ve konular da silinecektir.`)) {
            return;
        }

        try {
            adminBase.showLoading();
            
            const response = await adminBase.deleteItem('grade', gradeId);
            
            if (response.success) {
                adminBase.showSuccess('Sınıf başarıyla silindi');
                await this.loadGrades();
            } else {
                adminBase.showError(response.message);
            }
        } catch (error) {
            console.error('Delete error:', error);
            adminBase.showError('Silme işlemi sırasında hata oluştu: ' + error.message);
        } finally {
            adminBase.hideLoading();
        }
    }
}

// Global functions for template usage
window.showAddModal = function() {
    window.adminGrades.showAddModal();
};

window.editGrade = function(gradeId) {
    window.adminGrades.showEditModal(gradeId);
};

window.deleteGrade = function(gradeId) {
    window.adminGrades.deleteGrade(gradeId);
};

window.saveGrade = function() {
    window.adminGrades.saveGrade();
};

// Initialize grades when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.adminGrades = new AdminGrades();
});
