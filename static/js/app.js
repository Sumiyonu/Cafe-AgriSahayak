// Global State
let currentTab = 'sales-entry';
let allMenuItems = [];
let pendingPriceItemId = null;
let activeCategory = 'All';
let activeSearchQuery = '';
let cart = [];

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
    const dailyInput = document.getElementById('daily-date-filter');
    if (dailyInput) dailyInput.value = now.toISOString().split('T')[0];

    const monthSelect = document.getElementById('monthly-month-filter');
    const yearSelect = document.getElementById('monthly-year-filter');

    if (monthSelect) monthSelect.value = String(now.getMonth() + 1).padStart(2, '0');

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
    if (element) element.textContent = now.toLocaleDateString('en-US', options);
}

function navigateTo(tabId) {
    document.querySelectorAll('#sidebar .nav-link').forEach(link => {
        link.classList.remove('active');
        const onclickAttr = link.getAttribute('onclick');
        if (onclickAttr && onclickAttr.includes(tabId)) link.classList.add('active');
    });

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

    const mobileTitle = document.getElementById('mobile-current-page');
    if (mobileTitle) mobileTitle.textContent = titles[tabId];

    currentTab = tabId;

    if (tabId === 'daily-view') loadDailyDashboard();
    if (tabId === 'monthly-view') loadMonthlyDashboard();
    if (tabId === 'yearly-view') loadYearlyDashboard();
    if (tabId === 'staff-performance-view') loadStaffPerformance();

    if (window.innerWidth < 992) {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) sidebar.classList.remove('active');
    }
}

async function loadMenuItems() {
    const container = document.getElementById('menu-container');
    if (container) {
        container.innerHTML = `
            <div class="menu-item-card shimmer" style="height: 150px;"></div>
            <div class="menu-item-card shimmer" style="height: 150px;"></div>
            <div class="menu-item-card shimmer" style="height: 150px;"></div>
            <div class="menu-item-card shimmer" style="height: 150px;"></div>
        `;
    }

    try {
        const url = new URL('/api/menu-items', window.location.origin);
        if (activeCategory !== 'All') url.searchParams.append('category', activeCategory);
        if (activeSearchQuery) url.searchParams.append('search', activeSearchQuery);

        const response = await fetch(url);
        const data = await response.json();

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
    if (clearBtn) clearBtn.style.display = activeSearchQuery ? 'block' : 'none';

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

    const userRole = localStorage.getItem('user_role') || (document.querySelector('.badge.bg-danger') ? 'admin' : 'staff');

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

            const adminControls = userRole === 'admin' ? `
                <div class="admin-controls">
                    <button class="edit-price-btn" onclick="openPriceModal('${item.item_id}', '${(item.name || 'Item').replace(/'/g, "\\'")}', ${item.price})" title="Edit Price">
                        <i class="fas fa-pencil-alt"></i>
                    </button>
                </div>
            ` : '';

            const isOffer = item.is_offer === true;
            const originalPrice = item.original_price || 0;
            const currentPrice = item.price || 0;

            const priceHtml = isOffer ? `
                <div class="price-display-compact">
                    <span class="price-original" style="text-decoration: line-through; opacity: 0.6; font-size: 0.8em;">₹${originalPrice.toFixed(0)}</span>
                    <span class="price-arrow" style="margin: 0 4px; opacity: 0.8;">→</span>
                    <span class="price-current fw-bold">₹${currentPrice.toFixed(0)}</span>
                </div>
            ` : `₹${currentPrice.toFixed(0)}`;

            card.innerHTML = `
                ${adminControls}
                <div class="item-img-container">
                    <img src="${imageUrl}" alt="${item.name}" loading="lazy" onerror="this.src='https://via.placeholder.com/400x300?text=${encodeURIComponent(item.name)}'">
                    <div class="img-overlay">
                        <span class="price-badge">${priceHtml}</span>
                    </div>
                </div>
                <div class="item-content text-center">
                    <div class="item-name fw-bold mb-2">${item.name}</div>
                    <button class="add-btn w-100" onclick="addToCart('${item.item_id}', '${(item.name || 'Item').replace(/'/g, "\\'")}', ${item.price})">
                        <i class="fas fa-plus"></i> ADD
                    </button>
                </div>
            `;
            container.appendChild(card);
        });

        container.style.opacity = '1';
    }, 150);
}

// --- Cart Logic ---
function addToCart(id, name, price) {
    const existing = cart.find(i => i.id === id);
    if (existing) {
        existing.qty++;
    } else {
        cart.push({ id, name, price, qty: 1 });
    }
    updateCartUI();

    // Animate badge
    const badge = document.getElementById('cart-count-badge');
    if (badge) {
        badge.classList.remove('pulse');
        void badge.offsetWidth;
        badge.classList.add('pulse');
    }

    showToast(`${name} added!`, 'success');
}

function updateCartUI() {
    const count = cart.reduce((acc, item) => acc + item.qty, 0);
    const total = cart.reduce((acc, item) => acc + (item.price * item.qty), 0);

    const badge = document.getElementById('cart-count-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }

    const cartList = document.getElementById('cart-items-list');
    const totalEl = document.getElementById('cart-total');
    if (totalEl) totalEl.textContent = `₹${total}`;

    if (cartList) {
        if (cart.length === 0) {
            cartList.innerHTML = `
                <div class="text-center py-5 text-muted">
                    <i class="fas fa-shopping-basket fa-3x mb-3 opacity-20"></i>
                    <p>Your cart is empty</p>
                </div>`;
            return;
        }

        cartList.innerHTML = cart.map(item => `
            <div class="cart-item">
                <div>
                    <div class="fw-bold">${item.name}</div>
                    <div class="small text-muted">₹${item.price} each</div>
                </div>
                <div class="quantity-control">
                    <button class="qty-btn" onclick="updateQty('${item.id}', -1)">-</button>
                    <span class="fw-bold">${item.qty}</span>
                    <button class="qty-btn" onclick="updateQty('${item.id}', 1)">+</button>
                </div>
            </div>
        `).join('');
    }
}

function updateQty(id, delta) {
    const item = cart.find(i => i.id === id);
    if (!item) return;
    item.qty += delta;
    if (item.qty <= 0) {
        cart = cart.filter(i => i.id !== id);
    }
    updateCartUI();
}

function toggleCart() {
    const panel = document.getElementById('cart-panel');
    const overlay = document.getElementById('cart-overlay');
    if (panel.classList.contains('open')) {
        panel.classList.remove('open');
        overlay.style.display = 'none';
    } else {
        panel.classList.add('open');
        overlay.style.display = 'block';
        updateCartUI();
    }
}

async function completeCartSale() {
    if (cart.length === 0) {
        showToast('Cart is empty!', 'warning');
        return;
    }

    const paymentMethod = document.querySelector('input[name="payment"]:checked').value;

    try {
        showToast('Processing sale...', 'info');

        for (const item of cart) {
            for (let i = 0; i < item.qty; i++) {
                await fetch('/api/record-sale', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        item_id: item.id,
                        payment_method: paymentMethod
                    })
                });
            }
        }

        showToast('Order completed successfully!', 'success');
        cart = [];
        updateCartUI();
        toggleCart();

    } catch (error) {
        showToast('Error processing order', 'danger');
    }
}

// --- Admin Logic ---
function openPriceModal(itemId, itemName, currentPrice) {
    pendingPriceItemId = itemId;
    document.getElementById('price-modal-item-name').textContent = itemName;
    document.getElementById('current-item-price-display').value = `₹${parseFloat(currentPrice).toFixed(2)}`;
    document.getElementById('new-item-price').value = currentPrice;
    document.getElementById('is-offer-switch').checked = false;
    document.getElementById('price-change-reason').value = '';

    const modalEl = document.getElementById('priceModal');
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
}

async function saveNewPrice() {
    if (!pendingPriceItemId) return;

    const newPrice = document.getElementById('new-item-price').value;
    const isOffer = document.getElementById('is-offer-switch').checked;
    const reason = document.getElementById('price-change-reason').value;

    if (!newPrice || parseFloat(newPrice) <= 0) {
        showToast('Please enter a valid price greater than 0', 'warning');
        return;
    }

    try {
        const response = await fetch(`/api/admin/update-price/${pendingPriceItemId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                price: parseFloat(newPrice),
                is_offer: isOffer,
                reason: reason
            })
        });

        if (response.ok) {
            showToast('Price updated successfully!', 'success');
            const modalEl = document.getElementById('priceModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            loadMenuItems();
        } else {
            const errorData = await response.json();
            showToast(errorData.error || 'Failed to update price', 'danger');
        }
    } catch (error) {
        showToast('Server error', 'danger');
    } finally {
        pendingPriceItemId = null;
    }
}

// --- Other Utilities ---
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

if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark-mode');
    document.addEventListener('DOMContentLoaded', () => {
        const icon = document.querySelector('.theme-toggle i');
        if (icon) icon.className = 'fas fa-sun';
    });
}

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
    const dFilter = document.getElementById('staff-date-filter');
    if (dFilter) dFilter.value = '';
    const monthFilter = document.getElementById('staff-month-filter');
    const yearFilter = document.getElementById('staff-year-filter');
    if (monthFilter) monthFilter.value = '';
    if (yearFilter) yearFilter.value = '';
    loadStaffPerformance();
}

function showToast(message, type = 'success') {
    const toastEl = document.getElementById('liveToast');
    const toastMsg = document.getElementById('toast-message');
    if (!toastEl || !toastMsg) return;

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
