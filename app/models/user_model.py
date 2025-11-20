# backend/app/models/user_model.py
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, db):
        self.collection = db["users"]

    def create_user(self, username, password):
        if self.collection.find_one({"username": username}):
            return None  # usuário já existe
        hashed = generate_password_hash(password)
        user = {"username": username, "password": hashed, "score": 0}
        self.collection.insert_one(user)
        return user

    def authenticate(self, username, password):
        user = self.collection.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            return user
        return None

    def get_user(self, username):
        return self.collection.find_one({"username": username})
