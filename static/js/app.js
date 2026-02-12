// Global State
let currentTab = 'sales-entry';
let menuItems = [];
let charts = {};

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    updateDateTime();
    setInterval(updateDateTime, 1000);
    loadMenuItems();
    setupTooltips();
});

function updateDateTime() {
    const now = new Date();
    const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' };
    document.getElementById('current-datetime').textContent = now.toLocaleDateString('en-US', options);
}

function navigateTo(tabId) {
    // Update active links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('onclick').includes(tabId)) {
            link.classList.add('active');
        }
    });

    // Toggle sections
    document.querySelectorAll('.dashboard-section').forEach(sec => {
        sec.classList.remove('active');
    });
    document.getElementById(tabId).classList.add('active');

    // Update title
    const titles = {
        'sales-entry': 'Sales Entry',
        'daily-view': 'Daily Dashboard',
        'monthly-view': 'Monthly Dashboard',
        'yearly-view': 'Yearly Dashboard',
        'time-view': 'Time Intelligence'
    };
    document.getElementById('page-title').textContent = titles[tabId];

    currentTab = tabId;

    // Load data for the specific tab
    if (tabId === 'daily-view') loadDailyDashboard();
    if (tabId === 'monthly-view') loadMonthlyDashboard();
    if (tabId === 'yearly-view') loadYearlyDashboard();
    if (tabId === 'time-view') loadTimeIntelligence();
}

// --- Sales Entry Logic ---

async function loadMenuItems() {
    try {
        const response = await fetch('/api/menu-items');
        menuItems = await response.json();
        renderMenu(menuItems);
    } catch (error) {
        showToast('Error loading menu items', 'danger');
    }
}

function renderMenu(items) {
    const container = document.getElementById('menu-container');
    container.innerHTML = '';

    items.forEach(item => {
        const card = document.createElement('div');
        card.className = `menu-item-card category-${item.category.toLowerCase().replace(/\s+/g, '-')}`;
        card.innerHTML = `
            <div class="fw-bold">${item.name}</div>
            <div class="text-muted extra-small mb-1">${item.category}</div>
            <div class="text-muted small mb-2" style="font-size: 0.75rem;">${item.description || ''}</div>
            <div class="fw-bold text-primary">₹${item.price.toFixed(2)}</div>
        `;
        card.onclick = () => recordSale(item.item_id, item.name);
        container.appendChild(card);
    });
}

function filterMenu(category) {
    // Update button states
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent === category) btn.classList.add('active');
    });

    if (category === 'All') {
        renderMenu(menuItems);
    } else {
        const filtered = menuItems.filter(item => item.category === category);
        renderMenu(filtered);
    }
}

async function recordSale(itemId, itemName) {
    try {
        const response = await fetch('/api/record-sale', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId })
        });

        if (response.ok) {
            showToast(`Success! Recorded sale for ${itemName}`, 'success');
        } else {
            showToast('Failed to record sale', 'danger');
        }
    } catch (error) {
        showToast('Server error', 'danger');
    }
}

// --- Dashboard Data Loading ---

async function loadDailyDashboard() {
    const response = await fetch('/api/daily-dashboard');
    const data = await response.json();

    const s = data.summary;
    document.getElementById('daily-revenue').textContent = `₹${s.total_revenue.toFixed(2)}`;
    document.getElementById('daily-profit').textContent = `₹${s.total_profit.toFixed(2)}`;
    document.getElementById('daily-orders').textContent = s.order_count;
    document.getElementById('daily-avg').textContent = `₹${(s.avg_order_value || 0).toFixed(2)}`;

    updateDailyCharts(data);
}

async function loadMonthlyDashboard() {
    const response = await fetch('/api/monthly-dashboard');
    const data = await response.json();

    document.getElementById('monthly-revenue').textContent = `₹${data.summary.total_revenue.toFixed(2)}`;
    document.getElementById('monthly-profit').textContent = `₹${data.summary.total_profit.toFixed(2)}`;
    document.getElementById('monthly-orders').textContent = data.summary.order_count;

    updateMonthlyCharts(data);
}

async function loadYearlyDashboard() {
    const response = await fetch('/api/yearly-dashboard');
    const data = await response.json();

    const s = data.summary;
    document.getElementById('yearly-revenue').textContent = `₹${s.total_revenue.toFixed(2)}`;
    document.getElementById('yearly-profit').textContent = `₹${s.total_profit.toFixed(2)}`;
    document.getElementById('yearly-orders').textContent = s.order_count;

    const margin = s.total_revenue > 0 ? (s.total_profit / s.total_revenue * 100).toFixed(1) : 0;
    document.getElementById('yearly-margin').textContent = `${margin}%`;

    updateYearlyCharts(data);
}

async function loadTimeIntelligence() {
    const response = await fetch('/api/time-intelligence');
    const data = await response.json();

    updateTimeIntelligenceCharts(data);
    renderTimeHeatmap(data);
}

// --- Chart Rendering ---

function updateDailyCharts(data) {
    // Time Slot Chart
    const timeLabels = data.time_slots.map(t => t._id);
    const timeCounts = data.time_slots.map(t => t.count);

    renderChart('dailyTimeChart', 'bar', timeLabels, timeCounts, 'Orders by Time Slot', '#6d4c41');

    // Category Chart
    const catLabels = data.categories.map(c => c._id);
    const catRevenue = data.categories.map(c => c.revenue);

    renderChart('dailyCategoryChart', 'doughnut', catLabels, catRevenue, 'Revenue by Category', ['#6d4c41', '#8d6e63', '#ffab91', '#4caf50', '#ff9800']);
}

function updateMonthlyCharts(data) {
    const labels = data.trend.map(t => t._id.split('-')[2]); // Just day
    const values = data.trend.map(t => t.revenue);

    renderChart('monthlyTrendChart', 'line', labels, values, 'Daily Revenue Trend', '#1976d2');
}

function updateYearlyCharts(data) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const revenueByMonth = new Array(12).fill(0);
    const profitByMonth = new Array(12).fill(0);

    data.monthly_breakdown.forEach(m => {
        const idx = parseInt(m._id) - 1;
        revenueByMonth[idx] = m.revenue;
        profitByMonth[idx] = m.profit;
    });

    renderMultiChart('yearlyMonthlyChart', months, [
        { label: 'Revenue', data: revenueByMonth, backgroundColor: '#6d4c41' },
        { label: 'Profit', data: profitByMonth, backgroundColor: '#4caf50' }
    ]);
}

function updateTimeIntelligenceCharts(data) {
    const labels = data.map(d => d._id);
    const values = data.map(d => d.avg_profit);

    renderChart('timeProfitChart', 'polarArea', labels, values, 'Average Profit per Transaction', ['#673ab7', '#3f51b5', '#2196f3', '#00bcd4', '#009688']);
}

function renderChart(canvasId, type, labels, data, label, colors) {
    if (charts[canvasId]) charts[canvasId].destroy();

    const ctx = document.getElementById(canvasId).getContext('2d');
    charts[canvasId] = new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: colors,
                borderColor: Array.isArray(colors) ? 'white' : colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: type === 'doughnut' || type === 'polarArea' }
            }
        }
    });
}

function renderMultiChart(canvasId, labels, datasets) {
    if (charts[canvasId]) charts[canvasId].destroy();

    const ctx = document.getElementById(canvasId).getContext('2d');
    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: true } }
        }
    });
}

function renderTimeHeatmap(data) {
    const container = document.getElementById('time-heatmap');
    container.innerHTML = '<div class="table-responsive"><table class="table table-sm text-center"><thead><tr><th>Time Slot</th><th>Orders</th><th>Revenue</th></tr></thead><tbody id="heatmap-body"></tbody></table></div>';

    const body = document.getElementById('heatmap-body');
    data.sort((a, b) => b.revenue - a.revenue).forEach(d => {
        const row = document.createElement('tr');
        const heat = Math.min(d.count * 10, 100);
        row.innerHTML = `
            <td>${d._id}</td>
            <td><span class="badge" style="background: rgba(109, 76, 65, ${heat / 100})">${d.count}</span></td>
            <td>₹${d.revenue.toFixed(2)}</td>
        `;
        body.appendChild(row);
    });
}

// --- Utilities ---

function showToast(message, type = 'success') {
    const toastEl = document.getElementById('liveToast');
    const toastMsg = document.getElementById('toast-message');

    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastMsg.textContent = message;

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('active');
}

function setupTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}
