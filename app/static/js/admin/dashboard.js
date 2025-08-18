// =============================================================================
// ADMIN DASHBOARD JAVASCRIPT
// =============================================================================
// Dashboard sayfası için JavaScript fonksiyonları
// =============================================================================

class AdminDashboard {
    constructor() {
        this.init();
    }

    async waitForAdminBase() {
        return new Promise((resolve) => {
            const checkAdminBase = () => {
                if (window.adminBase) {
                    console.log('AdminBase found');
                    resolve();
                } else {
                    console.log('Waiting for AdminBase...');
                    setTimeout(checkAdminBase, 100);
                }
            };
            checkAdminBase();
        });
    }

    async init() {
        console.log('Dashboard initializing...');
        
        // Wait for adminBase to be ready
        await this.waitForAdminBase();
        
        // Add debug logging
        console.log('AdminBase ready, loading dashboard data...');
        await this.loadDashboardData();
        this.setupEventListeners();
        
        console.log('Dashboard initialized successfully');
    }

    setupEventListeners() {
        // Refresh button
        document.addEventListener('click', (e) => {
            if (e.target.matches('.refresh-dashboard')) {
                this.loadDashboardData();
            }
        });
    }

    async loadDashboardData() {
        try {
            console.log('Loading dashboard data...');
            if (window.adminBase) {
                window.adminBase.showLoading();
            }
            
            const response = await window.adminBase.getDashboardStats();
            console.log('Dashboard API response:', response);
            
            if (response.success) {
                console.log('Updating statistics with data:', response.data);
                this.updateStatistics(response.data);
                this.updateGradeBreakdown(response.data.grade_breakdown || []);
            } else {
                console.error('Dashboard API returned error:', response);
                window.adminBase.showError('Dashboard verileri yüklenirken hata oluştu');
            }
        } catch (error) {
            console.error('Dashboard loading error:', error);
            if (window.adminBase) {
                window.adminBase.showError('Dashboard verileri yüklenirken hata oluştu: ' + error.message);
            }
        } finally {
            if (window.adminBase) {
                window.adminBase.hideLoading();
            }
        }
    }

    updateStatistics(data) {
        // Update stat cards - using correct IDs from template
        const statElements = {
            total_grades: document.getElementById('total-grades'),
            total_subjects: document.getElementById('total-subjects'),
            total_units: document.getElementById('total-units'),
            total_topics: document.getElementById('total-topics')
        };

        Object.keys(statElements).forEach(key => {
            const element = statElements[key];
            if (element && data[key] !== undefined) {
                this.animateNumber(element, data[key]);
            }
        });
    }

    updateGradeBreakdown(gradeBreakdown) {
        const tableColumns = [
            { field: 'grade_name', render: (item) => `<strong>${item.grade_name}</strong>` },
            { field: 'subject_count', render: (item) => `<span class="badge bg-success">${item.subject_count}</span>` },
            { field: 'unit_count', render: (item) => `<span class="badge bg-warning">${item.unit_count}</span>` },
            { field: 'topic_count', render: (item) => `<span class="badge bg-info">${item.topic_count}</span>` },
            { 
                field: 'actions', 
                render: (item) => `
                    <div class="btn-group btn-group-sm">
                        <a href="/admin/subjects?grade_id=${item.grade_id}" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-eye"></i> Görüntüle
                        </a>
                        <button class="btn btn-outline-secondary btn-sm" onclick="exportGrade(${item.grade_id})">
                            <i class="fas fa-download"></i> Export
                        </button>
                    </div>
                `
            }
        ];

        if (window.adminBase) {
            window.adminBase.updateTable('gradeBreakdownTable', gradeBreakdown, tableColumns);
        }
    }

    animateNumber(element, targetNumber) {
        const startNumber = parseInt(element.textContent) || 0;
        const duration = 1000; // 1 second
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
}

// Global functions for template usage
window.exportGrade = async function(gradeId) {
    try {
        if (window.adminBase) {
            window.adminBase.showLoading();
        }
        
        const response = await window.adminBase.apiRequest(`/curriculum/export/${gradeId}`);
        
        if (response.success) {
            // Create and download JSON file
            const dataStr = JSON.stringify(response.data, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = `grade_${gradeId}_curriculum.json`;
            link.click();
            
            if (window.adminBase) {
                window.adminBase.showSuccess('Müfredat başarıyla export edildi');
            }
        } else {
            if (window.adminBase) {
                window.adminBase.showError('Export işlemi başarısız: ' + response.message);
            }
        }
    } catch (error) {
        console.error('Export error:', error);
        if (window.adminBase) {
            window.adminBase.showError('Export işlemi sırasında hata oluştu: ' + error.message);
        }
    } finally {
        if (window.adminBase) {
            window.adminBase.hideLoading();
        }
    }
};

// Initialize dashboard when DOM is loaded and adminBase is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait for adminBase to be initialized
    const initDashboard = () => {
        if (window.adminBase) {
            window.adminDashboard = new AdminDashboard();
        } else {
            setTimeout(initDashboard, 100);
        }
    };
    initDashboard();
});
