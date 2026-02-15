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
app.config["DEBUG"] = True
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

# Ensure Unique Index on Name
menu_items.create_index("name", unique=True)

def sync_menu_items():
    from datetime import datetime
    
    # 1. Initialize default fields for existing items if they don't exist
    menu_items.update_many({"is_active": {"$exists": False}}, {"$set": {"is_active": True}})
    menu_items.update_many({"order_count": {"$exists": False}}, {"$set": {"order_count": 0}})
    menu_items.update_many({"created_at": {"$exists": False}}, {"$set": {"created_at": datetime.now()}})
    menu_items.update_many({"updated_at": {"$exists": False}}, {"$set": {"updated_at": datetime.now()}})
    
    # 2. Get existing names
    existing_names = set(
        item["name"] for item in menu_items.find({}, {"name": 1})
    )

    MASTER_MENU = [
        # MILKSHAKES (25)
        {"name": "Oreo Milkshake", "category": "Milkshakes", "price": 100, "description": "Rich and creamy milkshake featuring Oreo cookies blended with chilled milk."},
        {"name": "Belgian Dark Chocolate Milkshake", "category": "Milkshakes", "price": 100, "description": "Premium dark chocolate blended into a smooth and indulgent shake."},
        {"name": "Dry Fruit Milkshake", "category": "Milkshakes", "price": 150, "description": "Energy-packed milkshake blended with cashews, almonds, pistachios and chilled milk."},
        {"name": "Brownie Milkshake", "category": "Milkshakes", "price": 120, "description": "Chocolate brownie blended with creamy milk for a rich dessert-style shake."},
        {"name": "Strawberry Milkshake", "category": "Milkshakes", "price": 80, "description": "Fresh strawberry flavored shake, smooth and refreshing."},
        {"name": "Watermelon Milkshake", "category": "Milkshakes", "price": 80, "description": "Light and refreshing milkshake made with chilled watermelon."},
        {"name": "Blueberry Milkshake", "category": "Milkshakes", "price": 90, "description": "Sweet and tangy blueberry milkshake with smooth texture."},
        {"name": "Black Current Milkshake", "category": "Milkshakes", "price": 90, "description": "Fruity and refreshing black currant flavored milkshake."},
        {"name": "Butterscotch Milkshake", "category": "Milkshakes", "price": 80, "description": "Classic butterscotch flavor blended into creamy chilled milk."},
        {"name": "Mango Milkshake", "category": "Milkshakes", "price": 80, "description": "Sweet tropical mango milkshake made with fresh mango crush."},
        {"name": "Orange Milkshake", "category": "Milkshakes", "price": 80, "description": "Citrusy orange milkshake blended into creamy milk."},
        {"name": "Banana Milkshake", "category": "Milkshakes", "price": 80, "description": "Creamy banana blended with milk for natural sweetness."},
        {"name": "Vanilla Milkshake", "category": "Milkshakes", "price": 80, "description": "Classic vanilla flavored creamy milkshake."},
        {"name": "Pineapple Milkshake", "category": "Milkshakes", "price": 80, "description": "Refreshing pineapple crush blended into chilled milk."},
        {"name": "Guava Milkshake", "category": "Milkshakes", "price": 80, "description": "Sweet guava blended into a smooth and fruity shake."},
        {"name": "Kiwi Milkshake", "category": "Milkshakes", "price": 80, "description": "Tangy kiwi flavored refreshing milkshake."},
        {"name": "Kolkata Pan Milkshake", "category": "Milkshakes", "price": 100, "description": "Milkshake infused with traditional paan flavor."},
        {"name": "Pista Milkshake", "category": "Milkshakes", "price": 80, "description": "Creamy pistachio flavored milkshake."},
        {"name": "Banana Bonkers Milkshake", "category": "Milkshakes", "price": 90, "description": "Banana based milkshake with enhanced sweetness."},
        {"name": "Kitkat Milkshake", "category": "Milkshakes", "price": 100, "description": "Creamy chocolate milkshake blended with Kitkat pieces."},
        {"name": "5 Star Chocolate Milkshake", "category": "Milkshakes", "price": 100, "description": "Chocolate milkshake blended with 5 Star chocolate."},
        {"name": "Gems Milkshake", "category": "Milkshakes", "price": 100, "description": "Colorful Gems chocolate blended into a creamy milkshake."},
        {"name": "Snickers Milkshake", "category": "Milkshakes", "price": 100, "description": "Snickers chocolate blended into rich milkshake."},
        {"name": "Choco Butterscotch Milkshake", "category": "Milkshakes", "price": 100, "description": "Butterscotch and chocolate blended into creamy milk."},
        {"name": "Choco-nut Crunch Supreme", "category": "Milkshakes", "price": 120, "description": "Chocolate and nut infused premium thick milkshake."},

        # ICE CREAM SHAKES (23)
        {"name": "Kitkat Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Ice cream blended with Kitkat chocolate and milk."},
        {"name": "Mango Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Mango flavored ice cream blended into thick shake."},
        {"name": "Belgian Dark Chocolate Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Premium Belgian chocolate ice cream blended smoothly."},
        {"name": "Blended Brownie Ice Cream Shake", "category": "Ice Cream Shakes", "price": 180, "description": "Chocolate brownie blended with creamy ice cream."},
        {"name": "Gems Ice Cream Shake", "category": "Ice Cream Shakes", "price": 80, "description": "Ice cream blended with Gems chocolates."},
        {"name": "Black Current Ice Cream Shake", "category": "Ice Cream Shakes", "price": 80, "description": "Black currant ice cream blended into smooth shake."},
        {"name": "Butterscotch Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Butterscotch ice cream blended into creamy shake."},
        {"name": "Watermelon Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Watermelon flavored ice cream blended with milk."},
        {"name": "Pineapple Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Pineapple flavored ice cream blended smoothly."},
        {"name": "Guava Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Guava flavored ice cream blended creamy."},
        {"name": "Vanilla Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Classic vanilla ice cream blended shake."},
        {"name": "Orange Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Citrusy orange flavored ice cream shake."},
        {"name": "Banana Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Banana flavored creamy ice cream shake."},
        {"name": "Strawberry Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Strawberry ice cream blended into thick shake."},
        {"name": "Kiwi Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Kiwi flavored ice cream blended smoothly."},
        {"name": "Kolkata Pan Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Paan flavored ice cream blended shake."},
        {"name": "Pista Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Pistachio ice cream blended into creamy shake."},
        {"name": "Blueberry Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Blueberry flavored ice cream shake."},
        {"name": "Chocolate Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Chocolate ice cream blended into smooth shake."},
        {"name": "Banana Bonkers Ice Cream Shake", "category": "Ice Cream Shakes", "price": 170, "description": "Banana ice cream shake topped with chocolate."},
        {"name": "5 Star Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "5 Star chocolate blended into ice cream shake."},
        {"name": "Choco Butterscotch Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "description": "Chocolate and butterscotch blended ice cream shake."},
        {"name": "Belgian Dark Chocolate Ice Cream Shake (Special)", "category": "Ice Cream Shakes", "price": 150, "description": "Premium Belgian chocolate ice cream blend."},

        # SNACKS (6)
        {"name": "Peri Peri French Fries", "category": "Snacks", "price": 100, "description": "Crispy fries coated in peri peri spice blend."},
        {"name": "Masala Fries", "category": "Snacks", "price": 70, "description": "Classic fries tossed with spicy masala seasoning."},
        {"name": "Peri Smilies", "category": "Snacks", "price": 50, "description": "Smiley shaped potato snacks with peri peri flavor."},
        {"name": "Cheesy Fries", "category": "Snacks", "price": 150, "description": "Loaded fries topped with melted cheese."},
        {"name": "Classic Salted Smilies", "category": "Snacks", "price": 50, "description": "Golden fried smiley potatoes lightly salted."},
        {"name": "Classic Salted French Fries", "category": "Snacks", "price": 85, "description": "Classic salted crispy French fries."},

        # COMBO OFFERS (5)
        {"name": "Mango Milkshake + French Fries", "category": "Combo Offers", "price": 140, "description": "Sweet mango milkshake paired with crispy fries."},
        {"name": "Watermelon Milkshake + Classic French Fries", "category": "Combo Offers", "price": 140, "description": "Refreshing watermelon shake with salted fries."},
        {"name": "Vanilla Milkshake + Classic French Fries", "category": "Combo Offers", "price": 140, "description": "Classic vanilla shake with crispy fries."},
        {"name": "Chocolate Milkshake + Classic French Fries", "category": "Combo Offers", "price": 160, "description": "Chocolate milkshake served with fries."},
        {"name": "Orange Milkshake + Classic French Fries", "category": "Combo Offers", "price": 140, "description": "Citrusy orange milkshake paired with salted fries."}
    ]

    # 3. Synchronize Master Menu
    all_items = list(menu_items.find().sort("item_id", -1).limit(1))
    next_id = 1
    if all_items:
        last_id = all_items[0].get("item_id", 0)
        if isinstance(last_id, int):
            next_id = last_id + 1
        else:
            next_id = menu_items.count_documents({}) + 1

    for item in MASTER_MENU:
        if item["name"] not in existing_names:
            item["item_id"] = next_id
            item["is_active"] = True
            item["created_at"] = datetime.utcnow()
            item["order_count"] = 0
            item["image_url"] = ""
            menu_items.insert_one(item)
            next_id += 1
        else:
            # Update existing items to match MASTER_MENU specs (price/category/active)
            menu_items.update_one(
                {"name": item["name"]},
                {"$set": {
                    "category": item["category"],
                    "price": item["price"],
                    "is_active": True
                }}
            )

    # 4. Final Cleanup: Ensure every record has required fields
    menu_items.update_many({"order_count": {"$exists": False}}, {"$set": {"order_count": 0}})
    menu_items.update_many({"image_url": {"$exists": False}}, {"$set": {"image_url": ""}})
    
    print(f"✅ Menu sync complete. Total items: {menu_items.count_documents({})}")

# Run Sync
sync_menu_items()

# --- Authentication Models & Decorators ---

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['username']
        self.username = user_data['username']
        self.role = user_data['role']

@login_manager.user_loader
def load_user(user_id):
    user_data = users.find_one({"username": user_id})
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
    if 6 <= hour < 12: return "Morning"
    if 12 <= hour < 17: return "Afternoon"
    if 17 <= hour < 22: return "Evening"
    return "Unknown"

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
            import traceback
            traceback.print_exc()
            error_details = f"Login Error: {str(e)}"
            if request.is_json:
                return jsonify({"error": error_details}), 500
            return error_details
    
    return render_template('login.html')

@app.route('/health')
def health():
    return "OK", 200

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

@app.route('/api/admin/reset-password', methods=['POST'])
@admin_required
def reset_password():
    try:
        data = request.json
        target_username = data.get('username')
        new_password = data.get('password')
        
        if not target_username or not new_password:
            return jsonify({"error": "Missing username or password"}), 400
            
        users.update_one(
            {"username": target_username},
            {"$set": {"password": bcrypt.generate_password_hash(new_password).decode('utf-8')}}
        )
        return jsonify({"message": f"Password for {target_username} reset successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Default User Bootstrap Logic ---
if users.count_documents({}) == 0:
    admin_user = {
        "username": "admin",
        "password": bcrypt.generate_password_hash("admin123").decode('utf-8'),
        "role": "admin",
        "created_by": "system",
        "created_at": datetime.now(),
        "is_active": True
    }
    
    staff_user = {
        "username": "staff1",
        "password": bcrypt.generate_password_hash("staff123").decode('utf-8'),
        "role": "staff",
        "created_by": "admin",
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

@app.route('/api/admin/update-price/<int:item_id>', methods=['PUT'])
@app.route('/admin/update-price/<int:item_id>', methods=['PUT']) # Alias for shorter URL
@admin_required
def update_price(item_id):
    try:
        data = request.json
        new_price = data.get('price')
        
        if new_price is None:
            return jsonify({"error": "Price is required"}), 400
            
        try:
            new_price = float(new_price)
        except (ValueError, TypeError):
            return jsonify({"error": "Price must be a valid number"}), 400
            
        if new_price <= 0:
            return jsonify({"error": "Price must be greater than 0"}), 400
            
        if new_price > 10000:
            return jsonify({"error": "Price exceeds maximum limit (10,000)"}), 400

        # Find item
        item = menu_items.find_one({"item_id": int(item_id)})
        if not item:
            return jsonify({"error": "Item not found"}), 404
            
        old_price = item.get('price', 0)
        is_offer = data.get('is_offer', False)
        
        update_data = {"price": new_price}
        if is_offer:
            update_data["is_offer"] = True
            update_data["original_price"] = old_price if not item.get('is_offer') else item.get('original_price', old_price)
        else:
            update_data["is_offer"] = False
            update_data["original_price"] = 0

        # Update price and offer status
        menu_items.update_one(
            {"item_id": int(item_id)},
            {"$set": update_data}
        )
        
        # Log the change
        price_logs = db.price_logs
        price_logs.insert_one({
            "item_id": int(item_id),
            "item_name": item['name'],
            "old_price": old_price,
            "new_price": new_price,
            "is_offer": is_offer,
            "reason": data.get('reason', ''),
            "changed_by": current_user.username,
            "changed_at": datetime.now()
        })
        
        return jsonify({
            "message": "Price updated successfully",
            "new_price": new_price
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/static/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/menu-items', methods=['GET'])
@login_required
def get_menu_items():
    try:
        search_query = request.args.get('search')
        category = request.args.get('category', 'All')
        
        # Only show active items for sales entry
        query = {"is_active": {"$ne": False}}
        
        if category and category != 'All':
            query["category"] = category
            
        if search_query:
            search_regex = {"$regex": search_query, "$options": "i"}
            if "category" in query:
                query["name"] = search_regex
            else:
                query["$or"] = [{"name": search_regex}, {"category": search_regex}]
        
        # Sort by most sold first (Existing requirement)
        items = list(menu_items.find(query, {"_id": 0}).sort("order_count", -1))
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/menu-items', methods=['GET'])
@admin_required
def admin_get_menu_items():
    try:
        # Admin gets everything, sorted by creation or name
        items = list(menu_items.find({}, {"_id": 0}).sort("item_id", 1))
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/item', methods=['POST'])
@admin_required
def add_item():
    try:
        data = request.json
        name = data.get('name')
        category = data.get('category')
        price = float(data.get('price', 0))
        
        if not name or not category:
            return jsonify({"error": "Name and Category are required"}), 400
            
        # Get next ID
        last_item = menu_items.find_one(sort=[("item_id", -1)])
        next_id = (last_item["item_id"] + 1) if last_item else 1
        
        new_item = {
            "item_id": next_id,
            "name": name,
            "category": category,
            "price": price,
            "description": data.get('description', ''),
            "image_url": data.get('image_url', ''),
            "order_count": 0,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        menu_items.insert_one(new_item)
        return jsonify({"message": "Item added successfully", "item_id": next_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/item/<int:item_id>', methods=['PUT', 'DELETE'])
@admin_required
def update_item_full(item_id):
    try:
        if request.method == 'DELETE':
            # Soft delete (toggle is_active)
            item = menu_items.find_one({"item_id": item_id})
            if not item: return jsonify({"error": "Item not found"}), 404
            
            new_status = not item.get("is_active", True)
            menu_items.update_one({"item_id": item_id}, {"$set": {"is_active": new_status, "updated_at": datetime.now()}})
            return jsonify({"message": f"Item {'disabled' if not new_status else 'enabled'} successfully", "is_active": new_status})

        # PUT (Update)
        data = request.json
        update_data = {
            "name": data.get('name'),
            "category": data.get('category'),
            "price": float(data.get('price', 0)),
            "description": data.get('description', ''),
            "is_active": data.get('is_active', True),
            "updated_at": datetime.now()
        }
        
        if data.get('image_url'):
            update_data["image_url"] = data.get('image_url')

        result = menu_items.update_one({"item_id": item_id}, {"$set": update_data})
        if result.matched_count == 0:
            return jsonify({"error": "Item not found"}), 404
            
        return jsonify({"message": "Item updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/record-sale', methods=['POST'])
@login_required
def record_sale():
    try:
        data = request.json
        item_id = data.get('item_id')
        payment_method = data.get('payment_method', 'Cash')
        
        if payment_method not in ['Cash', 'PhonePe', 'UPI']:
            return jsonify({"error": "Invalid payment method"}), 400

        item = menu_items.find_one({"item_id": int(item_id)})
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
        menu_items.update_one({"item_id": int(item_id)}, {"$inc": {"order_count": 1}})
        
        return jsonify({"message": "Sale recorded successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/staff-performance', methods=['GET'])
@admin_required
def staff_performance():
    try:
        date_filter = request.args.get('date')
        month_filter = request.args.get('month')
        year_filter = request.args.get('year')
        
        match_query = {}
        if date_filter: match_query["date"] = date_filter
        if month_filter: match_query["month"] = month_filter
        if year_filter: match_query["year"] = year_filter
            
        pipeline = []
        if match_query: pipeline.append({"$match": match_query})
            
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
                "phonepe_amount": {"$sum": {"$cond": [{"$eq": ["$payment_method", "PhonePe"]}, "$price", 0]}},
                "upi_amount": {"$sum": {"$cond": [{"$eq": ["$payment_method", "UPI"]}, "$price", 0]}}
            }}
        ]
        stats = list(sales.aggregate(pipeline))
        summary = stats[0] if stats else {"total_revenue": 0, "order_count": 0, "cash_amount": 0, "phonepe_amount": 0, "upi_amount": 0}
        return jsonify(summary)
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
                "phonepe_amount": {"$sum": {"$cond": [{"$eq": ["$payment_method", "PhonePe"]}, "$price", 0]}},
                "upi_amount": {"$sum": {"$cond": [{"$eq": ["$payment_method", "UPI"]}, "$price", 0]}}
            }}
        ]
        stats = list(sales.aggregate(pipeline))
        summary = stats[0] if stats else {"total_revenue": 0, "order_count": 0, "cash_amount": 0, "phonepe_amount": 0, "upi_amount": 0}
        return jsonify(summary)
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
                "_id": None,
                "total_revenue": {"$sum": "$price"},
                "order_count": {"$sum": 1},
                "cash_amount": {"$sum": {"$cond": [{"$eq": ["$payment_method", "Cash"]}, "$price", 0]}},
                "phonepe_amount": {"$sum": {"$cond": [{"$eq": ["$payment_method", "PhonePe"]}, "$price", 0]}},
                "upi_amount": {"$sum": {"$cond": [{"$eq": ["$payment_method", "UPI"]}, "$price", 0]}}
            }}
        ]
        overall = list(sales.aggregate(pipeline))
        summary = overall[0] if overall else {"total_revenue": 0, "order_count": 0, "cash_amount": 0, "phonepe_amount": 0, "upi_amount": 0}
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/time-intelligence', methods=['GET'])
@admin_required
def time_intelligence():
    try:
        pipeline = [{"$group": {"_id": "$time_slot", "revenue": {"$sum": "$price"}, "count": {"$sum": 1}}}]
        data = list(sales.aggregate(pipeline))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

