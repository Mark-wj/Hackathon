// Global variables
let authToken = localStorage.getItem('authToken');
let currentUser = null;

// API Base URL
const API_BASE = 'http://localhost:5000/api';

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    if (authToken) {
        checkAuth();
    }
    
    // Form handlers
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    document.getElementById('profileForm').addEventListener('submit', handleProfileUpdate);
});

// Show message
function showMessage(message, type = 'success') {
    const messageDiv = document.getElementById('message');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    messageDiv.style.display = 'block';
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}

// Tab switching
function showTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    if (tabName === 'login') {
        document.querySelector('.tab:nth-child(1)').classList.add('active');
        document.getElementById('loginTab').classList.add('active');
    } else {
        document.querySelector('.tab:nth-child(2)').classList.add('active');
        document.getElementById('registerTab').classList.add('active');
    }
}

function showAppTab(tabName) {
    document.querySelectorAll('#appSection .tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('#appSection .tab-content').forEach(content => content.classList.remove('active'));
    
    const tabIndex = ['profile', 'jobs', 'matches', 'applications'].indexOf(tabName);
    document.querySelectorAll('#appSection .tab')[tabIndex].classList.add('active');
    document.getElementById(tabName + 'Tab').classList.add('active');
    
    // Load data for the tab
    if (tabName === 'jobs') {
        searchJobs();
    } else if (tabName === 'applications') {
        loadApplications();
    } else if (tabName === 'profile') {
        loadProfile();
    }
}

// Authentication
async function handleLogin(e) {
    e.preventDefault();
    
    const data = {
        email: document.getElementById('loginEmail').value,
        password: document.getElementById('loginPassword').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            authToken = result.access_token;
            localStorage.setItem('authToken', authToken);
            currentUser = result.user;
            showApp();
            showMessage('Login successful!');
        } else {
            showMessage(result.error || 'Login failed', 'error');
        }
    } catch (error) {
        showMessage('Network error', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const data = {
        email: document.getElementById('registerEmail').value,
        password: document.getElementById('registerPassword').value,
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            authToken = result.access_token;
            localStorage.setItem('authToken', authToken);
            currentUser = result.user;
            showApp();
            showMessage('Registration successful!');
        } else {
            showMessage(result.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showMessage('Network error', 'error');
    }
}

async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE}/users/profile`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data;
            showApp();
        } else {
            logout();
        }
    } catch (error) {
        logout();
    }
}

function showApp() {
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('appSection').style.display = 'block';
    document.getElementById('userName').textContent = 
        `${currentUser.first_name || ''} ${currentUser.last_name || ''}`.trim() || currentUser.email;
    loadProfile();
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    document.getElementById('authSection').style.display = 'block';
    document.getElementById('appSection').style.display = 'none';
}

// Profile - UPDATED VERSION
async function loadProfile() {
    try {
        const response = await fetch(`${API_BASE}/users/profile`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.profile) {
                document.getElementById('phone').value = data.profile.phone || '';
                document.getElementById('location').value = data.profile.location || '';
                document.getElementById('summary').value = data.profile.summary || '';
                document.getElementById('skills').value = data.profile.skills ? data.profile.skills.join(', ') : '';
                document.getElementById('experienceYears').value = data.profile.experience_years || '';
                
                // Handle education and work experience (stored as JSON)
                if (data.profile.education && data.profile.education.items) {
                    document.getElementById('education').value = data.profile.education.items.join('\n');
                } else {
                    document.getElementById('education').value = '';
                }
                
                if (data.profile.work_experience && data.profile.work_experience.items) {
                    document.getElementById('workExperience').value = data.profile.work_experience.items.join('\n');
                } else {
                    document.getElementById('workExperience').value = '';
                }
                
                // URLs
                document.getElementById('linkedinUrl').value = data.profile.linkedin_url || '';
                document.getElementById('githubUrl').value = data.profile.github_url || '';
                document.getElementById('portfolioUrl').value = data.profile.portfolio_url || '';
            }
        }
    } catch (error) {
        showMessage('Failed to load profile', 'error');
    }
}

// UPDATED handleProfileUpdate
async function handleProfileUpdate(e) {
    e.preventDefault();
    
    const skillsInput = document.getElementById('skills').value;
    const skills = skillsInput ? skillsInput.split(',').map(s => s.trim()) : [];
    
    // Parse education and work experience into structured format
    const educationText = document.getElementById('education').value;
    const education = educationText ? { items: educationText.split('\n').filter(line => line.trim()) } : null;
    
    const workExperienceText = document.getElementById('workExperience').value;
    const work_experience = workExperienceText ? { items: workExperienceText.split('\n').filter(line => line.trim()) } : null;
    
    const data = {
        phone: document.getElementById('phone').value,
        location: document.getElementById('location').value,
        summary: document.getElementById('summary').value,
        skills: skills,
        experience_years: parseInt(document.getElementById('experienceYears').value) || 0,
        education: education,
        work_experience: work_experience,
        linkedin_url: document.getElementById('linkedinUrl').value,
        github_url: document.getElementById('githubUrl').value,
        portfolio_url: document.getElementById('portfolioUrl').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/users/profile`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showMessage('Profile updated successfully!');
            // Reload profile to show updated data
            loadProfile();
        } else {
            showMessage('Failed to update profile', 'error');
        }
    } catch (error) {
        showMessage('Network error', 'error');
    }
}

async function analyzeProfile() {
    try {
        const response = await fetch(`${API_BASE}/ai/analyze-profile`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            const analysisDiv = document.getElementById('profileAnalysis');
            analysisDiv.innerHTML = `
                <h3>Profile Analysis</h3>
                <p>Completeness: ${data.profile_completeness}%</p>
                ${data.missing_fields.length > 0 ? 
                    `<p>Missing fields: ${data.missing_fields.join(', ')}</p>` : ''}
                ${data.suggestions.length > 0 ? 
                    `<p>Suggestions:<ul>${data.suggestions.map(s => `<li>${s}</li>`).join('')}</ul></p>` : ''}
            `;
        }
    } catch (error) {
        showMessage('Failed to analyze profile', 'error');
    }
}

// Jobs
async function searchJobs() {
    const query = document.getElementById('searchQuery').value;
    
    try {
        const response = await fetch(`${API_BASE}/jobs/search?q=${encodeURIComponent(query)}`);
        
        if (response.ok) {
            const data = await response.json();
            displayJobs(data.jobs);
        }
    } catch (error) {
        showMessage('Failed to load jobs', 'error');
    }
}

function displayJobs(jobs) {
    const jobsList = document.getElementById('jobsList');
    
    if (jobs.length === 0) {
        jobsList.innerHTML = '<p>No jobs found</p>';
        return;
    }
    
    jobsList.innerHTML = jobs.map(job => `
        <div class="job-card">
            <h3>${job.title}</h3>
            <p><strong>Company:</strong> ${job.company ? job.company.name : 'Unknown'}</p>
            <p><strong>Location:</strong> ${job.location} ${job.is_remote ? '(Remote)' : ''}</p>
            <p><strong>Experience:</strong> ${job.experience_level}</p>
            <p>${job.description}</p>
            <div class="skills">
                ${job.skills_required ? job.skills_required.map(skill => 
                    `<span class="skill-tag">${skill}</span>`).join('') : ''}
            </div>
            <button onclick="applyToJob(${job.id})">Apply</button>
            <button onclick="getMatchScore(${job.id})">Check Match Score</button>
        </div>
    `).join('');
}

async function applyToJob(jobId) {
    if (confirm('Generate a cover letter for this application?')) {
        try {
            const response = await fetch(`${API_BASE}/applications/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    job_id: jobId,
                    generate_cover_letter: true
                })
            });
            
            if (response.ok) {
                showMessage('Application submitted successfully!');
                loadApplications();
            } else {
                const error = await response.json();
                showMessage(error.error || 'Failed to apply', 'error');
            }
        } catch (error) {
            showMessage('Network error', 'error');
        }
    }
}

async function getMatchScore(jobId) {
    try {
        const response = await fetch(`${API_BASE}/jobs/${jobId}/match`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            alert(`Match Score: ${data.scores.overall.toFixed(1)}%
Skills Match: ${data.scores.skill_match.toFixed(1)}%
Experience Match: ${data.scores.experience_match.toFixed(1)}%
Location Match: ${data.scores.location_match.toFixed(1)}%

${data.recommendation}`);
        } else {
            const error = await response.json();
            showMessage(error.error || 'Failed to get match score', 'error');
        }
    } catch (error) {
        showMessage('Network error', 'error');
    }
}

// Matches
async function findMatches() {
    try {
        const response = await fetch(`${API_BASE}/ai/match-jobs`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ min_match_score: 50 })
        });
        
        if (response.ok) {
            const data = await response.json();
            displayMatches(data.matches);
        } else {
            const error = await response.json();
            showMessage(error.error || 'Failed to find matches', 'error');
        }
    } catch (error) {
        showMessage('Network error', 'error');
    }
}

function displayMatches(matches) {
    const matchesList = document.getElementById('matchesList');
    
    if (matches.length === 0) {
        matchesList.innerHTML = '<p>No matches found. Please complete your profile.</p>';
        return;
    }
    
    matchesList.innerHTML = matches.map(match => `
        <div class="job-card">
            <h3>${match.job.title} <span class="match-score">${match.scores.overall.toFixed(1)}% Match</span></h3>
            <p><strong>Company:</strong> ${match.job.company ? match.job.company.name : 'Unknown'}</p>
            <p><strong>Location:</strong> ${match.job.location} ${match.job.is_remote ? '(Remote)' : ''}</p>
            <p>${match.job.description}</p>
            <p><strong>Match Details:</strong> 
                Skills: ${match.scores.skill_match.toFixed(1)}% | 
                Experience: ${match.scores.experience_match.toFixed(1)}% | 
                Location: ${match.scores.location_match.toFixed(1)}%
            </p>
            <button onclick="applyToJob(${match.job.id})">Apply</button>
        </div>
    `).join('');
}

// Applications
async function loadApplications() {
    try {
        const response = await fetch(`${API_BASE}/applications/`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayApplications(data.applications);
        }
    } catch (error) {
        showMessage('Failed to load applications', 'error');
    }
}

function displayApplications(applications) {
    const applicationsList = document.getElementById('applicationsList');
    
    if (applications.length === 0) {
        applicationsList.innerHTML = '<p>No applications yet</p>';
        return;
    }
    
    applicationsList.innerHTML = applications.map(app => `
        <div class="job-card">
            <h3>${app.job.title}</h3>
            <p><strong>Company:</strong> ${app.job.company ? app.job.company.name : 'Unknown'}</p>
            <p><strong>Status:</strong> ${app.status}</p>
            <p><strong>Applied:</strong> ${new Date(app.applied_at).toLocaleDateString()}</p>
            ${app.match_score ? `<p><strong>Match Score:</strong> ${app.match_score.toFixed(1)}%</p>` : ''}
        </div>
    `).join('');
}

// Resume Upload
async function uploadResume() {
    const fileInput = document.getElementById('resumeFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showMessage('Please select a file', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('resume', file);
    
    try {
        const response = await fetch(`${API_BASE}/users/resume`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('Resume uploaded and parsed successfully!');
            
            // Display parsed data
            const resultDiv = document.getElementById('resumeParseResult');
            resultDiv.innerHTML = `
                <h4>Parsed Resume Data:</h4>
                <p><strong>Skills found:</strong> ${result.parsed_data.skills.join(', ')}</p>
                <p><strong>Summary:</strong> ${result.parsed_data.summary}</p>
            `;
            
            // Reload profile to show updated data
            loadProfile();
        } else {
            showMessage(result.error || 'Failed to upload resume', 'error');
        }
    } catch (error) {
        showMessage('Network error', 'error');
    }
}

// Interview Preparation
async function getInterviewPrep(jobId) {
    try {
        const response = await fetch(`${API_BASE}/ai/interview-prep/${jobId}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Create a modal or alert with interview prep
            const prepContent = `
Interview Preparation for ${data.job_title} at ${data.company_name}

POTENTIAL QUESTIONS:
${data.questions.map((q, i) => `${i + 1}. ${q}`).join('\n')}

PREPARATION TIPS:
${data.tips.map((t, i) => `${i + 1}. ${t}`).join('\n')}
            `;
            
            alert(prepContent);
        } else {
            showMessage('Failed to get interview prep', 'error');
        }
    } catch (error) {
        showMessage('Network error', 'error');
    }
}

// Update the displayApplications function to include interview prep button
function displayApplicationsWithPrep(applications) {
    const applicationsList = document.getElementById('applicationsList');
    
    if (applications.length === 0) {
        applicationsList.innerHTML = '<p>No applications yet</p>';
        return;
    }
    
    applicationsList.innerHTML = applications.map(app => `
        <div class="job-card">
            <h3>${app.job.title}</h3>
            <p><strong>Company:</strong> ${app.job.company ? app.job.company.name : 'Unknown'}</p>
            <p><strong>Status:</strong> <span style="color: ${getStatusColor(app.status)}">${app.status}</span></p>
            <p><strong>Applied:</strong> ${new Date(app.applied_at).toLocaleDateString()}</p>
            ${app.match_score ? `<p><strong>Match Score:</strong> ${app.match_score.toFixed(1)}%</p>` : ''}
            ${app.status === 'shortlisted' || app.status === 'accepted' ? 
                `<button onclick="getInterviewPrep(${app.job.id})">Get Interview Prep</button>` : ''}
        </div>
    `).join('');
}

function getStatusColor(status) {
    const colors = {
        'pending': '#f39c12',
        'reviewing': '#3498db',
        'shortlisted': '#27ae60',
        'rejected': '#e74c3c',
        'accepted': '#27ae60',
        'withdrawn': '#95a5a6'
    };
    return colors[status] || '#000';
}

// Add this function to redirect based on user role
function redirectBasedOnRole(user) {
    if (user.role === 'employer') {
        window.location.href = '/employer';
    } else if (user.role === 'admin') {
        window.location.href = '/admin';
    }
}

// Update the showApp function to check role
function showAppWithRoleCheck() {
    if (currentUser.role === 'employer') {
        window.location.href = '/employer';
    } else if (currentUser.role === 'admin') {
        window.location.href = '/admin';
    } else {
        showApp();
    }
}
