# backend/app/__init__.py
from flask import Flask
from pymongo import MongoClient
from .routes.auth import auth_bp
from .routes.game_routes import game_bp
from .sockets.events import socketio_events
from .config.config import Config
from .extensions import socketio  # import do Socket.IO separado

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Conexão com MongoDB Atlas
    client = MongoClient(app.config["MONGO_URI"])
    app.db = client[app.config["DB_NAME"]]

    # Registrar Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)

    # Inicializar Socket.IO
    socketio.init_app(app)
    socketio_events(socketio)

    return app
