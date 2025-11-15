# backend/app/sockets/game_ws.py    
from flask import current_app
from flask_socketio import emit, join_room
from app.services.game_service import GameService
from app.services.card_service import CardService

def socketio_game_events(socketio):
    @socketio.on("join_game")
    def on_join(data):
        game_id = data["game_id"]
        username = data["username"]
        join_room(game_id)
        emit("player_joined", {"username": username}, room=game_id)

    @socketio.on("draw_card")
    def on_draw_card(data):
        difficulty = data.get("difficulty")
        card_service = CardService(current_app.db)
        card = card_service.draw_card(difficulty)
        emit("new_card", card)

    @socketio.on("submit_answer")
    def on_submit_answer(data):
        game_id = data.get("game_id")
        username = data.get("username")
        difficulty = data.get("difficulty")
        correct = data.get("correct")  # True ou False enviado pelo client

        game_service = GameService(current_app.db)
        game = game_service.move_player(game_id, username, steps=None, correct=correct, difficulty=difficulty)

        # Envia estado atualizado para todos os jogadores
        emit("game_updated", game, room=game_id)
