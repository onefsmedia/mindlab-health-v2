// Role-Specific Dashboard Implementations
// Generates custom dashboards for different user roles with appropriate themes and functionality
// TEST: Updated October 18, 2025 - v42

console.log('🔧 DEBUG: role-dashboards.js loaded successfully!');

// Simple test function
window.testDashboard = function() {
    console.log('✅ Test function works!');
    return 'Dashboard functions are loaded';
};

// Test function to verify file loading
window.testDashboardLoading = function() {
    console.log('✅ Dashboard functions are available!');
    return 'role-dashboards.js loaded';
};

// Admin Dashboard (Red Theme)
let adminDashboardRendered = false;
function createAdminDashboard() {
    console.log('🔧 DEBUG: createAdminDashboard() called!');
    
    // Prevent duplicate calls
    if (adminDashboardRendered) {
        console.log('⚠️ Admin dashboard already rendered, skipping...');
        return;
    }
    
    console.log('🔧 DEBUG: DOM ready state:', document.readyState);
    
    const dashboardContainer = document.getElementById('dashboard-modules');
    if (!dashboardContainer) {
        console.error('❌ Dashboard container not found!');
        console.log('🔧 DEBUG: Available elements:', document.querySelectorAll('[id*="dashboard"]'));
        return;
    }

    console.log('📱 Dashboard container found:', dashboardContainer);
    console.log('🔧 DEBUG: Creating admin dashboard with all modules...');
    
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
            action: () => openUsersModule(),
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
            action: () => openMessagingModule(),
            color: '#dc3545'
        },
        {
            id: 'analytics-admin',
            icon: '📊',
            title: 'Analytics',
            description: 'View system analytics and reports',
            action: () => openAnalyticsModule(),
            color: '#dc3545'
        },
        {
            id: 'security-admin',
            icon: '🔒',
            title: 'Security',
            description: 'View security logs and audit trails',
            action: () => openSecurityModule(),
            color: '#dc3545'
        },
        {
            id: 'settings-admin',
            icon: '⚙️',
            title: 'Settings',
            description: 'Configure system settings',
            action: () => openSettingsModule(),
            color: '#dc3545'
        },
        {
            id: 'patients-admin',
            icon: '👤',
            title: 'Patient Management',
            description: 'Manage all patients and assignments',
            action: () => openPatientsModule(),
            color: '#dc3545'
        },
        {
            id: 'health-records-admin',
            icon: '📋',
            title: 'Health Records',
            description: 'Access all patient health records',
            action: () => openHealthRecordsModule(),
            color: '#dc3545'
        },
        {
            id: 'nutrition-admin',
            icon: '🥗',
            title: 'Nutrition Management',
            description: 'Monitor nutritional data and plans',
            action: () => openNutritionPlanModule(),
            color: '#dc3545'
        },
        {
            id: 'meals-admin',
            icon: '🍽️',
            title: 'Meals Management',
            description: 'Manage meal plans and dietary recommendations',
            action: () => openMealPlanModule(),
            color: '#dc3545'
        },
        {
            id: 'earnings-admin',
            icon: '💰',
            title: 'Earnings & Commission',
            description: 'Manage provider earnings and commission structures',
            action: () => openEarningsModule(),
            color: '#dc3545'
        },
        {
            id: 'system-admin',
            icon: '🛠️',
            title: 'System Admin',
            description: 'Advanced system administration',
            action: () => openSystemAdminModule(),
            color: '#dc3545'
        }
    ];

    console.log('🔧 DEBUG: Admin modules array created with', adminModules.length, 'modules');
    console.log('🔧 DEBUG: Module titles:', adminModules.map(m => m.title));

    renderDashboardModules(dashboardContainer, adminModules);
    console.log('✅ Admin dashboard modules rendered!');
    updateQuickStats('admin');
}

// Reset admin dashboard flag when switching roles
window.resetDashboardFlags = function() {
    adminDashboardRendered = false;
    physicianDashboardRendered = false;
    therapistDashboardRendered = false;
    healthCoachDashboardRendered = false;
    patientDashboardRendered = false;
    partnerDashboardRendered = false;
};

// Physician Dashboard (Blue Theme)
let physicianDashboardRendered = false;
function createPhysicianDashboard() {
    if (physicianDashboardRendered) {
        console.log('⚠️ Physician dashboard already rendered, skipping...');
        return;
    }
    physicianDashboardRendered = true;
    const dashboardContainer = document.getElementById('dashboard-modules');
    if (!dashboardContainer) return;

    // Update dashboard header
    updateDashboardHeader(
        'Physician Dashboard',
        'Patient care and medical management tools',
        '#0d6efd'
    );

    // Physician-specific modules
    const physicianModules = [
        {
            id: 'my-patients',
            icon: '👥',
            title: 'My Patients',
            description: 'View and manage assigned patients',
            action: () => openPatientsModule(),
            color: '#0d6efd'
        },
        {
            id: 'patient-appointments',
            icon: '📅',
            title: 'Patient Appointments',
            description: 'View and manage all patient appointments',
            action: () => openAppointmentsModule(),
            color: '#0d6efd'
        },
        {
            id: 'health-records',
            icon: '🏥',
            title: 'Health Records',
            description: 'Access and create patient health records',
            action: () => openHealthRecordsModule(),
            color: '#0d6efd'
        },
        {
            id: 'medical-analytics',
            icon: '📊',
            title: 'Medical Analytics',
            description: 'View patient outcomes and medical statistics',
            action: () => openAnalyticsModule(),
            color: '#0d6efd'
        },
        {
            id: 'patient-communication',
            icon: '💬',
            title: 'Patient Messages',
            description: 'Communicate with patients and care team',
            action: () => openMessagingModule(),
            color: '#0d6efd'
        },
        {
            id: 'nutrition-management',
            icon: '🥗',
            title: 'Nutrition Plans',
            description: 'Create and manage patient nutrition plans',
            action: () => openNutritionPlanModule(),
            color: '#0d6efd'
        },
        {
            id: 'meal-planning',
            icon: '🍽️',
            title: 'Meal Planning',
            description: 'Design and track patient meal plans',
            action: () => openMealPlanModule(),
            color: '#0d6efd'
        },
        {
            id: 'earnings-tracking',
            icon: '💰',
            title: 'Earnings & Commission',
            description: 'Track earnings and commission statements',
            action: () => openEarningsModule(),
            color: '#0d6efd'
        }
    ];

    renderDashboardModules(dashboardContainer, physicianModules);
    updateQuickStats('physician');
}

// Therapist Dashboard (Green Theme)
let therapistDashboardRendered = false;
function createTherapistDashboard() {
    if (therapistDashboardRendered) {
        console.log('⚠️ Therapist dashboard already rendered, skipping...');
        return;
    }
    therapistDashboardRendered = true;
    
    console.log('🔧 DEBUG: createTherapistDashboard() called!');
    const dashboardContainer = document.getElementById('dashboard-modules');
    if (!dashboardContainer) {
        console.error('❌ Dashboard container not found!');
        return;
    }

    console.log('📱 Dashboard container found:', dashboardContainer);

    // Update dashboard header
    updateDashboardHeader(
        'Therapist Dashboard',
        'Therapy session and patient progress management',
        '#198754'
    );

    // Therapist-specific modules
    const therapistModules = [
        {
            id: 'my-patients',
            icon: '👥',
            title: 'My Patients',
            description: 'View and manage assigned patients',
            action: () => openPatientsModule(),
            color: '#198754'
        },
        {
            id: 'therapy-sessions',
            icon: '🗣️',
            title: 'Therapy Sessions',
            description: 'Schedule and manage therapy appointments',
            action: () => openAppointmentsModule(),
            color: '#198754'
        },
        {
            id: 'health-records',
            icon: '🏥',
            title: 'Health Records',
            description: 'Access and create patient health records',
            action: () => openHealthRecordsModule(),
            color: '#198754'
        },
        {
            id: 'patient-progress',
            icon: '📈',
            title: 'Patient Progress',
            description: 'Track patient mental health progress',
            action: () => openAnalyticsModule(),
            color: '#198754'
        },
        {
            id: 'session-notes',
            icon: '📝',
            title: 'Session Notes',
            description: 'Document therapy sessions and observations',
            action: () => openHealthRecordsModule(),
            color: '#198754'
        },
        {
            id: 'nutrition-planning',
            icon: '🥗',
            title: 'Nutrition Plans',
            description: 'Create and manage patient nutrition plans',
            action: () => openNutritionPlanModule(),
            color: '#198754'
        },
        {
            id: 'meal-planning',
            icon: '🍽️',
            title: 'Meal Planning',
            description: 'Design therapy-specific meal plans',
            action: () => openMealPlanModule(),
            color: '#198754'
        },
        {
            id: 'earnings-tracking',
            icon: '💰',
            title: 'Earnings & Commission',
            description: 'Track earnings and commission statements',
            action: () => openEarningsModule(),
            color: '#198754'
        }
    ];

    renderDashboardModules(dashboardContainer, therapistModules);
    console.log('✅ Therapist modules rendered:', therapistModules.length);
    updateQuickStats('therapist');
}

// Health Coach Dashboard (Orange Theme)
let healthCoachDashboardRendered = false;
function createHealthCoachDashboard() {
    if (healthCoachDashboardRendered) {
        console.log('⚠️ Health Coach dashboard already rendered, skipping...');
        return;
    }
    healthCoachDashboardRendered = true;
    
    const dashboardContainer = document.getElementById('dashboard-modules');
    if (!dashboardContainer) return;

    // Update dashboard header
    updateDashboardHeader(
        'Health Coach Dashboard',
        'Wellness coaching and nutrition guidance',
        '#fd7e14'
    );

    // Health Coach-specific modules
    const healthCoachModules = [
        {
            id: 'my-patients',
            icon: '👥',
            title: 'My Patients',
            description: 'View and manage assigned patients',
            action: () => openPatientsModule(),
            color: '#fd7e14'
        },
        {
            id: 'coaching-sessions',
            icon: '🎯',
            title: 'Coaching Sessions',
            description: 'Schedule wellness coaching appointments',
            action: () => openAppointmentsModule(),
            color: '#fd7e14'
        },
        {
            id: 'health-records',
            icon: '🏥',
            title: 'Health Records',
            description: 'Access and create patient health records',
            action: () => openHealthRecordsModule(),
            color: '#fd7e14'
        },
        {
            id: 'nutrition-planning',
            icon: '🥗',
            title: 'Nutrition Planning',
            description: 'Create personalized nutrition plans',
            action: () => openNutritionPlanModule(),
            color: '#fd7e14'
        },
        {
            id: 'meal-management',
            icon: '🍽️',
            title: 'Meal Management',
            description: 'Track and manage client meal plans',
            action: () => openMealPlanModule(),
            color: '#fd7e14'
        },
        {
            id: 'wellness-goals',
            icon: '🏆',
            title: 'Wellness Goals',
            description: 'Set and track client wellness objectives',
            action: () => openHealthRecordsModule(),
            color: '#fd7e14'
        },
        {
            id: 'client-messages',
            icon: '💬',
            title: 'Client Messages',
            description: 'Motivational support and communication',
            action: () => openMessagingModule(),
            color: '#fd7e14'
        },
        {
            id: 'earnings-tracking',
            icon: '�',
            title: 'Earnings & Commission',
            description: 'Track earnings and commission statements',
            action: () => openEarningsModule(),
            color: '#fd7e14'
        }
    ];

    renderDashboardModules(dashboardContainer, healthCoachModules);
    updateQuickStats('health_coach');
}

// Patient Dashboard (Purple Theme)
let patientDashboardRendered = false;
function createPatientDashboard() {
    if (patientDashboardRendered) {
        console.log('⚠️ Patient dashboard already rendered, skipping...');
        return;
    }
    patientDashboardRendered = true;
    
    const dashboardContainer = document.getElementById('dashboard-modules');
    if (!dashboardContainer) return;

    // Update dashboard header
    updateDashboardHeader(
        'Patient Portal',
        'Your personal health and wellness management',
        '#6f42c1'
    );

    // Patient-specific modules
    const patientModules = [
        {
            id: 'my-appointments',
            icon: '📅',
            title: 'My Appointments',
            description: 'View and manage your appointments',
            action: () => openAppointmentsModule(),
            color: '#6f42c1'
        },
        {
            id: 'health-records',
            icon: '📋',
            title: 'My Health Records',
            description: 'Access your personal health information',
            action: () => openHealthRecordsModule(),
            color: '#6f42c1'
        },
        {
            id: 'meal-tracking',
            icon: '🍽️',
            title: 'Meal Tracking',
            description: 'Log and track your daily meals',
            action: () => openMealsModule(),
            color: '#6f42c1'
        },
        {
            id: 'nutrition-info',
            icon: '🥗',
            title: 'Nutrition Guide',
            description: 'Access nutritional information and tips',
            action: () => openNutrientModule(),
            color: '#6f42c1'
        },
        {
            id: 'messages',
            icon: '💬',
            title: 'Messages',
            description: 'Communicate with your care team',
            action: () => openMessagingModule(),
            color: '#6f42c1'
        },
        {
            id: 'progress-tracking',
            icon: '📈',
            title: 'My Progress',
            description: 'Track your health and wellness progress',
            action: () => openAnalyticsModule(),
            color: '#6f42c1'
        }
    ];

    renderDashboardModules(dashboardContainer, patientModules);
    updateQuickStats('patient');
}

// Partner Dashboard (Teal Theme)
let partnerDashboardRendered = false;
function createPartnerDashboard() {
    if (partnerDashboardRendered) {
        console.log('⚠️ Partner dashboard already rendered, skipping...');
        return;
    }
    partnerDashboardRendered = true;
    
    const dashboardContainer = document.getElementById('dashboard-modules');
    if (!dashboardContainer) return;

    // Update dashboard header
    updateDashboardHeader(
        'Partner Access Portal',
        'Limited access to wellness information',
        '#20c997'
    );

    // Partner-specific modules (limited access)
    const partnerModules = [
        {
            id: 'wellness-overview',
            icon: '🌿',
            title: 'Wellness Overview',
            description: 'View general wellness information',
            action: () => openHealthRecordsModule(),
            color: '#20c997'
        },
        {
            id: 'nutrition-basics',
            icon: '🥗',
            title: 'Nutrition Basics',
            description: 'Access basic nutritional information',
            action: () => openNutrientModule(),
            color: '#20c997'
        },
        {
            id: 'wellness-resources',
            icon: '📚',
            title: 'Wellness Resources',
            description: 'Educational health and wellness materials',
            action: () => showNotification('Wellness resources coming soon', 'info'),
            color: '#20c997'
        },
        {
            id: 'support-info',
            icon: '🤝',
            title: 'Support Information',
            description: 'Information about supporting wellness',
            action: () => showNotification('Support information coming soon', 'info'),
            color: '#20c997'
        }
    ];

    renderDashboardModules(dashboardContainer, partnerModules);
    updateQuickStats('partner');
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
        roleIndicator.textContent = currentUser?.role?.toUpperCase() || 'USER';
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
        containerStyle: container.style.display,
        containerVisible: container.offsetParent !== null,
        moduleCount: modules.length,
        containerHTML: container.innerHTML.substring(0, 200) // First 200 chars of current content
    });
    
    // Clear existing content
    console.log('🔧 DEBUG: Clearing container content...');
    container.innerHTML = '';
    console.log('🔧 DEBUG: Container cleared, new innerHTML length:', container.innerHTML.length);
    
    // Set up container for modern flexbox layout
    container.style.cssText = `
        display: flex;
        flex-wrap: wrap;
        gap: 0;
        justify-content: center;
        align-items: stretch;
        padding: 30px 20px;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 16px;
        margin: 20px 0;
        min-height: 300px;
    `;
    
    modules.forEach((module, index) => {
        console.log(`🔧 DEBUG: Creating module ${index + 1}:`, module.title);
        const moduleCard = createModuleCard(module);
        console.log(`🔧 DEBUG: Module card created:`, moduleCard.outerHTML.substring(0, 150));
        container.appendChild(moduleCard);
        console.log(`🔧 DEBUG: Module ${index + 1} appended to container`);
    });
    
    console.log('🔧 DEBUG: Final container HTML length:', container.innerHTML.length);
    console.log('🔧 DEBUG: Container children count:', container.children.length);
    
    // Check if container is visible
    const containerRect = container.getBoundingClientRect();
    console.log('🔧 DEBUG: Container dimensions:', {
        width: containerRect.width,
        height: containerRect.height,
        top: containerRect.top,
        left: containerRect.left
    });
    
    // Add explicit test to see if modules are actually visible
    console.log('🔧 DEBUG: First module visibility test:');
    if (container.children.length > 0) {
        const firstModule = container.children[0];
        const firstModuleRect = firstModule.getBoundingClientRect();
        console.log('🔧 DEBUG: First module dimensions:', {
            width: firstModuleRect.width,
            height: firstModuleRect.height,
            display: window.getComputedStyle(firstModule).display,
            visibility: window.getComputedStyle(firstModule).visibility
        });
    }
}

// Enhanced modern module card creation
function createModuleCard(module) {
    const card = document.createElement('div');
    
    // Modern glassmorphism-inspired design
    card.style.cssText = `
        flex: 0 0 auto;
        width: 300px;
        height: 260px;
        margin: 12px;
        background: linear-gradient(145deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transition: all 0.4s cubic-bezier(0.23, 1, 0.320, 1);
        cursor: pointer;
        padding: 0;
        text-align: center;
        display: flex;
        flex-direction: column;
        position: relative;
        overflow: hidden;
    `;
    
    card.className = 'module-card';
    card.setAttribute('data-module', module.id);
    
    // Add dynamic hover effects
    card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-12px) scale(1.02)';
        card.style.boxShadow = `0 20px 60px rgba(0,0,0,0.2), 0 0 0 1px ${module.color}40`;
        const icon = card.querySelector('.module-icon');
        if (icon) {
            icon.style.transform = 'scale(1.1) rotate(5deg)';
        }
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0) scale(1)';
        card.style.boxShadow = '0 8px 32px rgba(0,0,0,0.1)';
        const icon = card.querySelector('.module-icon');
        if (icon) {
            icon.style.transform = 'scale(1) rotate(0deg)';
        }
    });
    
    // Create gradient overlay for visual depth
    const gradientOverlay = `linear-gradient(145deg, ${module.color}15, ${module.color}05)`;
    
    card.innerHTML = `
        <!-- Top colored accent -->
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, ${module.color}, ${module.color}cc);
        "></div>
        
        <!-- Content Container -->
        <div style="
            flex: 1;
            padding: 30px 25px 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            background: ${gradientOverlay};
        ">
            <!-- Icon and Title Section -->
            <div>
                <div style="margin-bottom: 16px;">
                    <span class="module-icon" style="
                        font-size: 3.5rem;
                        color: ${module.color};
                        display: block;
                        transition: all 0.4s cubic-bezier(0.23, 1, 0.320, 1);
                        text-shadow: 0 4px 12px ${module.color}30;
                        filter: drop-shadow(0 2px 4px ${module.color}20);
                    ">${module.icon}</span>
                </div>
                
                <h3 style="
                    color: #2c3e50;
                    font-weight: 700;
                    margin-bottom: 12px;
                    font-size: 18px;
                    line-height: 1.3;
                    text-shadow: 0 1px 2px rgba(0,0,0,0.1);
                ">${module.title}</h3>
                
                <p style="
                    color: #64748b;
                    font-size: 13px;
                    line-height: 1.5;
                    margin: 0;
                    font-weight: 400;
                ">${module.description}</p>
            </div>
            
            <!-- Action Button -->
            <button class="module-btn" style="
                padding: 12px 24px;
                background: linear-gradient(135deg, ${module.color}, ${module.color}dd);
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
                transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1);
                box-shadow: 0 4px 15px ${module.color}40;
                position: relative;
                overflow: hidden;
            " 
            onmouseenter="
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 8px 25px ${module.color}50';
                this.style.background = 'linear-gradient(135deg, ${module.color}ee, ${module.color})';
            "
            onmouseleave="
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '0 4px 15px ${module.color}40';
                this.style.background = 'linear-gradient(135deg, ${module.color}, ${module.color}dd)';
            "
            onclick="(${module.action})()">
                <span style="position: relative; z-index: 2;">Launch ${module.title.split(' ')[0]}</span>
            </button>
        </div>
    `;
    
    return card;
}

// Update quick stats based on role
function updateQuickStats(role) {
    const statsGrid = document.getElementById('dashboard-stats');
    if (!statsGrid) return;

    // Role-specific stats
    const roleStats = {
        physician: [
            { title: 'Today\'s Patients', id: 'todays-patients', icon: '👥' },
            { title: 'Pending Reviews', id: 'pending-reviews', icon: '📋' },
            { title: 'Critical Alerts', id: 'critical-alerts', icon: '🚨' },
            { title: 'This Week\'s Appointments', id: 'week-appointments', icon: '📅' }
        ],
        therapist: [
            { title: 'Today\'s Sessions', id: 'todays-sessions', icon: '🗣️' },
            { title: 'Active Clients', id: 'active-clients', icon: '👥' },
            { title: 'Session Notes Due', id: 'notes-due', icon: '📝' },
            { title: 'Next Session', id: 'next-session', icon: '⏰' }
        ],
        health_coach: [
            { title: 'Active Clients', id: 'coaching-clients', icon: '🎯' },
            { title: 'Meal Plans Created', id: 'meal-plans', icon: '🍽️' },
            { title: 'Goals Achieved', id: 'goals-achieved', icon: '🏆' },
            { title: 'Next Check-in', id: 'next-checkin', icon: '📅' }
        ],
        patient: [
            { title: 'Next Appointment', id: 'next-appointment', icon: '📅' },
            { title: 'Meals Logged Today', id: 'meals-today', icon: '🍽️' },
            { title: 'Unread Messages', id: 'unread-messages', icon: '💬' },
            { title: 'Progress This Week', id: 'week-progress', icon: '📈' }
        ],
        partner: [
            { title: 'Wellness Tips', id: 'wellness-tips', icon: '💡' },
            { title: 'Resources Available', id: 'resources-count', icon: '📚' },
            { title: 'Support Articles', id: 'support-articles', icon: '📄' },
            { title: 'Community Updates', id: 'community-updates', icon: '🌟' }
        ]
    };

    const stats = roleStats[role] || [];
    
    // Clear existing stats
    statsGrid.innerHTML = '';
    
    // Add role-specific stats
    stats.forEach(stat => {
        const statCard = document.createElement('div');
        statCard.className = 'stat-card';
        statCard.innerHTML = `
            <h3>${stat.icon} ${stat.title}</h3>
            <div class="stat-value" id="${stat.id}">Loading...</div>
        `;
        statsGrid.appendChild(statCard);
    });

    // Load actual stat values
    loadRoleSpecificStats(role);
}

// Load role-specific statistics
async function loadRoleSpecificStats(role) {
    try {
        // This would typically fetch from various APIs based on role
        // For now, we'll show placeholder values
        
        const mockStats = {
            physician: {
                'todays-patients': '12',
                'pending-reviews': '3',
                'critical-alerts': '1',
                'week-appointments': '48'
            },
            therapist: {
                'todays-sessions': '6',
                'active-clients': '24',
                'notes-due': '2',
                'next-session': '2:00 PM'
            },
            health_coach: {
                'coaching-clients': '18',
                'meal-plans': '5',
                'goals-achieved': '12',
                'next-checkin': 'Tomorrow'
            },
            patient: {
                'next-appointment': 'Oct 20, 2:00 PM',
                'meals-today': '2/3',
                'unread-messages': '1',
                'week-progress': '85%'
            },
            partner: {
                'wellness-tips': '15',
                'resources-count': '42',
                'support-articles': '8',
                'community-updates': '3'
            }
        };

        const stats = mockStats[role] || {};
        
        // Update stat values
        Object.entries(stats).forEach(([key, value]) => {
            const element = document.getElementById(key);
            if (element) {
                element.textContent = value;
            }
        });
        
    } catch (error) {
        console.error('Error loading role-specific stats:', error);
    }
}

// Old duplicate functions removed - using the correct ones defined later in the file

// Duplicate function removed - using correct version later in file

function openAdminEarningsManagement() {
    showNotification('Loading earnings management...', 'info');
    
    // Create admin earnings management interface
    const modal = document.createElement('div');
    modal.className = 'modal fade show';
    modal.style.display = 'block';
    modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
    
    modal.innerHTML = `
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">💰 Earnings & Commission Management</h5>
                    <button type="button" class="close" onclick="this.closest('.modal').remove()">
                        <span>&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <ul class="nav nav-tabs" id="adminEarningsTabs" role="tablist">
                        <li class="nav-item">
                            <a class="nav-link active" id="overview-tab" data-toggle="tab" href="#overview" role="tab">Overview</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" id="commission-tab" data-toggle="tab" href="#commission" role="tab">Commission Structures</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" id="providers-tab" data-toggle="tab" href="#providers" role="tab">Provider Earnings</a>
                        </li>
                    </ul>
                    
                    <div class="tab-content mt-3">
                        <div class="tab-pane fade show active" id="overview" role="tabpanel">
                            <div id="earnings-overview">Loading overview...</div>
                        </div>
                        <div class="tab-pane fade" id="commission" role="tabpanel">
                            <div class="mb-3">
                                <button class="btn btn-primary" onclick="createCommissionStructure()">
                                    <i class="fas fa-plus"></i> Add Commission Structure
                                </button>
                            </div>
                            <div id="commission-structures">Loading commission structures...</div>
                        </div>
                        <div class="tab-pane fade" id="providers" role="tabpanel">
                            <div id="provider-earnings">Loading provider earnings...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Load initial data
    loadEarningsOverview();
    loadCommissionStructures();
    
    // Tab event handlers
    modal.querySelectorAll('.nav-link').forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            modal.querySelectorAll('.nav-link').forEach(t => t.classList.remove('active'));
            modal.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('show', 'active'));
            this.classList.add('active');
            const target = modal.querySelector(this.getAttribute('href'));
            target.classList.add('show', 'active');
        });
    });
}

function showProviderEarnings() {
    showNotification('Loading earnings data...', 'info');
    fetch('/api/earnings', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Earnings data:', data);
        showNotification(`Found ${data.earnings.length || 0} earnings records`, 'success');
    })
    .catch(error => {
        console.error('Error loading earnings:', error);
        showNotification('Error loading earnings data', 'error');
    });
}

function loadEarningsOverview() {
    fetch('/api/admin/earnings-overview', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        const overview = document.getElementById('earnings-overview');
        overview.innerHTML = `
            <div class="row">
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="text-success">$${data.total_system_earnings.toFixed(2)}</h5>
                            <p class="card-text">Total Earnings</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="text-info">$${data.total_system_commission.toFixed(2)}</h5>
                            <p class="card-text">Total Commission</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="text-primary">${data.total_services}</h5>
                            <p class="card-text">Total Services</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="text-warning">${Object.keys(data.provider_breakdown).length}</h5>
                            <p class="card-text">Provider Types</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="mt-4">
                <h6>Provider Breakdown:</h6>
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Provider Type</th>
                                <th>Total Earnings</th>
                                <th>Total Commission</th>
                                <th>Services</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${Object.entries(data.provider_breakdown).map(([type, stats]) => `
                                <tr>
                                    <td>${type.charAt(0).toUpperCase() + type.slice(1)}</td>
                                    <td>$${stats.total_earnings.toFixed(2)}</td>
                                    <td>$${stats.total_commission.toFixed(2)}</td>
                                    <td>${stats.service_count}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    })
    .catch(error => {
        console.error('Error loading overview:', error);
        document.getElementById('earnings-overview').innerHTML = '<div class="alert alert-danger">Error loading overview</div>';
    });
}

function loadCommissionStructures() {
    fetch('/api/admin/commission-structures', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        const container = document.getElementById('commission-structures');
        if (data.commission_structures.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No commission structures found.</div>';
            return;
        }
        
        container.innerHTML = `
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Provider Type</th>
                            <th>Service Type</th>
                            <th>Commission Rate</th>
                            <th>Flat Fee</th>
                            <th>Min Threshold</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.commission_structures.map(structure => `
                            <tr>
                                <td>${structure.provider_type}</td>
                                <td>${structure.service_type}</td>
                                <td>${(structure.commission_rate * 100).toFixed(1)}%</td>
                                <td>${structure.flat_fee ? '$' + structure.flat_fee.toFixed(2) : 'N/A'}</td>
                                <td>${structure.minimum_threshold ? '$' + structure.minimum_threshold.toFixed(2) : 'N/A'}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" onclick="editCommissionStructure(${structure.id})">Edit</button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteCommissionStructure(${structure.id})">Delete</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    })
    .catch(error => {
        console.error('Error loading commission structures:', error);
        document.getElementById('commission-structures').innerHTML = '<div class="alert alert-danger">Error loading commission structures</div>';
    });
}

function createCommissionStructure() {
    const modal = document.createElement('div');
    modal.className = 'modal fade show';
    modal.style.display = 'block';
    modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
    
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create Commission Structure</h5>
                    <button type="button" class="close" onclick="this.closest('.modal').remove()">
                        <span>&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <form id="commissionForm">
                        <div class="form-group">
                            <label>Provider Type</label>
                            <select class="form-control" name="provider_type" required>
                                <option value="">Select provider type</option>
                                <option value="physician">Physician</option>
                                <option value="therapist">Therapist</option>
                                <option value="health_coach">Health Coach</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Service Type</label>
                            <input type="text" class="form-control" name="service_type" placeholder="e.g., consultation, therapy_session" required>
                        </div>
                        <div class="form-group">
                            <label>Commission Rate (%)</label>
                            <input type="number" class="form-control" name="commission_rate" min="0" max="100" step="0.1" required>
                        </div>
                        <div class="form-group">
                            <label>Flat Fee ($) <small class="text-muted">(optional)</small></label>
                            <input type="number" class="form-control" name="flat_fee" min="0" step="0.01">
                        </div>
                        <div class="form-group">
                            <label>Minimum Threshold ($) <small class="text-muted">(optional)</small></label>
                            <input type="number" class="form-control" name="minimum_threshold" min="0" step="0.01">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="submitCommissionStructure(this)">Create</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function submitCommissionStructure(button) {
    const form = document.getElementById('commissionForm');
    const formData = new FormData(form);
    
    const data = {
        provider_type: formData.get('provider_type'),
        service_type: formData.get('service_type'),
        commission_rate: parseFloat(formData.get('commission_rate')) / 100, // Convert percentage to decimal
        flat_fee: formData.get('flat_fee') ? parseFloat(formData.get('flat_fee')) : null,
        minimum_threshold: formData.get('minimum_threshold') ? parseFloat(formData.get('minimum_threshold')) : null
    };
    
    fetch('/api/admin/commission-structures', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.message) {
            showNotification('Commission structure created successfully', 'success');
            button.closest('.modal').remove();
            loadCommissionStructures(); // Reload the list
        } else {
            showNotification('Error creating commission structure', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error creating commission structure', 'error');
    });
}

// Module action functions
function openUsersModule() {
    openUserManagementModule();
}

function openAppointmentsModule() {
    showNotification('Loading appointments management...', 'info');
    // Navigate to appointments tab
    switchDashboardTab('appointments');
}

function openMessagingModule() {
    showNotification('Loading messaging system...', 'info');
    // Navigate to messages tab
    switchDashboardTab('messages');
}

function openAnalyticsModule() {
    showNotification('Loading analytics dashboard...', 'info');
    // Navigate to analytics tab
    switchDashboardTab('analytics');
}

function openSecurityModule() {
    showNotification('Loading security dashboard...', 'info');
    // This would open the security monitoring interface
}

function openSettingsModule() {
    showNotification('Loading system settings...', 'info');
    // This would open the settings interface
}

function openPatientsModule() {
    showNotification('Loading Patient Management...', 'info');
    switchDashboardTab('patient-management');
    setTimeout(loadPatientManagementData, 100);
}

function openHealthRecordsModule() {
    showNotification('Loading Health Records...', 'info');
    switchDashboardTab('health-records');
    setTimeout(loadHealthRecordsData, 100);
}

function openNutritionPlanModule() {
    showNotification('Loading Nutrition Management...', 'info');
    switchDashboardTab('nutrition-management');
    setTimeout(loadNutritionManagementData, 100);
}

function openMealPlanModule() {
    showNotification('Loading Meals Management...', 'info');
    switchDashboardTab('meals-management');
    setTimeout(loadMealsManagementData, 100);
}

function openEarningsModule() {
    showNotification('Loading Earnings & Commission...', 'info');
    switchDashboardTab('earnings-commission');
    setTimeout(loadEarningsCommissionData, 100);
}

function openSystemAdminModule() {
    showNotification('Loading System Administration...', 'info');
    switchDashboardTab('system-admin');
    setTimeout(loadSystemAdminData, 100);
}

function openUserManagementModule() {
    showNotification('Loading User Management...', 'info');
    switchDashboardTab('user-management');
    setTimeout(loadUserManagementData, 100);
}

function openMessagesModule() {
    showNotification('Opening Messages...', 'info');
    switchDashboardTab('messages');
}

function openAdminModule() {
    showNotification('Opening Admin Panel...', 'info');
    switchDashboardTab('admin');
}

// Data loading functions for new modules
async function loadPatientManagementData() {
    try {
        const response = await fetch('/api/patients', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const patients = data.patients || data || [];
            
            document.getElementById('total-patients').textContent = patients.length || '0';
            document.getElementById('active-cases').textContent = patients.filter(p => p.status === 'active').length || '0';
            
            // Calculate new patients this month
            const thisMonth = new Date().getMonth();
            const newThisMonth = patients.filter(p => {
                if (!p.created_at) return false;
                const created = new Date(p.created_at);
                return created.getMonth() === thisMonth;
            }).length;
            document.getElementById('new-patients').textContent = newThisMonth || '0';
            showNotification('Patient data loaded successfully', 'success');
        } else {
            throw new Error('Failed to load patient data');
        }
    } catch (error) {
        console.error('Error loading patient data:', error);
        document.getElementById('total-patients').textContent = 'Error';
        document.getElementById('active-cases').textContent = 'Error';
        document.getElementById('new-patients').textContent = 'Error';
        showNotification('Error loading patient data', 'error');
    }
}

async function loadHealthRecordsData() {
    try {
        const response = await fetch('/api/health-records', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const records = data.records || data || [];
            
            document.getElementById('total-records').textContent = records.length || '0';
            
            // Calculate recent updates (last 7 days)
            const weekAgo = new Date();
            weekAgo.setDate(weekAgo.getDate() - 7);
            const recentUpdates = records.filter(r => {
                if (!r.updated_at) return false;
                const updated = new Date(r.updated_at);
                return updated > weekAgo;
            }).length;
            document.getElementById('recent-updates').textContent = recentUpdates || '0';
            document.getElementById('pending-reviews').textContent = records.filter(r => r.status === 'pending_review').length || '0';
            showNotification('Health records loaded successfully', 'success');
        } else {
            throw new Error('Failed to load health records');
        }
    } catch (error) {
        console.error('Error loading health records data:', error);
        document.getElementById('total-records').textContent = 'Error';
        document.getElementById('recent-updates').textContent = 'Error';
        document.getElementById('pending-reviews').textContent = 'Error';
        showNotification('Error loading health records', 'error');
    }
}

async function loadNutritionManagementData() {
    try {
        const response = await fetch('/api/patients/nutrition-plans', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const plans = data.plans || data || [];
            
            document.getElementById('active-nutrition-plans').textContent = plans.filter(p => p.status === 'active').length || '0';
            document.getElementById('completed-plans').textContent = plans.filter(p => p.status === 'completed').length || '0';
            
            // Calculate average compliance (placeholder)
            const avgCompliance = plans.length > 0 ? '85%' : 'N/A';
            document.getElementById('avg-compliance').textContent = avgCompliance;
            showNotification('Nutrition data loaded successfully', 'success');
        } else {
            // If API not available, show placeholder data
            document.getElementById('active-nutrition-plans').textContent = '12';
            document.getElementById('completed-plans').textContent = '8';
            document.getElementById('avg-compliance').textContent = '85%';
            showNotification('Nutrition management loaded', 'info');
        }
    } catch (error) {
        console.error('Error loading nutrition data:', error);
        document.getElementById('active-nutrition-plans').textContent = '12';
        document.getElementById('completed-plans').textContent = '8';
        document.getElementById('avg-compliance').textContent = '85%';
        showNotification('Nutrition management loaded', 'info');
    }
}

async function loadMealsManagementData() {
    try {
        const response = await fetch('/api/patients/meal-plans', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const plans = data.plans || data || [];
            
            document.getElementById('total-meal-plans').textContent = plans.length || '0';
            document.getElementById('active-meal-plans').textContent = plans.filter(p => p.status === 'active').length || '0';
            
            // Calculate average rating (placeholder)
            const avgRating = plans.length > 0 ? '4.2/5' : 'N/A';
            document.getElementById('avg-meal-rating').textContent = avgRating;
            showNotification('Meal plans loaded successfully', 'success');
        } else {
            // If API not available, show placeholder data
            document.getElementById('total-meal-plans').textContent = '24';
            document.getElementById('active-meal-plans').textContent = '18';
            document.getElementById('avg-meal-rating').textContent = '4.2/5';
            showNotification('Meal management loaded', 'info');
        }
    } catch (error) {
        console.error('Error loading meal plans data:', error);
        document.getElementById('total-meal-plans').textContent = '24';
        document.getElementById('active-meal-plans').textContent = '18';
        document.getElementById('avg-meal-rating').textContent = '4.2/5';
        showNotification('Meal management loaded', 'info');
    }
}

async function loadEarningsCommissionData() {
    try {
        const response = await fetch('/api/earnings', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const earnings = data.earnings || data || [];
            
            const totalEarnings = earnings.reduce((sum, record) => sum + parseFloat(record.amount || 0), 0);
            document.getElementById('total-earnings').textContent = `$${totalEarnings.toFixed(2)}`;
            
            const pendingPayments = earnings.filter(r => r.status === 'pending').reduce((sum, record) => sum + parseFloat(record.amount || 0), 0);
            document.getElementById('pending-payments').textContent = `$${pendingPayments.toFixed(2)}`;
            
            // Calculate this month earnings
            const thisMonth = new Date().getMonth();
            const monthEarnings = earnings.filter(r => {
                if (!r.created_at) return false;
                const created = new Date(r.created_at);
                return created.getMonth() === thisMonth;
            }).reduce((sum, record) => sum + parseFloat(record.amount || 0), 0);
            document.getElementById('month-earnings').textContent = `$${monthEarnings.toFixed(2)}`;
            showNotification('Earnings data loaded successfully', 'success');
        } else {
            // If API not available, show placeholder data
            document.getElementById('total-earnings').textContent = '$12,450.00';
            document.getElementById('pending-payments').textContent = '$2,340.00';
            document.getElementById('month-earnings').textContent = '$3,200.00';
            showNotification('Earnings management loaded', 'info');
        }
    } catch (error) {
        console.error('Error loading earnings data:', error);
        document.getElementById('total-earnings').textContent = '$12,450.00';
        document.getElementById('pending-payments').textContent = '$2,340.00';
        document.getElementById('month-earnings').textContent = '$3,200.00';
        showNotification('Earnings management loaded', 'info');
    }
}

async function loadSystemAdminData() {
    try {
        // System status data (placeholder values for now)
        document.getElementById('server-uptime').textContent = '15 days, 8 hours';
        document.getElementById('db-status-detail').textContent = 'Online';
        document.getElementById('active-sessions').textContent = '47';
        
        showNotification('System administration loaded', 'success');
    } catch (error) {
        console.error('Error loading system data:', error);
        document.getElementById('server-uptime').textContent = '15 days, 8 hours';
        document.getElementById('db-status-detail').textContent = 'Online';
        document.getElementById('active-sessions').textContent = '47';
        showNotification('System administration loaded', 'info');
    }
}

async function loadUserManagementData() {
    try {
        // User management content loading
        const contentDiv = document.getElementById('user-management-content');
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
        showNotification('User management interface loaded', 'success');
    } catch (error) {
        console.error('Error loading user management data:', error);
        showNotification('User management loaded', 'info');
    }
}

// Export functions for global use
window.createAdminDashboard = createAdminDashboard;
window.createPhysicianDashboard = createPhysicianDashboard;
window.createTherapistDashboard = createTherapistDashboard;
window.createHealthCoachDashboard = createHealthCoachDashboard;
window.createPatientDashboard = createPatientDashboard;
window.createPartnerDashboard = createPartnerDashboard;

// Debug function for browser console testing
window.debugDashboard = function() {
    console.log('🔧 DASHBOARD DEBUG REPORT:');
    const container = document.getElementById('dashboard-modules');
    if (container) {
        console.log('✅ Container found:', container);
        console.log('📦 Container innerHTML length:', container.innerHTML.length);
        console.log('👥 Container children count:', container.children.length);
        console.log('👁️ Container visibility:', {
            display: window.getComputedStyle(container).display,
            visibility: window.getComputedStyle(container).visibility,
            opacity: window.getComputedStyle(container).opacity
        });
        console.log('📏 Container dimensions:', container.getBoundingClientRect());
        
        if (container.children.length > 0) {
            console.log('🎯 First child details:');
            const firstChild = container.children[0];
            console.log('  Element:', firstChild);
            console.log('  Classes:', firstChild.className);
            console.log('  Visibility:', {
                display: window.getComputedStyle(firstChild).display,
                visibility: window.getComputedStyle(firstChild).visibility,
                opacity: window.getComputedStyle(firstChild).opacity
            });
            console.log('  Dimensions:', firstChild.getBoundingClientRect());
        }
        
        console.log('🔍 Container HTML preview:', container.innerHTML.substring(0, 500));
    } else {
        console.error('❌ Container not found!');
    }
    
    // Test manual dashboard creation
    console.log('🔧 Testing manual dashboard creation...');
    if (typeof createAdminDashboard === 'function') {
        createAdminDashboard();
    } else {
        console.error('❌ createAdminDashboard function not available!');
    }
};