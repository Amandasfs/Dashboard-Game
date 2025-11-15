from flask import Blueprint, request, jsonify
from flask_socketio import join_room
from app.extensions import socketio
from app.services.game_service import GameService

game_bp = Blueprint("game", __name__)

# GameService será inicializado **na primeira chamada**
# usando current_app.db
from flask import current_app

def get_game_service():
    return GameService(current_app.db, socketio)

# -------------------- Criar Partida --------------------
@game_bp.route("/api/game/create", methods=["POST"])
def criar_partida():
    data = request.json
    host_user = data.get("host")
    max_jogadores = data.get("max_jogadores", 4)
    game_service = get_game_service()
    game_code = game_service.criar_partida(host_user, max_jogadores)
    return jsonify({"game_code": game_code, "msg": "Partida criada com sucesso"}), 201

# -------------------- Entrar em Partida --------------------
@game_bp.route("/api/game/join", methods=["POST"])
def entrar_partida():
    data = request.json
    game_code = data.get("game_code")
    jogador = data.get("player")
    game_service = get_game_service()
    sucesso, partida = game_service.entrar_partida(game_code, jogador)
    if not sucesso:
        return jsonify({"error": partida}), 400

    join_room(game_code)
    return jsonify({"msg": f"{jogador} entrou na partida", "partida": partida})

# -------------------- Responder Pergunta --------------------
@socketio.on("responder_pergunta")
def responder_pergunta(data):
    game_service = get_game_service()
    game_code = data.get("game_code")
    player_name = data.get("player")
    resposta_idx = data.get("resposta")

    partida = game_service.games.get(game_code)
    if not partida:
        socketio.emit("error", {"msg": "Partida não encontrada"}, room=game_code)
        return

    jogador = next(p for p in partida["players"] if p["name"] == player_name)
    carta = data.get("carta")
    resposta_correta = carta["answer"] == resposta_idx

    jogador = game_service.calcular_movimento(jogador, carta, resposta_correta)
    jogador = game_service.verificar_casa_especial(jogador, partida["tabuleiro"])
    proximo = game_service.proximo_turno(game_code)

    socketio.emit(
        "atualizacao_jogo",
        {
            "jogadores": partida["players"],
            "turno_atual": proximo["name"]
        },
        room=game_code
    )

    game_service.enviar_pergunta_socket(game_code)
