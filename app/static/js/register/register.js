// =============================================================================
// REGISTER PAGE - MODULAR JAVASCRIPT STRUCTURE
// =============================================================================

// =============================================================================
// 1.0. MODÜL BAŞLIĞI VE AÇIKLAMASI
// =============================================================================
// Bu modül, register sayfasının tüm JavaScript işlevselliğini yönetir.
// Form validation, password strength, API communication ve UI feedback
// işlemlerini içerir.
// =============================================================================

// =============================================================================
// 2.0. İÇİNDEKİLER
// =============================================================================
// 3.0. DOM READY EVENT
// 4.0. FORM VALIDATION MODULE
//   4.1. Real-time Validation Setup
//   4.2. Field Validation Functions
//   4.3. Error Display Functions
// 5.0. PASSWORD STRENGTH MODULE
//   5.1. Strength Indicator Setup
//   5.2. Strength Calculation
// 6.0. FORM HANDLING MODULE
//   6.1. Form Submission Handler
//   6.2. API Communication
// 7.0. UI FEEDBACK MODULE
//   7.1. Message Display Functions
//   7.2. Form State Management
// =============================================================================

// =============================================================================
// 3.0. DOM READY EVENT
// =============================================================================
document.addEventListener('DOMContentLoaded', () => {
    initializeRegisterPage();
});

// =============================================================================
// 4.0. FORM VALIDATION MODULE
// =============================================================================

// -------------------------------------------------------------------------
// 4.1. Real-time Validation Setup
// -------------------------------------------------------------------------
function setupRealTimeValidation() {
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const password2Input = document.getElementById('password2');
    
    // Name validation
    nameInput.addEventListener('blur', () => validateName());
    nameInput.addEventListener('input', () => clearError('name'));
    
    // Email validation
    emailInput.addEventListener('blur', () => validateEmail());
    emailInput.addEventListener('input', () => clearError('email'));
    
    // Password validation
    passwordInput.addEventListener('blur', () => validatePassword());
    passwordInput.addEventListener('input', () => {
        clearError('password');
        updatePasswordStrength();
    });
    
    // Password confirmation validation
    password2Input.addEventListener('blur', () => validatePassword2());
    password2Input.addEventListener('input', () => clearError('password2'));
}

// -------------------------------------------------------------------------
// 4.2. Field Validation Functions
// -------------------------------------------------------------------------
function validateName() {
    const name = document.getElementById('name').value.trim();
    const usernamePattern = /^[a-zA-Z0-9_]+$/;
    
    if (!name) {
        showFieldError('name', 'Kullanıcı adı gereklidir');
        return false;
    }
    if (name.length < 3) {
        showFieldError('name', 'Kullanıcı adı en az 3 karakter olmalıdır');
        return false;
    }
    if (name.length > 30) {
        showFieldError('name', 'Kullanıcı adı en fazla 30 karakter olabilir');
        return false;
    }
    if (!usernamePattern.test(name)) {
        showFieldError('name', 'Kullanıcı adı sadece harf, rakam ve alt çizgi içerebilir');
        return false;
    }
    clearError('name');
    return true;
}

function validateEmail() {
    const email = document.getElementById('email').value.trim();
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!email) {
        showFieldError('email', 'E-posta alanı gereklidir');
        return false;
    }
    if (!emailPattern.test(email)) {
        showFieldError('email', 'Geçerli bir e-posta adresi giriniz');
        return false;
    }
    clearError('email');
    return true;
}

function validatePassword() {
    const password = document.getElementById('password').value;
    
    if (!password) {
        showFieldError('password', 'Şifre alanı gereklidir');
        return false;
    }
    if (password.length < 6) {
        showFieldError('password', 'Şifre en az 6 karakter olmalıdır');
        return false;
    }
    clearError('password');
    return true;
}

function validatePassword2() {
    const password = document.getElementById('password').value;
    const password2 = document.getElementById('password2').value;
    
    if (!password2) {
        showFieldError('password2', 'Şifre tekrar alanı gereklidir');
        return false;
    }
    if (password !== password2) {
        showFieldError('password2', 'Şifreler eşleşmiyor');
        return false;
    }
    clearError('password2');
    return true;
}

// -------------------------------------------------------------------------
// 4.3. Error Display Functions
// -------------------------------------------------------------------------
function showFieldError(fieldName, message) {
    const input = document.getElementById(fieldName);
    const errorDiv = document.getElementById(`${fieldName}-error`);
    
    input.classList.add('error');
    input.classList.remove('success');
    
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
}

function clearError(fieldName) {
    const input = document.getElementById(fieldName);
    const errorDiv = document.getElementById(`${fieldName}-error`);
    
    input.classList.remove('error');
    
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

// =============================================================================
// 5.0. PASSWORD STRENGTH MODULE
// =============================================================================

// -------------------------------------------------------------------------
// 5.1. Strength Indicator Setup
// -------------------------------------------------------------------------
function setupPasswordStrength() {
    const passwordInput = document.getElementById('password');
    passwordInput.addEventListener('input', updatePasswordStrength);
}

// -------------------------------------------------------------------------
// 5.2. Strength Calculation
// -------------------------------------------------------------------------
function updatePasswordStrength() {
    const password = document.getElementById('password').value;
    const strengthFill = document.getElementById('strength-fill');
    const strengthText = document.getElementById('strength-text');
    
    if (!password) {
        strengthFill.style.width = '0%';
        strengthFill.className = 'strength-fill';
        strengthText.textContent = 'Şifre gücü';
        return;
    }
    
    let strength = 0;
    let feedback = '';
    
    // Length check
    if (password.length >= 6) strength += 25;
    if (password.length >= 8) strength += 25;
    
    // Character variety checks
    if (/[a-z]/.test(password)) strength += 15;
    if (/[A-Z]/.test(password)) strength += 15;
    if (/[0-9]/.test(password)) strength += 10;
    if (/[^A-Za-z0-9]/.test(password)) strength += 10;
    
    // Update visual indicator
    strengthFill.style.width = strength + '%';
    
    // Determine strength level
    if (strength < 30) {
        strengthFill.className = 'strength-fill strength-weak';
        feedback = 'Zayıf';
    } else if (strength < 70) {
        strengthFill.className = 'strength-fill strength-medium';
        feedback = 'Orta';
    } else {
        strengthFill.className = 'strength-fill strength-strong';
        feedback = 'Güçlü';
    }
    
    strengthText.textContent = `Şifre gücü: ${feedback}`;
}

// =============================================================================
// 6.0. FORM HANDLING MODULE
// =============================================================================

// -------------------------------------------------------------------------
// 6.1. Form Submission Handler
// -------------------------------------------------------------------------
async function handleRegister(event) {
    event.preventDefault();
    
    // Form verilerini al
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const password2 = document.getElementById('password2').value;
    
    // Client-side validation
    const isNameValid = validateName();
    const isEmailValid = validateEmail();
    const isPasswordValid = validatePassword();
    const isPassword2Valid = validatePassword2();
    
    if (!isNameValid || !isEmailValid || !isPasswordValid || !isPassword2Valid) {
        showError('Lütfen tüm alanları doğru şekilde doldurun.');
        return;
    }
    
    // Submit butonunu devre dışı bırak
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const originalText = btnText.textContent;
    
    submitBtn.disabled = true;
    btnText.textContent = 'Kayıt yapılıyor...';
    
    try {
        // API'ye gönder
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                email: email,
                password: password,
                password2: password2
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
            // Başarılı kayıt
            showSuccess('Kayıt başarıyla tamamlandı! Giriş sayfasına yönlendiriliyorsunuz...');
            
            // Form'u temizle
            clearForm();
            
            // 2 saniye sonra login sayfasına yönlendir
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
            
        } else {
            // Hata durumu
            const errorMessage = result.message || 'Kayıt işlemi başarısız oldu.';
            showError(errorMessage);
        }
        
    } catch (error) {
        console.error('Register error:', error);
        showError('Bağlantı hatası oluştu. Lütfen tekrar deneyin.');
    } finally {
        // Submit butonunu tekrar aktif et
        submitBtn.disabled = false;
        btnText.textContent = originalText;
    }
}

// -------------------------------------------------------------------------
// 6.2. API Communication
// -------------------------------------------------------------------------
async function sendRegisterRequest(formData) {
    const response = await fetch('/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    });
    
    return await response.json();
}

// =============================================================================
// 7.0. UI FEEDBACK MODULE
// =============================================================================

// -------------------------------------------------------------------------
// 7.1. Message Display Functions
// -------------------------------------------------------------------------
function showError(message) {
    const messageContainer = document.getElementById('message-container');
    
    // Mevcut mesajları temizle
    messageContainer.innerHTML = '';
    
    // Yeni hata mesajı oluştur
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    
    messageContainer.appendChild(errorDiv);
    
    // 5 saniye sonra otomatik kaldır
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 5000);
}

function showSuccess(message) {
    const messageContainer = document.getElementById('message-container');
    
    // Mevcut mesajları temizle
    messageContainer.innerHTML = '';
    
    // Yeni başarı mesajı oluştur
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    
    messageContainer.appendChild(successDiv);
}

// -------------------------------------------------------------------------
// 7.2. Form State Management
// -------------------------------------------------------------------------
function clearForm() {
    document.getElementById('register-form').reset();
    document.querySelectorAll('.error-text').forEach(el => el.style.display = 'none');
    document.querySelectorAll('input').forEach(input => {
        input.classList.remove('error', 'success');
    });
    updatePasswordStrength();
}

// =============================================================================
// 8.0. INITIALIZATION FUNCTION
// =============================================================================
function initializeRegisterPage() {
    // Register form handling
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
        
        // Real-time validation
        setupRealTimeValidation();
        
        // Password strength indicator
        setupPasswordStrength();
    }
} 