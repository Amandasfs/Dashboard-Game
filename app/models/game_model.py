# backend/app/models/game_model.py
from bson.objectid import ObjectId
import random

class Game:
    def __init__(self, db):
        self.collection = db["games"]

    def create_game(self, host_username, max_players=4):
        game = {
            "host": host_username,
            "players": [{"username": host_username, "position": 0, "score": 0, "lives": 0}],
            "max_players": max_players,
            "status": "waiting",
            "board": self.generate_board(),
            "start_time": None
        }
        result = self.collection.insert_one(game)
        game["_id"] = str(result.inserted_id)
        return game

    def generate_board(self):
        board = []
        for i in range(30):
            board.append({"position": i, "type": "normal"})
        # Casas especiais
        board[5]["type"] = "challenge"
        board[10]["type"] = "special10"
        board[15]["type"] = "special20"
        board[20]["type"] = "special10"
        return board

    def get_game(self, game_id):
        return self.collection.find_one({"_id": ObjectId(game_id)})

    def update_game(self, game_id, data):
        self.collection.update_one({"_id": ObjectId(game_id)}, {"$set": data})

    def move_player(self, game_id, username, steps, correct=True, difficulty=None):
        game = self.get_game(game_id)
        if not game:
            return None

        # Localiza jogador
        for player in game["players"]:
            if player["username"] == username:
                current_pos = player["position"]
                # RN-01 a RN-03
                if correct:
                    if difficulty == "easy":
                        move = 2
                    elif difficulty == "medium":
                        move = 4
                    elif difficulty == "hard":
                        move = 6
                    else:
                        move = steps
                    new_pos = (current_pos + move) % len(game["board"])
                else:
                    # se errou ou não respondeu
                    new_pos = (current_pos - (steps//2 if difficulty else 1)) % len(game["board"])
                player["position"] = new_pos
                # Verificar tipo da casa
                board_cell = game["board"][new_pos]
                if board_cell["type"] == "special10":
                    player["score"] += 10  # ou 0 se for pegadinha, pode randomizar
                elif board_cell["type"] == "special20":
                    player["score"] += 20
                    player["lives"] += 1  # vida extra
                elif board_cell["type"] == "challenge":
                    player["score"] += 20
                break

        self.update_game(game_id, {"players": game["players"]})
        return game
