# backend/app/services/user_service.py
from app.models.user_model import User

class UserService:
    def __init__(self, db):
        self.user_model = User(db)

    def register_user(self, username, password):
        return self.user_model.create_user(username, password)

    def login_user(self, username, password):
        return self.user_model.authenticate(username, password)
