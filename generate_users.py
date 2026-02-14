from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from datetime import datetime

# Initialize bcrypt
bcrypt = Bcrypt()

# MongoDB connection
MONGO_URI = "mongodb+srv://ricky27333_db_user:GPxvNLS4kXbaP8eM@cafe-agrisahayak.xsa55vo.mongodb.net/cafe_management?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client.get_database()
users_collection = db["users"]

# Helper function to create user
def create_user(username, password, role, created_by="system"):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    user = {
        "username": username,
        "password": hashed_password,
        "role": role,
        "created_by": created_by,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    users_collection.insert_one(user)
    print(f"✅ Created {role}: {username}")

# ---- CREATE USERS ----

# Admins
create_user("1133557799", "2244668800", "admin")
create_user("9988776655", "1122334455", "admin")

# Staff
create_user("0088664422", "9977553311", "staff", "1133557799")
create_user("0088664433", "9977553311", "staff", "1133557799")
create_user("0088664444", "9977553311", "staff", "1133557799")
create_user("0088664455", "9977553311", "staff", "1133557799")
create_user("0088664466", "9977553311", "staff", "1133557799")

print("🎉 All users created successfully!")
