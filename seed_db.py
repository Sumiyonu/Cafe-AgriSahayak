import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def seed_database():
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client.get_database()
    
    # Collections
    menu_collection = db.menu_items
    
    # Clear existing data
    menu_collection.delete_many({})
    
    menu_items = []
    
    # Milkshakes (20)
    milkshake_names = [
        "Chocolate", "Strawberry", "Vanilla", "Banana", "Mango", 
        "Oreo", "Blueberry", "Pistachio", "Dates", "Kiwi", 
        "Peanut Butter", "Caramel", "Coffee", "Hazelnut", "Coconut", 
        "Walnut", "Buttermilk", "Lassi", "Mocha", "Maple"
    ]
    for i, name in enumerate(milkshake_names):
        menu_items.append({
            "item_id": f"M{str(i+1).zfill(3)}",
            "name": f"{name} Milkshake",
            "category": "Milkshake",
            "price": 150,
            "description": f"Refreshing {name} flavored milkshake.",
            "image_url": ""
        })

    # Ice Cream Shakes (20)
    ice_cream_names = [
        "Vanilla", "Chocolate", "Strawberry", "Butterscotch", "Mint Choco", 
        "Mango", "Pistachio", "Banana", "Oreo", "Dates", 
        "Kiwi", "Coffee", "Caramel", "Hazelnut", "Peanut Butter", 
        "Coconut", "Walnut", "Black Forest", "Mocha", "Blueberry"
    ]
    for i, name in enumerate(ice_cream_names):
        menu_items.append({
            "item_id": f"I{str(i+1).zfill(3)}",
            "name": f"{name} Ice Cream Shake",
            "category": "Ice Cream Shake",
            "price": 200,
            "description": f"Creamy {name} flavored ice cream shake.",
            "image_url": ""
        })

    # Snacks (12)
    snacks = [
        ("Samosa", 40), ("Pakora", 50), ("Vada Pav", 60), ("Bread Pakora", 50),
        ("Cheese Fries", 80), ("Garlic Bread", 70), ("Momos", 60), ("Spring Roll", 70),
        ("Nachos", 90), ("French Fries", 60), ("Paneer Fritters", 80), ("Chilli Cheese Toast", 75)
    ]
    for i, (name, price) in enumerate(snacks):
        menu_items.append({
            "item_id": f"S{str(i+1).zfill(3)}",
            "name": name,
            "category": "Snacks",
            "price": price,
            "description": f"Delicious {name}.",
            "image_url": ""
        })

    # Combos (7)
    combos = [
        ("Milkshake + Samosa", 180), ("Milkshake + Pakora", 190), 
        ("Ice Cream + Fries", 240), ("Milkshake + Garlic Bread", 210),
        ("Ice Cream + Nachos", 260), ("Milkshake + Momos", 200),
        ("Ice Cream + Spring Roll", 250)
    ]
    for i, (name, price) in enumerate(combos):
        menu_items.append({
            "item_id": f"C{str(i+1).zfill(3)}",
            "name": name,
            "category": "Combos",
            "price": price,
            "description": f"Special combo: {name}.",
            "image_url": ""
        })
    
    result = menu_collection.insert_many(menu_items)
    print(f"✅ Successfully seeded {len(result.inserted_ids)} menu items!")

if __name__ == "__main__":
    seed_database()
