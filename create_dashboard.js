// Enhanced Dashboard with AI Integration

function showDashboard() {
    const dashboardHTML = `
        <div class="section">
            <div class="dashboard-header">
                <h2>🤖 AI-Powered Dashboard</h2>
                <div class="ai-status" id="aiStatus">
                    <span class="loading">Checking AI status...</span>
                </div>
            </div>
            
            <!-- Key Metrics -->
            <div class="metrics-grid">
                <div class="stat-card ai-enabled">
                    <div class="stat-icon">🎯</div>
                    <h3>Profile Completeness</h3>
                    <div id="profileScore" class="stat-value">--%</div>
                    <div id="profileSuggestion" class="stat-subtitle">Loading...</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <h3>Applications</h3>
                    <div id="applicationCount" class="stat-value">0</div>
                    <div class="stat-subtitle">Total submitted</div>
                </div>
                <div class="stat-card ai-enabled">
                    <div class="stat-icon">🔍</div>
                    <h3>AI Matches</h3>
                    <div id="matchCount" class="stat-value">0</div>
                    <div class="stat-subtitle">Jobs found</div>
                </div>
                <div class="stat-card ai-enabled">
                    <div class="stat-icon">⭐</div>
                    <h3>Avg Match Score</h3>
                    <div id="avgMatchScore" class="stat-value">--%</div>
                    <div class="stat-subtitle">AI compatibility</div>
                </div>
            </div>
            
            <!-- AI Actions -->
            <div class="ai-actions">
                <button class="ai-btn primary" onclick="findAIMatches()">
                    🤖 Find AI Matches
                </button>
                <button class="ai-btn secondary" onclick="analyzeProfile()">
                    📊 Analyze Profile
                </button>
                <button class="ai-btn secondary" onclick="showMatchHistory()">
                    📈 Match History
                </button>
            </div>
            
            <!-- Application Status Chart -->
            <div class="chart-section">
                <h3>📋 Application Status</h3>
                <div id="statusChart" class="chart-container"></div>
            </div>
            
            <!-- AI Insights -->
            <div class="insights-section">
                <h3>🧠 AI Insights</h3>
                <div id="aiInsights" class="insights-container">
                    <div class="loading">Loading AI insights...</div>
                </div>
            </div>
            
            <!-- Recent Activity -->
            <div class="activity-section">
                <h3>🕒 Recent Activity</h3>
                <div id="recentActivity" class="activity-container"></div>
            </div>
        </div>
    `;
    
    // Add dashboard tab if it doesn't exist
    const tabContainer = document.querySelector('#appSection .tab-container');
    if (!document.getElementById('dashboardTab')) {
        tabContainer.innerHTML = `
            <div class="tab active" onclick="showAppTab('dashboard')">🤖 AI Dashboard</div>
        ` + tabContainer.innerHTML;
        
        const appSection = document.getElementById('appSection');
        const dashboardDiv = document.createElement('div');
        dashboardDiv.id = 'dashboardTab';
        dashboardDiv.className = 'tab-content active';
        dashboardDiv.innerHTML = dashboardHTML;
        appSection.appendChild(dashboardDiv);
    }
    
    // Load dashboard data
    loadDashboardData();
    checkAIStatus();
}

async function checkAIStatus() {
    try {
        const response = await fetch(`${API_BASE}/ai/model-status`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const status = await response.json();
            const aiStatusEl = document.getElementById('aiStatus');
            
            const totalModels = Object.values(status).filter(s => s.loaded).length;
            if (totalModels === 3) {
                aiStatusEl.innerHTML = `<span class="status-success">✅ AI Fully Operational</span>`;
            } else if (totalModels > 0) {
                aiStatusEl.innerHTML = `<span class="status-warning">⚠️ AI Partially Available</span>`;
            } else {
                aiStatusEl.innerHTML = `<span class="status-error">❌ AI Models Not Loaded</span>`;
            }
        }
    } catch (error) {
        console.error('AI status check failed:', error);
        document.getElementById('aiStatus').innerHTML = `<span class="status-error">❌ AI Status Unknown</span>`;
    }
}

async function loadDashboardData() {
    try {
        // Load profile analysis with AI insights
        await loadProfileAnalysis();
        
        // Load application status
        await loadApplicationStatus();
        
        // Load AI match data
        await loadMatchData();
        
        // Load recent activity
        await loadRecentActivity();
        
    } catch (error) {
        console.error('Dashboard loading error:', error);
    }
}

async function loadProfileAnalysis() {
    try {
        const response = await fetch(`${API_BASE}/ai/analyze-profile`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Update profile score
            document.getElementById('profileScore').textContent = `${data.profile_completeness}%`;
            
            // Update suggestion
            const suggestionEl = document.getElementById('profileSuggestion');
            if (data.suggestions.length > 0) {
                suggestionEl.textContent = data.suggestions[0];
                suggestionEl.className = 'stat-subtitle suggestion';
            } else {
                suggestionEl.textContent = 'Profile complete!';
                suggestionEl.className = 'stat-subtitle success';
            }
            
            // Update AI insights
            updateAIInsights(data);
        }
    } catch (error) {
        console.error('Profile analysis error:', error);
    }
}

async function loadApplicationStatus() {
    try {
        const response = await fetch(`${API_BASE}/applications/status`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            document.getElementById('applicationCount').textContent = data.total_applications || 0;
            
            // Create status chart
            createStatusChart(data.status_summary || {});
        }
    } catch (error) {
        console.error('Application status error:', error);
    }
}

async function loadMatchData() {
    try {
        const response = await fetch(`${API_BASE}/ai/match-jobs`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ min_match_score: 0 })
        });
        
        if (response.ok) {
            const data = await response.json();
            document.getElementById('matchCount').textContent = data.total_matches || 0;
            
            // Calculate average match score
            if (data.matches && data.matches.length > 0) {
                const avgScore = data.matches.reduce((sum, m) => sum + m.scores.overall, 0) / data.matches.length;
                document.getElementById('avgMatchScore').textContent = `${avgScore.toFixed(1)}%`;
            } else {
                document.getElementById('avgMatchScore').textContent = '--';
            }
        }
    } catch (error) {
        console.error('Match data error:', error);
        // Set default values on error
        document.getElementById('matchCount').textContent = '--';
        document.getElementById('avgMatchScore').textContent = '--';
    }
}

async function loadRecentActivity() {
    try {
        const response = await fetch(`${API_BASE}/ai/match-history`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            const activityEl = document.getElementById('recentActivity');
            
            if (data.matches && data.matches.length > 0) {
                activityEl.innerHTML = data.matches.slice(0, 5).map(match => `
                    <div class="activity-item">
                        <div class="activity-icon">🎯</div>
                        <div class="activity-content">
                            <div class="activity-title">Matched with ${match.job.title}</div>
                            <div class="activity-meta">
                                Score: ${match.match_score.toFixed(1)}% • 
                                ${formatTimeAgo(match.created_at)}
                            </div>
                        </div>
                    </div>
                `).join('');
            } else {
                activityEl.innerHTML = '<div class="no-data">No recent AI matches. Try finding matches!</div>';
            }
        }
    } catch (error) {
        console.error('Recent activity error:', error);
        document.getElementById('recentActivity').innerHTML = '<div class="error">Unable to load recent activity</div>';
    }
}

function createStatusChart(statusSummary) {
    const chartEl = document.getElementById('statusChart');
    const total = Object.values(statusSummary).reduce((sum, count) => sum + count, 0);
    
    if (total === 0) {
        chartEl.innerHTML = '<div class="no-data">No applications yet</div>';
        return;
    }
    
    chartEl.innerHTML = Object.entries(statusSummary)
        .map(([status, count]) => {
            const percentage = (count / total * 100).toFixed(1);
            return `
                <div class="status-bar">
                    <div class="status-label">
                        <span class="status-name">${status.replace('_', ' ')}</span>
                        <span class="status-count">${count}</span>
                    </div>
                    <div class="status-progress">
                        <div class="status-fill ${status}" style="width: ${percentage}%"></div>
                    </div>
                </div>
            `;
        }).join('');
}

function updateAIInsights(profileData) {
    const insightsEl = document.getElementById('aiInsights');
    
    const insights = [];
    
    // Profile completeness insights
    if (profileData.profile_completeness < 50) {
        insights.push({
            type: 'warning',
            title: 'Profile Needs Attention',
            message: 'Complete your profile to unlock AI-powered job matching'
        });
    } else if (profileData.profile_completeness < 80) {
        insights.push({
            type: 'info',
            title: 'Almost Ready',
            message: 'A few more details will optimize your AI match results'
        });
    } else {
        insights.push({
            type: 'success',
            title: 'AI-Ready Profile',
            message: 'Your profile is optimized for AI-powered job matching'
        });
    }
    
    // Suggestions as insights
    profileData.suggestions.slice(0, 2).forEach(suggestion => {
        insights.push({
            type: 'tip',
            title: 'AI Suggestion',
            message: suggestion
        });
    });
    
    if (insights.length === 0) {
        insightsEl.innerHTML = '<div class="no-data">All insights look good! 🎉</div>';
        return;
    }
    
    insightsEl.innerHTML = insights.map(insight => `
        <div class="insight-item ${insight.type}">
            <div class="insight-icon">${getInsightIcon(insight.type)}</div>
            <div class="insight-content">
                <div class="insight-title">${insight.title}</div>
                <div class="insight-message">${insight.message}</div>
            </div>
        </div>
    `).join('');
}

function getInsightIcon(type) {
    const icons = {
        'success': '✅',
        'warning': '⚠️',
        'info': 'ℹ️',
        'tip': '💡',
        'error': '❌'
    };
    return icons[type] || '📊';
}

async function findAIMatches() {
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = '🔍 Finding Matches...';
    button.disabled = true;
    
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
            
            // Show results
            showNotification(`🎯 Found ${data.total_matches} AI-powered matches!`, 'success');
            
            // Refresh match data
            await loadMatchData();
            
            // Switch to jobs tab to show results
            showAppTab('jobSearch');
        } else {
            const error = await response.json();
            showNotification(`❌ ${error.error}`, 'error');
        }
    } catch (error) {
        console.error('AI matching error:', error);
        showNotification('❌ Failed to find AI matches', 'error');
    } finally {
        button.textContent = originalText;
        button.disabled = false;
    }
}

async function analyzeProfile() {
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = '🔍 Analyzing...';
    button.disabled = true;
    
    try {
        await loadProfileAnalysis();
        showNotification('📊 Profile analysis updated!', 'success');
    } catch (error) {
        showNotification('❌ Failed to analyze profile', 'error');
    } finally {
        button.textContent = originalText;
        button.disabled = false;
    }
}

async function showMatchHistory() {
    try {
        const response = await fetch(`${API_BASE}/ai/match-history`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Create modal with match history
            const modal = createModal('AI Match History', `
                <div class="match-history">
                    ${data.matches.length > 0 ? 
                        data.matches.map(match => `
                            <div class="match-item">
                                <div class="match-job">
                                    <h4>${match.job.title}</h4>
                                    <p>${match.job.company?.name || 'Company'}</p>
                                </div>
                                <div class="match-scores">
                                    <div class="score-item">
                                        <span class="score-label">Overall</span>
                                        <span class="score-value">${match.match_score.toFixed(1)}%</span>
                                    </div>
                                    <div class="score-item">
                                        <span class="score-label">Skills</span>
                                        <span class="score-value">${match.skill_match_score.toFixed(1)}%</span>
                                    </div>
                                    <div class="score-item">
                                        <span class="score-label">Experience</span>
                                        <span class="score-value">${match.experience_match_score.toFixed(1)}%</span>
                                    </div>
                                </div>
                                <div class="match-date">${formatTimeAgo(match.created_at)}</div>
                            </div>
                        `).join('') :
                        '<div class="no-data">No match history yet. Try finding AI matches!</div>'
                    }
                </div>
            `);
            
            document.body.appendChild(modal);
        }
    } catch (error) {
        showNotification('❌ Failed to load match history', 'error');
    }
}

function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffDays > 0) {
        return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else if (diffHours > 0) {
        return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else {
        return 'Just now';
    }
}

function getStatusColor(status) {
    const colors = {
        'pending': '#f39c12',
        'reviewed': '#3498db',
        'interviewing': '#9b59b6',
        'accepted': '#27ae60',
        'rejected': '#e74c3c'
    };
    return colors[status] || '#95a5a6';
}

// Enhanced CSS for AI dashboard
const dashboardStyles = `
    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .ai-status .status-success { color: #27ae60; }
    .ai-status .status-warning { color: #f39c12; }
    .ai-status .status-error { color: #e74c3c; }
    .ai-status .loading { color: #3498db; }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .stat-card {
        background: white;
        border: 1px solid #ddd;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    .stat-card.ai-enabled {
        border-left: 4px solid #3498db;
    }
    
    .stat-icon {
        font-size: 2em;
        margin-bottom: 10px;
    }
    
    .stat-card h3 {
        margin: 0 0 10px 0;
        color: #2c3e50;
        font-size: 0.9em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stat-value {
        font-size: 2.5em;
        font-weight: bold;
        color: #3498db;
        margin-bottom: 5px;
    }
    
    .stat-subtitle {
        font-size: 0.8em;
        color: #7f8c8d;
    }
    
    .stat-subtitle.suggestion {
        color: #f39c12;
        font-weight: 500;
    }
    
    .stat-subtitle.success {
        color: #27ae60;
        font-weight: 500;
    }
    
    .ai-actions {
        display: flex;
        gap: 15px;
        margin-bottom: 30px;
        flex-wrap: wrap;
    }
    
    .ai-btn {
        padding: 12px 24px;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 0.9em;
    }
    
    .ai-btn.primary {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
    }
    
    .ai-btn.primary:hover {
        background: linear-gradient(135deg, #2980b9, #21618c);
        transform: translateY(-1px);
    }
    
    .ai-btn.secondary {
        background: #f8f9fa;
        color: #2c3e50;
        border: 1px solid #dee2e6;
    }
    
    .ai-btn.secondary:hover {
        background: #e9ecef;
        transform: translateY(-1px);
    }
    
    .chart-section, .insights-section, .activity-section {
        background: white;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .chart-section h3, .insights-section h3, .activity-section h3 {
        margin: 0 0 20px 0;
        color: #2c3e50;
    }
    
    .status-bar {
        margin-bottom: 15px;
    }
    
    .status-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
        font-size: 0.9em;
    }
    
    .status-name {
        text-transform: capitalize;
        color: #2c3e50;
    }
    
    .status-count {
        font-weight: bold;
        color: #7f8c8d;
    }
    
    .status-progress {
        height: 8px;
        background: #ecf0f1;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .status-fill {
        height: 100%;
        transition: width 0.3s ease;
    }
    
    .status-fill.pending { background: #f39c12; }
    .status-fill.reviewed { background: #3498db; }
    .status-fill.interviewing { background: #9b59b6; }
    .status-fill.accepted { background: #27ae60; }
    .status-fill.rejected { background: #e74c3c; }
    
    .insight-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    
    .insight-item.success { background: #d5f4e6; }
    .insight-item.warning { background: #fef9e7; }
    .insight-item.info { background: #e3f2fd; }
    .insight-item.tip { background: #fff3e0; }
    
    .insight-icon {
        font-size: 1.2em;
        margin-top: 2px;
    }
    
    .insight-title {
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 4px;
    }
    
    .insight-message {
        color: #5d6d7e;
        font-size: 0.9em;
        line-height: 1.4;
    }
    
    .activity-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 0;
        border-bottom: 1px solid #f1f2f6;
    }
    
    .activity-item:last-child {
        border-bottom: none;
    }
    
    .activity-icon {
        font-size: 1.2em;
        width: 32px;
        text-align: center;
    }
    
    .activity-title {
        font-weight: 500;
        color: #2c3e50;
    }
    
    .activity-meta {
        font-size: 0.8em;
        color: #7f8c8d;
        margin-top: 2px;
    }
    
    .no-data, .error {
        text-align: center;
        color: #7f8c8d;
        font-style: italic;
        padding: 20px;
    }
    
    .error {
        color: #e74c3c;
    }
    
    .loading {
        color: #3498db;
        font-style: italic;
    }
`;

// Add enhanced styles
if (!document.getElementById('dashboardStyles')) {
    const style = document.createElement('style');
    style.id = 'dashboardStyles';
    style.textContent = dashboardStyles;
    document.head.appendChild(style);
}