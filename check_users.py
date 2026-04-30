from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def check_users():
    try:
        client = MongoClient(os.getenv('MONGO_URI'))
        db = client.project_manager
        
        users = list(db.users.find({}, {'password_hash': 0}))
        
        print("\n" + "="*60)
        print("👥 Users in Database:")
        print("="*60)
        
        if not users:
            print("❌ No users found!")
            print("\n💡 Run: python init_db.py")
        else:
            for user in users:
                print(f"\n✅ {user['username']}")
                print(f"   Email: {user['email']}")
                print(f"   Role: {user['role']}")
                print(f"   Created: {user['created_at']}")
        
        print("\n" + "="*60)
        print(f"Total Users: {len(users)}")
        print("="*60 + "\n")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_users()