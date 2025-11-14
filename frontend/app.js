// MindLab Health - Frontend JavaScript

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Helper function for API calls
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
    };

    // Add auth token if exists
    const token = localStorage.getItem('token');
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || 'API call failed');
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Show message
function showMessage(message, type = 'success') {
    const messageEl = document.getElementById('message');
    if (messageEl) {
        messageEl.textContent = message;
        messageEl.className = `message ${type}`;
        messageEl.style.display = 'block';  // Make sure it's visible
        
        // Hide after 5 seconds
        setTimeout(() => {
            messageEl.style.display = 'none';
        }, 5000);
    } else {
        // Fallback if message element doesn't exist
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}

// Login Form Handler
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            console.log('Login attempt for user:', username);
            
            // OAuth2 expects form data, not JSON
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);
            
            const response = await fetch(`${API_BASE_URL}/api/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }
            
            const result = await response.json();

            // Store token
            console.log('Login successful! Token received');
            localStorage.setItem('token', result.access_token);
            localStorage.setItem('username', username);
            console.log('Token and username stored. Redirecting to dashboard...');

            // Show success message
            showMessage('Login successful! Redirecting...', 'success');

            // Redirect to dashboard with enhanced logging and fallbacks
            console.log('REDIRECT: Scheduling redirect in 1 second...');
            
            setTimeout(() => {
                console.log('REDIRECT: setTimeout callback executing...');
                
                try {
                    console.log('REDIRECT: Attempting redirect to /dashboard.html (absolute path)');
                    window.location.href = '/dashboard.html';
                    
                    // This may not log if redirect is instant
                    console.log('REDIRECT: window.location.href set successfully');
                } catch (error) {
                    console.error('REDIRECT ERROR (absolute path):', error);
                    
                    // Fallback 1: Try relative path
                    try {
                        console.log('REDIRECT: Fallback - trying relative path dashboard.html');
                        window.location.href = 'dashboard.html';
                    } catch (error2) {
                        console.error('REDIRECT ERROR (relative path):', error2);
                        
                        // Fallback 2: Try window.location.replace
                        try {
                            console.log('REDIRECT: Fallback - trying window.location.replace');
                            window.location.replace('/dashboard.html');
                        } catch (error3) {
                            console.error('REDIRECT ERROR (replace):', error3);
                            
                            // Fallback 3: Try window.location.assign
                            try {
                                console.log('REDIRECT: Fallback - trying window.location.assign');
                                window.location.assign('/dashboard.html');
                            } catch (error4) {
                                console.error('REDIRECT ERROR (assign):', error4);
                                
                                // Last resort: Alert user
                                alert('Redirect failed. Please click OK to go to dashboard.');
                                window.location.href = '/dashboard.html';
                            }
                        }
                    }
                }
            }, 1000);
        } catch (error) {
            showMessage(error.message || 'Login failed', 'error');
        }
    });
}

// Register Form Handler
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const role = document.getElementById('role').value;

        try {
            await apiCall('/api/register', 'POST', {
                username,
                email,
                password,
                role
            });

            showMessage('Registration successful! Redirecting to login...', 'success');

            setTimeout(() => {
                window.location.href = 'login.html';
            }, 1500);
        } catch (error) {
            showMessage(error.message || 'Registration failed', 'error');
        }
    });
}

// Dashboard: Load user info
if (window.location.pathname.includes('dashboard.html')) {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');

    if (!token) {
        window.location.href = 'login.html';
    } else {
        // Display user name
        const userNameEl = document.getElementById('userName');
        if (userNameEl) {
            userNameEl.textContent = username || 'User';
        }

        // Load user data
        async function loadUserData() {
            try {
                const user = await apiCall('/api/users/me');
                const userRoleEl = document.getElementById('userRole');
                if (userRoleEl) {
                    userRoleEl.textContent = user.role || 'User';
                }
                
                // Show admin modules if user is admin
                if (user.role === 'admin') {
                    const adminModules = document.getElementById('adminModules');
                    if (adminModules) {
                        adminModules.style.display = 'block';
                    }
                }
                
                // Load dashboard statistics
                await loadDashboardStats(user.role);
            } catch (error) {
                console.error('Failed to load user data:', error);
            }
        }
        
        // Load dashboard statistics
        async function loadDashboardStats(userRole) {
            try {
                // Load appointment count
                const appointments = await apiCall('/api/appointments/my');
                const appointmentCountEl = document.getElementById('appointmentCount');
                if (appointmentCountEl) {
                    appointmentCountEl.textContent = appointments.length || 0;
                }
            } catch (error) {
                console.error('Failed to load appointments:', error);
                const appointmentCountEl = document.getElementById('appointmentCount');
                if (appointmentCountEl) {
                    appointmentCountEl.textContent = '0';
                }
            }
            
            try {
                // Load message count
                const messages = await apiCall('/api/messages/inbox');
                const messageCountEl = document.getElementById('messageCount');
                if (messageCountEl) {
                    messageCountEl.textContent = messages.length || 0;
                }
            } catch (error) {
                console.error('Failed to load messages:', error);
                const messageCountEl = document.getElementById('messageCount');
                if (messageCountEl) {
                    messageCountEl.textContent = '0';
                }
            }
            
            // User count placeholder (would need admin endpoint)
            const userCountEl = document.getElementById('userCount');
            if (userCountEl) {
                userCountEl.textContent = userRole === 'admin' ? '1+' : '-';
            }
        }

        loadUserData();
    }
}

// Logout Handler
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        window.location.href = 'index.html';
    });
}

// Load Module Function
function loadModule(moduleName) {
    alert(`Loading ${moduleName} module...\n\nThis module is currently under development.\n\nAvailable API endpoints:\n- Users: /api/users/me\n- Appointments: /api/appointments/my\n- Messages: /api/messages/inbox\n- Health: /api/health`);
    console.log(`Module requested: ${moduleName}`);
}

// Check API Health
async function checkAPIHealth() {
    try {
        const health = await apiCall('/api/health');
        console.log('API Health:', health);
    } catch (error) {
        console.warn('API might be offline:', error);
    }
}

// Check health on page load
checkAPIHealth();
