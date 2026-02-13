# ⚡ Quick Start Guide (5 Minutes)

Follow these steps to get your Café Management System running on Windows, macOS, or Linux.

## 1. Environment Setup

### Install Python
Ensure you have Python 3.8+ installed. Check with:
```bash
python --version
```

### Install MongoDB
Ensure MongoDB is running locally. By default, the app looks for `mongodb://localhost:27017/`.

## 2. Dependencies Installation

Open your terminal in the project root and run:
```bash
pip install -r requirements.txt
```

## 3. Database Initialization

Seed the database with the pre-configured 59 menu items:
```bash
python seed_db.py
```
**Expected Output:** `✅ Successfully seeded 59 menu items!`

## 4. Run the Application

Start the Flask development server:
```bash
python app.py
```

## 5. Access the Dashboard

Open your browser and navigate to:
**[http://localhost:5000](http://localhost:5000)**

---

## 🛠️ Troubleshooting Checklist

- **MongoDB Connection Error**: Check if MongoDB service is running and the URI in `.env` is correct.
- **Port 5000 in Use**: Change the port in `app.py` or stop the existing process.
- **Missing Dependencies**: Re-run `pip install -r requirements.txt`.

## 💡 Quick API Test
Test the API using cURL:
```bash
curl http://localhost:5000/api/menu-items
```
