# 📚 API Documentation

## Base URL
`http://localhost:5000`

## Endpoints

### 1. Get Menu Items
- **URL**: `/api/menu-items`
- **Method**: `GET`
- **Query Params**: `category` (optional)
- **Response**: List of menu items.

### 2. Record a Sale
- **URL**: `/api/record-sale`
- **Method**: `POST`
- **Body**: `{"item_id": 1}`
- **Response**: Success message and recorded sale details.

### 3. Daily Dashboard
- **URL**: `/api/daily-dashboard`
- **Method**: `GET`
- **Query Params**: `date` (format: YYYY-MM-DD, defaults to today)
- **Response**: Summary stats, category breakdown, and time slot counts.

### 4. Monthly Dashboard
- **URL**: `/api/monthly-dashboard`
- **Method**: `GET`
- **Query Params**: `month`, `year`
- **Response**: Revenue, profit, order count, and daily trend.

### 5. Yearly Dashboard
- **URL**: `/api/yearly-dashboard`
- **Method**: `GET`
- **Query Params**: `year`
- **Response**: Yearly totals and monthly performance breakdown.

### 6. Time Intelligence
- **URL**: `/api/time-intelligence`
- **Method**: `GET`
- **Response**: Performance metrics grouped by time slots.

## HTTP Status Codes
- `200 OK`: Request successful.
- `404 Not Found`: Item not found.
- `500 Internal Server Error`: Server-side error.

## Example Request (JavaScript)
```javascript
fetch('/api/record-sale', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ item_id: 1 })
})
.then(response => response.json())
.then(data => console.log(data));
```
