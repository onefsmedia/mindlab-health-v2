// Demo Data and Helper Functions for Role-Specific Dashboards
// Provides realistic demo data and functionality for testing role-based dashboards

// Demo data for different roles
const demoData = {
    physician: {
        todaysPatients: [
            { name: 'John Smith', time: '9:00 AM', condition: 'Routine Checkup' },
            { name: 'Mary Johnson', time: '10:30 AM', condition: 'Follow-up' },
            { name: 'Robert Brown', time: '2:00 PM', condition: 'Consultation' }
        ],
        pendingReviews: [
            { patient: 'Sarah Wilson', type: 'Lab Results', priority: 'High' },
            { patient: 'Michael Davis', type: 'X-Ray Results', priority: 'Medium' },
            { patient: 'Lisa Anderson', type: 'Blood Work', priority: 'Low' }
        ],
        criticalAlerts: [
            { patient: 'Emergency Patient', alert: 'Abnormal vital signs', time: '30 min ago' }
        ]
    },
    therapist: {
        todaysSessions: [
            { client: 'Client A', time: '9:00 AM', type: 'Individual Therapy' },
            { client: 'Client B', time: '11:00 AM', type: 'Group Session' },
            { client: 'Client C', time: '2:00 PM', type: 'Family Therapy' }
        ],
        activeClients: 24,
        notesDue: [
            { client: 'Client A', session: 'Oct 16', type: 'Individual' },
            { client: 'Client D', session: 'Oct 15', type: 'Group' }
        ]
    },
    health_coach: {
        activeClients: 18,
        mealPlansCreated: [
            { client: 'Jane Doe', plan: 'Weight Loss', created: 'Today' },
            { client: 'Tom Smith', plan: 'Muscle Gain', created: 'Yesterday' }
        ],
        goalsAchieved: [
            { client: 'Mary K.', goal: '10k steps daily', achieved: 'Oct 16' },
            { client: 'John D.', goal: 'Reduce sugar intake', achieved: 'Oct 15' }
        ]
    },
    patient: {
        nextAppointment: { date: 'Oct 20', time: '2:00 PM', provider: 'Dr. Smith' },
        mealsToday: { logged: 2, total: 3 },
        unreadMessages: 1,
        weekProgress: {
            exercise: '4/5 days',
            meals: '85% logged',
            sleep: '7.5 hrs avg'
        }
    },
    partner: {
        wellnessTips: [
            'Stay hydrated throughout the day',
            'Take regular walking breaks',
            'Practice deep breathing exercises'
        ],
        resources: 42,
        supportArticles: [
            'Supporting Mental Health',
            'Nutrition for Wellness',
            'Exercise and Mood'
        ]
    }
};

// Create test users for different roles
async function createTestUsers() {
    const testUsers = [
        { username: 'physician1', email: 'physician@test.com', password: 'test123', role: 'physician' },
        { username: 'therapist1', email: 'therapist@test.com', password: 'test123', role: 'therapist' },
        { username: 'coach1', email: 'coach@test.com', password: 'test123', role: 'health_coach' },
        { username: 'patient1', email: 'patient@test.com', password: 'test123', role: 'patient' },
        { username: 'partner1', email: 'partner@test.com', password: 'test123', role: 'partner' }
    ];

    console.log('Demo users available for testing:');
    testUsers.forEach(user => {
        console.log(`- Username: ${user.username}, Password: ${user.password}, Role: ${user.role}`);
    });
}

// Enhanced notification system for role-specific messages
function showRoleBasedNotification(message, type = 'info', role = null) {
    const roleColors = {
        admin: '#dc3545',
        physician: '#0d6efd',
        therapist: '#198754',
        health_coach: '#fd7e14',
        patient: '#6f42c1',
        partner: '#20c997'
    };

    const color = role ? roleColors[role] : '#007bff';
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 400px;
        border-left: 4px solid ${color};
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    `;
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Quick action functions for different roles
const roleActions = {
    physician: {
        quickSchedule: () => {
            showRoleBasedNotification('Quick scheduling for physicians coming soon!', 'info', 'physician');
        },
        viewCriticalAlerts: () => {
            const alerts = demoData.physician.criticalAlerts;
            let alertText = 'Critical Alerts:\n';
            alerts.forEach(alert => {
                alertText += `• ${alert.patient}: ${alert.alert} (${alert.time})\n`;
            });
            alert(alertText);
        },
        emergencyProtocol: () => {
            showRoleBasedNotification('Emergency protocol activated!', 'warning', 'physician');
        }
    },
    therapist: {
        quickNote: () => {
            showRoleBasedNotification('Quick note feature for therapists coming soon!', 'info', 'therapist');
        },
        clientProgress: () => {
            showRoleBasedNotification('Client progress tracking updated!', 'success', 'therapist');
        },
        resourceLibrary: () => {
            showRoleBasedNotification('Accessing therapy resource library...', 'info', 'therapist');
        }
    },
    health_coach: {
        createMealPlan: () => {
            showRoleBasedNotification('Meal plan creator opened!', 'success', 'health_coach');
        },
        trackGoals: () => {
            showRoleBasedNotification('Goal tracking system activated!', 'info', 'health_coach');
        },
        nutritionAnalysis: () => {
            showRoleBasedNotification('Nutrition analysis tools loading...', 'info', 'health_coach');
        }
    },
    patient: {
        logMeal: () => {
            showRoleBasedNotification('Meal logged successfully!', 'success', 'patient');
        },
        checkProgress: () => {
            const progress = demoData.patient.weekProgress;
            let progressText = 'Your Weekly Progress:\n';
            Object.entries(progress).forEach(([key, value]) => {
                progressText += `• ${key.charAt(0).toUpperCase() + key.slice(1)}: ${value}\n`;
            });
            alert(progressText);
        },
        bookAppointment: () => {
            showRoleBasedNotification('Appointment booking opened!', 'info', 'patient');
        }
    },
    partner: {
        viewResources: () => {
            const tips = demoData.partner.wellnessTips;
            let tipText = 'Today\'s Wellness Tips:\n';
            tips.forEach((tip, index) => {
                tipText += `${index + 1}. ${tip}\n`;
            });
            alert(tipText);
        },
        supportInfo: () => {
            showRoleBasedNotification('Support information accessed!', 'info', 'partner');
        }
    }
};

// Enhanced module opening function with role-specific features
function openRoleSpecificModule(moduleName, role) {
    console.log(`Opening ${moduleName} module for ${role}`);
    
    // Add role-specific functionality
    switch (role) {
        case 'physician':
            if (moduleName === 'appointments') {
                // Show physician-specific appointment view
                showRoleBasedNotification('Opening physician appointment management...', 'info', 'physician');
            }
            break;
        case 'therapist':
            if (moduleName === 'appointments') {
                showRoleBasedNotification('Opening therapy session scheduler...', 'info', 'therapist');
            }
            break;
        case 'health_coach':
            if (moduleName === 'nutrition') {
                showRoleBasedNotification('Opening nutrition planning tools...', 'info', 'health_coach');
            }
            break;
        case 'patient':
            if (moduleName === 'appointments') {
                showRoleBasedNotification('Opening your appointment portal...', 'info', 'patient');
            }
            break;
        case 'partner':
            showRoleBasedNotification('Accessing partner resources...', 'info', 'partner');
            break;
    }
    
    // Call the original module opening function
    if (typeof openModule === 'function') {
        openModule(moduleName);
    }
}

// Quick stats refresh function
function refreshRoleStats() {
    const role = window.currentUser?.role;
    if (role && typeof updateQuickStats === 'function') {
        updateQuickStats(role);
        showRoleBasedNotification('Statistics refreshed!', 'success', role);
    }
}

// Role-based welcome message
function showRoleWelcomeMessage(role, username) {
    const welcomeMessages = {
        admin: `Welcome back, ${username}! You have full system access as an administrator.`,
        physician: `Welcome, Dr. ${username}! Ready to provide excellent patient care today.`,
        therapist: `Hello, ${username}! Your clients are looking forward to their sessions today.`,
        health_coach: `Hi ${username}! Time to help your clients achieve their wellness goals.`,
        patient: `Welcome back, ${username}! Let's continue your health journey together.`,
        partner: `Hello ${username}! Access your wellness resources and support materials.`
    };
    
    const message = welcomeMessages[role] || `Welcome, ${username}!`;
    setTimeout(() => {
        showRoleBasedNotification(message, 'success', role);
    }, 1000);
}

// Initialize demo data display
function initializeDemoFeatures() {
    // Add quick action buttons to dashboard if user is logged in
    if (window.currentUser) {
        addQuickActionButtons(window.currentUser.role);
        showRoleWelcomeMessage(window.currentUser.role, window.currentUser.username);
    }
}

// Add quick action buttons based on role
function addQuickActionButtons(role) {
    const dashboardHeader = document.querySelector('.dashboard-header');
    if (!dashboardHeader) return;
    
    const quickActions = {
        physician: [
            { text: 'Emergency Protocol', action: 'emergencyProtocol', color: '#dc3545' },
            { text: 'Critical Alerts', action: 'viewCriticalAlerts', color: '#fd7e14' }
        ],
        therapist: [
            { text: 'Quick Note', action: 'quickNote', color: '#198754' },
            { text: 'Resource Library', action: 'resourceLibrary', color: '#6f42c1' }
        ],
        health_coach: [
            { text: 'Create Meal Plan', action: 'createMealPlan', color: '#fd7e14' },
            { text: 'Track Goals', action: 'trackGoals', color: '#198754' }
        ],
        patient: [
            { text: 'Log Meal', action: 'logMeal', color: '#6f42c1' },
            { text: 'Check Progress', action: 'checkProgress', color: '#198754' }
        ],
        partner: [
            { text: 'Wellness Tips', action: 'viewResources', color: '#20c997' }
        ]
    };
    
    const actions = quickActions[role] || [];
    if (actions.length === 0) return;
    
    const quickActionDiv = document.createElement('div');
    quickActionDiv.className = 'quick-actions mt-3';
    quickActionDiv.innerHTML = '<h6>Quick Actions:</h6>';
    
    actions.forEach(action => {
        const button = document.createElement('button');
        button.className = 'btn btn-sm me-2 mb-2';
        button.style.cssText = `
            background-color: ${action.color};
            border-color: ${action.color};
            color: white;
            border-radius: 15px;
        `;
        button.textContent = action.text;
        button.onclick = () => roleActions[role][action.action]();
        quickActionDiv.appendChild(button);
    });
    
    dashboardHeader.appendChild(quickActionDiv);
}

// Export functions
window.demoData = demoData;
window.roleActions = roleActions;
window.showRoleBasedNotification = showRoleBasedNotification;
window.openRoleSpecificModule = openRoleSpecificModule;
window.refreshRoleStats = refreshRoleStats;
window.initializeDemoFeatures = initializeDemoFeatures;
window.createTestUsers = createTestUsers;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    createTestUsers();
});