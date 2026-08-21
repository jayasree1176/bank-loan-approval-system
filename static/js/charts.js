/**
 * Chart.js Visualizations for Bank Loan Intelligence System
 */

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('statusChart')) {
        loadAnalyticsCharts();
    }
});

function loadAnalyticsCharts() {
    fetch('/api/analytics-data')
        .then(response => response.json())
        .then(data => {
            renderStatusChart(data.status_distribution);
            renderRiskChart(data.risk_distribution);
            renderCreditScoreChart(data.credit_score_distribution);
            renderTrendChart(data.monthly_trends);
            renderPurposeChart(data.loan_purposes);
        })
        .catch(err => console.error("Error loading analytics data:", err));
}

// 1. Approval vs Rejection Doughnut Chart
function renderStatusChart(statusData) {
    const ctx = document.getElementById('statusChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Approved', 'Rejected'],
            datasets: [{
                data: [statusData.approved, statusData.rejected],
                backgroundColor: ['#10b981', '#ef4444'],
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

// 2. Risk Distribution Pie Chart
function renderRiskChart(riskData) {
    const ctx = document.getElementById('riskChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Low Risk', 'Medium Risk', 'High Risk'],
            datasets: [{
                data: [riskData.low, riskData.medium, riskData.high],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

// 3. Credit Score Distribution Bar Chart
function renderCreditScoreChart(scoreData) {
    const ctx = document.getElementById('creditScoreChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(scoreData),
            datasets: [{
                label: 'Applicant Count',
                data: Object.values(scoreData),
                backgroundColor: '#2563eb',
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

// 4. Monthly Trends Line Chart
function renderTrendChart(trendData) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: trendData.labels,
            datasets: [{
                label: 'Loan Applications',
                data: trendData.counts,
                borderColor: '#1e3a8a',
                backgroundColor: 'rgba(30, 58, 138, 0.1)',
                fill: true,
                tension: 0.3,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

// 5. Loan Purpose Horizontal Bar Chart
function renderPurposeChart(purposeData) {
    const ctx = document.getElementById('purposeChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(purposeData),
            datasets: [{
                label: 'Applications',
                data: Object.values(purposeData),
                backgroundColor: '#0284c7',
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
                legend: { display: false }
            }
        }
    });
}
