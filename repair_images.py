import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def repair_images():
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client.get_database()
    menu_collection = db.menu_items
    
    upload_dir = os.path.join('static', 'uploads')
    if not os.path.exists(upload_dir):
        print(f"❌ {upload_dir} does not exist.")
        return

    files = os.listdir(upload_dir)
    updated_count = 0
    
    # We want to use the latest file for each item_id if there are multiple
    # Actually, let's just sort and map.
    files.sort()
    
    for filename in files:
        if filename.startswith('item_'):
            try:
                # Format: item_ID_...
                parts = filename.split('_')
                if len(parts) >= 2:
                    item_id = int(parts[1])
                    image_url = f"/static/uploads/{filename}"
                    
                    # Update DB
                    result = menu_collection.update_one(
                        {"item_id": item_id},
                        {"$set": {"image_url": image_url}}
                    )
                    
                    if result.modified_count > 0:
                        print(f"✅ Updated Item {item_id} with image: {filename}")
                        updated_count += 1
                    else:
                        # Check if it was already set to this
                        existing = menu_collection.find_one({"item_id": item_id})
                        if existing and existing.get('image_url') == image_url:
                            print(f"ℹ️ Item {item_id} already has correct image: {filename}")
                        else:
                            print(f"⚠️ Item {item_id} not found or update failed for {filename}")
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")

    print(f"\n✨ Repair complete. Updated {updated_count} items.")

if __name__ == "__main__":
    repair_images()
