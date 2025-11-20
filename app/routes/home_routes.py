# backend/app/routes/home_routes.py
from flask import Blueprint, render_template, request, redirect, url_for

home_bp = Blueprint("home", __name__)

@home_bp.route("/home")
def home():
    # Futuramente podemos pegar o username do token/session
    username = request.args.get("username", "Jogador")
    return render_template("home.html", username=username)
