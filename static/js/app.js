// Global State
let currentTab = 'sales-entry';
let menuItems = [];
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

    // Set initial tab based on role (Check both localStorage and common patterns)
    const userRole = localStorage.getItem('user_role') || (document.querySelector('.badge.bg-danger') ? 'admin' : 'staff');

    // Default to sales-entry for staff, daily-view for admin
    if (userRole === 'admin') {
        navigateTo('daily-view');
    } else {
        navigateTo('sales-entry');
    }
});

function initMobileGestures() {
    let touchstartX = 0;
    let touchendX = 0;
    let touchstartY = 0;
    let touchendY = 0;

    document.addEventListener('touchstart', e => {
        touchstartX = e.changedTouches[0].screenX;
        touchstartY = e.changedTouches[0].screenY;
    }, false);

    document.addEventListener('touchend', e => {
        touchendX = e.changedTouches[0].screenX;
        touchendY = e.changedTouches[0].screenY;
        handleGesture();
    }, false);

    function handleGesture() {
        const xDist = touchendX - touchstartX;
        const yDist = Math.abs(touchendY - touchstartY);

        // Swipe from left edge (within first 50px) to right
        if (touchstartX < 50 && xDist > 100 && yDist < 50) {
            handleSmartBack();
        }
    }
}

function handleSmartBack() {
    if (window.history.length > 1) {
        window.history.back();
    } else {
        const userRole = localStorage.getItem('user_role') || (document.querySelector('.badge.bg-danger') ? 'admin' : 'staff');
        if (userRole === 'admin') {
            navigateTo('daily-view');
        } else {
            navigateTo('sales-entry');
        }
    }
}

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
    const element = document.getElementById('current-datetime');
    if (element) {
        element.textContent = now.toLocaleDateString('en-US', options);
    }
}

function navigateTo(tabId) {
    // Sync Sidebar
    document.querySelectorAll('#sidebar .nav-link').forEach(link => {
        link.classList.remove('active');
        const onclickAttr = link.getAttribute('onclick');
        if (onclickAttr && onclickAttr.includes(tabId)) link.classList.add('active');
    });

    // Sync Bottom Nav
    document.querySelectorAll('.bottom-nav-item').forEach(item => {
        item.classList.remove('active');
        const onclickAttr = item.getAttribute('onclick');
        if (onclickAttr && onclickAttr.includes(tabId)) item.classList.add('active');
    });

    document.querySelectorAll('.dashboard-section').forEach(sec => sec.classList.remove('active'));
    const targetSection = document.getElementById(tabId);
    if (targetSection) targetSection.classList.add('active');

    const titles = {
        'sales-entry': 'Menu & Sales',
        'daily-view': 'Daily Stats',
        'monthly-view': 'Business Health',
        'yearly-view': 'Annual Growth',
        'staff-performance-view': 'Team Rankings'
    };

    const titleElement = document.getElementById('page-title');
    if (titleElement) titleElement.textContent = titles[tabId];

    // Update Mobile Header Title
    const mobileTitle = document.getElementById('mobile-current-page');
    if (mobileTitle) mobileTitle.textContent = titles[tabId];

    currentTab = tabId;

    if (tabId === 'daily-view') loadDailyDashboard();
    if (tabId === 'monthly-view') loadMonthlyDashboard();
    if (tabId === 'yearly-view') loadYearlyDashboard();
    if (tabId === 'staff-performance-view') loadStaffPerformance();

    // Auto-close sidebar on mobile after navigation
    if (window.innerWidth < 992) {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) sidebar.classList.remove('active');
    }
}

// --- Sales Entry Logic ---
let allMenuItems = [];

async function loadMenuItems() {
    const container = document.getElementById('menu-container');
    if (container) {
        container.innerHTML = `
            <div class="menu-item-card shimmer" style="height: 400px;"></div>
            <div class="menu-item-card shimmer" style="height: 400px;"></div>
            <div class="menu-item-card shimmer" style="height: 400px;"></div>
            <div class="menu-item-card shimmer" style="height: 400px;"></div>
        `;
    }

    try {
        const url = new URL('/api/menu-items', window.location.origin);
        if (activeCategory !== 'All') url.searchParams.append('category', activeCategory);
        if (activeSearchQuery) url.searchParams.append('search', activeSearchQuery);

        const response = await fetch(url);
        const data = await response.json();

        // If it's a cold load (All items, no search), store it
        if (activeCategory === 'All' && !activeSearchQuery) {
            allMenuItems = data;
        }

        renderMenu(data);
    } catch (error) {
        console.error('Error loading menu:', error);
        showToast('Error loading menu items', 'danger');
    }
}

function handleSearch(query) {
    activeSearchQuery = query.trim();
    const clearBtn = document.getElementById('clear-search');

    if (clearBtn) {
        clearBtn.style.display = activeSearchQuery ? 'block' : 'none';
    }

    // Debounce search to avoid too many requests
    clearTimeout(window.searchTimeout);
    window.searchTimeout = setTimeout(() => {
        loadMenuItems();
    }, 300);
}

function clearSearch() {
    const searchInput = document.getElementById('item-search');
    if (searchInput) searchInput.value = '';
    activeSearchQuery = '';
    const clearBtn = document.getElementById('clear-search');
    if (clearBtn) clearBtn.style.display = 'none';
    loadMenuItems();
}

function filterMenu(category, element) {
    activeCategory = category;
    document.querySelectorAll('.category-pill').forEach(pill => pill.classList.remove('active'));
    if (element) {
        element.classList.add('active');
        element.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
    }

    loadMenuItems();
}

function renderMenu(items) {
    const container = document.getElementById('menu-container');
    if (!container) return;

    container.style.opacity = '0.3';

    setTimeout(() => {
        container.innerHTML = '';
        if (items.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search"></i>
                    <h3>No items found</h3>
                    <p>Try a different search term or category.</p>
                </div>`;
            container.style.opacity = '1';
            return;
        }

        items.forEach((item, index) => {
            const card = document.createElement('div');
            card.className = 'menu-item-card';
            card.style.animationDelay = `${index * 0.05}s`;

            const imageUrl = item.image_url || `https://images.unsplash.com/photo-1572490122747-3968b75cc699?auto=format&fit=crop&q=80&w=400&h=300`;

            card.innerHTML = `
                <div class="item-img-container">
                    <img src="${imageUrl}" alt="${item.name}" loading="lazy" onerror="this.src='https://via.placeholder.com/400x300?text=${encodeURIComponent(item.name)}'">
                    <div class="img-overlay">
                        <span class="price-badge">₹${(item.price || 0).toFixed(2)}</span>
                    </div>
                </div>
                <div class="item-content">
                    <div class="item-name">${item.name}</div>
                    <div class="item-desc">Premium selection from our ${item.category} menu, prepared fresh for you.</div>
                    <button class="add-btn" onclick="openPaymentModal('${item.item_id}', '${(item.name || 'Item').replace(/'/g, "\\'")}')">
                        <i class="fas fa-plus-circle"></i> ADD SALE
                    </button>
                </div>
            `;
            container.appendChild(card);
        });

        container.style.opacity = '1';
    }, 150);
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

let activeUploadItemId = null;
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

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    const icon = document.querySelector('.theme-toggle i');
    if (icon) icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
}

// Initialize theme
if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark-mode');
    document.addEventListener('DOMContentLoaded', () => {
        const icon = document.querySelector('.theme-toggle i');
        if (icon) icon.className = 'fas fa-sun';
    });
}

// --- Dashboard Data Loading ---

async function loadDailyDashboard() {
    const dateInput = document.getElementById('daily-date-filter');
    if (!dateInput) return;
    const date = dateInput.value;
    const response = await fetch(`/api/daily-dashboard?date=${date}`);
    const summary = await response.json();

    document.getElementById('daily-revenue').textContent = `₹${(summary.total_revenue || 0).toFixed(2)}`;
    document.getElementById('daily-orders').textContent = summary.order_count || 0;
    document.getElementById('daily-phonepe').textContent = `₹${(summary.phonepe_amount || 0).toFixed(2)}`;
    document.getElementById('daily-cash').textContent = `₹${(summary.cash_amount || 0).toFixed(2)}`;
}

async function loadMonthlyDashboard() {
    const monthSelect = document.getElementById('monthly-month-filter');
    const yearSelect = document.getElementById('monthly-year-filter');
    if (!monthSelect || !yearSelect) return;

    const month = monthSelect.value;
    const year = yearSelect.value;

    const response = await fetch(`/api/monthly-dashboard?month=${month}&year=${year}`);
    const summary = await response.json();

    document.getElementById('monthly-revenue').textContent = `₹${(summary.total_revenue || 0).toFixed(2)}`;
    document.getElementById('monthly-orders').textContent = summary.order_count || 0;
    document.getElementById('monthly-phonepe').textContent = `₹${(summary.phonepe_amount || 0).toFixed(2)}`;
    document.getElementById('monthly-cash').textContent = `₹${(summary.cash_amount || 0).toFixed(2)}`;
}

async function loadYearlyDashboard() {
    const response = await fetch('/api/yearly-dashboard');
    const summary = await response.json();

    document.getElementById('yearly-revenue').textContent = `₹${(summary.total_revenue || 0).toFixed(2)}`;
    document.getElementById('yearly-orders').textContent = summary.order_count || 0;
    document.getElementById('yearly-phonepe').textContent = `₹${(summary.phonepe_amount || 0).toFixed(2)}`;
    document.getElementById('yearly-cash').textContent = `₹${(summary.cash_amount || 0).toFixed(2)}`;
}

async function loadStaffPerformance() {
    try {
        const date = document.getElementById('staff-date-filter').value;
        // Check if other filters exist
        const monthFilter = document.getElementById('staff-month-filter');
        const yearFilter = document.getElementById('staff-year-filter');

        const month = monthFilter ? monthFilter.value : '';
        const year = yearFilter ? yearFilter.value : '';

        let queryParams = [];
        if (date) queryParams.push(`date=${date}`);
        if (month) queryParams.push(`month=${month}`);
        if (year) queryParams.push(`year=${year}`);

        const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
        const response = await fetch(`/api/admin/staff-performance${queryString}`);
        const data = await response.json();
        const tbody = document.getElementById('staff-performance-body');
        if (!tbody) return;
        tbody.innerHTML = '';

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center py-4 text-muted">No sales found</td></tr>';
            return;
        }

        data.forEach((staff, index) => {
            const tr = document.createElement('tr');
            let statusBadge = '';
            if (index === 0) statusBadge = '<span class="badge bg-warning text-dark"><i class="fas fa-crown me-1"></i> Winner</span>';
            else if (index === 1) statusBadge = '<span class="badge bg-secondary"><i class="fas fa-star me-1"></i> Star</span>';
            else statusBadge = '<span class="badge bg-light text-muted">Reliable</span>';

            tr.innerHTML = `
                <td class="ps-4 fw-bold">
                    <div class="d-flex align-items-center">
                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-3" style="width: 32px; height: 32px; font-size: 0.8rem;">
                            ${staff._id.substring(0, 2).toUpperCase()}
                        </div>
                        ${staff._id || 'Unknown'}
                    </div>
                </td>
                <td><div class="fw-bold">${staff.total_sales}</div><small class="text-muted">Total Orders</small></td>
                <td class="text-success fw-bold">₹${(staff.total_revenue || 0).toFixed(2)}</td>
                <td>${statusBadge}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        showToast('Error loading performance', 'danger');
    }
}

function resetStaffFilters() {
    document.getElementById('staff-date-filter').value = '';
    const monthFilter = document.getElementById('staff-month-filter');
    const yearFilter = document.getElementById('staff-year-filter');
    if (monthFilter) monthFilter.value = '';
    if (yearFilter) yearFilter.value = '';
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
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.toggle('active');
}

function setupTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}
