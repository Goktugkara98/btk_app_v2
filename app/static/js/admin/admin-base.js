// =============================================================================
// ADMIN BASE JAVASCRIPT
// =============================================================================
// Admin paneli için temel JavaScript fonksiyonları
// =============================================================================

class AdminBase {
    constructor() {
        this.apiBaseUrl = '/api/admin';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupAjaxDefaults();
    }

    setupEventListeners() {
        // Mobile sidebar toggle
        document.addEventListener('click', (e) => {
            if (e.target.matches('.mobile-sidebar-toggle')) {
                this.toggleSidebar();
            }
        });

        // Close modals on escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    setupAjaxDefaults() {
        // Set default headers for AJAX requests
        const token = this.getAuthToken();
        if (token && typeof $ !== 'undefined') {
            $.ajaxSetup({
                beforeSend: function(xhr) {
                    xhr.setRequestHeader('Authorization', `Bearer ${token}`);
                }
            });
        }
    }

    // =============================================================================
    // UTILITY FUNCTIONS
    // =============================================================================

    showLoading() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    showAlert(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const alertContainer = document.querySelector('.admin-alerts') || 
                              document.querySelector('.admin-page-content');
        
        if (alertContainer) {
            alertContainer.insertAdjacentHTML('afterbegin', alertHtml);
        }
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showError(message) {
        this.showAlert(message, 'danger');
    }

    showWarning(message) {
        this.showAlert(message, 'warning');
    }

    toggleSidebar() {
        const sidebar = document.querySelector('.admin-sidebar');
        if (sidebar) {
            sidebar.classList.toggle('show');
        }
    }

    closeAllModals() {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        });
    }

    getAuthToken() {
        // In a real application, this would get the JWT token from localStorage or cookies
        return localStorage.getItem('admin_token') || 'dummy-token';
    }

    // =============================================================================
    // API FUNCTIONS
    // =============================================================================

    async apiRequest(endpoint, method = 'GET', data = null) {
        const url = `${this.apiBaseUrl}${endpoint}`;
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.getAuthToken()}`
            }
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.message || 'API request failed');
            }

            return result;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    async getDashboardStats() {
        return await this.apiRequest('/dashboard');
    }

    async getGrades() {
        return await this.apiRequest('/grades');
    }

    async getSubjects(gradeId = null) {
        const endpoint = gradeId ? `/subjects?grade_id=${gradeId}` : '/subjects';
        return await this.apiRequest(endpoint);
    }

    async getUnits(subjectId = null) {
        const endpoint = subjectId ? `/units?subject_id=${subjectId}` : '/units';
        return await this.apiRequest(endpoint);
    }

    async getTopics(unitId = null) {
        const endpoint = unitId ? `/topics?unit_id=${unitId}` : '/topics';
        return await this.apiRequest(endpoint);
    }

    async createItem(type, data) {
        return await this.apiRequest(`/${type}s`, 'POST', data);
    }

    async updateItem(type, id, data) {
        return await this.apiRequest(`/${type}s/${id}`, 'PUT', data);
    }

    async deleteItem(type, id) {
        return await this.apiRequest(`/${type}s/${id}`, 'DELETE');
    }

    // =============================================================================
    // FORM HELPERS
    // =============================================================================

    resetForm(formId) {
        const form = document.getElementById(formId);
        if (form) {
            form.reset();
            // Clear validation states
            form.querySelectorAll('.is-invalid').forEach(el => {
                el.classList.remove('is-invalid');
            });
            form.querySelectorAll('.invalid-feedback').forEach(el => {
                el.remove();
            });
        }
    }

    validateForm(formId) {
        const form = document.getElementById(formId);
        if (!form) return false;

        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'Bu alan zorunludur');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });

        return isValid;
    }

    showFieldError(field, message) {
        field.classList.add('is-invalid');
        
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    // =============================================================================
    // TABLE HELPERS
    // =============================================================================

    updateTable(tableId, data, columns) {
        const table = document.getElementById(tableId);
        if (!table) return;

        const tbody = table.querySelector('tbody');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (!data || data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="${columns.length}" class="text-center text-muted py-4">
                        Veri bulunamadı
                    </td>
                </tr>
            `;
            return;
        }

        data.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = columns.map(col => {
                if (typeof col.render === 'function') {
                    return `<td>${col.render(item)}</td>`;
                } else {
                    return `<td>${item[col.field] || '-'}</td>`;
                }
            }).join('');
            tbody.appendChild(row);
        });
    }

    // =============================================================================
    // DATE/TIME HELPERS
    // =============================================================================

    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('tr-TR');
    }

    formatDateTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('tr-TR');
    }

    // =============================================================================
    // CONFIRMATION DIALOGS
    // =============================================================================

    confirm(message, callback) {
        if (window.confirm(message)) {
            callback();
        }
    }

    // =============================================================================
    // LOCAL STORAGE HELPERS
    // =============================================================================

    setLocalStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('LocalStorage set error:', error);
        }
    }

    getLocalStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('LocalStorage get error:', error);
            return defaultValue;
        }
    }

    removeLocalStorage(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('LocalStorage remove error:', error);
        }
    }
}

// Initialize AdminBase when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Wait for jQuery to be available
    function initAdminBase() {
        if (typeof $ !== 'undefined' && typeof window.adminBase === 'undefined') {
            window.adminBase = new AdminBase();
            console.log('AdminBase initialized successfully');
        } else if (typeof $ === 'undefined') {
            // Retry after 100ms if jQuery not loaded yet
            setTimeout(initAdminBase, 100);
        }
    }
    initAdminBase();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdminBase;
}
