from pymongo import MongoClient
from config import MONGO_URI
from bson.objectid import ObjectId
import bcrypt

def connect_to_mongo():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()  # Test connection
        db = client['memories_db']
        print("MongoDB connection successful for users")
        return db
    except Exception as e:
        print(f"MongoDB connection failed for users: {e}")
        return None

def create_user(username, email, password):
    db = connect_to_mongo()
    if db is None:
        raise Exception("MongoDB not connected")
    try:
        # Check if username or email already exists
        if db.users.find_one({'$or': [{'username': username}, {'email': email}]}):
            return None
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = {
            'username': username,
            'email': email,
            'password_hash': password_hash
        }
        result = db.users.insert_one(user)
        print(f"Created user {username} with ID: {result.inserted_id}")
        return user
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def authenticate_user(username, password):
    db = connect_to_mongo()
    if db is None:
        raise Exception("MongoDB not connected")
    try:
        user = db.users.find_one({'username': username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            print(f"Authenticated user: {username}")
            return user
        print(f"Authentication failed for user: {username}")
        return None
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None

def get_user_by_username(user_id):
    db = connect_to_mongo()
    if db is None:
        raise Exception("MongoDB not connected")
    try:
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if user:
            print(f"Retrieved user: {user['username']}")
            return user
        print(f"User with ID {user_id} not found")
        return None
    except Exception as e:
        print(f"Error retrieving user {user_id}: {e}")
        return None