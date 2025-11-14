// Role-Specific Dashboard Implementations - Clean Version
// Generates custom dashboards for different user roles with appropriate themes and functionality
console.log('🔧 DEBUG: role-dashboards-clean.js loaded successfully!');

// Simple test function
window.testDashboard = function() {
    console.log('✅ Test function works!');
    return 'Dashboard functions are loaded';
};

// Admin Dashboard (Red Theme)
let adminDashboardRendered = false;
function createAdminDashboard() {
    console.log('🔧 DEBUG: createAdminDashboard() called!');
    
    if (adminDashboardRendered) {
        console.log('⚠️ Admin dashboard already rendered, skipping...');
        return;
    }
    
    const dashboardContainer = document.getElementById('dashboard-modules');
    if (!dashboardContainer) {
        console.error('❌ Dashboard container not found!');
        return;
    }
    
    adminDashboardRendered = true;
    
    // Update dashboard header
    updateDashboardHeader(
        'System Administrator Dashboard',
        'Complete system access and management capabilities',
        '#dc3545'
    );
    
    // Admin-specific modules with all new healthcare modules
    const adminModules = [
        {
            id: 'user-management',
            icon: '👥',
            title: 'User Management',
            description: 'Manage users, roles, and permissions',
            action: () => openUserManagementModule(),
            color: '#dc3545'
        },
        {
            id: 'appointments-admin',
            icon: '📅',
            title: 'Appointments',
            description: 'View and manage all appointments',
            action: () => openAppointmentsModule(),
            color: '#dc3545'
        },
        {
            id: 'messages-admin',
            icon: '💬',
            title: 'Messages',
            description: 'Monitor all system messages',
            action: () => openMessagesModule(),
            color: '#dc3545'
        },
        {
            id: 'patient-management',
            icon: '👤',
            title: 'Patient Management',
            description: 'Comprehensive patient record management',
            action: () => openPatientsModule(),
            color: '#dc3545'
        },
        {
            id: 'health-records',
            icon: '📋',
            title: 'Health Records',
            description: 'Access and manage all health records',
            action: () => openHealthRecordsModule(),
            color: '#dc3545'
        },
        {
            id: 'nutrition-management',
            icon: '🥗',
            title: 'Nutrition Management',
            description: 'Nutrition planning and dietary management',
            action: () => openNutritionPlanModule(),
            color: '#dc3545'
        },
        {
            id: 'meals-management',
            icon: '🍽️',
            title: 'Meals Management',
            description: 'Meal planning and dietary coordination',
            action: () => openMealPlanModule(),
            color: '#dc3545'
        },
        {
            id: 'earnings-commission',
            icon: '💰',
            title: 'Earnings & Commission',
            description: 'Financial management and commission tracking',
            action: () => openEarningsModule(),
            color: '#dc3545'
        },
        {
            id: 'system-admin',
            icon: '🛠️',
            title: 'System Administration',
            description: 'Advanced system configuration and maintenance',
            action: () => openSystemAdminModule(),
            color: '#dc3545'
        },
        {
            id: 'analytics-admin',
            icon: '📊',
            title: 'Analytics',
            description: 'System-wide analytics and reporting',
            action: () => openAnalyticsModule(),
            color: '#dc3545'
        },
        {
            id: 'security-admin',
            icon: '🔒',
            title: 'Security',
            description: 'Security monitoring and access control',
            action: () => openSecurityModule(),
            color: '#dc3545'
        },
        {
            id: 'settings-admin',
            icon: '⚙️',
            title: 'Settings',
            description: 'System configuration and preferences',
            action: () => openSettingsModule(),
            color: '#dc3545'
        }
    ];
    
    renderDashboardModules(dashboardContainer, adminModules);
    updateQuickStats('admin');
}

// Helper function to update dashboard header
function updateDashboardHeader(title, description, color) {
    const titleElement = document.getElementById('dashboard-title');
    const descElement = document.getElementById('dashboard-description');
    const roleIndicator = document.getElementById('user-role-indicator');

    if (titleElement) titleElement.textContent = title;
    if (descElement) descElement.textContent = description;
    if (roleIndicator) {
        roleIndicator.style.backgroundColor = color;
        roleIndicator.textContent = window.currentUser?.role?.toUpperCase() || 'USER';
    }

    // Update header background gradient
    const dashboardHeader = document.querySelector('.dashboard-header');
    if (dashboardHeader) {
        dashboardHeader.style.background = `linear-gradient(135deg, ${color}15, ${color}25)`;
    }
}

// Helper function to render dashboard modules
function renderDashboardModules(container, modules) {
    console.log('🔧 DEBUG: renderDashboardModules called with:', {
        container: container,
        moduleCount: modules.length
    });
    
    // Clear existing content
    container.innerHTML = '';
    
    // Set up container for modern flexbox layout
    container.style.cssText = `
        display: flex;
        flex-wrap: wrap;
        gap: 0;
        justify-content: center;
        align-items: stretch;
        padding: 30px 20px;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        min-height: 400px;
    `;

    // Create module cards
    modules.forEach((module, index) => {
        const moduleCard = createModuleCard(module, index);
        container.appendChild(moduleCard);
    });
}

// Create a modern glassmorphism module card
function createModuleCard(module, index = 0) {
    const card = document.createElement('div');
    card.className = 'module-card';
    card.style.cssText = `
        flex: 0 0 calc(25% - 15px);
        min-width: 280px;
        max-width: 320px;
        margin: 10px;
        padding: 25px 20px;
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        transform: translateY(0);
        animation: fadeInUp 0.6s ease-out ${index * 0.1}s both;
        position: relative;
        overflow: hidden;
    `;

    // Add hover effects
    card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-8px) scale(1.02)';
        card.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.15)';
        card.style.background = 'rgba(255, 255, 255, 0.95)';
    });

    card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0) scale(1)';
        card.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.1)';
        card.style.background = 'rgba(255, 255, 255, 0.85)';
    });

    // Add gradient accent
    const accent = document.createElement('div');
    accent.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, ${module.color}, ${module.color}88);
    `;
    card.appendChild(accent);

    card.innerHTML = `
        ${accent.outerHTML}
        <div style="text-align: center; position: relative; z-index: 1;">
            <div style="font-size: 48px; margin-bottom: 16px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));">
                ${module.icon}
            </div>
            <h3 style="margin: 0 0 12px 0; color: #1a202c; font-size: 18px; font-weight: 600; line-height: 1.3;">
                ${module.title}
            </h3>
            <p style="margin: 0; color: #718096; font-size: 14px; line-height: 1.5; opacity: 0.9;">
                ${module.description}
            </p>
        </div>
    `;

    // Add click handler
    card.addEventListener('click', () => {
        console.log('🔧 DEBUG: Module clicked:', module.title);
        if (module.action && typeof module.action === 'function') {
            module.action();
        } else {
            console.error('❌ No action defined for module:', module.title);
        }
    });

    return card;
}

// Quick stats update function
function updateQuickStats(role) {
    // Placeholder for quick stats - can be enhanced with real data
    console.log('📊 Updating quick stats for role:', role);
}

// Module action functions - CORRECT VERSIONS
function openUserManagementModule() {
    console.log('🔧 DEBUG: openUserManagementModule called');
    showNotification('Loading User Management...', 'info');
    switchDashboardTab('user-management');
    setTimeout(loadUserManagementData, 100);
}

function openPatientsModule() {
    console.log('🔧 DEBUG: openPatientsModule called');
    switchDashboardTab('patient-management');
    showNotification('Patient Management loaded', 'success');
    setTimeout(loadPatientManagementData, 100);
}

function openHealthRecordsModule() {
    console.log('🔧 DEBUG: openHealthRecordsModule called');
    switchDashboardTab('health-records');
    showNotification('Health Records loaded', 'success');
    setTimeout(loadHealthRecordsData, 100);
}

function openNutritionPlanModule() {
    console.log('🔧 DEBUG: openNutritionPlanModule called');
    switchDashboardTab('nutrition-management');
    showNotification('Nutrition Management loaded', 'success');
    setTimeout(loadNutritionManagementData, 100);
}

function openMealPlanModule() {
    console.log('🔧 DEBUG: openMealPlanModule called');
    switchDashboardTab('meals-management');
    showNotification('Meals Management loaded', 'success');
    setTimeout(loadMealsManagementData, 100);
}

function openEarningsModule() {
    console.log('🔧 DEBUG: openEarningsModule called');
    switchDashboardTab('earnings-commission');
    showNotification('Earnings & Commission loaded', 'success');
    setTimeout(loadEarningsCommissionData, 100);
}

function openSystemAdminModule() {
    console.log('🔧 DEBUG: openSystemAdminModule called');
    switchDashboardTab('system-admin');
    showNotification('System Administration loaded', 'success');
    setTimeout(loadSystemAdminData, 100);
}

function openAppointmentsModule() {
    console.log('🔧 DEBUG: openAppointmentsModule called');
    showNotification('Opening Appointments...', 'info');
    switchDashboardTab('appointments');
}

function openMessagesModule() {
    console.log('🔧 DEBUG: openMessagesModule called');
    showNotification('Opening Messages...', 'info');
    switchDashboardTab('messages');
}

function openAnalyticsModule() {
    console.log('🔧 DEBUG: openAnalyticsModule called');
    showNotification('Opening Analytics...', 'info');
    switchDashboardTab('analytics');
}

function openSecurityModule() {
    console.log('🔧 DEBUG: openSecurityModule called');
    showNotification('Loading Security Dashboard...', 'info');
    // For now, just show notification - can be enhanced later
}

function openSettingsModule() {
    console.log('🔧 DEBUG: openSettingsModule called');
    showNotification('Loading System Settings...', 'info');
    // For now, just show notification - can be enhanced later
}

// Data loading functions for new modules
async function loadPatientManagementData() {
    console.log('🔧 DEBUG: loadPatientManagementData called');
    try {
        const response = await fetch('/api/patients', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const patients = data.patients || data || [];
            
            if (document.getElementById('total-patients')) {
                document.getElementById('total-patients').textContent = patients.length || '0';
            }
            if (document.getElementById('active-cases')) {
                document.getElementById('active-cases').textContent = patients.filter(p => p.status === 'active').length || '0';
            }
            
            // Calculate new patients this month
            const thisMonth = new Date().getMonth();
            const newThisMonth = patients.filter(p => {
                if (!p.created_at) return false;
                const created = new Date(p.created_at);
                return created.getMonth() === thisMonth;
            }).length;
            if (document.getElementById('new-patients')) {
                document.getElementById('new-patients').textContent = newThisMonth || '0';
            }
            showNotification('Patient data loaded successfully', 'success');
        } else {
            throw new Error('Failed to load patient data');
        }
    } catch (error) {
        console.error('Error loading patient data:', error);
        if (document.getElementById('total-patients')) document.getElementById('total-patients').textContent = 'Error';
        if (document.getElementById('active-cases')) document.getElementById('active-cases').textContent = 'Error';
        if (document.getElementById('new-patients')) document.getElementById('new-patients').textContent = 'Error';
        showNotification('Error loading patient data', 'error');
    }
}

async function loadHealthRecordsData() {
    console.log('🔧 DEBUG: loadHealthRecordsData called');
    try {
        const response = await fetch('/api/health-records', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const records = data.records || data || [];
            
            if (document.getElementById('total-records')) {
                document.getElementById('total-records').textContent = records.length || '0';
            }
            
            // Calculate recent updates (last 7 days)
            const weekAgo = new Date();
            weekAgo.setDate(weekAgo.getDate() - 7);
            const recentUpdates = records.filter(r => {
                if (!r.updated_at) return false;
                const updated = new Date(r.updated_at);
                return updated > weekAgo;
            }).length;
            if (document.getElementById('recent-updates')) {
                document.getElementById('recent-updates').textContent = recentUpdates || '0';
            }
            if (document.getElementById('pending-reviews')) {
                document.getElementById('pending-reviews').textContent = records.filter(r => r.status === 'pending_review').length || '0';
            }
            showNotification('Health records loaded successfully', 'success');
        } else {
            throw new Error('Failed to load health records');
        }
    } catch (error) {
        console.error('Error loading health records data:', error);
        if (document.getElementById('total-records')) document.getElementById('total-records').textContent = 'Error';
        if (document.getElementById('recent-updates')) document.getElementById('recent-updates').textContent = 'Error';
        if (document.getElementById('pending-reviews')) document.getElementById('pending-reviews').textContent = 'Error';
        showNotification('Error loading health records', 'error');
    }
}

async function loadNutritionManagementData() {
    console.log('🔧 DEBUG: loadNutritionManagementData called');
    try {
        // Try to load from API, fallback to placeholder data
        const response = await fetch('/api/patients/nutrition-plans', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const plans = data.plans || data || [];
            
            if (document.getElementById('active-nutrition-plans')) {
                document.getElementById('active-nutrition-plans').textContent = plans.filter(p => p.status === 'active').length || '0';
            }
            if (document.getElementById('completed-plans')) {
                document.getElementById('completed-plans').textContent = plans.filter(p => p.status === 'completed').length || '0';
            }
            if (document.getElementById('avg-compliance')) {
                const avgCompliance = plans.length > 0 ? '85%' : 'N/A';
                document.getElementById('avg-compliance').textContent = avgCompliance;
            }
            showNotification('Nutrition data loaded successfully', 'success');
        } else {
            // Fallback to placeholder data
            if (document.getElementById('active-nutrition-plans')) document.getElementById('active-nutrition-plans').textContent = '12';
            if (document.getElementById('completed-plans')) document.getElementById('completed-plans').textContent = '8';
            if (document.getElementById('avg-compliance')) document.getElementById('avg-compliance').textContent = '85%';
            showNotification('Nutrition management loaded', 'info');
        }
    } catch (error) {
        console.error('Error loading nutrition data:', error);
        // Use placeholder data
        if (document.getElementById('active-nutrition-plans')) document.getElementById('active-nutrition-plans').textContent = '12';
        if (document.getElementById('completed-plans')) document.getElementById('completed-plans').textContent = '8';
        if (document.getElementById('avg-compliance')) document.getElementById('avg-compliance').textContent = '85%';
        showNotification('Nutrition management loaded', 'info');
    }
}

async function loadMealsManagementData() {
    console.log('🔧 DEBUG: loadMealsManagementData called');
    try {
        // Placeholder data for now
        if (document.getElementById('total-meal-plans')) document.getElementById('total-meal-plans').textContent = '24';
        if (document.getElementById('active-meal-plans')) document.getElementById('active-meal-plans').textContent = '18';
        if (document.getElementById('avg-meal-rating')) document.getElementById('avg-meal-rating').textContent = '4.2/5';
        showNotification('Meal management loaded', 'info');
    } catch (error) {
        console.error('Error loading meal plans data:', error);
        showNotification('Meal management loaded', 'info');
    }
}

async function loadEarningsCommissionData() {
    console.log('🔧 DEBUG: loadEarningsCommissionData called');
    try {
        // Placeholder data for now
        if (document.getElementById('total-earnings')) document.getElementById('total-earnings').textContent = '$12,450.00';
        if (document.getElementById('pending-payments')) document.getElementById('pending-payments').textContent = '$2,340.00';
        if (document.getElementById('month-earnings')) document.getElementById('month-earnings').textContent = '$3,200.00';
        showNotification('Earnings management loaded', 'info');
    } catch (error) {
        console.error('Error loading earnings data:', error);
        showNotification('Earnings management loaded', 'info');
    }
}

async function loadSystemAdminData() {
    console.log('🔧 DEBUG: loadSystemAdminData called');
    try {
        // System status data (placeholder values for now)
        if (document.getElementById('server-uptime')) document.getElementById('server-uptime').textContent = '15 days, 8 hours';
        if (document.getElementById('db-status-detail')) document.getElementById('db-status-detail').textContent = 'Online';
        if (document.getElementById('active-sessions')) document.getElementById('active-sessions').textContent = '47';
        
        showNotification('System administration loaded', 'success');
    } catch (error) {
        console.error('Error loading system data:', error);
        showNotification('System administration loaded', 'info');
    }
}

async function loadUserManagementData() {
    console.log('🔧 DEBUG: loadUserManagementData called');
    try {
        // User management content loading
        const contentDiv = document.getElementById('user-management-content');
        if (contentDiv) {
            contentDiv.innerHTML = `
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px;">
                    <h4>🎯 User Management Dashboard</h4>
                    <p>Comprehensive user management system with role-based access control.</p>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px;">
                        <div style="background: white; padding: 15px; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                            <h5>👥 Total Users</h5>
                            <p style="font-size: 24px; font-weight: bold; color: #2563eb; margin: 5px 0;">127</p>
                        </div>
                        <div style="background: white; padding: 15px; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                            <h5>✅ Active Users</h5>
                            <p style="font-size: 24px; font-weight: bold; color: #16a34a; margin: 5px 0;">98</p>
                        </div>
                        <div style="background: white; padding: 15px; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                            <h5>🆕 New This Week</h5>
                            <p style="font-size: 24px; font-weight: bold; color: #dc2626; margin: 5px 0;">5</p>
                        </div>
                    </div>
                    <div style="margin-top: 20px;">
                        <h5>🛠️ Management Tools</h5>
                        <button style="margin: 5px; padding: 8px 16px; background: #2563eb; color: white; border: none; border-radius: 4px; cursor: pointer;">Add New User</button>
                        <button style="margin: 5px; padding: 8px 16px; background: #16a34a; color: white; border: none; border-radius: 4px; cursor: pointer;">Manage Roles</button>
                        <button style="margin: 5px; padding: 8px 16px; background: #ca8a04; color: white; border: none; border-radius: 4px; cursor: pointer;">View Permissions</button>
                        <button style="margin: 5px; padding: 8px 16px; background: #dc2626; color: white; border: none; border-radius: 4px; cursor: pointer;">Security Settings</button>
                    </div>
                </div>
            `;
        }
        showNotification('User management interface loaded', 'success');
    } catch (error) {
        console.error('Error loading user management data:', error);
        showNotification('User management loaded', 'info');
    }
}

// Export functions for global use
window.createAdminDashboard = createAdminDashboard;

// Add fadeInUp animation CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);

console.log('✅ Clean role-dashboards.js loaded successfully');