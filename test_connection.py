from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def test_mongodb():
    try:
        # Get MongoDB URI from .env
        mongo_uri = os.getenv('MONGO_URI')
        
        if not mongo_uri:
            print("❌ Error: .env file में MONGO_URI नहीं मिला!")
            print("💡 Tip: .env file बनाएं और MONGO_URI add करें")
            return
        
        print("🔄 MongoDB से connect हो रहा है...")
        print(f"📍 URI: {mongo_uri[:30]}...") 
        
        # Connect to MongoDB
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        
        print("✅ MongoDB connection सफल!")
        print("✅ आपका database तैयार है!")
        
        # Get database
        db = client.project_manager
        
        # Insert test document
        test_data = {
            "message": "Hello from Python!",
            "status": "working"
        }
        
        result = db.test.insert_one(test_data)
        print(f"✅ Test data insert हो गया! ID: {result.inserted_id}")
        
        # Read it back
        found = db.test.find_one({"_id": result.inserted_id})
        print(f"✅ Test data मिल गया: {found}")
        
        # Delete test data
        db.test.delete_one({"_id": result.inserted_id})
        print("✅ Test data delete हो गया!")
        
        # Close connection
        client.close()
        print("🎉 सब कुछ ठीक काम कर रहा है!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Common Solutions:")
        print("1. Check .env file में MONGO_URI सही है")
        print("2. Password में special characters हैं तो URL encode करें")
        print("3. MongoDB Atlas में IP whitelist check करें (0.0.0.0/0)")
        print("4. Internet connection check करें")

if __name__ == "__main__":
    test_mongodb()