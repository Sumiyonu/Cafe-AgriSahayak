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
    setupUploadHandlers();
});

let activeUploadItemId = null;

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
        'yearly-view': 'Yearly Dashboard'
    };
    document.getElementById('page-title').textContent = titles[tabId];

    currentTab = tabId;

    // Load data for the specific tab
    if (tabId === 'daily-view') loadDailyDashboard();
    if (tabId === 'monthly-view') loadMonthlyDashboard();
    if (tabId === 'yearly-view') loadYearlyDashboard();
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

        // Use provided image or a generic placeholder
        const imageUrl = item.image_url || `https://via.placeholder.com/150?text=${encodeURIComponent(item.name)}`;

        card.innerHTML = `
            <div class="upload-icon" title="Upload Image" onclick="triggerUpload(event, ${item.item_id})">
                <i class="fas fa-camera"></i>
            </div>
            <div class="item-image-box">
                <img src="${imageUrl}" alt="${item.name}">
            </div>
            <div class="category-badge bg-light text-dark shadow-sm">${item.category}</div>
            <div class="fw-bold">${item.name}</div>
            <div class="text-muted small mb-2" style="font-size: 0.75rem; min-height: 2.5rem;">${item.description || ''}</div>
            <div class="fw-bold text-primary mb-2">₹${item.price.toFixed(2)}</div>
            <button class="order-btn" onclick="recordSale(event, ${item.item_id}, '${item.name.replace(/'/g, "\\'")}')">
                <i class="fas fa-check-circle"></i> Complete Sale
            </button>
        `;
        container.appendChild(card);
    });
}

function triggerUpload(event, itemId) {
    event.stopPropagation();
    activeUploadItemId = itemId;
    document.getElementById('global-file-input').click();
}

function setupUploadHandlers() {
    const fileInput = document.getElementById('global-file-input');
    if (!fileInput) return;

    fileInput.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file || !activeUploadItemId) return;

        const formData = new FormData();
        formData.append('image', file);
        formData.append('item_id', activeUploadItemId);

        try {
            showToast('Uploading image...', 'info');
            const response = await fetch('/api/upload-image', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            if (response.ok) {
                showToast('Image uploaded successfully!', 'success');
                loadMenuItems(); // Reload to show new image
            } else {
                showToast(result.error || 'Upload failed', 'danger');
            }
        } catch (error) {
            showToast('Upload error', 'danger');
        } finally {
            fileInput.value = ''; // Reset input
            activeUploadItemId = null;
        }
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

async function recordSale(event, itemId, itemName) {
    if (event) event.stopPropagation();

    // Confirmation
    if (!confirm(`Record complete sale for ${itemName}?`)) return;

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
    // document.getElementById('daily-revenue').textContent = `₹${s.total_revenue.toFixed(2)}`;
    // document.getElementById('daily-profit').textContent = `₹${s.total_profit.toFixed(2)}`;
    document.getElementById('daily-orders').textContent = s.order_count;
    document.getElementById('daily-cost').textContent = `₹${(s.total_cost || 0).toFixed(2)}`;
    // document.getElementById('daily-avg').textContent = `₹${(s.avg_order_value || 0).toFixed(2)}`;

    renderPerformanceGraph('dailyAmountGraph', data.sales_data, 'Daily Revenue', 100000, '#FF6600');
}

async function loadMonthlyDashboard() {
    const response = await fetch('/api/monthly-dashboard');
    const data = await response.json();

    // document.getElementById('monthly-revenue').textContent = `₹${data.summary.total_revenue.toFixed(2)}`;
    // document.getElementById('monthly-profit').textContent = `₹${data.summary.total_profit.toFixed(2)}`;
    document.getElementById('monthly-orders').textContent = data.summary.order_count;
    document.getElementById('monthly-cost').textContent = `₹${(data.summary.total_cost || 0).toFixed(2)}`;

    renderPerformanceGraph('monthlyAmountGraph', data.sales_data, 'Monthly Revenue', 1000000, '#FF00FF');
}

async function loadYearlyDashboard() {
    const response = await fetch('/api/yearly-dashboard');
    const data = await response.json();

    const s = data.summary;
    // document.getElementById('yearly-revenue').textContent = `₹${s.total_revenue.toFixed(2)}`;
    // document.getElementById('yearly-profit').textContent = `₹${s.total_profit.toFixed(2)}`;
    document.getElementById('yearly-orders').textContent = s.order_count;

    // const margin = s.total_revenue > 0 ? (s.total_profit / s.total_revenue * 100).toFixed(1) : 0;
    // document.getElementById('yearly-margin').textContent = `${margin}%`;

    // updateYearlyCharts(data); // Removed chart
}



// --- Chart Rendering ---

function updateDailyCharts(data) {
    // Category Chart
    const catLabels = data.categories.map(c => c._id);
    const catRevenue = data.categories.map(c => c.revenue);

    renderChart('dailyCategoryChart', 'doughnut', catLabels, catRevenue, 'Revenue by Category', ['#6d4c41', '#8d6e63', '#ffab91', '#4caf50', '#ff9800']);
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



function renderPerformanceGraph(canvasId, rawData, label, yLimit, color) {
    if (charts[canvasId]) charts[canvasId].destroy();

    // Data Transformation: Cumulative Total
    let cumulative = 0;
    const data = rawData.map(val => {
        cumulative += val;
        return cumulative;
    });

    const labels = rawData.map((_, i) => `Order ${i + 1}`);

    const ctx = document.getElementById(canvasId).getContext('2d');
    charts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                borderColor: color,
                borderWidth: 3,
                fill: false,
                tension: 0,
                pointRadius: 5,
                pointBackgroundColor: '#fff',
                pointBorderColor: color,
                pointBorderWidth: 2,
                pointStyle: 'circle'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'Number of Orders', font: { weight: 'bold' } },
                    grid: { display: true, color: '#e0e0e0' }
                },
                y: {
                    beginAtZero: true,
                    max: yLimit,
                    title: { display: true, text: 'Amount (₹)', font: { weight: 'bold' } },
                    grid: { display: true, color: '#e0e0e0' },
                    ticks: {
                        callback: function (value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `Total Amount: ₹${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            }
        }
    });
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
            },
            elements: {
                line: {
                    tension: 0.4, // Smooth curves
                    fill: type === 'line' ? 'start' : false,
                    backgroundColor: type === 'line' ? 'rgba(109, 76, 65, 0.1)' : colors
                }
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
