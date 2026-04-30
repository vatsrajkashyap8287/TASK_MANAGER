from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from datetime import datetime
import os

load_dotenv()

def initialize_database():
    """Database को setup करें sample data के साथ"""
    
    try:
        # MongoDB से connect करें
        mongo_uri = os.getenv('MONGO_URI')
        client = MongoClient(mongo_uri)
        db = client.project_manager
        
        print("🔄 Database initialize हो रहा है...")
        
        # Indexes बनाएं
        db.users.create_index("email", unique=True)
        print("✅ Indexes बन गए")
        
        # Check if admin already exists
        existing_admin = db.users.find_one({"email": "admin@example.com"})
        
        if existing_admin:
            print("ℹ️  Database पहले से ही setup है!")
            print("\n🔐 Login करें:")
            print("   Email: admin@example.com")
            print("   Password: admin123")
        else:
            # Admin user बनाएं
            admin = {
                "username": "admin",
                "email": "admin@example.com",
                "password_hash": generate_password_hash("admin123"),
                "role": "admin",
                "created_at": datetime.utcnow()
            }
            admin_id = db.users.insert_one(admin).inserted_id
            print("✅ Admin user बन गया!")
            
            # Member user बनाएं
            member = {
                "username": "john_doe",
                "email": "john@example.com",
                "password_hash": generate_password_hash("password123"),
                "role": "member",
                "created_at": datetime.utcnow()
            }
            member_id = db.users.insert_one(member).inserted_id
            print("✅ Member user बन गया!")
            
            # Sample project बनाएं
            project = {
                "name": "Welcome Project",
                "description": "यह एक sample project है",
                "created_by": str(admin_id),
                "team_members": [str(member_id)],
                "created_at": datetime.utcnow(),
                "status": "active"
            }
            project_id = db.projects.insert_one(project).inserted_id
            print("✅ Sample project बन गया!")
            
            # Sample task बनाएं
            task = {
                "title": "First Task",
                "description": "यह आपका पहला task है",
                "project_id": str(project_id),
                "assigned_to": str(member_id),
                "created_by": str(admin_id),
                "due_date": datetime.utcnow(),
                "status": "pending",
                "priority": "medium",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            db.tasks.insert_one(task)
            print("✅ Sample task बन गया!")
            
            print("\n📊 Database Statistics:")
            print(f"   Users: {db.users.count_documents({})}")
            print(f"   Projects: {db.projects.count_documents({})}")
            print(f"   Tasks: {db.tasks.count_documents({})}")
            
            print("\n🎉 Database setup complete!")
            print("\n🔐 Login Credentials:")
            print("   Admin:")
            print("   Email: admin@example.com")
            print("   Password: admin123")
            print("\n   Member:")
            print("   Email: john@example.com")
            print("   Password: password123")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    initialize_database()