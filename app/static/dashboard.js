// static/dashboard.js - Role-based dashboard navigation

const API_BASE = 'http://localhost:5000/api';

class DashboardManager {
    constructor() {
        this.authToken = localStorage.getItem('authToken');
        this.currentUser = null;
        this.init();
    }

    async init() {
        // Check if user is logged in and redirect accordingly
        await this.checkAuthAndRedirect();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load dashboard data if user is authenticated
        if (this.authToken) {
            await this.loadDashboardData();
        }
    }

    async checkAuthAndRedirect() {
        if (!this.authToken) {
            // No token, show login page
            this.showLoginInterface();
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/auth/me`, {
                headers: { 'Authorization': `Bearer ${this.authToken}` }
            });

            if (response.ok) {
                const data = await response.json();
                this.currentUser = data.user;
                
                // Redirect to appropriate dashboard based on role
                this.redirectToDashboard(data.user.role);
            } else {
                // Invalid token, clear it and show login
                this.logout();
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            this.logout();
        }
    }

    redirectToDashboard(role) {
        const currentPath = window.location.pathname;
        
        // Define role-specific paths
        const rolePaths = {
            'job_seeker': '/',
            'employer': '/employer',
            'admin': '/admin'
        };

        const targetPath = rolePaths[role];
        
        // Only redirect if not already on the correct page
        if (currentPath !== targetPath) {
            window.location.href = targetPath;
            return;
        }

        // If already on correct page, hide login and show dashboard
        this.showDashboard();
    }

    showLoginInterface() {
        const authSection = document.getElementById('authSection');
        const appSection = document.getElementById('appSection');
        
        if (authSection) authSection.style.display = 'block';
        if (appSection) appSection.style.display = 'none';
    }

    showDashboard() {
        const authSection = document.getElementById('authSection');
        const appSection = document.getElementById('appSection');
        
        if (authSection) authSection.style.display = 'none';
        if (appSection) appSection.style.display = 'block';
        
        // Update user name if element exists
        const userNameElement = document.getElementById('userName');
        if (userNameElement && this.currentUser) {
            userNameElement.textContent = this.currentUser.first_name || this.currentUser.email;
        }
    }

    setupEventListeners() {
        // Login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Register form
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        // Tab switching
        window.showTab = (tabName) => this.showTab(tabName);
        window.showAppTab = (tabName) => this.showAppTab(tabName);
        window.logout = () => this.logout();
    }

    async handleLogin(event) {
        event.preventDefault();
        
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        
        try {
            const response = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                // Store token and user info
                localStorage.setItem('authToken', data.access_token);
                this.authToken = data.access_token;
                this.currentUser = data.user;
                
                // Show success message
                this.showMessage(data.message, 'success');
                
                // Redirect to role-specific dashboard
                setTimeout(() => {
                    this.redirectToDashboard(data.user.role);
                }, 1000);
                
            } else {
                this.showMessage(data.error, 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showMessage('Login failed. Please try again.', 'error');
        }
    }

    async handleRegister(event) {
        event.preventDefault();
        
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        const firstName = document.getElementById('firstName').value;
        const lastName = document.getElementById('lastName').value;
        
        // Get role if role selector exists
        const roleSelect = document.getElementById('userRole');
        const role = roleSelect ? roleSelect.value : 'job_seeker';
        
        try {
            const response = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email,
                    password,
                    first_name: firstName,
                    last_name: lastName,
                    role
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Store token and user info
                localStorage.setItem('authToken', data.access_token);
                this.authToken = data.access_token;
                this.currentUser = data.user;
                
                // Show success message
                this.showMessage(data.message, 'success');
                
                // Redirect to role-specific dashboard
                setTimeout(() => {
                    this.redirectToDashboard(data.user.role);
                }, 1000);
                
            } else {
                this.showMessage(data.error, 'error');
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showMessage('Registration failed. Please try again.', 'error');
        }
    }

    async loadDashboardData() {
        if (!this.authToken) return;
        
        try {
            // Load dashboard stats
            const statsResponse = await fetch(`${API_BASE}/dashboard/stats`, {
                headers: { 'Authorization': `Bearer ${this.authToken}` }
            });

            if (statsResponse.ok) {
                const statsData = await statsResponse.json();
                this.updateDashboardStats(statsData);
            }

            // Load recent activity
            const activityResponse = await fetch(`${API_BASE}/dashboard/recent-activity`, {
                headers: { 'Authorization': `Bearer ${this.authToken}` }
            });

            if (activityResponse.ok) {
                const activityData = await activityResponse.json();
                this.updateRecentActivity(activityData);
            }

            // Load role-specific data
            if (this.currentUser) {
                await this.loadRoleSpecificData();
            }

        } catch (error) {
            console.error('Dashboard data loading error:', error);
        }
    }

    updateDashboardStats(data) {
        const role = data.role;
        const stats = data.stats;

        if (role === 'job_seeker') {
            this.updateElement('applicationsCount', stats.applications);
            this.updateElement('pendingCount', stats.pending);
            this.updateElement('interviewsCount', stats.interviews);
            this.updateElement('profileCompleteness', stats.profile_completeness + '%');
        } else if (role === 'employer') {
            this.updateElement('totalJobs', stats.total_jobs);
            this.updateElement('activeJobs', stats.active_jobs);
            this.updateElement('totalApplications', stats.total_applications);
            this.updateElement('pendingApplications', stats.pending_applications);
        } else if (role === 'admin') {
            this.updateElement('totalUsers', stats.total_users);
            this.updateElement('activeUsers', stats.active_users);
            this.updateElement('totalJobs', stats.total_jobs);
            this.updateElement('activeJobs', stats.active_jobs);
            this.updateElement('totalApplications', stats.total_applications);
        }
    }

    updateRecentActivity(data) {
        const activities = data.activities || [];
        const activityContainer = document.getElementById('recentActivity');
        
        if (!activityContainer) return;

        if (activities.length === 0) {
            activityContainer.innerHTML = '<p>No recent activity</p>';
            return;
        }

        const activityHTML = activities.map(activity => {
            const date = new Date(activity.timestamp).toLocaleDateString();
            const statusClass = activity.status ? `status-${activity.status}` : '';
            
            return `
                <div class="activity-item">
                    <div class="activity-content">
                        <p>${activity.message}</p>
                        <span class="activity-date">${date}</span>
                    </div>
                    ${activity.status ? `<span class="status-badge ${statusClass}">${activity.status}</span>` : ''}
                </div>
            `;
        }).join('');

        activityContainer.innerHTML = activityHTML;
    }

    async loadRoleSpecificData() {
        if (this.currentUser.role === 'job_seeker') {
            await this.loadJobRecommendations();
        } else if (this.currentUser.role === 'employer') {
            await this.loadEmployerJobs();
        } else if (this.currentUser.role === 'admin') {
            await this.loadAdminData();
        }
    }

    async loadJobRecommendations() {
        try {
            const response = await fetch(`${API_BASE}/dashboard/recommendations`, {
                headers: { 'Authorization': `Bearer ${this.authToken}` }
            });

            if (response.ok) {
                const data = await response.json();
                this.displayJobRecommendations(data.recommendations);
            }
        } catch (error) {
            console.error('Job recommendations loading error:', error);
        }
    }

    displayJobRecommendations(recommendations) {
        const container = document.getElementById('jobRecommendations');
        if (!container) return;

        if (recommendations.length === 0) {
            container.innerHTML = '<p>No job recommendations available. Complete your profile to get better matches.</p>';
            return;
        }

        const recommendationsHTML = recommendations.map(job => `
            <div class="job-recommendation">
                <h4>${job.title}</h4>
                <p class="company">${job.company}</p>
                <p class="location">${job.location}</p>
                <div class="job-meta">
                    <span class="match-score">Match: ${job.match_percentage}%</span>
                    <span class="job-type">${job.job_type}</span>
                    ${job.salary_range ? `<span class="salary">${job.salary_range}</span>` : ''}
                </div>
                <button onclick="applyToJob(${job.job_id})" class="apply-btn">Apply Now</button>
            </div>
        `).join('');

        container.innerHTML = recommendationsHTML;
    }

    async loadEmployerJobs() {
        try {
            const response = await fetch(`${API_BASE}/employer/jobs`, {
                headers: { 'Authorization': `Bearer ${this.authToken}` }
            });

            if (response.ok) {
                const data = await response.json();
                this.displayEmployerJobs(data.jobs);
            }
        } catch (error) {
            console.error('Employer jobs loading error:', error);
        }
    }

    displayEmployerJobs(jobs) {
        const container = document.getElementById('employerJobs');
        if (!container) return;

        if (jobs.length === 0) {
            container.innerHTML = '<p>No jobs posted yet. <button onclick="showCreateJobModal()">Post Your First Job</button></p>';
            return;
        }

        const jobsHTML = jobs.map(job => `
            <div class="employer-job">
                <h4>${job.title}</h4>
                <p class="job-status ${job.is_active ? 'active' : 'inactive'}">
                    ${job.is_active ? 'Active' : 'Inactive'}
                </p>
                <p>Applications: ${job.application_count || 0}</p>
                <p>Posted: ${new Date(job.created_at).toLocaleDateString()}</p>
                <div class="job-actions">
                    <button onclick="viewJobApplications(${job.id})">View Applications</button>
                    <button onclick="editJob(${job.id})">Edit</button>
                    <button onclick="toggleJobStatus(${job.id}, ${job.is_active})">
                        ${job.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = jobsHTML;
    }

    async loadAdminData() {
        try {
            const response = await fetch(`${API_BASE}/admin/dashboard`, {
                headers: { 'Authorization': `Bearer ${this.authToken}` }
            });

            if (response.ok) {
                const data = await response.json();
                this.displayAdminData(data);
            }
        } catch (error) {
            console.error('Admin data loading error:', error);
        }
    }

    displayAdminData(data) {
        // Update admin-specific elements
        this.updateElement('platformGrowth', data.growth_rate + '%');
        this.updateElement('activeJobsToday', data.jobs_today);
        this.updateElement('applicationsToday', data.applications_today);
        
        // Display recent platform activity
        const systemActivity = document.getElementById('systemActivity');
        if (systemActivity && data.recent_system_activity) {
            const activityHTML = data.recent_system_activity.map(activity => `
                <div class="system-activity-item">
                    <span class="activity-type">${activity.type}</span>
                    <span class="activity-message">${activity.message}</span>
                    <span class="activity-time">${activity.time}</span>
                </div>
            `).join('');
            systemActivity.innerHTML = activityHTML;
        }
    }

    updateElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    showMessage(message, type) {
        const messageDiv = document.getElementById('message');
        if (messageDiv) {
            messageDiv.innerHTML = `<div class="message ${type}">${message}</div>`;
            
            // Auto-hide message after 5 seconds
            setTimeout(() => {
                messageDiv.innerHTML = '';
            }, 5000);
        }
    }

    showTab(tabName) {
        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // Remove active class from all tabs
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Show selected tab content
        const tabContent = document.getElementById(tabName + 'Tab');
        if (tabContent) {
            tabContent.classList.add('active');
        }
        
        // Add active class to clicked tab
        event.target.classList.add('active');
    }

    showAppTab(tabName) {
        // Similar to showTab but for app section tabs
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        const tabContent = document.getElementById(tabName + 'Tab');
        if (tabContent) {
            tabContent.classList.add('active');
        }
        
        event.target.classList.add('active');
    }

    logout() {
        // Clear stored data
        localStorage.removeItem('authToken');
        this.authToken = null;
        this.currentUser = null;
        
        // Redirect to login page
        window.location.href = '/';
    }

    // Role switching functionality (for testing or admin purposes)
    async switchRole(newRole) {
        if (!this.authToken) return;
        
        try {
            const response = await fetch(`${API_BASE}/auth/role-switch`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ role: newRole })
            });

            const data = await response.json();

            if (response.ok) {
                this.currentUser = data.user;
                this.showMessage(data.message, 'success');
                
                // Redirect to new role dashboard
                setTimeout(() => {
                    window.location.href = data.redirect_url;
                }, 1000);
            } else {
                this.showMessage(data.error, 'error');
            }
        } catch (error) {
            console.error('Role switch error:', error);
            this.showMessage('Role switch failed. Please try again.', 'error');
        }
    }
}

// Global functions for backward compatibility
window.applyToJob = async function(jobId) {
    const dashboardManager = window.dashboardManager;
    if (!dashboardManager.authToken) return;
    
    try {
        const response = await fetch(`${API_BASE}/applications/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${dashboardManager.authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ job_id: jobId })
        });

        const data = await response.json();

        if (response.ok) {
            dashboardManager.showMessage('Application submitted successfully!', 'success');
            dashboardManager.loadDashboardData(); // Refresh data
        } else {
            dashboardManager.showMessage(data.error, 'error');
        }
    } catch (error) {
        console.error('Application error:', error);
        dashboardManager.showMessage('Application failed. Please try again.', 'error');
    }
};

window.toggleJobStatus = async function(jobId, currentStatus) {
    const dashboardManager = window.dashboardManager;
    if (!dashboardManager.authToken) return;
    
    try {
        const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${dashboardManager.authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ is_active: !currentStatus })
        });

        if (response.ok) {
            dashboardManager.showMessage('Job status updated successfully!', 'success');
            dashboardManager.loadDashboardData(); // Refresh data
        } else {
            dashboardManager.showMessage('Failed to update job status', 'error');
        }
    } catch (error) {
        console.error('Job status update error:', error);
        dashboardManager.showMessage('Update failed. Please try again.', 'error');
    }
};

window.viewJobApplications = function(jobId) {
    // Navigate to applications view for specific job
    window.location.href = `/employer#applications?job=${jobId}`;
};

window.editJob = function(jobId) {
    // Navigate to job editing interface
    window.location.href = `/employer#edit-job?id=${jobId}`;
};

window.showCreateJobModal = function() {
    const modal = document.getElementById('createJobModal');
    if (modal) {
        modal.style.display = 'block';
    }
};

// Initialize dashboard manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardManager = new DashboardManager();
});

// Handle browser back/forward navigation
window.addEventListener('popstate', () => {
    if (window.dashboardManager) {
        window.dashboardManager.checkAuthAndRedirect();
    }
});