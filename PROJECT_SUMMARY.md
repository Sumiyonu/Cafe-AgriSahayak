# 📋 Project Summary | Café Management System

## Feature Set

### 1. Sales Management
- **One-Click Recording**: Fast sales entry via a grid UI.
- **Categorized Menu**: 59 pre-configured items (Coffee, Tea, Bakery, Food).
- **Automated Calculations**: Real-time revenue, cost, and profit tracking.

### 2. Advanced Analytics
- **Daily Performance**: 4 key metrics + 2 interactive charts.
- **Monthly Trends**: Track growth across the month with line charts.
- **Yearly Comparison**: Monthly bar charts to compare performance.
- **Time Slot Intelligence**: Heatmaps and polar charts for operational planning.

### 3. Technical Highlights
- **Full Stack Integration**: Flask backend seamlessly connected to a MongoDB database.
- **Responsive Web UI**: Fully mobile-compatible design with Bootstrap 5.
- **Dynamic Visuals**: interactive data visualization using Chart.js.
- **Environment Driven**: Configurable via `.env` for easy environment switching.

## Statistics
- **Total Files**: 11
- **Total Lines of Code**: ~2,900
- **Menu Items**: 59
- **API Endpoints**: 8
- **Charts**: 7

## Database Schema

### `menu_items` Collection
- `item_id`: Unique identifier (Int)
- `name`: Product name (String)
- `category`: Grouping (String)
- `price`: Sale price (Float)
- `cost`: Production cost (Float)

### `sales` Collection
- `item_id`: Reference to product
- `name`: Product name (Snapshot)
- `price`: Sale price (Snapshot)
- `profit`: Calculated profit (Float)
- `timestamp`: Execution time (Date)
- `time_slot`: Operational period (String)

## Operational Gains
- **Efficiency**: Reduces time spent calculating daily earnings manually.
- **Insights**: identifies peak hours to optimize staffing.
- **Profitability**: Highlights high-margin items versus high-volume items.

---
**Version**: 1.0.0 | **Last Updated**: Jan 2025
