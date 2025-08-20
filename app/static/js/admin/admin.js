/**
 * MODERN ADMIN PANEL JAVASCRIPT
 * =============================================================================
 * Modern, clean and efficient admin panel functionality
 * =============================================================================
 */

class AdminPanel {
    constructor() {
        this.currentPage = this.getCurrentPage();
        this.init();
    }

    init() {
        this.setupSidebar();
        this.setupHeader();
        this.setupNavigation();
        this.setupEventListeners();
        this.loadPageData();
        console.log('Admin Panel initialized successfully! 🚀');
    }

    // =============================================================================
    // SIDEBAR MANAGEMENT
    // =============================================================================

    setupSidebar() {
        this.sidebar = document.getElementById('adminSidebar');
        this.sidebarToggle = document.getElementById('sidebarToggle');
        this.mobileMenuToggle = document.getElementById('mobileMenuToggle');

        if (this.sidebarToggle) {
            this.sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }

        if (this.mobileMenuToggle) {
            this.mobileMenuToggle.addEventListener('click', () => this.toggleMobileMenu());
        }

        // Auto-collapse on mobile
        if (window.innerWidth <= 1024) {
            this.sidebar.classList.add('collapsed');
        }
    }

    toggleSidebar() {
        this.sidebar.classList.toggle('collapsed');
        document.querySelector('.admin-main').classList.toggle('sidebar-collapsed');
        
        // Save preference
        localStorage.setItem('adminSidebarCollapsed', this.sidebar.classList.contains('collapsed'));
    }

    toggleMobileMenu() {
        this.sidebar.classList.toggle('show');
    }

    // =============================================================================
    // HEADER MANAGEMENT
    // =============================================================================

    setupHeader() {
        this.refreshBtn = document.getElementById('refreshData');
        this.fullscreenBtn = document.getElementById('fullscreenToggle');
        this.notificationBtn = document.getElementById('notificationBtn');

        if (this.refreshBtn) {
            this.refreshBtn.addEventListener('click', () => this.refreshPageData());
        }

        if (this.fullscreenBtn) {
            this.fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
        }

        if (this.notificationBtn) {
            this.notificationBtn.addEventListener('click', () => this.showNotifications());
        }
    }

    refreshPageData() {
        this.showLoading('Veriler yenileniyor...');
        
        // Trigger page-specific refresh
        if (window.currentPageManager && window.currentPageManager.refresh) {
            window.currentPageManager.refresh();
        } else {
            // Default refresh - reload page
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
            this.fullscreenBtn.innerHTML = '<i class="fas fa-compress"></i>';
        } else {
            document.exitFullscreen();
            this.fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>';
        }
    }

    showNotifications() {
        // TODO: Implement notifications panel
        this.showToast('Bildirimler yakında eklenecek! 🔔', 'info');
    }

    // =============================================================================
    // NAVIGATION MANAGEMENT
    // =============================================================================

    setupNavigation() {
        this.navLinks = document.querySelectorAll('.nav-link');
        this.highlightCurrentPage();
    }

    getCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('dashboard')) return 'dashboard';
        if (path.includes('grades')) return 'grades';
        if (path.includes('subjects')) return 'subjects';
        if (path.includes('units')) return 'units';
        if (path.includes('topics')) return 'topics';
        if (path.includes('users')) return 'users';
        if (path.includes('import')) return 'import-export';
        return 'dashboard';
    }

    highlightCurrentPage() {
        this.navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.dataset.page === this.currentPage) {
                link.classList.add('active');
            }
        });
    }

    // =============================================================================
    // PAGE DATA LOADING
    // =============================================================================

    loadPageData() {
        switch (this.currentPage) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'grades':
                this.loadGradesData();
                break;
            case 'subjects':
                this.loadSubjectsData();
                break;
            case 'units':
                this.loadUnitsData();
                break;
            case 'topics':
                this.loadTopicsData();
                break;
            case 'users':
                this.loadUsersData();
                break;
            case 'import-export':
                this.loadImportExportData();
                break;
        }
    }

    async loadDashboardData() {
        try {
            const response = await this.apiRequest('/admin/curriculum/overview');
            if (response.success && response.data) {
                this.updateDashboardStats(response.data);
            }
        } catch (error) {
            console.error('Dashboard data loading error:', error);
            this.showToast('Dashboard verileri yüklenemedi', 'error');
        }
    }

    updateDashboardStats(data) {
        const stats = {
            'total-grades': data.total_grades || 0,
            'total-subjects': data.total_subjects || 0,
            'total-units': data.total_units || 0,
            'total-topics': data.total_topics || 0
        };

        Object.entries(stats).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                this.animateNumber(element, value);
            }
        });
    }

    // =============================================================================
    // API UTILITIES
    // =============================================================================

    async apiRequest(endpoint, options = {}) {
        const url = `/api${endpoint}`;
        const config = {
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                ...options.headers
            },
            ...options
        };

        if (options.body) {
            config.body = JSON.stringify(options.body);
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error(`API Request Error (${endpoint}):`, error);
            throw error;
        }
    }

    // =============================================================================
    // UI UTILITIES
    // =============================================================================

    showLoading(message = 'Yükleniyor...') {
        const overlay = document.getElementById('loadingOverlay');
        const text = overlay.querySelector('.loading-text');
        
        if (text) text.textContent = message;
        overlay.classList.add('show');
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.classList.remove('show');
    }

    showToast(message, type = 'info', duration = 5000) {
        const toastContainer = document.getElementById('toastContainer');
        
        const toast = document.createElement('div');
        toast.className = `toast show bg-${type} text-white`;
        toast.innerHTML = `
            <div class="toast-body d-flex align-items-center">
                <i class="fas fa-${this.getToastIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close btn-close-white ms-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, duration);

        // Bootstrap toast functionality
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    animateNumber(element, targetNumber) {
        const startNumber = parseInt(element.textContent) || 0;
        const duration = 1000;
        const steps = 60;
        const increment = (targetNumber - startNumber) / steps;
        let currentNumber = startNumber;
        let stepCount = 0;

        const timer = setInterval(() => {
            stepCount++;
            currentNumber += increment;
            
            if (stepCount >= steps) {
                currentNumber = targetNumber;
                clearInterval(timer);
            }
            
            element.textContent = Math.round(currentNumber);
        }, duration / steps);
    }

    confirmAction(message, callback) {
        if (confirm(message)) {
            callback();
        }
    }

    // =============================================================================
    // DATA LOADING METHODS (Placeholder implementations)
    // =============================================================================

    // Placeholder methods for page-specific data loading
    loadGradesData() {
        this.showLoading();
        this.apiRequest('/api/admin/grades', 'GET')
            .then(response => {
                if (response.success) {
                    this.renderGradesTable(response.data);
                } else {
                    this.showToast('Sınıf verileri yüklenirken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Grades loading error:', error);
                this.showToast('Sınıf verileri yüklenirken hata oluştu', 'error');
            })
            .finally(() => {
                this.hideLoading();
            });
    }

    loadSubjectsData() {
        this.showLoading();
        this.apiRequest('/api/admin/subjects', 'GET')
            .then(response => {
                if (response.success) {
                    this.renderSubjectsTable(response.data);
                } else {
                    this.showToast('Ders verileri yüklenirken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Subjects loading error:', error);
                this.showToast('Ders verileri yüklenirken hata oluştu', 'error');
            })
            .finally(() => {
                this.hideLoading();
            });
    }

    loadUnitsData() {
        this.showLoading();
        this.apiRequest('/api/admin/units', 'GET')
            .then(response => {
                if (response.success) {
                    this.renderUnitsTable(response.data);
                } else {
                    this.showToast('Ünite verileri yüklenirken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Units loading error:', error);
                this.showToast('Ünite verileri yüklenirken hata oluştu', 'error');
            })
            .finally(() => {
                this.hideLoading();
            });
    }

    loadTopicsData() {
        this.showLoading();
        this.apiRequest('/api/admin/topics', 'GET')
            .then(response => {
                if (response.success) {
                    this.renderTopicsTable(response.data);
                } else {
                    this.showToast('Konu verileri yüklenirken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Topics loading error:', error);
                this.showToast('Konu verileri yüklenirken hata oluştu', 'error');
            })
            .finally(() => {
                this.hideLoading();
            });
    }

    loadUsersData() {
        this.showLoading();
        this.apiRequest('/api/admin/users', 'GET')
            .then(response => {
                if (response.success) {
                    this.renderUsersTable(response.data);
                } else {
                    this.showToast('Kullanıcı verileri yüklenirken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Users loading error:', error);
                this.showToast('Kullanıcı verileri yüklenirken hata oluştu', 'error');
            })
            .finally(() => {
                this.hideLoading();
            });
    }

    // Table rendering methods
    renderGradesTable(grades) {
        const tbody = document.querySelector('#gradesTable tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        grades.forEach(grade => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${grade.grade_name}</td>
                <td>${grade.level || '-'}</td>
                <td>${grade.description || '-'}</td>
                <td>
                    <span class="badge ${grade.is_active ? 'bg-success' : 'bg-secondary'}">
                        ${grade.is_active ? 'Aktif' : 'Pasif'}
                    </span>
                </td>
                <td>
                    <div class="btn-group" role="group">
                        <button type="button" class="btn btn-sm btn-outline-primary" 
                                onclick="adminPanel.editGrade(${grade.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-danger" 
                                onclick="adminPanel.deleteGrade(${grade.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderSubjectsTable(subjects) {
        const tbody = document.querySelector('#subjectsTable tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        subjects.forEach(subject => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${subject.subject_name}</td>
                <td>${subject.grade_name || '-'}</td>
                <td>${subject.description || '-'}</td>
                <td>
                    <span class="badge ${subject.is_active ? 'bg-success' : 'bg-secondary'}">
                        ${subject.is_active ? 'Aktif' : 'Pasif'}
                    </span>
                </td>
                <td>
                    <div class="btn-group" role="group">
                        <button type="button" class="btn btn-sm btn-outline-primary" 
                                onclick="adminPanel.editSubject(${subject.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-danger" 
                                onclick="adminPanel.deleteSubject(${subject.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderUnitsTable(units) {
        const tbody = document.querySelector('#unitsTable tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        units.forEach(unit => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${unit.unit_number}</td>
                <td>${unit.unit_name}</td>
                <td>${unit.subject_name || '-'}</td>
                <td>${unit.description || '-'}</td>
                <td>
                    <span class="badge ${unit.is_active ? 'bg-success' : 'bg-secondary'}">
                        ${unit.is_active ? 'Aktif' : 'Pasif'}
                    </span>
                </td>
                <td>
                    <div class="btn-group" role="group">
                        <button type="button" class="btn btn-sm btn-outline-primary" 
                                onclick="adminPanel.editUnit(${unit.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-danger" 
                                onclick="adminPanel.deleteUnit(${unit.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderTopicsTable(topics) {
        const tbody = document.querySelector('#topicsTable tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        topics.forEach(topic => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${topic.topic_number}</td>
                <td>${topic.topic_name}</td>
                <td>${topic.unit_name || '-'}</td>
                <td>${topic.description || '-'}</td>
                <td>
                    <span class="button" class="btn btn-sm btn-outline-primary" 
                                onclick="adminPanel.editTopic(${topic.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-danger" 
                                onclick="adminPanel.deleteTopic(${topic.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderUsersTable(users) {
        const tbody = document.querySelector('#usersTable tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td>${user.first_name} ${user.last_name}</td>
                <td>
                    <span class="badge ${user.is_admin ? 'bg-danger' : 'bg-info'}">
                        ${user.is_admin ? 'Admin' : 'Kullanıcı'}
                    </span>
                </td>
                <td>
                    <span class="badge ${user.is_active ? 'bg-success' : 'bg-secondary'}">
                        ${user.is_active ? 'Aktif' : 'Pasif'}
                    </span>
                </td>
                <td>
                    <div class="btn-group" role="group">
                        <button type="button" class="btn btn-sm btn-outline-primary" 
                                onclick="adminPanel.editUser(${user.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-warning" 
                                onclick="adminPanel.toggleUserAdmin(${user.id})">
                            <i class="fas fa-user-shield"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-danger" 
                                onclick="adminPanel.deleteUser(${user.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // CRUD Operations for Grades
    createGrade(formData) {
        this.apiRequest('/api/admin/grades', 'POST', formData)
            .then(response => {
                if (response.success) {
                    this.showToast('Sınıf başarıyla oluşturuldu', 'success');
                    this.loadGradesData();
                    this.closeModal('gradeModal');
                } else {
                    this.showToast(response.message || 'Sınıf oluşturulurken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Grade creation error:', error);
                this.showToast('Sınıf oluşturulurken hata oluştu', 'error');
            });
    }

    editGrade(gradeId) {
        this.apiRequest(`/api/admin/grades/${gradeId}`, 'GET')
            .then(response => {
                if (response.success) {
                    this.populateGradeForm(response.data);
                    this.openModal('gradeModal');
                } else {
                    this.showToast('Sınıf bilgileri yüklenirken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Grade loading error:', error);
                this.showToast('Sınıf bilgileri yüklenirken hata oluştu', 'error');
            });
    }

    updateGrade(gradeId, formData) {
        this.apiRequest(`/api/admin/grades/${gradeId}`, 'PUT', formData)
            .then(response => {
                if (response.success) {
                    this.showToast('Sınıf başarıyla güncellendi', 'success');
                    this.loadGradesData();
                    this.closeModal('gradeModal');
                } else {
                    this.showToast(response.message || 'Sınıf güncellenirken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Grade update error:', error);
                this.showToast('Sınıf güncellenirken hata oluştu', 'error');
            });
    }

    deleteGrade(gradeId) {
        this.confirmAction('Bu sınıfı silmek istediğinizden emin misiniz?', () => {
            this.apiRequest(`/api/admin/grades/${gradeId}`, 'DELETE')
                .then(response => {
                    if (response.success) {
                        this.showToast('Sınıf başarıyla silindi', 'success');
                        this.loadGradesData();
                    } else {
                        this.showToast(response.message || 'Sınıf silinirken hata oluştu', 'error');
                    }
                })
                .catch(error => {
                    console.error('Grade deletion error:', error);
                    this.showToast('Sınıf silinirken hata oluştu', 'error');
                });
        });
    }

    // CRUD Operations for Subjects
    createSubject(formData) {
        this.apiRequest('/api/admin/subjects', 'POST', formData)
            .then(response => {
                if (response.success) {
                    this.showToast('Ders başarıyla oluşturuldu', 'success');
                    this.loadSubjectsData();
                    this.closeModal('subjectModal');
                } else {
                    this.showToast(response.message || 'Ders oluşturulurken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Subject creation error:', error);
                this.showToast('Ders oluşturulurken hata oluştu', 'error');
            });
    }

    editSubject(subjectId) {
        this.apiRequest(`/api/admin/subjects/${subjectId}`, 'GET')
            .then(response => {
                if (response.success) {
                    this.populateSubjectForm(response.data);
                    this.openModal('subjectModal');
                } else {
                    this.showToast('Ders bilgileri yüklenirken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Subject loading error:', error);
                this.showToast('Ders bilgileri yüklenirken hata oluştu', 'error');
            });
    }

    updateSubject(subjectId, formData) {
        this.apiRequest(`/api/admin/subjects/${subjectId}`, 'PUT', formData)
            .then(response => {
                if (response.success) {
                    this.showToast('Ders başarıyla güncellendi', 'success');
                    this.loadSubjectsData();
                    this.closeModal('subjectModal');
                } else {
                    this.showToast(response.message || 'Ders güncellenirken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Subject update error:', error);
                this.showToast('Ders güncellenirken hata oluştu', 'error');
            });
    }

    deleteSubject(subjectId) {
        this.confirmAction('Bu dersi silmek istediğinizden emin misiniz?', () => {
            this.apiRequest(`/api/admin/subjects/${subjectId}`, 'DELETE')
                .then(response => {
                    if (response.success) {
                        this.showToast('Ders başarıyla silindi', 'success');
                        this.loadSubjectsData();
                    } else {
                        this.showToast(response.message || 'Ders silinirken hata oluştu', 'error');
                    }
                })
                .catch(error => {
                    console.error('Subject deletion error:', error);
                    this.showToast('Ders silinirken hata oluştu', 'error');
                });
        });
    }

    // CRUD Operations for Units
    createUnit(formData) {
        this.apiRequest('/api/admin/units', 'POST', formData)
            .then(response => {
                if (response.success) {
                    this.showToast('Ünite başarıyla oluşturuldu', 'success');
                    this.loadUnitsData();
                    this.closeModal('unitModal');
                } else {
                    this.showToast(response.message || 'Ünite oluşturulurken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Unit creation error:', error);
                this.showToast('Ünite oluşturulurken hata oluştu', 'error');
            });
    }

    editUnit(unitId) {
        this.apiRequest(`/api/admin/units/${unitId}`, 'GET')
            .then(response => {
                if (response.success) {
                    this.populateUnitForm(response.data);
                    this.openModal('unitModal');
                } else {
                    this.showToast('Ünite bilgileri yüklenirken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Unit loading error:', error);
                this.showToast('Ünite bilgileri yüklenirken hata oluştu', 'error');
            });
    }

    updateUnit(unitId, formData) {
        this.apiRequest(`/api/admin/units/${unitId}`, 'PUT', formData)
            .then(response => {
                if (response.success) {
                    this.showToast('Ünite başarıyla güncellendi', 'success');
                    this.loadUnitsData();
                    this.closeModal('unitModal');
                } else {
                    this.showToast(response.message || 'Ünite güncellenirken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Unit update error:', error);
                this.showToast('Ünite güncellenirken hata oluştu', 'error');
            });
    }

    deleteUnit(unitId) {
        this.confirmAction('Bu üniteyi silmek istediğinizden emin misiniz?', () => {
            this.apiRequest(`/api/admin/units/${unitId}`, 'DELETE')
                .then(response => {
                    if (response.success) {
                        this.showToast('Ünite başarıyla silindi', 'success');
                        this.loadUnitsData();
                    } else {
                        this.showToast(response.message || 'Ünite silinirken hata oluştu', 'error');
                    }
                })
                .catch(error => {
                    console.error('Unit deletion error:', error);
                    this.showToast('Ünite silinirken hata oluştu', 'error');
                });
        });
    }

    // CRUD Operations for Topics
    createTopic(formData) {
        this.apiRequest('/api/admin/topics', 'POST', formData)
            .then(response => {
                if (response.success) {
                    this.showToast('Konu başarıyla oluşturuldu', 'success');
                    this.loadTopicsData();
                    this.closeModal('topicModal');
                } else {
                    this.showToast(response.message || 'Konu oluşturulurken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Topic creation error:', error);
                this.showToast('Konu oluşturulurken hata oluştu', 'error');
            });
    }

    editTopic(topicId) {
        this.apiRequest(`/api/admin/topics/${topicId}`, 'GET')
            .then(response => {
                if (response.success) {
                    this.populateTopicForm(response.data);
                    this.openModal('topicModal');
                } else {
                    this.showToast('Konu bilgileri yüklenirken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Topic loading error:', error);
                this.showToast('Konu bilgileri yüklenirken hata oluştu', 'error');
            });
    }

    updateTopic(topicId, formData) {
        this.apiRequest(`/api/admin/topics/${topicId}`, 'PUT', formData)
            .then(response => {
                if (response.success) {
                    this.showToast('Konu başarıyla güncellendi', 'success');
                    this.loadTopicsData();
                    this.closeModal('topicModal');
                } else {
                    this.showToast(response.message || 'Konu güncellenirken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Topic update error:', error);
                this.showToast('Konu güncellenirken hata oluştu', 'error');
            });
    }

    deleteTopic(topicId) {
        this.confirmAction('Bu konuyu silmek istediğinizden emin misiniz?', () => {
            this.apiRequest(`/api/admin/topics/${topicId}`, 'DELETE')
                .then(response => {
                    if (response.success) {
                        this.showToast('Konu başarıyla silindi', 'success');
                        this.loadTopicsData();
                    } else {
                        this.showToast(response.message || 'Konu silinirken hata oluştu', 'error');
                    }
                })
                .catch(error => {
                    console.error('Topic deletion error:', error);
                    this.showToast('Konu silinirken hata oluştu', 'error');
                });
        });
    }

    // User Management Operations
    createUser(formData) {
        this.apiRequest('/api/admin/users', 'POST', formData)
            .then(response => {
                if (response.success) {
                    this.showToast('Kullanıcı başarıyla oluşturuldu', 'success');
                    this.loadUsersData();
                    this.closeModal('userModal');
                } else {
                    this.showToast(response.message || 'Kullanıcı oluşturulurken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('User creation error:', error);
                this.showToast('Kullanıcı oluşturulurken hata oluştu', 'error');
            });
    }

    editUser(userId) {
        this.apiRequest(`/api/admin/users/${userId}`, 'GET')
            .then(response => {
                if (response.success) {
                    this.populateUserForm(response.data);
                    this.openModal('userModal');
                } else {
                    this.showToast('Kullanıcı bilgileri yüklenirken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('User loading error:', error);
                this.showToast('Kullanıcı bilgileri yüklenirken hata oluştu', 'error');
            });
    }

    updateUser(userId, formData) {
        this.apiRequest(`/api/admin/users/${userId}`, 'PUT', formData)
            .then(response => {
                if (response.success) {
                    this.showToast('Kullanıcı başarıyla güncellendi', 'success');
                    this.loadUsersData();
                    this.closeModal('userModal');
                } else {
                    this.showToast(response.message || 'Kullanıcı güncellenirken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('User update error:', error);
                this.showToast('Kullanıcı güncellenirken hata oluştu', 'error');
            });
    }

    deleteUser(userId) {
        this.confirmAction('Bu kullanıcıyı silmek istediğinizden emin misiniz?', () => {
            this.apiRequest(`/api/admin/users/${userId}`, 'DELETE')
                .then(response => {
                    if (response.success) {
                        this.showToast('Kullanıcı başarıyla silindi', 'success');
                        this.loadUsersData();
                    } else {
                        this.showToast(response.message || 'Kullanıcı silinirken hata oluştu', 'error');
                    }
                })
                .catch(error => {
                    console.error('User deletion error:', error);
                    this.showToast('Kullanıcı silinirken hata oluştu', 'error');
                });
        });
    }

    toggleUserAdmin(userId) {
        this.confirmAction('Bu kullanıcının admin yetkisini değiştirmek istediğinizden emin misiniz?', () => {
            this.apiRequest(`/api/admin/users/${userId}/toggle-admin`, 'PUT')
                .then(response => {
                    if (response.success) {
                        this.showToast('Kullanıcı yetkisi başarıyla güncellendi', 'success');
                        this.loadUsersData();
                    } else {
                        this.showToast(response.message || 'Kullanıcı yetkisi güncellenirken hata oluştu', 'error');
                    }
                })
                .catch(error => {
                    console.error('User admin toggle error:', error);
                    this.showToast('Kullanıcı yetkisi güncellenirken hata oluştu', 'error');
                });
        });
    }

    // Form population methods
    populateGradeForm(grade) {
        const form = document.getElementById('gradeForm');
        if (form) {
            form.querySelector('[name="grade_name"]').value = grade.grade_name || '';
            form.querySelector('[name="level"]').value = grade.level || '';
            form.querySelector('[name="description"]').value = grade.description || '';
            form.querySelector('[name="is_active"]').checked = grade.is_active;
            form.dataset.editId = grade.id;
        }
    }

    populateSubjectForm(subject) {
        const form = document.getElementById('subjectForm');
        if (form) {
            form.querySelector('[name="subject_name"]').value = subject.subject_name || '';
            form.querySelector('[name="grade_id"]').value = subject.grade_id || '';
            form.querySelector('[name="description"]').value = subject.description || '';
            form.querySelector('[name="is_active"]').checked = subject.is_active;
            form.dataset.editId = subject.id;
        }
    }

    populateUnitForm(unit) {
        const form = document.getElementById('unitForm');
        if (form) {
            form.querySelector('[name="unit_number"]').value = unit.unit_number || '';
            form.querySelector('[name="unit_name"]').value = unit.unit_name || '';
            form.querySelector('[name="subject_id"]').value = unit.subject_id || '';
            form.querySelector('[name="description"]').value = unit.description || '';
            form.querySelector('[name="is_active"]').checked = unit.is_active;
            form.dataset.editId = unit.id;
        }
    }

    populateTopicForm(topic) {
        const form = document.getElementById('topicForm');
        if (form) {
            form.querySelector('[name="topic_number"]').value = topic.topic_number || '';
            form.querySelector('[name="topic_name"]').value = topic.topic_name || '';
            form.querySelector('[name="unit_id"]').value = topic.unit_id || '';
            form.querySelector('[name="description"]').value = topic.description || '';
            form.querySelector('[name="is_active"]').checked = topic.is_active;
            form.dataset.editId = topic.id;
        }
    }

    populateUserForm(user) {
        const form = document.getElementById('userForm');
        if (form) {
            form.querySelector('[name="username"]').value = user.username || '';
            form.querySelector('[name="email"]').value = user.email || '';
            form.querySelector('[name="first_name"]').value = user.first_name || '';
            form.querySelector('[name="last_name"]').value = user.last_name || '';
            form.querySelector('[name="is_admin"]').checked = user.is_admin;
            form.querySelector('[name="is_active"]').checked = user.is_active;
            form.dataset.editId = user.id;
        }
    }

    // Modal management
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            if (bootstrapModal) {
                bootstrapModal.hide();
            }
        }
    }

    // Export functionality
    exportToCSV(tableId, filename) {
        const table = document.getElementById(tableId);
        if (!table) return;

        const rows = Array.from(table.querySelectorAll('tr'));
        const csvContent = rows.map(row => {
            const cells = Array.from(row.querySelectorAll('td, th'));
            return cells.map(cell => `"${cell.textContent.trim()}"`).join(',');
        }).join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // Import functionality
    importFromFile(file, type) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', type);

        this.apiRequest('/api/admin/import/curriculum', 'POST', formData)
            .then(response => {
                if (response.success) {
                    this.showToast('Veri başarıyla içe aktarıldı', 'success');
                    // Reload the appropriate data based on type
                    switch (type) {
                        case 'grades':
                            this.loadGradesData();
                            break;
                        case 'subjects':
                            this.loadSubjectsData();
                            break;
                        case 'units':
                            this.loadUnitsData();
                            break;
                        case 'topics':
                            this.loadTopicsData();
                            break;
                    }
                } else {
                    this.showToast(response.message || 'Veri içe aktarılırken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Import error:', error);
                this.showToast('Veri içe aktarılırken hata oluştu', 'error');
            });
    }

    // System utilities
    refreshSession() {
        this.apiRequest('/api/admin/refresh-session', 'POST')
            .then(response => {
                if (response.success) {
                    this.showToast('Oturum başarıyla yenilendi', 'success');
                    // Reload current page data
                    this.loadCurrentPageData();
                } else {
                    this.showToast(response.message || 'Oturum yenilenirken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('Session refresh error:', error);
                this.showToast('Oturum yenilenirken hata oluştu', 'error');
            });
    }

    getSystemStatus() {
        this.apiRequest('/api/admin/system/status', 'GET')
            .then(response => {
                if (response.success) {
                    this.updateSystemStatus(response.data);
                } else {
                    this.showToast('Sistem durumu alınırken hata oluştu', 'error');
                }
            })
            .catch(error => {
                console.error('System status error:', error);
                this.showToast('Sistem durumu alınırken hata oluştu', 'error');
            });
    }

    updateSystemStatus(status) {
        // Update system status display elements
        const elements = {
            'database_status': status.database_status,
            'server_uptime': status.server_uptime,
            'active_users': status.active_users,
            'total_requests': status.total_requests
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    // Utility method to load data based on current page
    loadCurrentPageData() {
        const currentPage = this.getCurrentPage();
        switch (currentPage) {
            case 'grades':
                this.loadGradesData();
                break;
            case 'subjects':
                this.loadSubjectsData();
                break;
            case 'units':
                this.loadUnitsData();
                break;
            case 'topics':
                this.loadTopicsData();
                break;
            case 'users':
                this.loadUsersData();
                break;
            case 'dashboard':
                // Dashboard data is handled by DashboardManager
                break;
        }
    }

    getCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('/grades')) return 'grades';
        if (path.includes('/subjects')) return 'subjects';
        if (path.includes('/units')) return 'units';
        if (path.includes('/topics')) return 'topics';
        if (path.includes('/users')) return 'users';
        if (path.includes('/dashboard') || path.endsWith('/admin')) return 'dashboard';
        return 'dashboard';
    }

    // =============================================================================
    // EVENT LISTENERS
    // =============================================================================

    setupEventListeners() {
        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.sidebar.contains(e.target) && !this.mobileMenuToggle.contains(e.target)) {
                this.sidebar.classList.remove('show');
            }
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth <= 1024) {
                this.sidebar.classList.add('collapsed');
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K to refresh
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.refreshPageData();
            }
            
            // Ctrl/Cmd + B to toggle sidebar
            if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
                e.preventDefault();
                this.toggleSidebar();
            }
        });
    }
}

// =============================================================================
// GLOBAL UTILITY FUNCTIONS
// =============================================================================

// Global loading functions
window.showLoading = function(message) {
    if (window.adminPanel) {
        window.adminPanel.showLoading(message);
    }
};

window.hideLoading = function() {
    if (window.adminPanel) {
        window.adminPanel.hideLoading();
    }
};

// Global toast functions
window.showToast = function(message, type, duration) {
    if (window.adminPanel) {
        window.adminPanel.showToast(message, type, duration);
    }
};

// Global API request function
window.apiRequest = function(endpoint, options) {
    if (window.adminPanel) {
        return window.adminPanel.apiRequest(endpoint, options);
    }
};

// Global confirmation function
window.confirmAction = function(message, callback) {
    if (window.adminPanel) {
        window.adminPanel.confirmAction(message, callback);
    }
};

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize admin panel
    window.adminPanel = new AdminPanel();
    
    // Set current page manager if exists
    if (window.currentPageManager) {
        console.log('Page manager found:', window.currentPageManager.constructor.name);
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdminPanel;
}
