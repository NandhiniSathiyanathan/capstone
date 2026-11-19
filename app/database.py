from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
client.admin.command("ping")

database = client["mini_rag"]
users_collection = database["users"]
documents_collection = database["documents"] 