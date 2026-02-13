import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

from datetime import datetime, date
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from bson import ObjectId
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

# Test Connection (Very Important)
try:
    client.admin.command('ping')
    print("✅ MongoDB Connected Successfully!")
except Exception as e:
    print("❌ MongoDB Connection Failed:", e)

db = client.get_database()
menu_items = db.menu_items
sales = db.sales

# --- Helper Functions ---

def get_time_slot(hour):
    if 5 <= hour < 11:
        return "Morning (5am-11am)"
    elif 11 <= hour < 14:
        return "Lunch (11am-2pm)"
    elif 14 <= hour < 17:
        return "Afternoon (2pm-5pm)"
    elif 17 <= hour < 21:
        return "Evening (5pm-9pm)"
    else:
        return "Late Night (9pm-5am)"

def format_doc(doc):
    if not doc:
        return None
    doc['_id'] = str(doc['_id'])
    return doc

# --- API Endpoints ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image part"}), 400
        file = request.files['image']
        item_id = request.form.get('item_id')
        
        if not item_id:
            return jsonify({"error": "No item_id provided"}), 400
            
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(f"item_{item_id}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Ensure folder exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file.save(filepath)
            
            # Update database
            image_url = f"/static/uploads/{filename}"
            menu_items.update_one({"item_id": int(item_id)}, {"$set": {"image_url": image_url}})
            
            return jsonify({"message": "Image uploaded successfully", "image_url": image_url})
            
        return jsonify({"error": "File type not allowed"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/menu-items', methods=['GET'])
def get_menu_items():
    try:
        items = list(menu_items.find({}, {"_id": 0}))
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/record-sale', methods=['POST'])
def record_sale():
    try:
        data = request.json
        item_id = data.get('item_id')
        payment_method = data.get('payment_method', 'Cash')
        
        if payment_method not in ['Cash', 'PhonePe']:
            return jsonify({"error": "Invalid payment method. Only Cash and PhonePe are allowed."}), 400

        item = menu_items.find_one({"item_id": item_id})
        if not item:
            return jsonify({"error": "Item not found"}), 404
        
        now = datetime.now()
        sale = {
            "item_id": item_id,
            "name": item['name'],
            "category": item['category'],
            "price": item['price'],
            "payment_method": payment_method,
            "timestamp": now,
            "date": now.strftime("%Y-%m-%d"),
            "month": now.strftime("%m"),
            "year": now.strftime("%Y"),
            "time_slot": get_time_slot(now.hour)
        }
        
        sales.insert_one(sale)
        return jsonify({"message": "Sale recorded successfully", "sale": format_doc(sale)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/daily-dashboard', methods=['GET'])
def daily_dashboard():
    try:
        target_date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
        
        pipeline = [
            {"$match": {"date": target_date}},
            {"$group": {
                "_id": None,
                "total_revenue": {"$sum": "$price"},
                "order_count": {"$sum": 1},
                "cash_amount": {"$sum": {"$cond": [{"$eq": ["$payment_method", "Cash"]}, "$price", 0]}},
                "phonepe_amount": {"$sum": {"$cond": [{"$eq": ["$payment_method", "PhonePe"]}, "$price", 0]}}
            }}
        ]
        
        stats = list(sales.aggregate(pipeline))
        result = stats[0] if stats else {"total_revenue": 0, "order_count": 0, "cash_amount": 0, "phonepe_amount": 0}
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/monthly-dashboard', methods=['GET'])
def monthly_dashboard():
    try:
        now = datetime.now()
        month = request.args.get('month', now.strftime("%m"))
        year = request.args.get('year', now.strftime("%Y"))
        
        pipeline = [
            {"$match": {"month": month, "year": year}},
            {"$group": {
                "_id": None,
                "total_revenue": {"$sum": "$price"},
                "order_count": {"$sum": 1},
                "cash_amount": {"$sum": {"$cond": [{"$eq": ["$payment_method", "Cash"]}, "$price", 0]}},
                "phonepe_amount": {"$sum": {"$cond": [{"$eq": ["$payment_method", "PhonePe"]}, "$price", 0]}}
            }}
        ]
        
        stats = list(sales.aggregate(pipeline))
        result = stats[0] if stats else {"total_revenue": 0, "order_count": 0, "cash_amount": 0, "phonepe_amount": 0}
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/yearly-dashboard', methods=['GET'])
def yearly_dashboard():
    try:
        year = request.args.get('year', datetime.now().strftime("%Y"))
        
        pipeline = [
            {"$match": {"year": year}},
            {"$group": {
                "_id": "$month",
                "revenue": {"$sum": "$price"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        monthly_data = list(sales.aggregate(pipeline))
        
        overall_pipeline = [
            {"$match": {"year": year}},
            {"$group": {
                "_id": None,
                "total_revenue": {"$sum": "$price"},
                "order_count": {"$sum": 1}
            }}
        ]
        overall = list(sales.aggregate(overall_pipeline))
        summary = overall[0] if overall else {"total_revenue": 0, "order_count": 0}
        
        return jsonify({"summary": summary, "monthly_breakdown": monthly_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/time-intelligence', methods=['GET'])
def time_intelligence():
    try:
        pipeline = [
            {"$group": {
                "_id": "$time_slot",
                "revenue": {"$sum": "$price"},
                "count": {"$sum": 1}
            }}
        ]
        
        data = list(sales.aggregate(pipeline))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
