import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def seed_database():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(mongo_uri)
    db = client.get_database("cafe_management")
    
    # Collections
    menu_collection = db.menu_items
    sales_collection = db.sales
    
    # Clear existing data
    menu_collection.delete_many({})
    
    menu_items = [
        # MILKSHAKES (25)
        {"item_id": 1, "name": "Oreo Milkshake", "category": "Milkshakes", "price": 100, "cost": 40, "description": "Rich and creamy milkshake featuring Oreo cookies blended with chilled milk.", "image_url": ""},
        {"item_id": 2, "name": "Belgian Dark Chocolate Milkshake", "category": "Milkshakes", "price": 100, "cost": 45, "description": "Premium dark chocolate blended into a smooth and indulgent shake.", "image_url": ""},
        {"item_id": 3, "name": "Dry Fruit Milkshake", "category": "Milkshakes", "price": 150, "cost": 70, "description": "Energy-packed milkshake blended with cashews, almonds, pistachios and chilled milk.", "image_url": ""},
        {"item_id": 4, "name": "Brownie Milkshake", "category": "Milkshakes", "price": 120, "cost": 50, "description": "Chocolate brownie blended with creamy milk for a rich dessert-style shake.", "image_url": ""},
        {"item_id": 5, "name": "Strawberry Milkshake", "category": "Milkshakes", "price": 80, "cost": 30, "description": "Fresh strawberry flavored shake, smooth and refreshing.", "image_url": ""},
        {"item_id": 6, "name": "Watermelon Milkshake", "category": "Milkshakes", "price": 80, "cost": 30, "description": "Light and refreshing milkshake made with chilled watermelon.", "image_url": ""},
        {"item_id": 7, "name": "Blueberry Milkshake", "category": "Milkshakes", "price": 90, "cost": 35, "description": "Sweet and tangy blueberry milkshake with smooth texture.", "image_url": ""},
        {"item_id": 8, "name": "Black Current Milkshake", "category": "Milkshakes", "price": 90, "cost": 35, "description": "Fruity and refreshing black currant flavored milkshake.", "image_url": ""},
        {"item_id": 9, "name": "Butterscotch Milkshake", "category": "Milkshakes", "price": 80, "cost": 30, "description": "Classic butterscotch flavor blended into creamy chilled milk.", "image_url": ""},
        {"item_id": 10, "name": "Mango Milkshake", "category": "Milkshakes", "price": 80, "cost": 30, "description": "Sweet tropical mango milkshake made with fresh mango crush.", "image_url": ""},
        {"item_id": 11, "name": "Orange Milkshake", "category": "Milkshakes", "price": 80, "cost": 30, "description": "Citrusy orange milkshake blended into creamy milk.", "image_url": ""},
        {"item_id": 12, "name": "Banana Milkshake", "category": "Milkshakes", "price": 80, "cost": 30, "description": "Creamy banana blended with milk for natural sweetness.", "image_url": ""},
        {"item_id": 13, "name": "Vanilla Milkshake", "category": "Milkshakes", "price": 80, "cost": 30, "description": "Classic vanilla flavored creamy milkshake.", "image_url": ""},
        {"item_id": 14, "name": "Pineapple Milkshake", "category": "Milkshakes", "price": 80, "cost": 30, "description": "Refreshing pineapple crush blended into chilled milk.", "image_url": ""},
        {"item_id": 15, "name": "Guava Milkshake", "category": "Milkshakes", "price": 80, "cost": 30, "description": "Sweet guava blended into a smooth and fruity shake.", "image_url": ""},
        {"item_id": 16, "name": "Kiwi Milkshake", "category": "Milkshakes", "price": 80, "cost": 30, "description": "Tangy kiwi flavored refreshing milkshake.", "image_url": ""},
        {"item_id": 17, "name": "Kolkata Pan Milkshake", "category": "Milkshakes", "price": 100, "cost": 40, "description": "Milkshake infused with traditional paan flavor.", "image_url": ""},
        {"item_id": 18, "name": "Pista Milkshake", "category": "Milkshakes", "price": 80, "cost": 30, "description": "Creamy pistachio flavored milkshake.", "image_url": ""},
        {"item_id": 19, "name": "Banana Bonkers Milkshake", "category": "Milkshakes", "price": 90, "cost": 35, "description": "Banana based milkshake with enhanced sweetness.", "image_url": ""},
        {"item_id": 20, "name": "Kitkat Milkshake", "category": "Milkshakes", "price": 100, "cost": 45, "description": "Creamy chocolate milkshake blended with Kitkat pieces.", "image_url": ""},
        {"item_id": 21, "name": "5 Star Chocolate Milkshake", "category": "Milkshakes", "price": 100, "cost": 45, "description": "Chocolate milkshake blended with 5 Star chocolate.", "image_url": ""},
        {"item_id": 22, "name": "Gems Milkshake", "category": "Milkshakes", "price": 100, "cost": 40, "description": "Colorful Gems chocolate blended into a creamy milkshake.", "image_url": ""},
        {"item_id": 23, "name": "Snickers Milkshake", "category": "Milkshakes", "price": 100, "cost": 50, "description": "Snickers chocolate blended into rich milkshake.", "image_url": ""},
        {"item_id": 24, "name": "Choco Butterscotch Milkshake", "category": "Milkshakes", "price": 100, "cost": 40, "description": "Butterscotch and chocolate blended into creamy milk.", "image_url": ""},
        {"item_id": 25, "name": "Choco-nut Crunch Supreme", "category": "Milkshakes", "price": 120, "cost": 55, "description": "Chocolate and nut infused premium thick milkshake.", "image_url": ""},

        # ICE CREAM SHAKES (23)
        {"item_id": 26, "name": "Kitkat Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 70, "description": "Ice cream blended with Kitkat chocolate and milk.", "image_url": ""},
        {"item_id": 27, "name": "Mango Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 65, "description": "Mango flavored ice cream blended into thick shake.", "image_url": ""},
        {"item_id": 28, "name": "Belgian Dark Chocolate Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 75, "description": "Premium Belgian chocolate ice cream blended smoothly.", "image_url": ""},
        {"item_id": 29, "name": "Blended Brownie Ice Cream Shake", "category": "Ice Cream Shakes", "price": 180, "cost": 85, "description": "Chocolate brownie blended with creamy ice cream.", "image_url": ""},
        {"item_id": 30, "name": "Gems Ice Cream Shake", "category": "Ice Cream Shakes", "price": 80, "cost": 35, "description": "Ice cream blended with Gems chocolates.", "image_url": ""},
        {"item_id": 31, "name": "Black Current Ice Cream Shake", "category": "Ice Cream Shakes", "price": 80, "cost": 35, "description": "Black currant ice cream blended into smooth shake.", "image_url": ""},
        {"item_id": 32, "name": "Butterscotch Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 65, "description": "Butterscotch ice cream blended into creamy shake.", "image_url": ""},
        {"item_id": 33, "name": "Watermelon Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 60, "description": "Watermelon flavored ice cream blended with milk.", "image_url": ""},
        {"item_id": 34, "name": "Pineapple Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 60, "description": "Pineapple flavored ice cream blended smoothly.", "image_url": ""},
        {"item_id": 35, "name": "Guava Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 60, "description": "Guava flavored ice cream blended creamy.", "image_url": ""},
        {"item_id": 36, "name": "Vanilla Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 60, "description": "Classic vanilla ice cream blended shake.", "image_url": ""},
        {"item_id": 37, "name": "Orange Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 60, "description": "Citrusy orange flavored ice cream shake.", "image_url": ""},
        {"item_id": 38, "name": "Banana Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 60, "description": "Banana flavored creamy ice cream shake.", "image_url": ""},
        {"item_id": 39, "name": "Strawberry Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 60, "description": "Strawberry ice cream blended into thick shake.", "image_url": ""},
        {"item_id": 40, "name": "Kiwi Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 65, "description": "Kiwi flavored ice cream blended smoothly.", "image_url": ""},
        {"item_id": 41, "name": "Kolkata Pan Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 65, "description": "Paan flavored ice cream blended shake.", "image_url": ""},
        {"item_id": 42, "name": "Pista Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 65, "description": "Pistachio ice cream blended into creamy shake.", "image_url": ""},
        {"item_id": 43, "name": "Blueberry Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 65, "description": "Blueberry flavored ice cream shake.", "image_url": ""},
        {"item_id": 44, "name": "Chocolate Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 65, "description": "Chocolate ice cream blended into smooth shake.", "image_url": ""},
        {"item_id": 45, "name": "Banana Bonkers Ice Cream Shake", "category": "Ice Cream Shakes", "price": 170, "cost": 75, "description": "Banana ice cream shake topped with chocolate.", "image_url": ""},
        {"item_id": 46, "name": "5 Star Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 70, "description": "5 Star chocolate blended into ice cream shake.", "image_url": ""},
        {"item_id": 47, "name": "Choco Butterscotch Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 70, "description": "Chocolate and butterscotch blended ice cream shake.", "image_url": ""},
        {"item_id": 48, "name": "Premium Belgian Dark Chocolate Ice Cream Shake", "category": "Ice Cream Shakes", "price": 150, "cost": 75, "description": "Premium Belgian chocolate ice cream blend.", "image_url": ""},

        # SNACKS (6)
        {"item_id": 49, "name": "Peri Peri French Fries", "category": "Snacks", "price": 100, "cost": 30, "description": "Crispy fries coated in peri peri spice blend.", "image_url": ""},
        {"item_id": 50, "name": "Masala Fries", "category": "Snacks", "price": 70, "cost": 20, "description": "Classic fries tossed with spicy masala seasoning.", "image_url": ""},
        {"item_id": 51, "name": "Peri Smilies", "category": "Snacks", "price": 50, "cost": 15, "description": "Smiley shaped potato snacks with peri peri flavor.", "image_url": ""},
        {"item_id": 52, "name": "Cheesy Fries", "category": "Snacks", "price": 150, "cost": 60, "description": "Loaded fries topped with melted cheese.", "image_url": ""},
        {"item_id": 53, "name": "Classic Salted Smilies", "category": "Snacks", "price": 50, "cost": 15, "description": "Golden fried smiley potatoes lightly salted.", "image_url": ""},
        {"item_id": 54, "name": "Classic Salted French Fries", "category": "Snacks", "price": 85, "cost": 25, "description": "Classic salted crispy French fries.", "image_url": ""},

        # COMBO OFFERS (5)
        {"item_id": 55, "name": "Mango Milkshake + French Fries", "category": "Combo Offers", "price": 140, "cost": 50, "description": "Sweet mango milkshake paired with crispy fries.", "image_url": ""},
        {"item_id": 56, "name": "Watermelon Milkshake + Classic French Fries", "category": "Combo Offers", "price": 140, "cost": 45, "description": "Refreshing watermelon shake with salted fries.", "image_url": ""},
        {"item_id": 57, "name": "Vanilla Milkshake + Classic French Fries", "category": "Combo Offers", "price": 140, "cost": 45, "description": "Classic vanilla shake with crispy fries.", "image_url": ""},
        {"item_id": 58, "name": "Chocolate Milkshake + Classic French Fries", "category": "Combo Offers", "price": 160, "cost": 60, "description": "Chocolate milkshake served with fries.", "image_url": ""},
        {"item_id": 59, "name": "Orange Milkshake + Classic French Fries", "category": "Combo Offers", "price": 140, "cost": 45, "description": "Orange milkshake paired with crispy fries.", "image_url": ""},
    ]
    
    result = menu_collection.insert_many(menu_items)
    print(f"✅ Successfully seeded {len(result.inserted_ids)} menu items!")

if __name__ == "__main__":
    seed_database()
