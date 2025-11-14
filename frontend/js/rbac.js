// Role-Based Access Control (RBAC) Frontend Management
// Handles permission checking, module access, and role-based UI rendering

class RBACManager {
    constructor() {
        this.userPermissions = [];
        this.userRole = null;
        this.accessibleModules = [];
        this.isInitialized = false;
    }

    // Initialize RBAC by fetching user permissions and modules
    async initialize() {
        try {
            await this.loadUserPermissions();
            await this.loadAccessibleModules();
            this.isInitialized = true;
            console.log('✅ RBAC Manager initialized successfully');
            return true;
        } catch (error) {
            console.error('❌ Failed to initialize RBAC Manager:', error);
            return false;
        }
    }

    // Fetch user permissions from API
    async loadUserPermissions() {
        try {
            const token = getAuthToken();
            if (!token) {
                throw new Error('No authentication token available');
            }

            const response = await fetch('/api/users/me/permissions', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to load permissions: ${response.status}`);
            }

            const data = await response.json();
            this.userPermissions = data.permissions || [];
            this.userRole = data.role;
            
            console.log(`📋 Loaded ${this.userPermissions.length} permissions for role: ${this.userRole}`);
            return this.userPermissions;
        } catch (error) {
            console.error('Failed to load user permissions:', error);
            throw error;
        }
    }

    // Fetch accessible modules from API
    async loadAccessibleModules() {
        try {
            const token = getAuthToken();
            if (!token) {
                throw new Error('No authentication token available');
            }

            const response = await fetch('/api/users/me/modules', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to load modules: ${response.status}`);
            }

            const data = await response.json();
            this.accessibleModules = data.accessible_modules || [];
            
            console.log(`🏗️ Accessible modules: ${this.accessibleModules.join(', ')}`);
            return this.accessibleModules;
        } catch (error) {
            console.error('Failed to load accessible modules:', error);
            throw error;
        }
    }

    // Check if user has specific permission
    hasPermission(permissionName) {
        return this.userPermissions.includes(permissionName);
    }

    // Check if user can access specific module
    canAccessModule(moduleName) {
        return this.accessibleModules.includes(moduleName);
    }

    // Check if user has admin role
    isAdmin() {
        return this.userRole === 'admin';
    }

    // Get user role
    getUserRole() {
        return this.userRole;
    }

    // Get all permissions
    getPermissions() {
        return [...this.userPermissions];
    }

    // Get all accessible modules
    getAccessibleModules() {
        return [...this.accessibleModules];
    }

    // Verify specific permission with server
    async verifyPermission(permissionName) {
        try {
            const token = getAuthToken();
            if (!token) {
                return false;
            }

            const response = await fetch('/api/rbac/check-permission', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ permission: permissionName })
            });

            if (!response.ok) {
                return false;
            }

            const data = await response.json();
            return data.has_permission === true;
        } catch (error) {
            console.error('Failed to verify permission:', error);
            return false;
        }
    }

    // Show/hide elements based on permissions
    applyPermissionBasedVisibility() {
        // Hide admin-only elements
        const adminElements = document.querySelectorAll('[data-admin-only]');
        adminElements.forEach(element => {
            element.style.display = this.isAdmin() ? 'block' : 'none';
        });

        // Hide elements based on permissions
        const permissionElements = document.querySelectorAll('[data-permission]');
        permissionElements.forEach(element => {
            const requiredPermission = element.getAttribute('data-permission');
            element.style.display = this.hasPermission(requiredPermission) ? 'block' : 'none';
        });

        // Hide modules based on access
        const moduleElements = document.querySelectorAll('[data-module]');
        moduleElements.forEach(element => {
            const moduleName = element.getAttribute('data-module');
            element.style.display = this.canAccessModule(moduleName) ? 'block' : 'none';
        });
    }

    // Create role-specific dashboard
    createRoleDashboard() {
        const timestamp = new Date().toLocaleTimeString();
        console.log(`🔄 [${timestamp}] Creating dashboard for role: ${this.userRole}`);
        
        const dashboardContainer = document.getElementById('dashboard-modules');
        if (!dashboardContainer) {
            console.error('❌ Dashboard container not found');
            return;
        }

        // Reset dashboard flags to prevent duplicates
        if (typeof window.resetDashboardFlags === 'function') {
            window.resetDashboardFlags();
        }
        console.log(`📋 Available global functions:`, {
            createPhysicianDashboard: typeof window.createPhysicianDashboard,
            createTherapistDashboard: typeof window.createTherapistDashboard,
            createHealthCoachDashboard: typeof window.createHealthCoachDashboard,
            createPatientDashboard: typeof window.createPatientDashboard,
            createPartnerDashboard: typeof window.createPartnerDashboard
        });

        // Use dedicated dashboard functions based on role
        switch (this.userRole) {
            case 'admin':
                console.log('📋 Creating admin dashboard');
                if (typeof createAdminDashboard === 'function') {
                    createAdminDashboard();
                } else {
                    console.warn('⚠️ createAdminDashboard function not found, using fallback');
                    this.createFallbackAdminDashboard();
                }
                break;
            case 'physician':
                console.log('🩺 Creating physician dashboard');
                if (typeof createPhysicianDashboard === 'function') {
                    createPhysicianDashboard();
                } else {
                    console.warn('⚠️ createPhysicianDashboard function not found, using fallback');
                    this.createFallbackDashboard('physician');
                }
                break;
            case 'therapist':
                console.log('🗣️ Creating therapist dashboard');
                if (typeof createTherapistDashboard === 'function') {
                    createTherapistDashboard();
                } else {
                    console.warn('⚠️ createTherapistDashboard function not found, using fallback');
                    this.createFallbackDashboard('therapist');
                }
                break;
            case 'health_coach':
                console.log('🎯 Creating health coach dashboard');
                if (typeof createHealthCoachDashboard === 'function') {
                    createHealthCoachDashboard();
                } else {
                    console.warn('⚠️ createHealthCoachDashboard function not found, using fallback');
                    this.createFallbackDashboard('health_coach');
                }
                break;
            case 'patient':
                console.log('🏥 Creating patient dashboard');
                if (typeof createPatientDashboard === 'function') {
                    createPatientDashboard();
                } else {
                    console.warn('⚠️ createPatientDashboard function not found, using fallback');
                    this.createFallbackDashboard('patient');
                }
                break;
            case 'partner':
                console.log('🤝 Creating partner dashboard');
                if (typeof createPartnerDashboard === 'function') {
                    createPartnerDashboard();
                } else {
                    console.warn('⚠️ createPartnerDashboard function not found, using fallback');
                    this.createFallbackDashboard('partner');
                }
                break;
            default:
                console.warn(`⚠️ Unknown role: ${this.userRole}, using patient fallback`);
                this.createFallbackDashboard('patient');
        }
    }

    // Create fallback admin dashboard (if role-specific function fails)
    createFallbackAdminDashboard() {
        const dashboardContainer = document.getElementById('dashboard-modules');
        if (!dashboardContainer) return;

        // Update dashboard header
        const titleElement = document.getElementById('dashboard-title');
        const descElement = document.getElementById('dashboard-description');
        const roleIndicator = document.getElementById('user-role-indicator');

        if (titleElement) titleElement.textContent = 'System Administrator Dashboard';
        if (descElement) descElement.textContent = 'Complete system access and management capabilities';
        if (roleIndicator) {
            roleIndicator.style.backgroundColor = '#dc3545';
            roleIndicator.textContent = 'ADMIN';
        }

        // Admin-specific modules
        const adminModules = ['users', 'appointments', 'messages', 'analytics', 'security', 'settings', 'meals', 'nutrition', 'health', 'admin', 'patients', 'health_records', 'earnings', 'commission'];
        
        // Create module cards based on role
        dashboardContainer.innerHTML = '';
        adminModules.forEach(module => {
            if (this.canAccessModule(module)) {
                const moduleCard = this.createModuleCard(module, '#dc3545');
                dashboardContainer.appendChild(moduleCard);
            }
        });
    }

    // Fallback dashboard for roles without dedicated dashboard functions
    createFallbackDashboard(role) {
        const dashboardContainer = document.getElementById('dashboard-modules');
        if (!dashboardContainer) return;

        const roleConfigs = {
            physician: {
                title: 'Physician Dashboard',
                description: 'Patient care and medical management tools',
                modules: ['appointments', 'health', 'analytics', 'messages', 'meals', 'nutrition', 'patients', 'health_records', 'earnings'],
                primaryColor: '#0d6efd'
            },
            therapist: {
                title: 'Therapist Dashboard',
                description: 'Therapy session and patient progress management',
                modules: ['appointments', 'health', 'messages', 'analytics', 'patients', 'health_records', 'earnings'],
                primaryColor: '#198754'
            },
            health_coach: {
                title: 'Health Coach Dashboard',
                description: 'Wellness coaching and nutrition guidance',
                modules: ['appointments', 'meals', 'nutrition', 'health', 'messages', 'patients', 'health_records', 'earnings'],
                primaryColor: '#fd7e14'
            },
            patient: {
                title: 'Patient Portal',
                description: 'Your personal health and wellness management',
                modules: ['appointments', 'messages', 'meals', 'nutrition', 'health'],
                primaryColor: '#6f42c1'
            },
            partner: {
                title: 'Partner Access',
                description: 'Limited access to wellness information',
                modules: ['health', 'nutrition'],
                primaryColor: '#20c997'
            }
        };

        const config = roleConfigs[role] || roleConfigs.patient;

        // Update dashboard title and description
        const titleElement = document.getElementById('dashboard-title');
        const descElement = document.getElementById('dashboard-description');
        
        if (titleElement) titleElement.textContent = config.title;
        if (descElement) descElement.textContent = config.description;

        // Create module cards based on role
        dashboardContainer.innerHTML = '';
        config.modules.forEach(module => {
            if (this.canAccessModule(module)) {
                const moduleCard = this.createModuleCard(module, config.primaryColor);
                dashboardContainer.appendChild(moduleCard);
            }
        });
    }

    // Create a module card for the dashboard
    createModuleCard(moduleName, primaryColor) {
        const moduleConfigs = {
            users: { icon: '👥', title: 'User Management', description: 'Manage system users and roles' },
            appointments: { icon: '📅', title: 'Appointments', description: 'Schedule and manage appointments' },
            messages: { icon: '💬', title: 'Messages', description: 'Communication and messaging' },
            analytics: { icon: '📊', title: 'Analytics', description: 'Reports and insights' },
            security: { icon: '🔒', title: 'Security', description: 'Security monitoring and audit' },
            settings: { icon: '⚙️', title: 'Settings', description: 'System configuration' },
            meals: { icon: '🍽️', title: 'Meals', description: 'Meal planning and tracking' },
            nutrition: { icon: '🥗', title: 'Nutrition', description: 'Nutritional information and guidance' },
            health: { icon: '🏥', title: 'Health Records', description: 'Medical records and health data' },
            admin: { icon: '🛠️', title: 'System Admin', description: 'Advanced system administration' },
            patients: { icon: '👤', title: 'Patient Management', description: 'Manage patient assignments and profiles' },
            health_records: { icon: '📋', title: 'Health Records', description: 'Patient health records and medical data' },
            earnings: { icon: '💰', title: 'Earnings', description: 'Provider earnings and financial tracking' },
            commission: { icon: '💳', title: 'Commission', description: 'Commission structures and payments' }
        };

        const config = moduleConfigs[moduleName] || { icon: '📦', title: moduleName, description: 'Module access' };

        const card = document.createElement('div');
        card.className = 'col-md-4 col-sm-6 mb-3';
        card.innerHTML = `
            <div class="card h-100 module-card" style="border-left: 4px solid ${primaryColor};" data-module="${moduleName}">
                <div class="card-body d-flex flex-column">
                    <div class="text-center mb-2">
                        <span class="module-icon" style="font-size: 2rem;">${config.icon}</span>
                    </div>
                    <h6 class="card-title text-center">${config.title}</h6>
                    <p class="card-text text-muted small text-center flex-grow-1">${config.description}</p>
                    <button class="btn btn-outline-primary btn-sm" onclick="openModule('${moduleName}')">
                        Access ${config.title}
                    </button>
                </div>
            </div>
        `;

        return card;
    }

    // Apply role-based styling
    applyRoleBasedStyling() {
        const roleColors = {
            admin: '#dc3545',
            physician: '#0d6efd',
            therapist: '#198754',
            health_coach: '#fd7e14',
            patient: '#6f42c1',
            partner: '#20c997'
        };

        const color = roleColors[this.userRole] || '#6c757d';
        
        // Update navbar brand color
        const navbarBrand = document.querySelector('.navbar-brand');
        if (navbarBrand) {
            navbarBrand.style.color = color;
        }

        // Update role indicator
        const roleIndicator = document.getElementById('user-role-indicator');
        if (roleIndicator) {
            roleIndicator.textContent = this.userRole?.toUpperCase() || 'USER';
            roleIndicator.style.backgroundColor = color;
        }
    }

    // Create fallback dashboard for when role-specific dashboards fail
    createFallbackDashboard(role) {
        const dashboardContainer = document.getElementById('dashboard-modules');
        if (!dashboardContainer) return;

        console.log(`🔄 Creating fallback dashboard for role: ${role}`);

        // Clear existing content
        dashboardContainer.innerHTML = '';

        // Only show modules that the user actually has access to
        const allowedModules = this.accessibleModules;
        
        // Role-specific module configurations
        const moduleConfigs = {
            users: { icon: '👥', title: 'User Management', description: 'Manage system users and roles' },
            appointments: { icon: '📅', title: 'Appointments', description: 'Schedule and manage appointments' },
            messages: { icon: '💬', title: 'Messages', description: 'Communication and messaging' },
            analytics: { icon: '📊', title: 'Analytics', description: 'Reports and insights' },
            security: { icon: '🔒', title: 'Security', description: 'Security monitoring and audit' },
            settings: { icon: '⚙️', title: 'Settings', description: 'System configuration' },
            meals: { icon: '🍽️', title: 'Meals', description: 'Meal planning and tracking' },
            nutrition: { icon: '🥗', title: 'Nutrition', description: 'Nutritional information and guidance' },
            health: { icon: '🏥', title: 'Health Records', description: 'Medical records and health data' },
            admin: { icon: '🛠️', title: 'System Admin', description: 'Advanced system administration' }
        };

        // Role-specific colors
        const roleColors = {
            admin: '#dc3545',
            physician: '#0d6efd', 
            therapist: '#198754',
            health_coach: '#fd7e14',
            patient: '#6f42c1',
            partner: '#20c997'
        };

        const primaryColor = roleColors[role] || '#6c757d';

        // Create cards only for accessible modules
        const moduleCards = allowedModules.map(moduleName => {
            const config = moduleConfigs[moduleName] || { icon: '📦', title: moduleName, description: 'Module access' };
            
            return `
                <div class="col-md-4 col-sm-6 mb-3">
                    <div class="card h-100 module-card" style="border-left: 4px solid ${primaryColor};" data-module="${moduleName}">
                        <div class="card-body d-flex flex-column">
                            <div class="text-center mb-2">
                                <span class="module-icon" style="font-size: 2rem;">${config.icon}</span>
                            </div>
                            <h6 class="card-title text-center">${config.title}</h6>
                            <p class="card-text text-muted small text-center flex-grow-1">${config.description}</p>
                            <button class="btn btn-outline-primary btn-sm" onclick="openModule('${moduleName}')" style="border-color: ${primaryColor}; color: ${primaryColor};">
                                Access ${config.title}
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        dashboardContainer.innerHTML = `<div class="row">${moduleCards}</div>`;
        
        console.log(`✅ Fallback dashboard created with ${allowedModules.length} modules for role: ${role}`);
    }

    // Check access before performing actions
    async checkActionPermission(action, target = null) {
        if (!this.isInitialized) {
            await this.initialize();
        }

        const actionPermissions = {
            'create_user': 'users.create',
            'edit_user': 'users.edit',
            'delete_user': 'users.delete',
            'view_all_users': 'users.view',
            'create_appointment': 'appointments.create',
            'view_all_appointments': 'appointments.view_all',
            'edit_appointment': 'appointments.edit_own',
            'view_analytics': 'analytics.view_personal',
            'system_settings': 'settings.edit',
            'security_monitoring': 'security.view_events'
        };

        const requiredPermission = actionPermissions[action];
        if (requiredPermission && !this.hasPermission(requiredPermission)) {
            showNotification('Access denied: Insufficient permissions', 'error');
            return false;
        }

        return true;
    }
}

// Global RBAC Manager instance
const rbacManager = new RBACManager();

// Note: RBAC initialization is now handled by loadUserProfile() after successful login
// This prevents initialization before user authentication

// Function to open module with permission check
async function openModule(moduleName) {
    if (!rbacManager.canAccessModule(moduleName)) {
        showNotification('Access denied: You do not have permission to access this module', 'error');
        return;
    }

    // Module-specific opening logic
    switch (moduleName) {
        case 'users':
            await openUserManagement();
            break;
        case 'appointments':
            await openAppointmentsModule();
            break;
        case 'messages':
            await openMessagingModule();
            break;
        case 'analytics':
            await openAnalyticsModule();
            break;
        case 'security':
            await openSecurityModule();
            break;
        case 'settings':
            await openSystemSettings();
            break;
        case 'meals':
            await openMealsModule();
            break;
        case 'nutrition':
            await openNutrientModule();
            break;
        case 'health':
            await openHealthRecordsModule();
            break;
        case 'admin':
            await openSystemAdministration();
            break;
        default:
            showNotification(`Module ${moduleName} is not yet implemented`, 'info');
    }
}

// Export for global use
window.rbacManager = rbacManager;
window.openModule = openModule;