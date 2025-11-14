// Debug script to test healthcare module functions
console.log('🔧 DEBUG: Testing healthcare module functions...');

// Function to test if all required functions and elements exist
function debugHealthcareModules() {
    console.log('=== DEBUGGING HEALTHCARE MODULES ===');
    
    const modules = [
        { name: 'Patient Management', func: 'openPatientsModule', pageId: 'patient-management-page' },
        { name: 'Health Records', func: 'openHealthRecordsModule', pageId: 'health-records-page' },
        { name: 'Nutrition Management', func: 'openNutritionPlanModule', pageId: 'nutrition-management-page' },
        { name: 'Earnings & Commission', func: 'openEarningsModule', pageId: 'earnings-commission-page' },
        { name: 'System Admin', func: 'openSystemAdminModule', pageId: 'system-admin-page' }
    ];
    
    modules.forEach(module => {
        console.log(`\n--- Testing ${module.name} ---`);
        
        // Check if function exists
        const funcExists = typeof window[module.func] === 'function';
        console.log(`Function ${module.func} exists:`, funcExists);
        
        // Check if page element exists
        const pageElement = document.getElementById(module.pageId);
        console.log(`Page element ${module.pageId} exists:`, !!pageElement);
        
        if (pageElement) {
            console.log(`Page element display:`, window.getComputedStyle(pageElement).display);
            console.log(`Page element has content-page class:`, pageElement.classList.contains('content-page'));
        }
        
        // Check if switchDashboardTab function exists
        console.log('switchDashboardTab function exists:', typeof switchDashboardTab === 'function');
        
        // Try calling the function if it exists
        if (funcExists) {
            try {
                console.log(`Attempting to call ${module.func}...`);
                window[module.func]();
                console.log(`✅ ${module.func} called successfully`);
            } catch (error) {
                console.error(`❌ Error calling ${module.func}:`, error);
            }
        }
    });
    
    // List all content pages
    console.log('\n--- All Content Pages ---');
    const allPages = document.querySelectorAll('.content-page');
    allPages.forEach(page => {
        const isActive = page.classList.contains('active');
        const display = window.getComputedStyle(page).display;
        console.log(`${page.id}: active=${isActive}, display=${display}`);
    });
}

// Make it available globally
window.debugHealthcareModules = debugHealthcareModules;

console.log('🔧 DEBUG: Use debugHealthcareModules() to test all modules');