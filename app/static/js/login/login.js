/* =============================================================================
 * LOGIN PAGE - ENHANCED JAVASCRIPT WITH MODERN UX
 * ============================================================================= */

document.addEventListener('DOMContentLoaded', () => {
    initializeLoginForm();
});

// Initialize login form with enhanced functionality
function initializeLoginForm() {
    const loginForm = document.getElementById('login-form');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const submitBtn = document.getElementById('submit-btn');
    const messageContainer = document.getElementById('message-container');

    if (loginForm) {
        // Form submission handler
        loginForm.addEventListener('submit', handleLoginSubmit);
        
        // Real-time validation
        emailInput.addEventListener('blur', () => validateEmail(emailInput));
        passwordInput.addEventListener('blur', () => validatePassword(passwordInput));
        
        // Input focus effects
        [emailInput, passwordInput].forEach(input => {
            input.addEventListener('focus', () => {
                input.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', () => {
                input.parentElement.classList.remove('focused');
            });
        });
    }
}

// Enhanced login form handler
async function handleLoginSubmit(event) {
    event.preventDefault();
    
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const submitBtn = document.getElementById('submit-btn');
    const messageContainer = document.getElementById('message-container');
    
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    
    // Clear previous messages
    clearMessages();
    
    // Validate form
    const isEmailValid = validateEmail(emailInput);
    const isPasswordValid = validatePassword(passwordInput);
    
    if (!isEmailValid || !isPasswordValid) {
        showMessage('Lütfen tüm alanları doğru şekilde doldurun.', 'error');
        return;
    }
    
    // Show loading state
    setLoadingState(true);
    
    try {
        // Real API call
        const result = await loginAPI(email, password);
        
        // Success handling
        showMessage('Giriş başarılı! Yönlendiriliyorsunuz...', 'success');
        
        // Redirect after short delay
        setTimeout(() => {
            window.location.href = '/';
        }, 1500);
        
    } catch (error) {
        // Error handling
        showMessage(error.message || 'Giriş yapılırken bir hata oluştu.', 'error');
        setLoadingState(false);
    }
}

// Email validation
function validateEmail(emailInput) {
    const email = emailInput.value.trim();
    const errorElement = document.getElementById('email-error');
    
    // Clear previous states
    emailInput.classList.remove('error', 'success');
    errorElement.style.display = 'none';
    
    if (!email) {
        showFieldError(emailInput, errorElement, 'E-posta adresi gereklidir.');
        return false;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showFieldError(emailInput, errorElement, 'Geçerli bir e-posta adresi giriniz.');
        return false;
    }
    
    // Success state
    emailInput.classList.add('success');
    return true;
}

// Password validation
function validatePassword(passwordInput) {
    const password = passwordInput.value;
    const errorElement = document.getElementById('password-error');
    
    // Clear previous states
    passwordInput.classList.remove('error', 'success');
    errorElement.style.display = 'none';
    
    if (!password) {
        showFieldError(passwordInput, errorElement, 'Şifre gereklidir.');
        return false;
    }
    
    if (password.length < 6) {
        showFieldError(passwordInput, errorElement, 'Şifre en az 6 karakter olmalıdır.');
        return false;
    }
    
    // Success state
    passwordInput.classList.add('success');
    return true;
}

// Show field error
function showFieldError(input, errorElement, message) {
    input.classList.add('error');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

// Show message in container
function showMessage(message, type) {
    const messageContainer = document.getElementById('message-container');
    const icon = type === 'error' ? 'fas fa-exclamation-circle' : 'fas fa-check-circle';
    
    messageContainer.innerHTML = `
        <div class="${type}-message">
            <i class="${icon}"></i>
            <span>${message}</span>
        </div>
    `;
}

// Clear all messages
function clearMessages() {
    const messageContainer = document.getElementById('message-container');
    messageContainer.innerHTML = '';
}

// Set loading state
function setLoadingState(isLoading) {
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnIcon = submitBtn.querySelector('i');
    
    if (isLoading) {
        submitBtn.disabled = true;
        btnText.textContent = 'Giriş Yapılıyor...';
        btnIcon.className = 'fas fa-spinner fa-spin';
    } else {
        submitBtn.disabled = false;
        btnText.textContent = 'Giriş Yap';
        btnIcon.className = 'fas fa-sign-in-alt';
    }
}

// Real login API call
async function loginAPI(email, password) {
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            return data;
        } else {
            throw new Error(data.message || 'Giriş yapılırken bir hata oluştu');
        }
    } catch (error) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Sunucuya bağlanılamıyor. Lütfen internet bağlantınızı kontrol edin.');
        }
        throw error;
    }
}

// Utility function to check if element exists
function elementExists(selector) {
    return document.querySelector(selector) !== null;
} 