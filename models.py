from pymongo import MongoClient
import gridfs
from config import MONGO_URI
from bson.objectid import ObjectId

def connect_to_mongo():
    global client, db, fs
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()  # Test connection
        db = client['memories_db']
        fs = gridfs.GridFS(db)
        print("MongoDB connection successful")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        client = None
        db = None
        fs = None

# Initial connection attempt
connect_to_mongo()

def save_memory(photo, title, date, description, user_id):
    if db is None or fs is None:
        connect_to_mongo()
        if db is None or fs is None:
            raise Exception("MongoDB not connected")
    try:
        photo_id = fs.put(photo, filename=photo.filename)
        print(f"Saved photo to GridFS with ID: {photo_id}")
        result = db.memories.insert_one({
            'photo_id': photo_id,
            'title': title,
            'date': date,
            'description': description,
            'user_id': ObjectId(user_id)
        })
        print(f"Inserted into memories with ID: {result.inserted_id}")
    except Exception as e:
        print(f"Error saving to memories: {e}")

def get_memories(user_id):
    if db is None:
        connect_to_mongo()
        if db is None:
            raise Exception("MongoDB not connected")
    return db.memories.find({'user_id': ObjectId(user_id)})

def get_photo(photo_id):
    if fs is None:
        connect_to_mongo()
        if fs is None:
            raise Exception("MongoDB not connected")
    try:
        photo = fs.get(ObjectId(photo_id))
        print(f"Retrieved photo: {photo.filename}")
        return photo
    except Exception as e:
        print(f"Error retrieving photo {photo_id}: {e}")
        return None

def delete_memory(memory_id, user_id):
    if db is None or fs is None:
        connect_to_mongo()
        if db is None or fs is None:
            raise Exception("MongoDB not connected")
    try:
        memory = db.memories.find_one({'_id': ObjectId(memory_id), 'user_id': ObjectId(user_id)})
        if memory:
            photo_id = memory['photo_id']
            fs.delete(ObjectId(photo_id))
            print(f"Deleted photo with ID: {photo_id}")
            db.memories.delete_one({'_id': ObjectId(memory_id)})
            print(f"Deleted memory with ID: {memory_id}")
        else:
            print(f"Memory {memory_id} not found or not authorized")
    except Exception as e:
        print(f"Error deleting memory {memory_id}: {e}")

def update_memory(memory_id, title, date, description, photo=None, user_id=None):
    if db is None or fs is None:
        connect_to_mongo()
        if db is None or fs is None:
            raise Exception("MongoDB not connected")
    try:
        memory = db.memories.find_one({'_id': ObjectId(memory_id), 'user_id': ObjectId(user_id)})
        if not memory:
            print(f"Memory {memory_id} not found or not authorized")
            return False
        update_data = {
            'title': title,
            'date': date,
            'description': description
        }
        if photo:
            old_photo_id = memory['photo_id']
            fs.delete(ObjectId(old_photo_id))
            print(f"Deleted old photo with ID: {old_photo_id}")
            new_photo_id = fs.put(photo, filename=photo.filename)
            update_data['photo_id'] = new_photo_id
            print(f"Saved new photo with ID: {new_photo_id}")
        db.memories.update_one({'_id': ObjectId(memory_id)}, {'$set': update_data})
        print(f"Updated memory with ID: {memory_id}")
        return True
    except Exception as e:
        print(f"Error updating memory {memory_id}: {e}")
        return False

def get_memory(memory_id, user_id):
    if db is None:
        connect_to_mongo()
        if db is None:
            raise Exception("MongoDB not connected")
    try:
        memory = db.memories.find_one({'_id': ObjectId(memory_id), 'user_id': ObjectId(user_id)})
        if memory:
            print(f"Retrieved memory with ID: {memory_id}")
            return memory
        print(f"Memory {memory_id} not found or not authorized")
        return None
    except Exception as e:
        print(f"Error retrieving memory {memory_id}: {e}")
        return None