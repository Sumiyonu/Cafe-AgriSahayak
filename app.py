import os
import secrets
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, date
from flask import Flask, request, jsonify, render_template, send_from_directory, session, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson import ObjectId
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(24))
CORS(app)
bcrypt = Bcrypt(app)

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = "info"

# Configuration for file uploads
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
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
users = db.users

# --- Authentication Models & Decorators ---

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.role = user_data['role']
        self.is_active = user_data.get('is_active', True)

@login_manager.user_loader
def load_user(user_id):
    user_data = users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

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

# --- Auth Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        try:
            user_data = users.find_one({"username": username})
            if user_data and user_data.get('is_active', True) and bcrypt.check_password_hash(user_data['password'], password.encode('utf-8')):
                user = User(user_data)
                login_user(user)
                
                if request.is_json:
                    return jsonify({
                        "message": "Login successful",
                        "role": user.role,
                        "username": user.username,
                        "redirect": url_for('index')
                    })
                return redirect(url_for('index'))
            
            error_msg = "Invalid username or password"
            if item := users.find_one({"username": username}):
                if not item.get('is_active', True):
                    error_msg = "Your account has been deactivated. Please contact the administrator."
            
            if request.is_json:
                return jsonify({"error": error_msg}), 401
            return render_template("login.html", error=error_msg)
            
        except Exception as e:
            print("Login Error:", e)
            if request.is_json:
                return jsonify({"error": "Server error. Please try again."}), 500
            return render_template("login.html", error="Server error. Please try again.")
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- User Management (Admin Only) ---

@app.route('/admin/users')
@admin_required
def user_management():
    return render_template('users.html')

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    try:
        all_users = list(users.find({}, {"password": 0}))
        for u in all_users:
            u['_id'] = str(u['_id'])
        return jsonify(all_users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/create-user', methods=['POST'])
@admin_required
def create_user():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        role = data.get('role') # 'admin' or 'staff'
        
        if role not in ['admin', 'staff']:
            return jsonify({"error": "Invalid role"}), 400
            
        # Constraints
        admin_count = users.count_documents({"role": "admin"})
        staff_count = users.count_documents({"role": "staff"})
        
        if role == 'admin' and admin_count >= 2:
            return jsonify({"error": "Maximum 2 admin accounts allowed"}), 400
        if role == 'staff' and staff_count >= 5:
            return jsonify({"error": "Maximum 5 staff accounts allowed"}), 400
            
        if users.find_one({"username": username}):
            return jsonify({"error": "Username already exists"}), 400
            
        new_user = {
            "username": username,
            "password": bcrypt.generate_password_hash(password).decode('utf-8'),
            "role": role,
            "created_by": current_user.username,
            "created_at": datetime.now(),
            "is_active": True
        }
        
        users.insert_one(new_user)
        return jsonify({"message": f"User {username} created successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/toggle-user-status', methods=['POST'])
@admin_required
def toggle_user_status():
    try:
        data = request.json
        target_username = data.get('username')
        
        if target_username == current_user.username:
            return jsonify({"error": "Cannot deactivate your own account"}), 400
            
        user_data = users.find_one({"username": target_username})
        if not user_data:
            return jsonify({"error": "User not found"}), 404
            
        # Prevent deleting/deactivating the last admin
        if user_data['role'] == 'admin' and user_data['is_active']:
            admin_count = users.count_documents({"role": "admin", "is_active": True})
            if admin_count <= 1:
                return jsonify({"error": "Cannot deactivate the last active admin"}), 400
                
        new_status = not user_data.get('is_active', True)
        users.update_one({"username": target_username}, {"$set": {"is_active": new_status}})
        
        return jsonify({"message": f"User {target_username} status updated", "is_active": new_status})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Default User Bootstrap Logic ---
if users.count_documents({}) == 0:
    admin_user = {
        "username": "DI1:1133557799",
        "password": bcrypt.generate_password_hash("2244668800").decode('utf-8'),
        "role": "admin",
        "created_by": "system",
        "created_at": datetime.now(),
        "is_active": True
    }
    
    staff_user = {
        "username": "0088664422",
        "password": bcrypt.generate_password_hash("9977553311").decode('utf-8'),
        "role": "staff",
        "created_by": "DI1:1133557799",
        "created_at": datetime.now(),
        "is_active": True
    }
    
    users.insert_many([admin_user, staff_user])
    print("Default admin and staff accounts created successfully.")

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/api/upload-image', methods=['POST'])
@admin_required
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

@app.route('/static/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/menu-items', methods=['GET'])
@login_required
def get_menu_items():
    try:
        items = list(menu_items.find({}, {"_id": 0}))
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/record-sale', methods=['POST'])
@login_required
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
            "time_slot": get_time_slot(now.hour),
            "sold_by": current_user.username
        }
        
        sales.insert_one(sale)
        return jsonify({"message": "Sale recorded successfully", "sale": format_doc(sale)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/staff-performance', methods=['GET'])
@admin_required
def staff_performance():
    try:
        # Get filters from query params
        date_filter = request.args.get('date')
        month_filter = request.args.get('month')
        year_filter = request.args.get('year')
        
        match_query = {}
        if date_filter:
            match_query["date"] = date_filter
        if month_filter:
            match_query["month"] = month_filter
        if year_filter:
            match_query["year"] = year_filter
            
        pipeline = []
        if match_query:
            pipeline.append({"$match": match_query})
            
        pipeline.extend([
            {"$group": {
                "_id": "$sold_by",
                "total_sales": {"$sum": 1},
                "total_revenue": {"$sum": "$price"}
            }},
            {"$sort": {"total_revenue": -1}}
        ])
        
        performance = list(sales.aggregate(pipeline))
        return jsonify(performance)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/daily-dashboard', methods=['GET'])
@login_required
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
@admin_required
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
@admin_required
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
@admin_required
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
