from pymongo import MongoClient

def connect_db():
    db = MongoClient()['joinhider_bot']
    db.joined_user.create_index([('chat_id', 1), ('user_id', 1)])
    db.joined_user.create_index([('date', 1)])
    db.chat.create_index([('active_date', 1)])
    return db
