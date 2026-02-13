import os
from datetime import datetime, date
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

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
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.get_database("cafe_management")
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
        category = request.args.get('category')
        query = {}
        if category:
            query['category'] = category
        
        items = list(menu_items.find(query))
        return jsonify([format_doc(i) for i in items])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/record-sale', methods=['POST'])
def record_sale():
    try:
        data = request.json
        item_id = data.get('item_id')
        
        item = menu_items.find_one({"item_id": item_id})
        if not item:
            return jsonify({"error": "Item not found"}), 404
        
        now = datetime.now()
        sale = {
            "item_id": item_id,
            "name": item['name'],
            "category": item['category'],
            "price": item['price'],
            "cost": item['cost'],
            "profit": round(item['price'] - item['cost'], 2),
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
                "total_profit": {"$sum": "$profit"},
                "total_cost": {"$sum": "$cost"},
                "order_count": {"$sum": 1},
                "avg_order_value": {"$avg": "$price"}
            }}
        ]
        
        stats = list(sales.aggregate(pipeline))
        summary = stats[0] if stats else {"total_revenue": 0, "total_profit": 0, "total_cost": 0, "order_count": 0, "avg_order_value": 0}
        
        # Category breakdown
        cat_pipeline = [
            {"$match": {"date": target_date}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}, "revenue": {"$sum": "$price"}}}
        ]
        categories = list(sales.aggregate(cat_pipeline))
        
        # Time slot breakdown
        time_pipeline = [
            {"$match": {"date": target_date}},
            {"$group": {"_id": "$time_slot", "count": {"$sum": 1}}}
        ]
        time_slots = list(sales.aggregate(time_pipeline))
        
        # Get cumulative sales data
        sales_data = list(sales.find({"date": target_date}, {"price": 1, "_id": 0}).sort("timestamp", 1))
        prices = [s['price'] for s in sales_data]
        
        return jsonify({
            "summary": summary,
            "categories": categories,
            "time_slots": time_slots,
            "sales_data": prices
        })
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
                "total_profit": {"$sum": "$profit"},
                "total_cost": {"$sum": "$cost"},
                "order_count": {"$sum": 1}
            }}
        ]
        
        stats = list(sales.aggregate(pipeline))
        summary = stats[0] if stats else {"total_revenue": 0, "total_profit": 0, "total_cost": 0, "order_count": 0}
        
        # Trend
        trend_pipeline = [
            {"$match": {"month": month, "year": year}},
            {"$group": {"_id": "$date", "revenue": {"$sum": "$price"}}},
            {"$sort": {"_id": 1}}
        ]
        trend = list(sales.aggregate(trend_pipeline))
        
        # Get cumulative sales data
        sales_data = list(sales.find({"month": month, "year": year}, {"price": 1, "_id": 0}).sort("timestamp", 1))
        prices = [s['price'] for s in sales_data]

        return jsonify({
            "summary": summary, 
            "trend": trend,
            "sales_data": prices
        })
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
                "profit": {"$sum": "$profit"},
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
                "total_profit": {"$sum": "$profit"},
                "order_count": {"$sum": 1}
            }}
        ]
        overall = list(sales.aggregate(overall_pipeline))
        summary = overall[0] if overall else {"total_revenue": 0, "total_profit": 0, "order_count": 0}
        
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
                "count": {"$sum": 1},
                "avg_profit": {"$avg": "$profit"}
            }}
        ]
        
        data = list(sales.aggregate(pipeline))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
