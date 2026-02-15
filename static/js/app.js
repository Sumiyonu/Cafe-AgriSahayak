// Global State
let currentTab = 'sales-entry';
let allMenuItems = [];
let pendingSaleItemId = null;
let activeCategory = 'All';
let activeSearchQuery = '';

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    updateDateTime();
    setInterval(updateDateTime, 1000);
    initFilters();
    loadMenuItems();
    setupTooltips();
    setupUploadHandlers();
    initMobileGestures();

    // Set initial tab based on role
    const userRole = localStorage.getItem('user_role') || (document.querySelector('.badge.bg-danger') ? 'admin' : 'staff');
    if (userRole === 'admin') {
        navigateTo('daily-view');
    } else {
        navigateTo('sales-entry');
    }
});

function initMobileGestures() {
    let touchstartX = 0;
    let touchendX = 0;
    document.addEventListener('touchstart', e => touchstartX = e.changedTouches[0].screenX, false);
    document.addEventListener('touchend', e => {
        touchendX = e.changedTouches[0].screenX;
        if (touchstartX < 50 && (touchendX - touchstartX) > 100) toggleSidebar();
    }, false);
}

function initFilters() {
    const now = new Date();
    const dailyInput = document.getElementById('daily-date-filter');
    if (dailyInput) dailyInput.value = now.toISOString().split('T')[0];

    const monthSelect = document.getElementById('monthly-month-filter');
    const yearSelect = document.getElementById('monthly-year-filter');
    if (monthSelect) monthSelect.value = String(now.getMonth() + 1).padStart(2, '0');
    if (yearSelect) yearSelect.value = now.getFullYear();
}

function updateDateTime() {
    const now = new Date();
    const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    const element = document.getElementById('current-datetime');
    if (element) element.textContent = now.toLocaleDateString('en-US', options);
}

function navigateTo(tabId) {
    document.querySelectorAll('.dashboard-section').forEach(sec => sec.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));

    const target = document.getElementById(tabId);
    if (target) target.classList.add('active');

    // Update sidebar links
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('onclick')?.includes(tabId)) link.classList.add('active');
    });

    const titles = {
        'sales-entry': 'Menu & Sales',
        'daily-view': 'Daily Analytics',
        'monthly-view': 'Business Performance',
        'staff-performance-view': 'Team Rankings',
        'admin-items-view': 'Item Management'
    };

    const titleEl = document.getElementById('page-title');
    if (titleEl) titleEl.textContent = titles[tabId] || 'Dashboard';

    const mobileTitle = document.getElementById('mobile-current-page');
    if (mobileTitle) mobileTitle.textContent = titles[tabId] || 'Dashboard';

    currentTab = tabId;
    if (tabId === 'admin-items-view') loadAdminItems();
    if (tabId === 'daily-view') loadDailyDashboard();
    if (tabId === 'monthly-view') loadMonthlyDashboard();
    if (tabId === 'staff-performance-view') loadStaffPerformance();

    if (window.innerWidth < 992) {
        document.getElementById('sidebar')?.classList.remove('active');
    }
}

async function loadMenuItems() {
    const container = document.getElementById('menu-container');
    if (!container) return;

    try {
        const url = new URL('/api/menu-items', window.location.origin);
        if (activeCategory !== 'All') url.searchParams.append('category', activeCategory);
        if (activeSearchQuery) url.searchParams.append('search', activeSearchQuery);

        const response = await fetch(url);
        const data = await response.json();
        renderMenu(data);
    } catch (error) {
        showToast('Error loading menu', 'danger');
    }
}

function renderMenu(items) {
    const container = document.getElementById('menu-container');
    if (!container) return;

    container.innerHTML = '';
    if (items.length === 0) {
        container.innerHTML = '<div class="empty-state text-center py-5 opacity-50"><i class="fas fa-search fa-3x mb-3"></i><p>No items found</p></div>';
        return;
    }

    const isMobile = window.innerWidth <= 768;

    if (isMobile) {
        // Mobile Compact List View
        items.forEach(item => {
            const row = document.createElement('div');
            row.className = 'item-row';
            row.onclick = () => openPaymentModal(item.item_id, item.name);
            row.innerHTML = `
                <img src="${item.image_url || 'https://via.placeholder.com/60'}" class="item-row-img" alt="${item.name}">
                <div class="item-row-info">
                    <div class="item-row-name">${item.name}</div>
                    <div class="item-row-price">₹${item.price}</div>
                </div>
                <div class="item-row-action">
                    <i class="fas fa-chevron-right"></i>
                </div>
            `;
            container.appendChild(row);
        });
    } else {
        // Desktop Grid View (4 columns via CSS)
        container.className = 'menu-grid';
        items.forEach(item => {
            const card = document.createElement('div');
            card.className = 'menu-item-card';
            card.innerHTML = `
                <div class="item-img-container" onclick="openPaymentModal('${item.item_id}', '${item.name.replace(/'/g, "\\'")}')">
                    <img src="${item.image_url || 'https://via.placeholder.com/200'}" alt="${item.name}">
                    <div class="img-overlay">
                        <span class="price-badge">₹${item.price}</span>
                    </div>
                </div>
                <div class="item-content">
                    <div class="item-name text-center mb-0">${item.name}</div>
                </div>
            `;
            container.appendChild(card);
        });
    }
}

// --- Sales & Payment Logic ---
function openPaymentModal(itemId, itemName) {
    pendingSaleItemId = itemId;
    document.getElementById('payment-modal-item-name').textContent = itemName;
    document.getElementById('payment-selection-ui').style.display = 'block';
    document.getElementById('payment-success-ui').style.display = 'none';

    const modal = new bootstrap.Modal(document.getElementById('paymentModal'));
    modal.show();
}

async function confirmSale(method) {
    if (!pendingSaleItemId) return;
    try {
        const response = await fetch('/api/record-sale', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: pendingSaleItemId, payment_method: method })
        });

        if (response.ok) {
            document.getElementById('payment-selection-ui').style.display = 'none';
            document.getElementById('payment-success-ui').style.display = 'block';
            setTimeout(() => {
                bootstrap.Modal.getInstance(document.getElementById('paymentModal')).hide();
                loadDailyDashboard();
            }, 1000);
        } else {
            showToast('Failed to record sale', 'danger');
        }
    } catch (error) {
        showToast('Server error', 'danger');
    }
}

// --- Admin Item Management Logic ---
async function loadAdminItems() {
    const tbody = document.getElementById('admin-items-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="6" class="text-center py-5"><div class="spinner-border text-primary"></div></td></tr>';

    try {
        const response = await fetch('/api/admin/menu-items');
        const items = await response.json();
        tbody.innerHTML = '';

        items.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="ps-4">
                    <div class="d-flex align-items-center">
                        <img src="${item.image_url || 'https://via.placeholder.com/40'}" class="admin-item-thumb me-3">
                        <span class="fw-bold">${item.name}</span>
                    </div>
                </td>
                <td><span class="badge bg-light text-dark">${item.category}</span></td>
                <td class="fw-bold">₹${item.price}</td>
                <td>${item.order_count || 0}</td>
                <td>
                    <button class="btn btn-toggle-active ${item.is_active ? 'btn-success' : 'btn-outline-secondary'}" 
                        onclick="toggleItemStatus('${item.item_id}')">
                        ${item.is_active ? 'Active' : 'Hidden'}
                    </button>
                </td>
                <td class="text-end pe-4">
                    <button class="btn btn-sm btn-outline-primary me-2" onclick='openItemEditModal(${JSON.stringify(item)})'>
                        <i class="fas fa-edit"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        showToast('Error loading items', 'danger');
    }
}

function openItemEditModal(item = null) {
    const form = document.getElementById('itemEditForm');
    form.reset();
    document.getElementById('itemModalTitle').textContent = item ? 'Edit Item' : 'Add New Item';
    document.getElementById('edit-item-preview').src = item?.image_url || 'https://via.placeholder.com/50';

    if (item) {
        document.getElementById('edit-item-id').value = item.item_id;
        document.getElementById('edit-item-name').value = item.name;
        document.getElementById('edit-item-category').value = item.category;
        document.getElementById('edit-item-price').value = item.price;
    } else {
        document.getElementById('edit-item-id').value = '';
    }

    new bootstrap.Modal(document.getElementById('itemEditModal')).show();
}

async function saveItemChanges() {
    const itemId = document.getElementById('edit-item-id').value;
    const name = document.getElementById('edit-item-name').value;
    const category = document.getElementById('edit-item-category').value;
    const price = document.getElementById('edit-item-price').value;
    const imageFile = document.getElementById('edit-item-image').files[0];

    if (!name || !price) return showToast('Please fill required fields', 'warning');

    const data = { name, category, price: parseFloat(price) };

    try {
        let finalImageUrl = null;
        if (imageFile) {
            const formData = new FormData();
            formData.append('image', imageFile);
            formData.append('item_id', itemId || 'new');
            const uploadRes = await fetch('/api/upload-image', { method: 'POST', body: formData });
            if (uploadRes.ok) {
                const uploadData = await uploadRes.json();
                data.image_url = uploadData.image_url;
            }
        }

        const method = itemId ? 'PUT' : 'POST';
        const url = itemId ? `/api/admin/item/${itemId}` : '/api/admin/item';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            showToast('Item saved successfully!');
            bootstrap.Modal.getInstance(document.getElementById('itemEditModal')).hide();
            loadAdminItems();
            loadMenuItems();
        }
    } catch (e) {
        showToast('Failed to save item', 'danger');
    }
}

async function toggleItemStatus(itemId) {
    try {
        const response = await fetch(`/api/admin/item/${itemId}`, { method: 'DELETE' });
        if (response.ok) {
            loadAdminItems();
            loadMenuItems();
        }
    } catch (e) {
        showToast('Error toggling status', 'danger');
    }
}

// --- Utilities ---
function handleSearch(q) {
    activeSearchQuery = q.trim();
    loadMenuItems();
}

function filterMenu(cat, el) {
    activeCategory = cat;
    document.querySelectorAll('.category-pill').forEach(p => p.classList.remove('active'));
    el.classList.add('active');
    loadMenuItems();
}

function showToast(msg, type = 'success') {
    const toastEl = document.getElementById('liveToast');
    document.getElementById('toast-message').textContent = msg;
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    new bootstrap.Toast(toastEl).show();
}

function toggleSidebar() {
    document.getElementById('sidebar')?.classList.toggle('active');
}

function setupUploadHandlers() { }
function setupTooltips() { }

// Dashboard loading functions (restored)
async function loadDailyDashboard() {
    const date = document.getElementById('daily-date-filter')?.value || new Date().toISOString().split('T')[0];
    const res = await fetch(`/api/daily-dashboard?date=${date}`);
    const data = await res.json();
    document.getElementById('daily-revenue').textContent = `₹${data.total_revenue.toFixed(2)}`;
    document.getElementById('daily-orders').textContent = data.order_count;
    document.getElementById('daily-phonepe').textContent = `₹${data.phonepe_amount.toFixed(0)}`;
    document.getElementById('daily-cash').textContent = `₹${data.cash_amount.toFixed(0)}`;
}

async function loadMonthlyDashboard() {
    const m = document.getElementById('monthly-month-filter').value;
    const y = document.getElementById('monthly-year-filter').value;
    const res = await fetch(`/api/monthly-dashboard?month=${m}&year=${y}`);
    const data = await res.json();
    document.getElementById('monthly-revenue').textContent = `₹${data.total_revenue.toLocaleString()}`;
    document.getElementById('monthly-orders').textContent = data.order_count;
}

async function loadStaffPerformance() {
    const res = await fetch('/api/admin/staff-performance');
    const data = await res.json();
    const tbody = document.getElementById('staff-performance-body');
    if (!tbody) return;
    tbody.innerHTML = data.map(s => `
        <tr>
            <td class="ps-4 fw-bold">${s._id}</td>
            <td>${s.total_sales}</td>
            <td class="text-success fw-bold">₹${s.total_revenue}</td>
            <td><span class="badge bg-light text-dark">Staff</span></td>
        </tr>
    `).join('');
}
