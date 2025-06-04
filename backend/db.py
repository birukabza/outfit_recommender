from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["outfit_db"]
outfit_collection = db["user_outfits"]
users_collection = db["users"]
sessions_collection = db["chat_sessions"]
