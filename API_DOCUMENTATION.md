# 📚 API Documentation | Café Management System

## 🔐 Authentication & Access Control
All sensitive routes require authentication. Admin routes further require an `admin` role.

### 1. Login
- **URL**: `/login`
- **Method**: `POST`
- **Body**: `{"username": "...", "password": "..."}`
- **Response**: User role and redirect URL.

### 2. Logout
- **URL**: `/logout`
- **Method**: `GET`
- **Response**: Redirect to login page.

---

## 💰 Sales & Menu API

### 3. Get Menu Items
- **URL**: `/api/menu-items`
- **Method**: `GET`
- **Response**: List of all available menu items.

### 4. Record a Sale
- **URL**: `/api/record-sale`
- **Method**: `POST`
- **Body**: `{"item_id": 1, "payment_method": "Cash"}`
- **Options**: `payment_method` can be `Cash` or `PhonePe`.
- **Response**: Recorded sale details.

---

## 📊 Dashboard & Analytics API

### 5. Daily Dashboard
- **URL**: `/api/daily-dashboard`
- **Method**: `GET`
- **Query Params**: `date` (YYYY-MM-DD)
- **Response**: Revenue, order count, and payment method split for the day.

### 6. Monthly Dashboard
- **URL**: `/api/monthly-dashboard`
- **Method**: `GET`
- **Query Params**: `month`, `year`
- **Response**: Aggregated stats for the specified month.

### 7. Yearly Dashboard (Admin Only)
- **URL**: `/api/yearly-dashboard`
- **Method**: `GET`
- **Query Params**: `year`
- **Response**: Annual summary and monthly breakdown.

### 8. Time Intelligence (Admin Only)
- **URL**: `/api/time-intelligence`
- **Method**: `GET`
- **Response**: Performance metrics grouped by time slots (Morning, Lunch, etc.).

---

## 👥 Admin Management API

### 9. Get All Users
- **URL**: `/api/admin/users`
- **Method**: `GET`
- **Response**: List of users (passwords excluded).

### 10. Create User
- **URL**: `/api/admin/create-user`
- **Method**: `POST`
- **Body**: `{"username": "...", "password": "...", "role": "staff|admin"}`
- **Constraints**: Max 2 admins, Max 5 staff.

### 11. Toggle User Status
- **URL**: `/api/admin/toggle-user-status`
- **Method**: `POST`
- **Body**: `{"username": "..."}`
- **Response**: New activation status.

### 12. Staff Performance
- **URL**: `/api/admin/staff-performance`
- **Method**: `GET`
- **Query Params**: `date`, `month`, `year` (optional filters)
- **Response**: Performance metrics grouped by staff member.

---

## 🖼️ Media Management

### 13. Upload Image (Admin Only)
- **URL**: `/api/upload-image`
- **Method**: `POST`
- **Form Data**: `image` (file), `item_id` (int)
- **Response**: Image URL.

---
**Base URL**: `http://localhost:10000` (Production) | `http://localhost:5000` (Development)
