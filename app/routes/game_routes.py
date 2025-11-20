# backend/app/routes/game_routes.py
from flask import Blueprint, request, jsonify, current_app
from app.extensions import socketio, game_service
from flask_socketio import join_room

game_bp = Blueprint("game", __name__)

# -------------------- Criar Partida --------------------
@game_bp.route("/api/game/create", methods=["POST"])
def criar_partida():
    import app.extensions
    gs = app.extensions.game_service

    if gs is None:
        from app.services.game_service import GameService
        gs = GameService(current_app.db, socketio)
        app.extensions.game_service = gs

    data = request.json
    if not data or "host" not in data:
        return jsonify({"error": "Host inválido"}), 400

    host_user = data["host"]
    max_jogadores = min(int(data.get("max_jogadores", 4)), 8)
    modo = data.get("modo", "multi")  # "multi" ou "bot"
    duracao = int(data.get("duracao", 15))

    print(f"🎮 [CREATE GAME] Modo: {modo}, Host: {host_user}, Max: {max_jogadores}")

    game_code = gs.criar_partida(host_user, max_jogadores, duracao, modo)

    partida_criada = gs.games.get(game_code)
    if partida_criada:
        print(f"✅ [CREATE GAME] Partida criada com modo: {partida_criada.get('modo')}")

    return jsonify({"codigo": game_code, "msg": "Partida criada com sucesso"}), 201


# -------------------- Entrar em Partida --------------------
@game_bp.route("/api/game/join", methods=["POST"])
def entrar_partida_route():
    data = request.json
    game_code = data.get("game_code")
    jogador = data.get("player")
    avatar = data.get("avatar")

    sucesso, partida = game_service.entrar_partida(game_code, jogador, avatar)
    if not sucesso:
        return jsonify({"error": partida}), 400

    return jsonify({"msg": f"{jogador} entrou na partida", "partida": partida}), 200


# ==================== SOCKET.IO ====================

@socketio.on("join_room")
def entrar_sala(data):
    game_code = data.get("token")
    player = data.get("username")
    avatar = data.get("avatar")

    sucesso, partida = game_service.entrar_partida(game_code, player, avatar)
    if not sucesso:
        socketio.emit("error", {"msg": partida})
        return

    join_room(game_code)
    print(f"[SOCKET] {player} entrou na sala {game_code}")

    socketio.emit("atualizacao_sala", {"players": partida["players"], "settings": partida}, room=game_code)

    if game_service.todos_prontos(game_code):
        game_state = game_service.iniciar_partida(game_code)
        if game_state:
            game_state["game_code"] = game_code
        socketio.emit("iniciar_partida", game_state or {"game_code": game_code}, room=game_code)


@socketio.on("puxar_carta")
def puxar_carta(data):
    game_code = data.get("token")
    player_name = data.get("nome")

    carta = game_service.puxar_carta(game_code, player_name)
    if carta:
        socketio.emit("carta_enviada", carta, room=game_code)
    else:
        socketio.emit("error", {"msg": "Não foi possível puxar a carta"}, room=game_code)


@socketio.on("responder_pergunta")
def responder_pergunta(data):
    game_code = data.get("game_code")
    player_data = data.get("player")  # pode ser dict com nome/avatar
    resposta_idx = data.get("resposta")
    carta = data.get("carta")

    partida = game_service.games.get(game_code)
    if not partida:
        socketio.emit("error", {"msg": "Partida não encontrada"}, room=game_code)
        return

    jogador = next((p for p in partida["players"] if p["name"] == player_data.get("nome")), None)
    if not jogador:
        socketio.emit("error", {"msg": f"Jogador {player_data.get('nome')} não encontrado"}, room=game_code)
        return

    resposta_correta = carta["answer"] == resposta_idx

    game_service.calcular_movimento(game_code, jogador, carta, resposta_correta)
    game_service.verificar_casa_especial(jogador, partida["tabuleiro"])

    proximo = game_service.proximo_turno(game_code)

    socketio.emit(
        "atualizacao_jogo",
        {
            "players": partida["players"],
            "turno_atual": proximo["name"]
        },
        room=game_code
    )

    game_service.enviar_pergunta_socket(game_code)
