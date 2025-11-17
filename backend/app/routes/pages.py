# backend/app/routes/pages.py
from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/")
def root():
    return render_template("Login.html")

@pages_bp.route("/login")
def login_page():
    return render_template("Login.html")

@pages_bp.route("/register")
def register_page():
    return render_template("Register.html")

@pages_bp.route("/home")
def home_page():
    return render_template("Home.html")

@pages_bp.route("/criar-partida")
def criar_partida_page():
    return render_template("CriarPartida.html")

@pages_bp.route("/token")
def token_page():
    return render_template("TokenModal.html")

@pages_bp.route("/tabuleiro")
def tabuleiro_page():
    return render_template("Tabuleiro.html")

@pages_bp.route("/card")
def card_page():
    return render_template("Card.html")

@pages_bp.route("/espera")
def waiting_room_page():
    return render_template("Espera.html")
