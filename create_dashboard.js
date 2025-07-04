// Add this to app.js

function showDashboard() {
    const dashboardHTML = `
        <div class="section">
            <h2>Dashboard</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <div class="stat-card">
                    <h3>Profile Completeness</h3>
                    <div id="profileScore" style="font-size: 2em; color: #3498db;">--%</div>
                </div>
                <div class="stat-card">
                    <h3>Applications</h3>
                    <div id="applicationCount" style="font-size: 2em; color: #27ae60;">0</div>
                </div>
                <div class="stat-card">
                    <h3>Matches Found</h3>
                    <div id="matchCount" style="font-size: 2em; color: #e74c3c;">0</div>
                </div>
                <div class="stat-card">
                    <h3>Average Match Score</h3>
                    <div id="avgMatchScore" style="font-size: 2em; color: #f39c12;">--%</div>
                </div>
            </div>
            
            <h3 style="margin-top: 30px;">Application Status</h3>
            <div id="statusChart"></div>
            
            <h3 style="margin-top: 30px;">Recent Activity</h3>
            <div id="recentActivity"></div>
        </div>
    `;
    
    // Add dashboard tab
    const tabContainer = document.querySelector('#appSection .tab-container');
    if (!document.getElementById('dashboardTab')) {
        tabContainer.innerHTML = `
            <div class="tab" onclick="showAppTab('dashboard')">Dashboard</div>
        ` + tabContainer.innerHTML;
        
        const appSection = document.getElementById('appSection');
        const dashboardDiv = document.createElement('div');
        dashboardDiv.id = 'dashboardTab';
        dashboardDiv.className = 'tab-content';
        dashboardDiv.innerHTML = dashboardHTML;
        appSection.appendChild(dashboardDiv);
    }
    
    loadDashboardData();
}

async function loadDashboardData() {
    try {
        // Get profile analysis
        const profileResponse = await fetch(`${API_BASE}/ai/analyze-profile`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (profileResponse.ok) {
            const profileData = await profileResponse.json();
            document.getElementById('profileScore').textContent = `${profileData.profile_completeness}%`;
        }
        
        // Get application status
        const statusResponse = await fetch(`${API_BASE}/applications/status`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (statusResponse.ok) {
            const statusData = await statusResponse.json();
            document.getElementById('applicationCount').textContent = statusData.total_applications;
            
            // Create simple status chart
            const statusChart = document.getElementById('statusChart');
            statusChart.innerHTML = Object.entries(statusData.status_summary)
                .map(([status, count]) => `
                    <div style="margin: 10px 0;">
                        <span style="text-transform: capitalize;">${status}:</span>
                        <span style="font-weight: bold;">${count}</span>
                        <div style="background: #ecf0f1; height: 20px; margin-top: 5px;">
                            <div style="background: ${getStatusColor(status)}; height: 100%; width: ${(count/statusData.total_applications*100)}%;"></div>
                        </div>
                    </div>
                `).join('');
        }
        
        // Get recent matches
        const matchResponse = await fetch(`${API_BASE}/ai/match-jobs`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ min_match_score: 0 })
        });
        if (matchResponse.ok) {
            const matchData = await matchResponse.json();
            document.getElementById('matchCount').textContent = matchData.total_matches;
            
            // Calculate average match score
            if (matchData.matches.length > 0) {
                const avgScore = matchData.matches.reduce((sum, m) => sum + m.scores.overall, 0) / matchData.matches.length;
                document.getElementById('avgMatchScore').textContent = `${avgScore.toFixed(1)}%`;
            }
        }
    } catch (error) {
        console.error('Dashboard error:', error);
    }
}

// Add CSS for stat cards
const style = document.createElement('style');
style.textContent = `
    .stat-card {
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stat-card h3 {
        margin: 0 0 10px 0;
        color: #2c3e50;
        font-size: 1em;
    }
`;
document.head.appendChild(style);
