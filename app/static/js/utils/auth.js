/* =============================================================================
 * AUTHENTICATION UTILITIES - CLIENT SIDE
 * ============================================================================= */

// Logout function
async function logout() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            // Redirect to login page
            window.location.href = '/login';
        } else {
            console.error('Logout failed:', data.message);
            // Still redirect to login page even if logout fails
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Logout error:', error);
        // Redirect to login page on error
        window.location.href = '/login';
    }
}

// Check authentication status
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/check-auth', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (response.ok) {
            return data;
        } else {
            return { logged_in: false };
        }
    } catch (error) {
        console.error('Auth check error:', error);
        return { logged_in: false };
    }
}

// Update UI based on authentication status
function updateAuthUI(isLoggedIn, userData = null) {
    const authElements = document.querySelectorAll('[data-auth]');
    
    authElements.forEach(element => {
        const authType = element.getAttribute('data-auth');
        
        if (authType === 'logged-in' && isLoggedIn) {
            element.style.display = '';
        } else if (authType === 'logged-out' && !isLoggedIn) {
            element.style.display = '';
        } else if (authType === 'logged-in' && !isLoggedIn) {
            element.style.display = 'none';
        } else if (authType === 'logged-out' && isLoggedIn) {
            element.style.display = 'none';
        }
    });
    
    // Update username display if user data is provided
    if (isLoggedIn && userData) {
        const usernameElements = document.querySelectorAll('[data-username]');
        usernameElements.forEach(element => {
            element.textContent = userData.username;
        });
    }
}

// Initialize authentication UI
async function initAuthUI() {
    const authStatus = await checkAuthStatus();
    updateAuthUI(authStatus.logged_in, authStatus.user);
    
    // Add logout event listeners
    const logoutButtons = document.querySelectorAll('[data-logout]');
    logoutButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    });
}

// Export functions for use in other modules
window.authUtils = {
    logout,
    checkAuthStatus,
    updateAuthUI,
    initAuthUI
}; 