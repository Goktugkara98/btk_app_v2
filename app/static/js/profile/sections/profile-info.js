/**
 * Profile Information Section JavaScript
 * Handles form interactions, validation, and data management
 * Now supports field-by-field editing
 */

class ProfileInfoSection {
    constructor() {
        this.form = null;
        this.editingFields = new Set(); // Track which fields are being edited
        this.originalData = {};
        this.fieldData = {}; // Store original data for each field
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadUserData();
        // Sayfa yüklendiğinde form alanlarını disabled yap
        this.disableFormFields();
    }

    bindEvents() {
        // Legacy global buttons (hidden but kept for compatibility)
        const editBtn = document.querySelector('.btn-edit-profile');
        if (editBtn) {
            editBtn.addEventListener('click', () => this.toggleEditMode());
        }

        const saveBtn = document.querySelector('.btn-save-profile');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveProfile());
        }

        const cancelBtn = document.querySelector('.btn-cancel-edit');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.cancelEdit());
        }

        // New field-specific buttons
        this.bindFieldButtons();

        // Form validation and keyboard shortcuts
        this.form = document.querySelector('.profile-info-form');
        if (this.form) {
            this.form.addEventListener('input', (e) => this.validateField(e.target));
            this.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveProfile();
            });

            // Add keyboard shortcuts for editing fields
            this.form.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && e.target.closest('.input-with-edit.editing')) {
                    e.preventDefault();
                    const fieldName = e.target.name;
                    if (fieldName) {
                        this.saveField(fieldName);
                    }
                } else if (e.key === 'Escape' && e.target.closest('.input-with-edit.editing')) {
                    e.preventDefault();
                    const fieldName = e.target.name;
                    if (fieldName) {
                        this.cancelFieldEdit(fieldName);
                    }
                }
            });
        }

        // Avatar upload
        const avatarUpload = document.querySelector('.avatar-upload');
        if (avatarUpload) {
            avatarUpload.addEventListener('change', (e) => this.handleAvatarUpload(e));
        }
    }

    bindFieldButtons() {
        // Field edit buttons
        document.querySelectorAll('.btn-edit-field').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const fieldName = e.target.closest('.btn-edit-field').dataset.field;
                this.toggleFieldEdit(fieldName);
            });
        });

        // Field save and cancel buttons (will be created dynamically)
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-save-field')) {
                e.preventDefault();
                e.stopPropagation();
                const fieldName = e.target.closest('.btn-save-field').dataset.field;
                this.saveField(fieldName);
            } else if (e.target.closest('.btn-cancel-field')) {
                e.preventDefault();
                e.stopPropagation();
                const fieldName = e.target.closest('.btn-cancel-field').dataset.field;
                this.cancelFieldEdit(fieldName);
            }
        });
    }

    toggleFieldEdit(fieldName) {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (!field) return;

        const isEditing = this.editingFields.has(fieldName);
        
        if (isEditing) {
            this.exitFieldEdit(fieldName);
        } else {
            this.enterFieldEdit(fieldName);
        }
    }

    enterFieldEdit(fieldName) {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (!field) return;

        const inputContainer = field.closest('.input-with-edit');
        if (!inputContainer) return;

        // Store original data for this field
        this.fieldData[fieldName] = field.value;

        // Enable the field
        field.disabled = false;
        field.focus();

        // Add editing class to container
        inputContainer.classList.add('editing');

        // Create save and cancel buttons
        this.createFieldButtons(inputContainer, fieldName);

        // Track editing state
        this.editingFields.add(fieldName);

        this.showNotification(`${this.getFieldDisplayName(fieldName)} düzenleme modunda`, 'info');
    }

    exitFieldEdit(fieldName) {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (!field) return;

        const inputContainer = field.closest('.input-with-edit');
        if (!inputContainer) return;

        // Disable the field
        field.disabled = true;

        // Remove editing class
        inputContainer.classList.remove('editing');

        // Remove save and cancel buttons
        this.removeFieldButtons(inputContainer);

        // Remove from editing set
        this.editingFields.delete(fieldName);
    }

    createFieldButtons(container, fieldName) {
        // Remove existing buttons first
        this.removeFieldButtons(container);

        // Create save button
        const saveBtn = document.createElement('button');
        saveBtn.type = 'button';
        saveBtn.className = 'btn-save-field';
        saveBtn.dataset.field = fieldName;
        saveBtn.innerHTML = '<i class="fas fa-check"></i>';
        saveBtn.title = 'Kaydet';
        saveBtn.setAttribute('aria-label', 'Kaydet');

        // Create cancel button
        const cancelBtn = document.createElement('button');
        cancelBtn.type = 'button';
        cancelBtn.className = 'btn-cancel-field';
        cancelBtn.dataset.field = fieldName;
        cancelBtn.innerHTML = '<i class="fas fa-times"></i>';
        cancelBtn.title = 'İptal';
        cancelBtn.setAttribute('aria-label', 'İptal');

        // Add buttons to container
        container.appendChild(saveBtn);
        container.appendChild(cancelBtn);

        // Focus the input field
        const input = container.querySelector('input, select, textarea');
        if (input) {
            setTimeout(() => input.focus(), 100);
        }
    }

    removeFieldButtons(container) {
        const saveBtn = container.querySelector('.btn-save-field');
        const cancelBtn = container.querySelector('.btn-cancel-field');
        
        if (saveBtn) saveBtn.remove();
        if (cancelBtn) cancelBtn.remove();
    }

    async saveField(fieldName) {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (!field) return;

        // Validate field
        if (!this.validateField(field)) {
            this.showNotification('Lütfen alanı doğru şekilde doldurun', 'error');
            return;
        }

        const fieldValue = field.value;
        
        // Debug log for gradeLevel
        if (fieldName === 'gradeLevel') {
            console.log('Saving gradeLevel:', fieldValue, 'Type:', typeof fieldValue);
        }
        
        // Get the save button and store original HTML
        const saveBtn = field.closest('.input-with-edit').querySelector('.btn-save-field');
        const originalHTML = saveBtn ? saveBtn.innerHTML : '';
        
        try {
            // Show loading state
            if (saveBtn) {
                saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                saveBtn.disabled = true;
            }

            // Make real API call to update profile
            const response = await fetch('/api/profile/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ [fieldName]: fieldValue })
            });

            const result = await response.json();

            if (result.status === 'success') {
                // Update original data
                this.fieldData[fieldName] = fieldValue;
                
                // Exit edit mode
                this.exitFieldEdit(fieldName);
                
                this.showNotification(`${this.getFieldDisplayName(fieldName)} başarıyla güncellendi`, 'success');
            } else {
                throw new Error(result.message || 'Güncelleme başarısız');
            }
            
        } catch (error) {
            console.error('Profile update error:', error);
            this.showNotification(error.message || 'Güncelleme sırasında bir hata oluştu', 'error');
        } finally {
            // Reset button
            const saveBtn = field.closest('.input-with-edit').querySelector('.btn-save-field');
            if (saveBtn) {
                saveBtn.innerHTML = originalHTML;
                saveBtn.disabled = false;
            }
        }
    }

    cancelFieldEdit(fieldName) {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (!field) return;

        // Restore original data
        const originalValue = this.fieldData[fieldName];
        if (originalValue !== undefined) {
            field.value = originalValue;
        }
        
        // Exit edit mode
        this.exitFieldEdit(fieldName);
        
        // Don't show notification for cancel to reduce noise
        // this.showNotification(`${this.getFieldDisplayName(fieldName)} değişiklikleri iptal edildi`, 'info');
    }

    getFieldDisplayName(fieldName) {
        const fieldNames = {
            'username': 'Kullanıcı Adı',
            'email': 'E-posta Adresi',
            'firstName': 'Ad',
            'lastName': 'Soyad',
            'phone': 'Telefon',
            'birthDate': 'Doğum Tarihi',
            'gender': 'Cinsiyet',

            'bio': 'Biyografi',
            'school': 'Okul',
            'gradeLevel': 'Sınıf',
            'avatar': 'Profil Fotoğrafı'
        };
        return fieldNames[fieldName] || fieldName;
    }

    loadUserData() {
        // Form alanlarından mevcut verileri al
        const userData = this.getCurrentFormData();
        
        if (userData) {
            this.populateForm(userData);
            this.originalData = { ...userData };
        }
    }

    getCurrentFormData() {
        // Form alanlarından mevcut verileri topla
        const form = document.querySelector('.profile-info-form');
        if (!form) return null;

        const formData = new FormData(form);
        const data = {};
        
        // Form alanlarını kontrol et
        const fields = [
            'username', 'email', 'firstName', 'lastName', 'phone',
            'birthDate', 'gender', 'bio', 'school', 'gradeLevel'
        ];

        fields.forEach(field => {
            const element = form.querySelector(`[name="${field}"]`);
            if (element) {
                data[field] = element.value || '';
            }
        });

        return data;
    }

    populateForm(data) {
        const fields = [
            'username', 'email', 'firstName', 'lastName', 'phone',
            'birthDate', 'gender', 'bio', 'school', 'gradeLevel'
        ];

        fields.forEach(field => {
            const element = document.querySelector(`[name="${field}"]`);
            if (element && data[field]) {
                element.value = data[field];
            }
        });

        // Update display fields
        this.updateDisplayFields(data);
    }

    updateDisplayFields(data) {
        // Update join date
        const joinDateElement = document.querySelector('.join-date');
        if (joinDateElement) {
            joinDateElement.textContent = this.formatDate(data.joinDate);
        }

        // Update last login
        const lastLoginElement = document.querySelector('.last-login');
        if (lastLoginElement) {
            lastLoginElement.textContent = this.formatDateTime(data.lastLogin);
        }

        // Update status
        const statusElement = document.querySelector('.user-status');
        if (statusElement) {
            statusElement.textContent = this.getStatusText(data.status);
            statusElement.className = `status-indicator status-${data.status}`;
        }
    }

    // Legacy methods for backward compatibility
    toggleEditMode() {
        // This method is now deprecated but kept for compatibility
        console.warn('toggleEditMode is deprecated. Use field-specific editing instead.');
    }

    async saveProfile() {
        // This method is now deprecated but kept for compatibility
        console.warn('saveProfile is deprecated. Use field-specific saving instead.');
    }

    cancelEdit() {
        // This method is now deprecated but kept for compatibility
        console.warn('cancelEdit is deprecated. Use field-specific canceling instead.');
    }

    getFormData() {
        const formData = {};
        const form = document.querySelector('.profile-info-form');
        
        if (form) {
            const formElements = form.elements;
            for (let element of formElements) {
                if (element.name) {
                    formData[element.name] = element.value;
                }
            }
        }
        
        return formData;
    }

    validateForm() {
        let isValid = true;
        const requiredFields = ['username', 'email', 'firstName', 'lastName'];
        
        requiredFields.forEach(fieldName => {
            const field = document.querySelector(`[name="${fieldName}"]`);
            if (field && !this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name;
        let isValid = true;
        let errorMessage = '';

        // Remove existing error
        this.removeFieldError(field);

        // Required field validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'Bu alan zorunludur';
        }

        // Email validation
        if (fieldName === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Geçerli bir e-posta adresi girin';
            }
        }

        // Username validation
        if (fieldName === 'username' && value) {
            const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
            if (!usernameRegex.test(value)) {
                isValid = false;
                errorMessage = 'Kullanıcı adı 3-20 karakter arasında olmalı ve sadece harf, rakam ve alt çizgi içerebilir';
            }
        }

        // Phone validation
        if (fieldName === 'phone' && value) {
            const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
            if (!phoneRegex.test(value)) {
                isValid = false;
                errorMessage = 'Geçerli bir telefon numarası girin';
            }
        }

        // Website validation
        if (fieldName === 'website' && value) {
            const urlRegex = /^https?:\/\/.+/;
            if (!urlRegex.test(value)) {
                isValid = false;
                errorMessage = 'Geçerli bir URL girin (http:// veya https:// ile başlamalı)';
            }
        }

        // Grade level validation
        if (fieldName === 'gradeLevel' && value) {
            const validGrades = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'];
            if (!validGrades.includes(value)) {
                isValid = false;
                errorMessage = 'Geçerli bir sınıf seçiniz';
            }
        }

        // Show error if invalid
        if (!isValid) {
            this.showFieldError(field, errorMessage);
        }

        return isValid;
    }

    showFieldError(field, message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
        field.classList.add('error');
    }

    removeFieldError(field) {
        const errorDiv = field.parentNode.querySelector('.form-error');
        if (errorDiv) {
            errorDiv.remove();
        }
        field.classList.remove('error');
    }

    async handleAvatarUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.showNotification('Lütfen geçerli bir resim dosyası seçin', 'error');
            return;
        }

        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            this.showNotification('Dosya boyutu 5MB\'dan küçük olmalıdır', 'error');
            return;
        }

        try {
            // Show preview
            const reader = new FileReader();
            reader.onload = (e) => {
                const avatarElements = document.querySelectorAll('.avatar-img');
                avatarElements.forEach(avatar => {
                    avatar.src = e.target.result;
                });
            };
            reader.readAsDataURL(file);

            // Create FormData for file upload
            const formData = new FormData();
            formData.append('avatar', file);

            // Make real API call to upload avatar
            const response = await fetch('/api/profile/avatar', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.status === 'success') {
                // Update avatar image with the new URL
                if (result.data && result.data.avatar_url) {
                    const avatarElements = document.querySelectorAll('.avatar-img');
                    avatarElements.forEach(avatar => {
                        avatar.src = result.data.avatar_url;
                    });
                }
                this.showNotification('Profil fotoğrafı başarıyla güncellendi', 'success');
            } else {
                throw new Error(result.message || 'Fotoğraf yükleme başarısız');
            }

        } catch (error) {
            console.error('Avatar upload error:', error);
            this.showNotification(error.message || 'Fotoğraf yüklenirken bir hata oluştu', 'error');
        }
    }

    // Utility methods
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('tr-TR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    formatDateTime(dateTimeString) {
        const date = new Date(dateTimeString);
        return date.toLocaleString('tr-TR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    getStatusText(status) {
        const statusMap = {
            active: 'Aktif',
            inactive: 'Pasif',
            pending: 'Beklemede'
        };
        return statusMap[status] || status;
    }



    showNotification(message, type = 'info') {
        // Use the notification system from main profile.js
        if (window.profilePage && window.profilePage.showNotification) {
            window.profilePage.showNotification(message, type);
        } else {
            // Fallback notification
            alert(message);
        }
    }

    disableFormFields() {
        // Tüm form alanlarını disabled yap
        const fields = document.querySelectorAll('.profile-info-form input, .profile-info-form select, .profile-info-form textarea');
        
        fields.forEach(field => {
            field.disabled = true;
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ProfileInfoSection();
}); 