import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def check_users():
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client.get_database()
    users = db.users
    
    print("Listing all users and their password hash formats:")
    for user in users.find():
        pw = user.get('password', '')
        fmt = "BCRYPT" if pw.startswith('$2b$') else "WERKZEUG/OTHER"
        print(f"User: {user['username']}, Role: {user['role']}, Format: {fmt}, Hash Start: {pw[:20] if pw else 'N/A'}")

if __name__ == "__main__":
    check_users()
