/* ==========================================================================
   PulseFit Authentication & Session Utility
   ========================================================================== */

const API_BASE = '/api';

// Save JWT Token and Remember Me preference
function saveToken(token, rememberMe) {
    if (rememberMe) {
        localStorage.setItem('pulsefit_token', token);
    } else {
        sessionStorage.setItem('pulsefit_token', token);
    }
}

// Get Active JWT Token
function getToken() {
    return localStorage.getItem('pulsefit_token') || sessionStorage.getItem('pulsefit_token');
}

// Clear Session Token
function clearToken() {
    localStorage.removeItem('pulsefit_token');
    sessionStorage.removeItem('pulsefit_token');
}

// Authenticated fetch wrapper
async function apiFetch(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        ...options,
        headers,
    };
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, config);
        
        // Handle Unauthorized Globally
        if (response.status === 401) {
            clearToken();
            if (!isPublicPage()) {
                window.location.href = 'login.html';
            }
        }
        
        return response;
    } catch (error) {
        console.error('API Fetch Error:', error);
        throw error;
    }
}

// Check if current page is public
function isPublicPage() {
    const path = window.location.pathname;
    const publicPages = [
        'login.html',
        'register.html',
        'forgot-password.html',
        'about.html',
        'contact.html',
        'faq.html',
        'privacy.html',
        'terms.html'
    ];
    // index.html serves as landing if logged out, so it is public
    if (path === '/' || path.endsWith('index.html') || path === '') {
        return true;
    }
    return publicPages.some(page => path.endsWith(page));
}

// Validate session and redirect if necessary
async function validateSession() {
    const token = getToken();
    const path = window.location.pathname;
    const isIndex = path === '/' || path.endsWith('index.html') || path === '';
    
    if (token) {
        try {
            const res = await fetch(`${API_BASE}/auth/profile`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                // If on auth pages (login/register/forgot-password), redirect to dashboard
                if (path.endsWith('login.html') || path.endsWith('register.html') || path.endsWith('forgot-password.html')) {
                    window.location.href = 'index.html';
                }
                return true;
            } else {
                clearToken();
                if (!isPublicPage()) {
                    window.location.href = 'login.html';
                }
            }
        } catch (err) {
            console.error('Session validation failed:', err);
        }
    } else {
        // No token
        if (!isPublicPage()) {
            window.location.href = 'login.html';
        }
    }
    return false;
}

// User Logout
async function logoutUser() {
    const token = getToken();
    if (token) {
        try {
            await fetch(`${API_BASE}/auth/logout`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
        } catch (e) {
            console.error('Logout request failed', e);
        }
    }
    clearToken();
    window.location.href = 'login.html';
}

// Toast Notifications helper
function showToast(message, type = 'success') {
    // Create toast container if it doesn't exist
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast-item toast-${type} slide-in`;
    
    let icon = 'info';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'alert-triangle';
    if (type === 'warning') icon = 'alert-circle';
    
    toast.innerHTML = `
        <i data-lucide="${icon}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    if (window.lucide) {
        window.lucide.createIcons();
    }
    
    // Remove toast after 4s
    setTimeout(() => {
        toast.classList.replace('slide-in', 'fade-out');
        setTimeout(() => toast.remove(), 500);
    }, 4000);
}

function setTheme(isDark) {
    if (isDark) {
        document.body.classList.remove('light-theme');
        document.body.classList.add('dark-theme');
        localStorage.setItem('pulsefit-theme', 'dark');
        const toggle = document.getElementById('settings-dark-mode');
        if (toggle) toggle.checked = true;
    } else {
        document.body.classList.remove('dark-theme');
        document.body.classList.add('light-theme');
        localStorage.setItem('pulsefit-theme', 'light');
        const toggle = document.getElementById('settings-dark-mode');
        if (toggle) toggle.checked = false;
    }
}

// Execute session validation immediately on load
document.addEventListener('DOMContentLoaded', async () => {
    const isAuthenticated = await validateSession();
    
    // Set up initial theme
    const savedTheme = localStorage.getItem('pulsefit-theme') || 'dark';
    setTheme(savedTheme === 'dark');
    
    // Bind theme toggle buttons
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const isDark = document.body.classList.contains('dark-theme');
            setTheme(!isDark);
        });
    }
    
    // Bind mouse glow positions
    const mouseGlow = document.getElementById('mouse-glow');
    if (mouseGlow) {
        document.addEventListener('mousemove', (e) => {
            mouseGlow.style.opacity = '1';
            mouseGlow.style.left = `${e.clientX}px`;
            mouseGlow.style.top = `${e.clientY}px`;
        });
        document.addEventListener('mouseleave', () => {
            mouseGlow.style.opacity = '0';
        });
    }

    // Configure nav bar based on authentication
    const authBtnWrap = document.getElementById('nav-auth-btn-wrap');
    if (authBtnWrap) {
        if (isAuthenticated) {
            try {
                const res = await apiFetch('/auth/profile');
                if (res.ok) {
                    const user = await res.json();
                    const avatarUrl = user.profile_pic || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=256&auto=format&fit=crop';
                    authBtnWrap.innerHTML = `
                        <a href="profile.html" class="profile-nav-avatar" style="display:block;">
                            <img src="${avatarUrl}" alt="${user.full_name}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 2px solid var(--primary-color);">
                        </a>
                    `;
                }
            } catch (e) {
                console.error("Error setting up navbar profile avatar", e);
            }
        } else {
            authBtnWrap.innerHTML = `
                <a href="login.html" class="btn btn-secondary btn-ripple" style="padding: 8px 16px; font-size: 14px; text-decoration: none;">Login</a>
            `;
        }
    }
});
