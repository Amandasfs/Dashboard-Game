# backend/app/routes/auth.py
from flask import Blueprint, request, jsonify
from app.services.user_service import UserService
from flask import current_app

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username e password são obrigatórios"}), 400

    service = UserService(current_app.db)
    user = service.register_user(username, password)
    if not user:
        return jsonify({"error": "Usuário já existe"}), 400

    return jsonify({"msg": "Usuário criado com sucesso", "username": user["username"]})

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username e password são obrigatórios"}), 400

    service = UserService(current_app.db)
    user = service.login_user(username, password)
    if not user:
        return jsonify({"error": "Credenciais inválidas"}), 401

    # Aqui futuramente podemos gerar token JWT
    return jsonify({"msg": "Login bem sucedido", "username": user["username"]})
