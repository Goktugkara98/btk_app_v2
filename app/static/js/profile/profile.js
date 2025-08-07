/**
 * Profile Page JavaScript
 * Handles tab navigation and user interactions
 */

class ProfilePage {
    constructor() {
        this.currentTab = 'profile';
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupTabNavigation();
    }

    bindEvents() {
        // Tab navigation events
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetTab = e.currentTarget.getAttribute('href').substring(1);
                this.switchTab(targetTab);
            });
        });

        // Logout button event
        const logoutBtn = document.querySelector('.logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                this.handleLogout();
            });
        }

        // Avatar edit event
        const avatarEdit = document.querySelector('.avatar-edit');
        if (avatarEdit) {
            avatarEdit.addEventListener('click', () => {
                this.handleAvatarEdit();
            });
        }
    }

    setupTabNavigation() {
        // Set initial active tab
        this.switchTab(this.currentTab);
    }

    switchTab(tabId) {
        // Remove active class from all tabs and content
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        document.querySelectorAll('.content-tab').forEach(tab => {
            tab.classList.remove('active');
        });

        // Add active class to selected tab and content
        const navItem = document.querySelector(`[href="#${tabId}"]`).parentElement;
        const contentTab = document.getElementById(tabId);
        
        if (navItem && contentTab) {
            navItem.classList.add('active');
            contentTab.classList.add('active');
            this.currentTab = tabId;
            
            // Update page title and description
            this.updatePageHeader(tabId);
        }
    }

    updatePageHeader(tabId) {
        const pageTitle = document.querySelector('.page-title');
        const pageDescription = document.querySelector('.page-description');
        
        const tabConfig = {
            profile: {
                title: 'Profil Bilgileri',
                description: 'Hesap bilgilerinizi görüntüleyin ve düzenleyin'
            },
            settings: {
                title: 'Ayarlar',
                description: 'Uygulama ayarlarınızı özelleştirin'
            },
            statistics: {
                title: 'İstatistikler',
                description: 'Quiz performansınızı ve istatistiklerinizi görüntüleyin'
            },
            security: {
                title: 'Güvenlik',
                description: 'Hesap güvenlik ayarlarınızı yönetin'
            },
            notifications: {
                title: 'Bildirimler',
                description: 'Bildirim tercihlerinizi ayarlayın'
            }
        };

        const config = tabConfig[tabId];
        if (config && pageTitle && pageDescription) {
            pageTitle.textContent = config.title;
            pageDescription.textContent = config.description;
        }
    }

    handleLogout() {
        // Show confirmation dialog
        if (confirm('Çıkış yapmak istediğinizden emin misiniz?')) {
            // Redirect to logout route
            window.location.href = '/logout';
        }
    }

    handleAvatarEdit() {
        // Create file input for avatar upload
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.style.display = 'none';
        
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.uploadAvatar(file);
            }
        });
        
        document.body.appendChild(input);
        input.click();
        document.body.removeChild(input);
    }

    uploadAvatar(file) {
        // Show loading state
        const avatarImg = document.querySelector('.avatar-img');
        const originalSrc = avatarImg.src;
        
        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
            avatarImg.src = e.target.result;
        };
        reader.readAsDataURL(file);

        // TODO: Implement actual file upload to server
        console.log('Avatar upload:', file.name);
        
        // For now, just show a success message
        setTimeout(() => {
            alert('Profil fotoğrafı güncellendi!');
        }, 1000);
    }

    // Utility method to show notifications
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        // Set background color based on type
        const colors = {
            success: '#48bb78',
            error: '#e53e3e',
            warning: '#ed8936',
            info: '#4299e1'
        };
        
        notification.style.background = colors[type] || colors.info;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize profile page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.profilePage = new ProfilePage();
});

// Profile Info Section will be loaded via script tag in HTML

// Add notification animations to CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style); 