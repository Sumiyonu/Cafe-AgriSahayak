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
    
    # --- MILKSHAKES (25) ---
    milkshakes = [
        ("Oreo Milkshake", 100, "Rich and creamy milkshake featuring Oreo cookies blended with chilled milk."),
        ("Belgian Dark Chocolate Milkshake", 100, "Premium dark chocolate blended into a smooth and indulgent shake."),
        ("Dry Fruit Milkshake", 150, "Energy-packed milkshake blended with cashews, almonds, pistachios and chilled milk."),
        ("Brownie Milkshake", 120, "Chocolate brownie blended with creamy milk for a rich dessert-style shake."),
        ("Strawberry Milkshake", 80, "Fresh strawberry flavored shake, smooth and refreshing."),
        ("Watermelon Milkshake", 80, "Light and refreshing milkshake made with chilled watermelon."),
        ("Blueberry Milkshake", 90, "Sweet and tangy blueberry milkshake with smooth texture."),
        ("Black Current Milkshake", 90, "Fruity and refreshing black currant flavored milkshake."),
        ("Butterscotch Milkshake", 80, "Classic butterscotch flavor blended into creamy chilled milk."),
        ("Mango Milkshake", 80, "Sweet tropical mango milkshake made with fresh mango crush."),
        ("Orange Milkshake", 80, "Citrusy orange milkshake blended into creamy milk."),
        ("Banana Milkshake", 80, "Creamy banana blended with milk for natural sweetness."),
        ("Vanilla Milkshake", 80, "Classic vanilla flavored creamy milkshake."),
        ("Pineapple Milkshake", 80, "Refreshing pineapple crush blended into chilled milk."),
        ("Guava Milkshake", 80, "Sweet guava blended into a smooth and fruity shake."),
        ("Kiwi Milkshake", 80, "Tangy kiwi flavored refreshing milkshake."),
        ("Kolkata Pan Milkshake", 100, "Milkshake infused with traditional paan flavor."),
        ("Pista Milkshake", 80, "Creamy pistachio flavored milkshake."),
        ("Banana Bonkers Milkshake", 90, "Banana based milkshake with enhanced sweetness."),
        ("Kitkat Milkshake", 100, "Creamy chocolate milkshake blended with Kitkat pieces."),
        ("5 Star Chocolate Milkshake", 100, "Chocolate milkshake blended with 5 Star chocolate."),
        ("Gems Milkshake", 100, "Colorful Gems chocolate blended into a creamy milkshake."),
        ("Snickers Milkshake", 100, "Snickers chocolate blended into rich milkshake."),
        ("Choco Butterscotch Milkshake", 100, "Butterscotch and chocolate blended into creamy milk."),
        ("Choco-nut Crunch Supreme", 120, "Chocolate and nut infused premium thick milkshake.")
    ]
    
    for i, (name, price, desc) in enumerate(milkshakes):
        menu_items.append({
            "item_id": f"M{str(i+1).zfill(3)}",
            "name": name,
            "category": "Milkshakes",
            "price": price,
            "description": desc,
            "image_url": ""
        })

    # --- ICE CREAM SHAKES (23) ---
    ice_cream_shakes = [
        ("Kitkat Ice Cream Shake", 150, "Ice cream blended with Kitkat chocolate and milk."),
        ("Mango Ice Cream Shake", 150, "Mango flavored ice cream blended into thick shake."),
        ("Belgian Dark Chocolate Ice Cream Shake", 150, "Premium Belgian chocolate ice cream blended smoothly."),
        ("Blended Brownie Ice Cream Shake", 180, "Chocolate brownie blended with creamy ice cream."),
        ("Gems Ice Cream Shake", 80, "Ice cream blended with Gems chocolates."),
        ("Black Current Ice Cream Shake", 80, "Black currant ice cream blended into smooth shake."),
        ("Butterscotch Ice Cream Shake", 150, "Butterscotch ice cream blended into creamy shake."),
        ("Watermelon Ice Cream Shake", 150, "Watermelon flavored ice cream blended with milk."),
        ("Pineapple Ice Cream Shake", 150, "Pineapple flavored ice cream blended smoothly."),
        ("Guava Ice Cream Shake", 150, "Guava flavored ice cream blended creamy."),
        ("Vanilla Ice Cream Shake", 150, "Classic vanilla ice cream blended shake."),
        ("Orange Ice Cream Shake", 150, "Citrusy orange flavored ice cream shake."),
        ("Banana Ice Cream Shake", 150, "Banana flavored creamy ice cream shake."),
        ("Strawberry Ice Cream Shake", 150, "Strawberry ice cream blended into thick shake."),
        ("Kiwi Ice Cream Shake", 150, "Kiwi flavored ice cream blended smoothly."),
        ("Kolkata Pan Ice Cream Shake", 150, "Paan flavored ice cream blended shake."),
        ("Pista Ice Cream Shake", 150, "Pistachio ice cream blended into creamy shake."),
        ("Blueberry Ice Cream Shake", 150, "Blueberry flavored ice cream shake."),
        ("Chocolate Ice Cream Shake", 150, "Chocolate ice cream blended into smooth shake."),
        ("Banana Bonkers Ice Cream Shake", 170, "Banana ice cream shake topped with chocolate."),
        ("5 Star Ice Cream Shake", 150, "5 Star chocolate blended into ice cream shake."),
        ("Choco Butterscotch Ice Cream Shake", 150, "Chocolate and butterscotch blended ice cream shake."),
        ("Belgian Dark Chocolate Ice Cream Shake (Special)", 150, "Premium Belgian chocolate ice cream blend.")
    ]
    
    for i, (name, price, desc) in enumerate(ice_cream_shakes):
        menu_items.append({
            "item_id": f"I{str(i+1).zfill(3)}",
            "name": name,
            "category": "Ice Cream Shakes",
            "price": price,
            "description": desc,
            "image_url": ""
        })

    # --- SNACKS (6) ---
    snacks = [
        ("Peri Peri French Fries", 100, "Crispy fries coated in peri peri spice blend."),
        ("Masala Fries", 70, "Classic fries tossed with spicy masala seasoning."),
        ("Peri Smilies", 50, "Smiley shaped potato snacks with peri peri flavor."),
        ("Cheesy Fries", 150, "Loaded fries topped with melted cheese."),
        ("Classic Salted Smilies", 50, "Golden fried smiley potatoes lightly salted."),
        ("Classic Salted French Fries", 85, "Classic salted crispy French fries.")
    ]
    
    for i, (name, price, desc) in enumerate(snacks):
        menu_items.append({
            "item_id": f"S{str(i+1).zfill(3)}",
            "name": name,
            "category": "Snacks",
            "price": price,
            "description": desc,
            "image_url": ""
        })

    # --- COMBO OFFERS (5) ---
    combos = [
        ("Mango Milkshake + French Fries", 140, "Sweet mango milkshake paired with crispy fries."),
        ("Watermelon Milkshake + Classic French Fries", 140, "Refreshing watermelon shake with salted fries."),
        ("Vanilla Milkshake + Classic French Fries", 140, "Classic vanilla shake with crispy fries."),
        ("Chocolate Milkshake + Classic French Fries", 160, "Chocolate milkshake served with fries."),
        ("Orange Milkshake + Classic French Fries", 140, "Citrusy orange milkshake paired with salted fries.")
    ]
    
    for i, (name, price, desc) in enumerate(combos):
        menu_items.append({
            "item_id": f"C{str(i+1).zfill(3)}",
            "name": name,
            "category": "Combo Offers",
            "price": price,
            "description": desc,
            "image_url": ""
        })
    
    result = menu_collection.insert_many(menu_items)
    print(f"✅ Successfully seeded {len(result.inserted_ids)} menu items!")

if __name__ == "__main__":
    seed_database()
