from dotenv import load_dotenv
import os

load_dotenv()

print("=" * 50)
print("Environment Variables Check")
print("=" * 50)

secret_key = os.getenv('SECRET_KEY')
mongo_uri = os.getenv('MONGO_URI')
flask_env = os.getenv('FLASK_ENV')
port = os.getenv('PORT')

if secret_key:
    print(f"✅ SECRET_KEY: {secret_key[:20]}... (length: {len(secret_key)})")
else:
    print("❌ SECRET_KEY: Not found!")

if mongo_uri:
    # Hide password for security
    if '@' in mongo_uri:
        parts = mongo_uri.split('@')
        hidden = parts[0].split(':')[0] + ':****@' + parts[1]
        print(f"✅ MONGO_URI: {hidden}")
    else:
        print(f"✅ MONGO_URI: {mongo_uri[:30]}...")
else:
    print("❌ MONGO_URI: Not found!")

if flask_env:
    print(f"✅ FLASK_ENV: {flask_env}")
else:
    print("❌ FLASK_ENV: Not found!")

if port:
    print(f"✅ PORT: {port}")
else:
    print("⚠️  PORT: Not set (will use default 5000)")

print("=" * 50)

if secret_key and mongo_uri:
    print("🎉 All required variables are set!")
else:
    print("⚠️  Some variables are missing. Check your .env file")