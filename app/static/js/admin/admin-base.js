/**
 * Admin Panel Base JavaScript
 * Müfredat yönetimi odaklı temel işlevler
 */

class AdminPanel {
    constructor() {
        this.isSidebarOpen = true;
        this.currentPage = this.getCurrentPage();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupSidebar();
        this.setupActiveNavigation();
        this.setupResponsive();
    }

    setupEventListeners() {
        // Sidebar toggle
        const sidebarToggle = document.querySelector('.sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }

        // Sidebar close button (mobile)
        const sidebarClose = document.querySelector('.sidebar-close');
        if (sidebarClose) {
            sidebarClose.addEventListener('click', () => this.toggleSidebar());
        }

        // Help button
        const helpBtn = document.querySelector('.help-btn');
        if (helpBtn) {
            helpBtn.addEventListener('click', () => this.showHelp());
        }

        // Global click outside sidebar
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                const sidebar = document.querySelector('.admin-sidebar');
                const toggle = document.querySelector('.sidebar-toggle');
                
                if (sidebar && !sidebar.contains(e.target) && !toggle.contains(e.target)) {
                    this.closeSidebar();
                }
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'h':
                        e.preventDefault();
                        this.showHelp();
                        break;
                    case 'm':
                        e.preventDefault();
                        this.toggleSidebar();
                        break;
                }
            }
        });
    }

    setupSidebar() {
        // Set initial state
        if (window.innerWidth <= 768) {
            this.closeSidebar();
        }
    }

    setupActiveNavigation() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    }

    setupResponsive() {
        window.addEventListener('resize', () => {
            if (window.innerWidth <= 768) {
                this.closeSidebar();
            } else {
                this.openSidebar();
            }
        });
    }

    toggleSidebar() {
        if (this.isSidebarOpen) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }

    openSidebar() {
        const sidebar = document.querySelector('.admin-sidebar');
        if (sidebar) {
            sidebar.classList.add('show');
            this.isSidebarOpen = true;
        }
    }

    closeSidebar() {
        const sidebar = document.querySelector('.admin-sidebar');
        if (sidebar) {
            sidebar.classList.remove('show');
            this.isSidebarOpen = false;
        }
    }

    getCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('/admin/dashboard')) return 'dashboard';
        if (path.includes('/admin/grades')) return 'grades';
        if (path.includes('/admin/subjects')) return 'subjects';
        if (path.includes('/admin/units')) return 'units';
        if (path.includes('/admin/topics')) return 'topics';
        if (path.includes('/admin/import-export')) return 'import-export';
        return 'dashboard';
    }

    showHelp() {
        const helpModal = new bootstrap.Modal(document.getElementById('helpModal'));
        helpModal.show();
    }

    // Utility functions
    static showLoading() {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner-border text-light" role="status">
                    <span class="visually-hidden">Yükleniyor...</span>
                </div>
                <div class="loading-text text-light">İşlem yapılıyor...</div>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    static hideLoading() {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    static showAlert(message, type = 'success') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.flash-messages') || document.querySelector('.page-content');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
            
            // Auto remove after 5 seconds
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }
    }

    static showConfirmDialog(message, callback) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Onay</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">İptal</button>
                        <button type="button" class="btn btn-danger confirm-btn">Onayla</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
        
        const confirmBtn = modal.querySelector('.confirm-btn');
        confirmBtn.addEventListener('click', () => {
            callback();
            modalInstance.hide();
        });
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    static formatDate(dateString) {
        if (!dateString) return '-';
        
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return '-';
        
        return date.toLocaleDateString('tr-TR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    static formatNumber(number) {
        if (number === null || number === undefined) return '0';
        return number.toLocaleString('tr-TR');
    }

    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    static validateForm(form) {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }

    static clearForm(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.value = '';
            input.classList.remove('is-invalid');
        });
        
        const checkboxes = form.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
    }

    static downloadCSV(data, filename) {
        const csvContent = this.convertToCSV(data);
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }

    static convertToCSV(data) {
        if (!data || data.length === 0) return '';
        
        const headers = Object.keys(data[0]);
        const csvRows = [];
        
        // Add headers
        csvRows.push(headers.join(','));
        
        // Add data rows
        data.forEach(row => {
            const values = headers.map(header => {
                const value = row[header];
                // Escape commas and quotes
                if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                    return `"${value.replace(/"/g, '""')}"`;
                }
                return value || '';
            });
            csvRows.push(values.join(','));
        });
        
        return csvRows.join('\n');
    }

    static exportToJSON(data, filename) {
        const jsonContent = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonContent], { type: 'application/json' });
        const link = document.createElement('a');
        
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }

    // API request methods
    static async apiRequest(endpoint, options = {}) {
        try {
            const response = await fetch(`/api/admin${endpoint}`, {
                method: options.method || 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                body: options.body ? JSON.stringify(options.body) : undefined,
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request error:', error);
            throw error;
        }
    }

    static async getDashboardStats() {
        try {
            const response = await this.apiRequest('/admin/curriculum/overview');
            return {
                success: true,
                data: response
            };
        } catch (error) {
            return {
                success: false,
                message: error.message
            };
        }
    }

    static showError(message) {
        this.showAlert(message, 'danger');
    }

    static showSuccess(message) {
        this.showAlert(message, 'success');
    }

    static updateTable(tableId, data, columns) {
        const table = document.getElementById(tableId);
        if (!table) return;

        const tbody = table.querySelector('tbody');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (data.length === 0) {
            const row = tbody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = columns.length;
            cell.className = 'text-center text-muted py-4';
            cell.textContent = 'Veri bulunamadı';
            return;
        }

        data.forEach(item => {
            const row = tbody.insertRow();
            columns.forEach(column => {
                const cell = row.insertCell();
                if (column.render) {
                    cell.innerHTML = column.render(item);
                } else {
                    cell.textContent = item[column.field] || '-';
                }
            });
        });
    }
}

// Data Table Manager
class DataTableManager {
    constructor(tableId, options = {}) {
        this.tableId = tableId;
        this.table = document.getElementById(tableId);
        this.options = {
            pageSize: 10,
            currentPage: 1,
            searchable: true,
            sortable: true,
            ...options
        };
        
        this.data = [];
        this.filteredData = [];
        this.init();
    }

    init() {
        if (!this.table) return;
        
        this.setupTable();
        this.setupSearch();
        this.setupPagination();
    }

    setupTable() {
        // Add table classes
        this.table.classList.add('table', 'table-hover');
        
        // Make table responsive
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        this.table.parentNode.insertBefore(wrapper, this.table);
        wrapper.appendChild(this.table);
    }

    setupSearch() {
        if (!this.options.searchable) return;
        
        const searchContainer = document.querySelector(`#${this.tableId}-search`);
        if (!searchContainer) return;
        
        const searchInput = searchContainer.querySelector('input');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce((e) => {
                this.filterData(e.target.value);
            }, 300));
        }
    }

    setupPagination() {
        const paginationContainer = document.querySelector(`#${this.tableId}-pagination`);
        if (!paginationContainer) return;
        
        this.renderPagination();
    }

    setData(data) {
        this.data = data;
        this.filteredData = [...data];
        this.renderTable();
        this.renderPagination();
    }

    filterData(searchTerm = '') {
        if (!searchTerm.trim()) {
            this.filteredData = [...this.data];
        } else {
            this.filteredData = this.data.filter(item => {
                return Object.values(item).some(value => 
                    String(value).toLowerCase().includes(searchTerm.toLowerCase())
                );
            });
        }
        
        this.options.currentPage = 1;
        this.renderTable();
        this.renderPagination();
    }

    renderTable() {
        const tbody = this.table.querySelector('tbody');
        if (!tbody) return;
        
        const startIndex = (this.options.currentPage - 1) * this.options.pageSize;
        const endIndex = startIndex + this.options.pageSize;
        const pageData = this.filteredData.slice(startIndex, endIndex);
        
        tbody.innerHTML = '';
        
        if (pageData.length === 0) {
            const row = tbody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = this.table.querySelector('thead tr').cells.length;
            cell.className = 'text-center text-muted py-4';
            cell.textContent = 'Veri bulunamadı';
            return;
        }
        
        pageData.forEach(item => {
            const row = tbody.insertRow();
            Object.values(item).forEach(value => {
                const cell = row.insertCell();
                cell.textContent = value || '-';
            });
        });
    }

    renderPagination() {
        const container = document.querySelector(`#${this.tableId}-pagination`);
        if (!container) return;
        
        const totalPages = Math.ceil(this.filteredData.length / this.options.pageSize);
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }
        
        let paginationHTML = '<ul class="pagination justify-content-center">';
        
        // Previous button
        const prevDisabled = this.options.currentPage === 1 ? 'disabled' : '';
        paginationHTML += `
            <li class="page-item ${prevDisabled}">
                <a class="page-link" href="#" data-page="${this.options.currentPage - 1}">Önceki</a>
            </li>
        `;
        
        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= this.options.currentPage - 2 && i <= this.options.currentPage + 2)) {
                const active = i === this.options.currentPage ? 'active' : '';
                paginationHTML += `
                    <li class="page-item ${active}">
                        <a class="page-link" href="#" data-page="${i}">${i}</a>
                    </li>
                `;
            } else if (i === this.options.currentPage - 3 || i === this.options.currentPage + 3) {
                paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
        }
        
        // Next button
        const nextDisabled = this.options.currentPage === totalPages ? 'disabled' : '';
        paginationHTML += `
            <li class="page-item ${nextDisabled}">
                <a class="page-link" href="#" data-page="${this.options.currentPage + 1}">Sonraki</a>
            </li>
        `;
        
        paginationHTML += '</ul>';
        container.innerHTML = paginationHTML;
        
        // Add event listeners
        container.querySelectorAll('.page-link[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(e.target.dataset.page);
                if (page >= 1 && page <= totalPages) {
                    this.goToPage(page);
                }
            });
        });
    }

    goToPage(page) {
        this.options.currentPage = page;
        this.renderTable();
        this.renderPagination();
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminPanel = new AdminPanel();
    
    // Create global adminBase object with static methods
    window.adminBase = {
        showLoading: AdminPanel.showLoading,
        hideLoading: AdminPanel.hideLoading,
        showAlert: AdminPanel.showAlert,
        showError: AdminPanel.showError,
        showSuccess: AdminPanel.showSuccess,
        showConfirmDialog: AdminPanel.showConfirmDialog,
        formatDate: AdminPanel.formatDate,
        formatNumber: AdminPanel.formatNumber,
        debounce: AdminPanel.debounce,
        validateForm: AdminPanel.validateForm,
        clearForm: AdminPanel.clearForm,
        downloadCSV: AdminPanel.downloadCSV,
        convertToCSV: AdminPanel.convertToCSV,
        exportToJSON: AdminPanel.exportToJSON,
        apiRequest: AdminPanel.apiRequest,
        getDashboardStats: AdminPanel.getDashboardStats,
        updateTable: AdminPanel.updateTable
    };
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Global utility functions
window.AdminUtils = {
    showLoading: AdminPanel.showLoading,
    hideLoading: AdminPanel.hideLoading,
    showAlert: AdminPanel.showAlert,
    showConfirmDialog: AdminPanel.showConfirmDialog,
    formatDate: AdminPanel.formatDate,
    formatNumber: AdminPanel.formatNumber,
    debounce: AdminPanel.debounce,
    validateForm: AdminPanel.validateForm,
    clearForm: AdminPanel.clearForm,
    downloadCSV: AdminPanel.downloadCSV,
    convertToCSV: AdminPanel.convertToCSV,
    exportToJSON: AdminPanel.exportToJSON
};
