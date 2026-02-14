// Global State
let currentTab = 'sales-entry';
let menuItems = [];
let charts = {};
let pendingSaleItemId = null;

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    updateDateTime();
    setInterval(updateDateTime, 1000);
    initFilters();
    loadMenuItems();
    setupTooltips();
    setupUploadHandlers();

    // Set initial tab based on role
    const userRole = localStorage.getItem('user_role');
    if (userRole === 'admin') {
        navigateTo('daily-view');
    } else {
        navigateTo('sales-entry');
    }
});

function initFilters() {
    const now = new Date();

    // Daily filter
    const dailyInput = document.getElementById('daily-date-filter');
    if (dailyInput) {
        dailyInput.value = now.toISOString().split('T')[0];
    }

    // Monthly filters
    const monthSelect = document.getElementById('monthly-month-filter');
    const yearSelect = document.getElementById('monthly-year-filter');

    if (monthSelect) {
        monthSelect.value = String(now.getMonth() + 1).padStart(2, '0');
    }

    if (yearSelect) {
        const currentYear = now.getFullYear();
        yearSelect.innerHTML = '';
        for (let i = currentYear + 2; i >= 2024; i--) {
            const opt = document.createElement('option');
            opt.value = i;
            opt.textContent = i;
            yearSelect.appendChild(opt);
        }
        yearSelect.value = currentYear;
    }

    // Staff filters
    const staffYearSelect = document.getElementById('staff-year-filter');
    if (staffYearSelect) {
        const currentYear = now.getFullYear();
        staffYearSelect.innerHTML = '<option value="">All Years</option>';
        for (let i = currentYear + 2; i >= 2024; i--) {
            const opt = document.createElement('option');
            opt.value = i;
            opt.textContent = i;
            staffYearSelect.appendChild(opt);
        }
    }
}

function updateDateTime() {
    const now = new Date();
    const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' };
    document.getElementById('current-datetime').textContent = now.toLocaleDateString('en-US', options);
}

function navigateTo(tabId) {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        const onclickAttr = link.getAttribute('onclick');
        if (onclickAttr && onclickAttr.includes(tabId)) {
            link.classList.add('active');
        }
    });

    document.querySelectorAll('.dashboard-section').forEach(sec => {
        sec.classList.remove('active');
    });
    document.getElementById(tabId).classList.add('active');

    const titles = {
        'sales-entry': 'Sales Entry',
        'daily-view': 'Daily Dashboard',
        'monthly-view': 'Monthly Dashboard',
        'yearly-view': 'Yearly Dashboard',
        'staff-performance-view': 'Staff Performance'
    };
    document.getElementById('page-title').textContent = titles[tabId];

    currentTab = tabId;

    if (tabId === 'daily-view') loadDailyDashboard();
    if (tabId === 'monthly-view') loadMonthlyDashboard();
    if (tabId === 'yearly-view') loadYearlyDashboard();
    if (tabId === 'staff-performance-view') loadStaffPerformance();
}

// --- Sales Entry Logic ---
let allMenuItems = [];

async function loadMenuItems() {
    try {
        const response = await fetch('/api/menu-items');
        allMenuItems = await response.json();
        renderMenu(allMenuItems);
    } catch (error) {
        console.error('Error loading menu:', error);
        showToast('Error loading menu items', 'danger');
    }
}

function renderMenu(items) {
    const container = document.getElementById('menu-container');
    container.innerHTML = '';

    if (items.length === 0) {
        container.innerHTML = '<div class="col-12 text-center text-muted">No items found</div>';
        return;
    }

    items.forEach(item => {
        const card = document.createElement('div');
        const catClass = item.category.toLowerCase().replace(/\s+/g, '-');
        card.className = `menu-item-card category-${catClass}`;

        const imageUrl = item.image_url || `https://via.placeholder.com/150?text=${encodeURIComponent(item.name)}`;

        card.innerHTML = `
            <div class="upload-icon" title="Upload Image" onclick="triggerUpload(event, '${item.item_id}')">
                <i class="fas fa-camera"></i>
            </div>
            <div class="item-image-box">
                <img src="${imageUrl}" alt="${item.name}">
            </div>
            <div class="category-badge bg-light text-dark shadow-sm">${item.category}</div>
            <div class="fw-bold">${item.name}</div>
            <div class="fw-bold text-primary mb-2">₹${(item.price || 0).toFixed(2)}</div>
            <button class="order-btn" onclick="openPaymentModal('${item.item_id}', '${(item.name || 'Item').replace(/'/g, "\\'")}')">
                <i class="fas fa-plus me-1"></i> ADD SALE
            </button>
        `;
        container.appendChild(card);
    });
}

function openPaymentModal(itemId, itemName) {
    pendingSaleItemId = itemId;
    document.getElementById('payment-modal-item-name').textContent = itemName;

    // Reset UI
    document.getElementById('payment-selection-ui').style.display = 'block';
    document.getElementById('payment-success-ui').style.display = 'none';
    document.querySelectorAll('.payment-card').forEach(c => {
        c.classList.remove('active');
    });

    const modalEl = document.getElementById('paymentModal');
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
}

async function confirmSale(paymentMethod, element) {
    if (!pendingSaleItemId) return;

    try {
        const response = await fetch('/api/record-sale', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                item_id: pendingSaleItemId,
                payment_method: paymentMethod
            })
        });

        if (response.ok) {
            document.getElementById('payment-selection-ui').style.display = 'none';
            document.getElementById('payment-success-ui').style.display = 'block';

            showToast(`Recorded ${paymentMethod} sale successfully!`, 'success');

            setTimeout(() => {
                const modalEl = document.getElementById('paymentModal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
            }, 1000);
        } else {
            const errorData = await response.json();
            showToast(errorData.error || 'Failed to record sale', 'danger');
        }
    } catch (error) {
        showToast('Server error', 'danger');
    } finally {
        pendingSaleItemId = null;
    }
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
            showToast('Uploading...', 'info');
            const response = await fetch('/api/upload-image', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                showToast('Uploaded!', 'success');
                loadMenuItems();
            } else {
                showToast('Upload failed', 'danger');
            }
        } catch (error) {
            showToast('Upload error', 'danger');
        } finally {
            fileInput.value = '';
            activeUploadItemId = null;
        }
    });
}

function filterMenu(category) {
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent === category) btn.classList.add('active');
    });

    if (category === 'All') {
        renderMenu(allMenuItems);
    } else {
        const filtered = allMenuItems.filter(item => item.category === category);
        renderMenu(filtered);
    }
}

// --- Dashboard Data Loading ---

async function loadDailyDashboard() {
    const date = document.getElementById('daily-date-filter').value;
    const response = await fetch(`/api/daily-dashboard?date=${date}`);
    const data = await response.json();

    const summary = data.summary;
    document.getElementById('daily-revenue').textContent = `₹${(summary.total_revenue || 0).toFixed(2)}`;
    document.getElementById('daily-orders').textContent = summary.order_count || 0;
    document.getElementById('daily-phonepe').textContent = `₹${(summary.phonepe_amount || 0).toFixed(2)}`;
    document.getElementById('daily-cash').textContent = `₹${(summary.cash_amount || 0).toFixed(2)}`;

    // Update Charts
    updateChart('daily-item-chart', 'bar', data.items.map(i => i._id), data.items.map(i => i.count), 'Units Sold', '#6d4c41');
    updateChart('daily-category-chart', 'pie', data.categories.map(c => c._id), data.categories.map(c => c.count), 'Categories', ['#6d4c41', '#8d6e63', '#ffab91', '#ff9800', '#4caf50']);
}

async function loadMonthlyDashboard() {
    const month = document.getElementById('monthly-month-filter').value;
    const year = document.getElementById('monthly-year-filter').value;

    const response = await fetch(`/api/monthly-dashboard?month=${month}&year=${year}`);
    const data = await response.json();

    const summary = data.summary;
    document.getElementById('monthly-revenue').textContent = `₹${(summary.total_revenue || 0).toFixed(2)}`;
    document.getElementById('monthly-orders').textContent = summary.order_count || 0;
    document.getElementById('monthly-phonepe').textContent = `₹${(summary.phonepe_amount || 0).toFixed(2)}`;
    document.getElementById('monthly-cash').textContent = `₹${(summary.cash_amount || 0).toFixed(2)}`;

    // Update Charts
    updateChart('monthly-trend-chart', 'line', data.trend.map(t => t._id.split('-')[2]), data.trend.map(t => t.revenue), 'Daily Revenue', '#6d4c41');
    updateChart('monthly-category-chart', 'bar', data.categories.map(c => c._id), data.categories.map(c => c.revenue), 'Revenue by Category', '#8d6e63');
}

async function loadYearlyDashboard() {
    const response = await fetch('/api/yearly-dashboard');
    const data = await response.json();

    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

    const summary = data.summary;
    document.getElementById('yearly-revenue').textContent = `₹${(summary.total_revenue || 0).toFixed(2)}`;

    const bestMonthName = data.best_month !== "None" ? monthNames[parseInt(data.best_month) - 1] : 'N/A';
    document.getElementById('yearly-best-month').textContent = bestMonthName;
    document.getElementById('yearly-top-item').textContent = data.top_product || 'N/A';

    const labels = data.monthly_breakdown.map(m => monthNames[parseInt(m._id) - 1]);
    const values = data.monthly_breakdown.map(m => m.revenue);

    updateChart('yearly-trend-chart', 'line', labels, values, 'Monthly Revenue', '#ffab91');
}

async function loadStaffPerformance() {
    try {
        const date = document.getElementById('staff-date-filter').value;
        const month = document.getElementById('staff-month-filter').value;
        const year = document.getElementById('staff-year-filter').value;

        let queryParams = [];
        if (date) queryParams.push(`date=${date}`);
        if (month) queryParams.push(`month=${month}`);
        if (year) queryParams.push(`year=${year}`);

        const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
        const response = await fetch(`/api/admin/staff-performance${queryString}`);
        const data = await response.json();
        const tbody = document.getElementById('staff-performance-body');
        tbody.innerHTML = '';

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center py-4 text-muted">No sales found</td></tr>';
            return;
        }

        data.forEach((staff, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="ps-4 fw-bold">${staff._id || 'Unknown'}</td>
                <td><span class="badge bg-light text-dark">${staff.total_sales} orders</span></td>
                <td class="text-success fw-bold">₹${(staff.total_revenue || 0).toFixed(2)}</td>
                <td>
                    <span class="badge ${index === 0 ? 'bg-warning text-dark' : 'bg-info'}">
                        ${index === 0 ? '🏆 Top Performer' : `#${index + 1}`}
                    </span>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        showToast('Error loading performance', 'danger');
    }
}

function updateChart(chartId, type, labels, data, label, color) {
    const ctx = document.getElementById(chartId);
    if (!ctx) return;

    if (charts[chartId]) {
        charts[chartId].destroy();
    }

    charts[chartId] = new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: Array.isArray(color) ? color : color + 'CC',
                borderColor: Array.isArray(color) ? '#fff' : color,
                borderWidth: 2,
                tension: 0.3,
                fill: type === 'line'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: type === 'pie'
                }
            },
            scales: type === 'pie' ? {} : {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function resetStaffFilters() {
    document.getElementById('staff-date-filter').value = '';
    document.getElementById('staff-month-filter').value = '';
    document.getElementById('staff-year-filter').value = '';
    loadStaffPerformance();
}

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
