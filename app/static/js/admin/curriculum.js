// =============================================================================
// ADMIN CURRICULUM JAVASCRIPT
// =============================================================================
// Müfredat yönetimi sayfası için JavaScript fonksiyonları
// =============================================================================

class AdminCurriculum {
    constructor() {
        this.selectedItem = null;
        this.curriculumData = {};
        this.init();
    }

    async init() {
        await this.loadCurriculumTree();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Tree node clicks
        document.addEventListener('click', (e) => {
            if (e.target.closest('.tree-item')) {
                this.handleTreeItemClick(e.target.closest('.tree-item'));
            }
            
            if (e.target.closest('.tree-toggle')) {
                this.handleTreeToggle(e.target.closest('.tree-toggle'));
            }
        });

        // Modal events
        const addEditModal = document.getElementById('addEditModal');
        if (addEditModal) {
            addEditModal.addEventListener('hidden.bs.modal', () => {
                adminBase.resetForm('addEditForm');
            });
        }
    }

    async loadCurriculumTree() {
        try {
            adminBase.showLoading();
            
            // Load all curriculum data
            const [gradesResponse, subjectsResponse, unitsResponse, topicsResponse] = await Promise.all([
                adminBase.getGrades(),
                adminBase.getSubjects(),
                adminBase.getUnits(),
                adminBase.getTopics()
            ]);

            if (gradesResponse.success && subjectsResponse.success && 
                unitsResponse.success && topicsResponse.success) {
                
                this.curriculumData = {
                    grades: gradesResponse.data,
                    subjects: subjectsResponse.data,
                    units: unitsResponse.data,
                    topics: topicsResponse.data
                };

                this.renderCurriculumTree();
            } else {
                adminBase.showError('Müfredat verileri yüklenirken hata oluştu');
            }
        } catch (error) {
            console.error('Curriculum loading error:', error);
            adminBase.showError('Müfredat verileri yüklenirken hata oluştu: ' + error.message);
        } finally {
            adminBase.hideLoading();
        }
    }

    renderCurriculumTree() {
        const treeContainer = document.getElementById('curriculumTree');
        if (!treeContainer) return;

        let html = '';
        
        this.curriculumData.grades.forEach(grade => {
            const gradeSubjects = this.curriculumData.subjects.filter(s => s.grade_id === grade.grade_id);
            
            html += `
                <div class="tree-node">
                    <div class="tree-item" data-type="grade" data-id="${grade.grade_id}">
                        <button class="tree-toggle" data-target="grade-${grade.grade_id}">
                            <i class="fas fa-chevron-right"></i>
                        </button>
                        <i class="tree-icon fas fa-layer-group text-primary"></i>
                        <span class="tree-label">${grade.grade_name}</span>
                        <div class="tree-actions">
                            <button class="tree-action-btn edit" onclick="editItem('grade', ${grade.grade_id})" title="Düzenle">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="tree-action-btn delete" onclick="deleteItem('grade', ${grade.grade_id})" title="Sil">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="tree-children" id="grade-${grade.grade_id}" style="display: none;">
                        ${this.renderSubjects(gradeSubjects)}
                    </div>
                </div>
            `;
        });

        treeContainer.innerHTML = html;
    }

    renderSubjects(subjects) {
        let html = '';
        
        subjects.forEach(subject => {
            const subjectUnits = this.curriculumData.units.filter(u => u.subject_id === subject.subject_id);
            
            html += `
                <div class="tree-node">
                    <div class="tree-item" data-type="subject" data-id="${subject.subject_id}">
                        <button class="tree-toggle" data-target="subject-${subject.subject_id}">
                            <i class="fas fa-chevron-right"></i>
                        </button>
                        <i class="tree-icon fas fa-book-open text-success"></i>
                        <span class="tree-label">${subject.subject_name}</span>
                        <div class="tree-actions">
                            <button class="tree-action-btn edit" onclick="editItem('subject', ${subject.subject_id})" title="Düzenle">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="tree-action-btn delete" onclick="deleteItem('subject', ${subject.subject_id})" title="Sil">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="tree-children" id="subject-${subject.subject_id}" style="display: none;">
                        ${this.renderUnits(subjectUnits)}
                    </div>
                </div>
            `;
        });

        return html;
    }

    renderUnits(units) {
        let html = '';
        
        units.forEach(unit => {
            const unitTopics = this.curriculumData.topics.filter(t => t.unit_id === unit.unit_id);
            
            html += `
                <div class="tree-node">
                    <div class="tree-item" data-type="unit" data-id="${unit.unit_id}">
                        <button class="tree-toggle" data-target="unit-${unit.unit_id}">
                            <i class="fas fa-chevron-right"></i>
                        </button>
                        <i class="tree-icon fas fa-folder text-warning"></i>
                        <span class="tree-label">${unit.unit_name}</span>
                        <div class="tree-actions">
                            <button class="tree-action-btn edit" onclick="editItem('unit', ${unit.unit_id})" title="Düzenle">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="tree-action-btn delete" onclick="deleteItem('unit', ${unit.unit_id})" title="Sil">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="tree-children" id="unit-${unit.unit_id}" style="display: none;">
                        ${this.renderTopics(unitTopics)}
                    </div>
                </div>
            `;
        });

        return html;
    }

    renderTopics(topics) {
        let html = '';
        
        topics.forEach(topic => {
            html += `
                <div class="tree-node">
                    <div class="tree-item" data-type="topic" data-id="${topic.topic_id}">
                        <span style="width: 20px; margin-right: 0.5rem;"></span>
                        <i class="tree-icon fas fa-list text-info"></i>
                        <span class="tree-label">${topic.topic_name}</span>
                        <div class="tree-actions">
                            <button class="tree-action-btn edit" onclick="editItem('topic', ${topic.topic_id})" title="Düzenle">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="tree-action-btn delete" onclick="deleteItem('topic', ${topic.topic_id})" title="Sil">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });

        return html;
    }

    handleTreeItemClick(item) {
        // Remove previous selection
        document.querySelectorAll('.tree-item.selected').forEach(el => {
            el.classList.remove('selected');
        });

        // Add selection to clicked item
        item.classList.add('selected');

        // Update selected item info
        const type = item.dataset.type;
        const id = parseInt(item.dataset.id);
        this.selectedItem = { type, id };
        this.showSelectedItemInfo();
    }

    handleTreeToggle(toggle) {
        const targetId = toggle.dataset.target;
        const target = document.getElementById(targetId);
        const icon = toggle.querySelector('i');

        if (target) {
            if (target.style.display === 'none') {
                target.style.display = 'block';
                icon.classList.remove('fa-chevron-right');
                icon.classList.add('fa-chevron-down');
            } else {
                target.style.display = 'none';
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-right');
            }
        }
    }

    showSelectedItemInfo() {
        const card = document.getElementById('selectedItemCard');
        const info = document.getElementById('selectedItemInfo');
        
        if (!this.selectedItem || !card || !info) return;

        const { type, id } = this.selectedItem;
        let item = null;

        switch (type) {
            case 'grade':
                item = this.curriculumData.grades.find(g => g.grade_id === id);
                break;
            case 'subject':
                item = this.curriculumData.subjects.find(s => s.subject_id === id);
                break;
            case 'unit':
                item = this.curriculumData.units.find(u => u.unit_id === id);
                break;
            case 'topic':
                item = this.curriculumData.topics.find(t => t.topic_id === id);
                break;
        }

        if (item) {
            const typeNames = {
                grade: 'Sınıf',
                subject: 'Ders',
                unit: 'Ünite',
                topic: 'Konu'
            };

            info.innerHTML = `
                <h6>${typeNames[type]}</h6>
                <p><strong>Ad:</strong> ${item[`${type}_name`] || item.grade_name}</p>
                ${item.description ? `<p><strong>Açıklama:</strong> ${item.description}</p>` : ''}
                <p><strong>Durum:</strong> 
                    <span class="badge ${item.is_active ? 'bg-success' : 'bg-danger'}">
                        ${item.is_active ? 'Aktif' : 'Pasif'}
                    </span>
                </p>
                <p><strong>Oluşturma:</strong> ${adminBase.formatDateTime(item.created_at)}</p>
                <div class="mt-3">
                    <button class="btn btn-sm btn-warning" onclick="editItem('${type}', ${id})">
                        <i class="fas fa-edit"></i> Düzenle
                    </button>
                    <button class="btn btn-sm btn-danger ms-2" onclick="deleteItem('${type}', ${id})">
                        <i class="fas fa-trash"></i> Sil
                    </button>
                </div>
            `;
            
            card.style.display = 'block';
        }
    }

    async showAddModal(type) {
        const modal = new bootstrap.Modal(document.getElementById('addEditModal'));
        const form = document.getElementById('addEditForm');
        
        // Reset form
        adminBase.resetForm('addEditForm');
        
        // Set form type
        document.getElementById('itemType').value = type;
        document.getElementById('itemId').value = '';
        
        // Update modal title and labels
        const typeNames = {
            grade: 'Sınıf',
            subject: 'Ders',
            unit: 'Ünite',
            topic: 'Konu'
        };
        
        document.getElementById('modalTitle').textContent = `Yeni ${typeNames[type]} Ekle`;
        document.getElementById('nameLabel').textContent = `${typeNames[type]} Adı`;
        
        // Setup parent selection
        await this.setupParentSelection(type);
        
        modal.show();
    }

    async setupParentSelection(type) {
        const parentGroup = document.getElementById('parentSelectGroup');
        const parentSelect = document.getElementById('parentSelect');
        const parentLabel = document.getElementById('parentLabel');
        
        parentSelect.innerHTML = '<option value="">Seçiniz...</option>';
        
        switch (type) {
            case 'grade':
                parentGroup.style.display = 'none';
                break;
            case 'subject':
                parentLabel.textContent = 'Sınıf';
                this.curriculumData.grades.forEach(grade => {
                    parentSelect.innerHTML += `<option value="${grade.grade_id}">${grade.grade_name}</option>`;
                });
                parentGroup.style.display = 'block';
                break;
            case 'unit':
                parentLabel.textContent = 'Ders';
                this.curriculumData.subjects.forEach(subject => {
                    parentSelect.innerHTML += `<option value="${subject.subject_id}">${subject.subject_name} (${subject.grade_name})</option>`;
                });
                parentGroup.style.display = 'block';
                break;
            case 'topic':
                parentLabel.textContent = 'Ünite';
                this.curriculumData.units.forEach(unit => {
                    parentSelect.innerHTML += `<option value="${unit.unit_id}">${unit.unit_name} (${unit.subject_name})</option>`;
                });
                parentGroup.style.display = 'block';
                break;
        }
    }

    async saveItem() {
        if (!adminBase.validateForm('addEditForm')) {
            return;
        }

        const form = document.getElementById('addEditForm');
        const formData = new FormData(form);
        const type = formData.get('itemType');
        const id = formData.get('itemId');
        const isEdit = id && id !== '';

        const data = {
            [`${type}_name`]: formData.get('name'),
            description: formData.get('description'),
            is_active: formData.get('isActive') === 'on'
        };

        // Add parent ID for hierarchical items
        if (type !== 'grade') {
            const parentIdField = {
                subject: 'grade_id',
                unit: 'subject_id',
                topic: 'unit_id'
            };
            data[parentIdField[type]] = parseInt(formData.get('parentId'));
        }

        try {
            adminBase.showLoading();
            
            let response;
            if (isEdit) {
                response = await adminBase.updateItem(type, id, data);
            } else {
                response = await adminBase.createItem(type, data);
            }

            if (response.success) {
                adminBase.showSuccess(`${type} başarıyla ${isEdit ? 'güncellendi' : 'oluşturuldu'}`);
                bootstrap.Modal.getInstance(document.getElementById('addEditModal')).hide();
                await this.loadCurriculumTree();
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
}

// Global functions for template usage
window.showAddModal = function(type) {
    window.adminCurriculum.showAddModal(type);
};

window.editItem = async function(type, id) {
    // Implementation for editing items
    console.log(`Edit ${type} with ID: ${id}`);
};

window.deleteItem = async function(type, id) {
    if (!confirm('Bu öğeyi silmek istediğinizden emin misiniz?')) {
        return;
    }

    try {
        adminBase.showLoading();
        
        const response = await adminBase.deleteItem(type, id);
        
        if (response.success) {
            adminBase.showSuccess(`${type} başarıyla silindi`);
            await window.adminCurriculum.loadCurriculumTree();
        } else {
            adminBase.showError(response.message);
        }
    } catch (error) {
        console.error('Delete error:', error);
        adminBase.showError('Silme işlemi sırasında hata oluştu: ' + error.message);
    } finally {
        adminBase.hideLoading();
    }
};

window.saveItem = function() {
    window.adminCurriculum.saveItem();
};

window.expandAll = function() {
    document.querySelectorAll('.tree-children').forEach(el => {
        el.style.display = 'block';
    });
    document.querySelectorAll('.tree-toggle i').forEach(icon => {
        icon.classList.remove('fa-chevron-right');
        icon.classList.add('fa-chevron-down');
    });
};

window.collapseAll = function() {
    document.querySelectorAll('.tree-children').forEach(el => {
        el.style.display = 'none';
    });
    document.querySelectorAll('.tree-toggle i').forEach(icon => {
        icon.classList.remove('fa-chevron-down');
        icon.classList.add('fa-chevron-right');
    });
};

// Initialize curriculum when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.adminCurriculum = new AdminCurriculum();
});
