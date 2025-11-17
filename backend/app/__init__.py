# backend/app/__init__.py
from flask import Flask
from pymongo import MongoClient

# Blueprints
from .routes.auth import auth_bp
from .routes.game_routes import game_bp
from .routes.home_routes import home_bp
from .routes.pages import pages_bp

# SocketIO e extensões
from .extensions import socketio, game_service
from .sockets.events import socketio_events

# Config
from .config.config import Config
from .services.game_service import GameService

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Conexão com MongoDB
    client = MongoClient(app.config["MONGO_URI"])
    app.db = client[app.config["DB_NAME"]]

    # Inicializar GameService apenas 1x
    global game_service
    if game_service is None:
        game_service = GameService(app.db, socketio)

    # Registrar Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(pages_bp)

    # Inicializar Socket.IO
    socketio.init_app(app)
    socketio_events(socketio)

    return app
