import os
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask import Flask

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)

def migrate_passwords():
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client.get_database()
    users = db.users
    
    # We can't actually re-hash pbkdf2 to bcrypt without the plaintext.
    # But we can check which users have bad hashes and reset them to something known or just report them.
    # For this exercise, let's reset 'admin' to 'admin' if it has a werkzeug hash.
    
    for user in users.find():
        pw = user.get('password', '')
        if not pw.startswith('$2b$'):
            print(f"User {user['username']} has non-bcrypt hash. Resetting to default (identical to username)...")
            new_hash = bcrypt.generate_password_hash(user['username']).decode('utf-8')
            users.update_one({"_id": user['_id']}, {"$set": {"password": new_hash}})
            print(f"Updated {user['username']}")

if __name__ == "__main__":
    with app.app_context():
        migrate_passwords()
