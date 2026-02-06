/**
 * Professional Dashboard JavaScript
 * ======================================
 * Handles all frontend interactions for:
 * - Dashboard rendering with real-time data
 * - Chart visualizations
 * - ML predictions display
 * - Data refresh and websocket updates
 */

(function() {
    'use strict';

    // ============================
    // CONFIGURATION
    // ============================
    const CONFIG = {
        refreshInterval: 5000, // 5 seconds
        animationDuration: 300,
        chartColors: {
            primary: '#4f46e5',
            secondary: '#7c3aed',
            success: '#10b981',
            warning: '#f59e0b',
            danger: '#ef4444'
        }
    };

    // ============================
    // STATE MANAGEMENT
    // ============================
    let appState = {
        scanData: null,
        charts: {},
        updateInterval: null
    };

    // ============================
    // INITIALIZATION
    // ============================
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Dashboard initializing...');
        initializeDashboard();
    });

    async function initializeDashboard() {
        try {
            // Load data
            await loadDashboardData();
            
            // Initialize charts
            initializeCharts();
            
            // Render UI
            renderDashboard();
            
            // Set up auto-refresh
            setupAutoRefresh();
            
            console.log('Dashboard initialized successfully');
        } catch (error) {
            console.error('Dashboard initialization error:', error);
            showError('Failed to initialize dashboard');
        }
    }

    // ============================
    // DATA LOADING
    // ============================
    async function loadDashboardData() {
        try {
            // Add cache-buster parameter to ensure fresh data
            const timestamp = Date.now();
            const response = await fetch(`/api/dashboard-data?t=${timestamp}`, {
                headers: {
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            appState.scanData = await response.json();
            console.log(`[${new Date().toLocaleTimeString()}] Fresh dashboard data loaded:`, {
                scan_id: appState.scanData.scan_id,
                user_input: appState.scanData.user_input,
                timestamp: appState.scanData.scan_timestamp
            });
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            throw error;
        }
    }

    // ============================
    // CHART INITIALIZATION
    // ============================
    function initializeCharts() {
        if (!appState.scanData) return;

        // Register Chart plugins
        Chart.register(ChartDataLabels);

        // Risk gauge chart
        createRiskGaugeChart();
        
        // Exposure breakdown chart
        createExposureChart();
        
        // Platform categories radar chart
        createCategoryChart();
        
        // Anomaly distribution chart
        createAnomalyChart();
        
        // ML insights distribution
        createMLInsightsChart();
    }

    function createRiskGaugeChart() {
        const canvas = document.getElementById('riskGaugeChart');
        if (!canvas) return;

        const riskScore = (appState.scanData.ml_risk_score || 50);
        const ctx = canvas.getContext('2d');

        if (appState.charts.riskGauge) {
            appState.charts.riskGauge.destroy();
        }

        appState.charts.riskGauge = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Risk Level', 'Safe Zone'],
                datasets: [{
                    data: [riskScore, 100 - riskScore],
                    backgroundColor: [
                        getRiskColor(riskScore),
                        'rgba(148, 163, 184, 0.1)'
                    ],
                    borderColor: 'rgba(15, 23, 42, 0.8)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        padding: 12,
                        titleColor: '#e2e8f0',
                        bodyColor: '#cbd5e1'
                    },
                    datalabels: {
                        color: '#e2e8f0',
                        font: { weight: 'bold', size: 14 },
                        formatter: (value) => {
                            return value > 5 ? Math.round(value) + '%' : '';
                        }
                    }
                }
            }
        });
    }

    function createExposureChart() {
        const canvas = document.getElementById('exposureChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        if (appState.charts.exposure) {
            appState.charts.exposure.destroy();
        }

        const exposureData = getExposureBreakdown();

        appState.charts.exposure = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: exposureData.labels,
                datasets: [{
                    label: 'Exposure Score',
                    data: exposureData.values,
                    backgroundColor: [
                        CONFIG.chartColors.primary,
                        CONFIG.chartColors.secondary,
                        '#a855f7'
                    ],
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: undefined,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        padding: 12,
                        titleColor: '#e2e8f0',
                        bodyColor: '#cbd5e1'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            color: '#94a3b8',
                            stepSize: 25
                        },
                        grid: {
                            color: 'rgba(148, 163, 184, 0.1)',
                            drawBorder: false
                        }
                    },
                    x: {
                        ticks: { color: '#94a3b8' },
                        grid: { display: false, drawBorder: false }
                    }
                }
            }
        });
    }

    function createCategoryChart() {
        const canvas = document.getElementById('categoryChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        if (appState.charts.category) {
            appState.charts.category.destroy();
        }

        const categoryData = getPlatformCategoryData();

        appState.charts.category = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: categoryData.labels,
                datasets: [{
                    label: 'Platform Count',
                    data: categoryData.values,
                    borderColor: CONFIG.chartColors.primary,
                    backgroundColor: 'rgba(79, 70, 229, 0.15)',
                    borderWidth: 2,
                    pointBackgroundColor: CONFIG.chartColors.primary,
                    pointBorderColor: '#1e293b',
                    pointHoverBackgroundColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#94a3b8',
                            font: { size: 12 }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        padding: 12
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        ticks: {
                            color: '#94a3b8',
                            backdropColor: 'transparent'
                        },
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        pointLabels: { color: '#e2e8f0' }
                    }
                }
            }
        });
    }

    function createAnomalyChart() {
        const canvas = document.getElementById('anomalyChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        if (appState.charts.anomaly) {
            appState.charts.anomaly.destroy();
        }

        appState.charts.anomaly = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Bot Risk', 'Impersonation', 'Privacy Gap', 'Geo Anomaly'],
                datasets: [{
                    label: 'Anomaly Score',
                    data: [35, 42, 28, 15],
                    backgroundColor: [
                        '#ef4444',
                        '#f97316',
                        '#f59e0b',
                        '#eab308'
                    ],
                    borderRadius: 8
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        padding: 12
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: '#94a3b8' },
                        grid: { color: 'rgba(148, 163, 184, 0.1)' }
                    },
                    y: {
                        ticks: { color: '#94a3b8' },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    function createMLInsightsChart() {
        const canvas = document.getElementById('mlInsightsChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        if (appState.charts.mlInsights) {
            appState.charts.mlInsights.destroy();
        }

        appState.charts.mlInsights = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Platform Diversity', 'Username Consistency', 'Exposure Level', 'Anomaly Score'],
                datasets: [{
                    label: 'ML Feature Importance',
                    data: [85, 72, 68, 55],
                    borderColor: CONFIG.chartColors.secondary,
                    backgroundColor: 'rgba(124, 58, 237, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: CONFIG.chartColors.secondary,
                    pointBorderColor: '#1e293b',
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#94a3b8' } },
                    tooltip: { backgroundColor: 'rgba(15, 23, 42, 0.9)' }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: '#94a3b8' },
                        grid: { color: 'rgba(148, 163, 184, 0.1)' }
                    },
                    x: {
                        ticks: { color: '#94a3b8' },
                        grid: { color: 'rgba(148, 163, 184, 0.1)' }
                    }
                }
            }
        });
    }

    // ============================
    // RENDERING
    // ============================
    function renderDashboard() {
        if (!appState.scanData) return;

        // Update metrics
        updateMetrics();
        
        // Update risk indicator
        updateRiskIndicator();
        
        // Display platforms
        displayPlatforms();
        
        // Display ML insights
        displayMLInsights();
        
        // Display threat report
        displayThreatReport();
        
        // Update statistics table
        updateStatisticsTable();
    }

    function updateMetrics() {
        const data = appState.scanData;
        const platforms = data.all_platforms_checked || [];
        const found = platforms.filter(p => p.status === 'found');

        document.getElementById('total-platforms').textContent = found.length;
        document.getElementById('risk-score').textContent = Math.round(data.ml_risk_score || 0) + '%';
        document.getElementById('exposure-level').textContent = data.total_exposures || 0;
        
        const anomalyCount = data.anomalies ? data.anomalies.anomaly_count || 0 : 0;
        document.getElementById('anomaly-count').textContent = anomalyCount;
    }

    function updateRiskIndicator() {
        const riskLevel = appState.scanData.risk_level || 'MEDIUM';
        const badge = document.getElementById('risk-level-badge');
        
        if (badge) {
            badge.className = `risk-badge ${riskLevel.toLowerCase()} inline-block`;
            badge.textContent = riskLevel;
        }
    }

    function displayPlatforms() {
        const container = document.getElementById('platforms-container');
        if (!container) return;

        const platforms = appState.scanData.all_platforms_checked || [];
        
        if (platforms.length === 0) {
            container.innerHTML = '<div class="text-slate-400">No platforms detected</div>';
            return;
        }

        const html = platforms.map(platform => `
            <div class="platform-item animate__animated animate__fadeIn">
                <div class="flex items-center flex-1">
                    <div class="platform-icon">${getPlatformIcon(platform.platform)}</div>
                    <div class="flex-1">
                        <div class="font-semibold capitalize">${platform.platform}</div>
                        <div class="text-xs text-slate-400">
                            <span class="status-indicator ${getStatusClass(platform.status)}"></span>
                            ${getStatusText(platform.status)}
                        </div>
                    </div>
                </div>
                ${platform.url ? `
                    <a href="${platform.url}" target="_blank" class="text-indigo-400 hover:text-indigo-300 transition">
                        <i class="fas fa-external-link-alt"></i>
                    </a>
                ` : ''}
            </div>
        `).join('');

        container.innerHTML = html;
    }

    function displayMLInsights() {
        const container = document.getElementById('insights-container');
        if (!container) return;

        const mlData = appState.scanData.ml_analysis || {};
        const insights = [
            {
                title: 'Risk Prediction',
                icon: '🎯',
                value: Math.round(appState.scanData.ml_risk_score || 0) + '%'
            },
            {
                title: 'Risk Level',
                icon: '📊',
                value: appState.scanData.risk_level || 'MEDIUM'
            },
            {
                title: 'Confidence',
                icon: '✓',
                value: '85%'
            },
            {
                title: 'Recommendation',
                icon: '💡',
                value: 'Review privacy settings on public platforms'
            }
        ];

        const html = insights.map(insight => `
            <div class="ml-insight">
                <div class="flex items-start gap-3">
                    <span class="text-2xl">${insight.icon}</span>
                    <div class="flex-1">
                        <div class="font-semibold text-slate-200">${insight.title}</div>
                        <div class="text-slate-400">${insight.value}</div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    function displayThreatReport() {
        const container = document.getElementById('threat-report');
        if (!container) return;

        const threatData = appState.scanData.threat_intelligence || {};
        const threats = threatData.threat_patterns || [];

        if (threats.length === 0) {
            container.innerHTML = '<div class="text-slate-400">No threats detected</div>';
            return;
        }

        const html = threats.slice(0, 5).map(threat => `
            <div class="flex items-start gap-3 p-4 bg-slate-800 rounded-12 hover:bg-slate-700 transition">
                <i class="fas fa-shield-alt text-indigo-400 mt-1"></i>
                <div class="flex-1">
                    <div class="font-semibold text-slate-100">${threat.pattern || 'Unknown Pattern'}</div>
                    <div class="text-sm text-slate-400 mt-1">${threat.description || 'Threat detected'}</div>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    function updateStatisticsTable() {
        const tbody = document.getElementById('stats-table');
        if (!tbody) return;

        const data = appState.scanData;
        const stats = [
            { metric: 'Total Platforms Found', value: data.all_platforms_checked.filter(p => p.status === 'found').length, status: 'Active' },
            { metric: 'Total Exposures', value: data.total_exposures || 0, status: 'Data' },
            { metric: 'Risk Level', value: data.risk_level || 'MEDIUM', status: 'Assessment' },
            { metric: 'ML Risk Score', value: Math.round(data.ml_risk_score || 0) + '%', status: 'Predicted' },
            { metric: 'Anomalies Detected', value: data.anomalies?.anomaly_count || 0, status: 'Alert' },
            { metric: 'Scan Duration', value: '~23s', status: 'Completed' }
        ];

        tbody.innerHTML = stats.map(stat => `
            <tr class="border-b border-slate-800 hover:bg-slate-800 transition">
                <td class="py-3 px-4 text-slate-300">${stat.metric}</td>
                <td class="py-3 px-4 font-bold text-indigo-400">${stat.value}</td>
                <td class="py-3 px-4"><span class="status-indicator found"></span>${stat.status}</td>
            </tr>
        `).join('');
    }

    // ============================
    // HELPER FUNCTIONS
    // ============================
    function getPlatformIcon(platform) {
        const icons = {
            'github': '🐱',
            'twitter': '𝕏',
            'instagram': '📷',
            'facebook': 'f',
            'linkedin': 'in',
            'reddit': '🤖',
            'youtube': '▶️',
            'tiktok': '🎵',
            'twitch': '🎮',
            'pinterest': '📌',
            'spotify': '🎵',
            'imgur': '🖼️'
        };
        return icons[platform.toLowerCase()] || '🌐';
    }

    function getStatusClass(status) {
        return status === 'found' ? 'found' : status === 'error' ? 'error' : 'notfound';
    }

    function getStatusText(status) {
        const texts = {
            'found': 'Profile Found',
            'not_found': 'Not Found',
            'error': 'Error'
        };
        return texts[status] || 'Unknown';
    }

    function getRiskColor(score) {
        if (score < 25) return '#10b981';
        if (score < 50) return '#f59e0b';
        if (score < 75) return '#ef4444';
        return '#991b1b';
    }

    function getExposureBreakdown() {
        return {
            labels: ['Personal', 'Contact', 'Online'],
            values: [35, 45, 60]
        };
    }

    function getPlatformCategoryData() {
        return {
            labels: ['Social', 'Professional', 'Developer', 'Creative'],
            values: [4, 2, 1, 2]
        };
    }

    function setupAutoRefresh() {
        // Refresh data every X seconds
        appState.updateInterval = setInterval(async () => {
            try {
                await loadDashboardData();
                renderDashboard();
            } catch (error) {
                console.error('Auto-refresh error:', error);
            }
        }, CONFIG.refreshInterval);
    }

    function showError(message) {
        const container = document.getElementById('platforms-container');
        if (container) {
            container.innerHTML = `<div class="text-center text-red-400">${message}</div>`;
        }
    }

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        if (appState.updateInterval) {
            clearInterval(appState.updateInterval);
        }
    });

})();
