# backend/app/routes/game_routes.py
from flask import Blueprint, request, jsonify, current_app
from app.extensions import socketio, game_service  # usa a instância global
from flask_socketio import join_room

game_bp = Blueprint("game", __name__)

# -------------------- Criar Partida --------------------
@game_bp.route("/api/game/create", methods=["POST"])
def criar_partida():
    # Importa game_service em tempo de execução para garantir que está inicializado
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
    max_jogadores = int(data.get("max_jogadores", 4))
    max_jogadores = min(max_jogadores, 8)
    modo = data.get("modo", "multi")  # "multi" ou "bot"
    duracao = int(data.get("duracao", 15))
    
    print(f"🎮 [CREATE GAME] Modo recebido: {modo}, Host: {host_user}, Max: {max_jogadores}")

    game_code = gs.criar_partida(host_user, max_jogadores, duracao, modo)
    
    # Verifica se o modo foi salvo corretamente
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


# ==========================================================
# EVENTOS SOCKET.IO
# ==========================================================

@socketio.on("entrar_sala")
def entrar_sala(data):
    game_code = data.get("game_code")
    player = data.get("player")
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


@socketio.on("responder_pergunta")
def responder_pergunta(data):
    game_code = data.get("game_code")
    player_name = data.get("player")
    resposta_idx = data.get("resposta")
    carta = data.get("carta")

    partida = game_service.games.get(game_code)
    if not partida:
        socketio.emit("error", {"msg": "Partida não encontrada"}, room=game_code)
        return

    # Encontra jogador
    jogador = next((p for p in partida["players"] if p["name"] == player_name), None)
    if not jogador:
        socketio.emit("error", {"msg": f"Jogador {player_name} não encontrado"}, room=game_code)
        return

    # Verifica se acertou
    resposta_correta = carta["answer"] == resposta_idx

    # Movimento e efeitos
    game_service.calcular_movimento(game_code, jogador, carta, resposta_correta)
    game_service.verificar_casa_especial(jogador, partida["tabuleiro"])

    # Alterna turno
    proximo = game_service.proximo_turno(game_code)

    # Envia atualização geral
    socketio.emit(
        "atualizacao_jogo",
        {
            "players": partida["players"],
            "turno_atual": proximo["name"]
        },
        room=game_code
    )

    # Envia próxima pergunta
    game_service.enviar_pergunta_socket(game_code)
