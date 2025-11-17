# backend/app/sockets/events.py
from flask_socketio import join_room, leave_room
from flask import current_app
from threading import Thread
import time
from app.services.game_service import GameService

# ==========================
# EVENTOS SOCKET.IO
# ==========================
def socketio_events(socketio):

    @socketio.on("connect")
    def on_connect():
        print("🔌 Cliente conectado!")

    @socketio.on("disconnect")
    def on_disconnect():
        print("❌ Cliente desconectado!")

    # -------------------- Entrar Sala --------------------
    @socketio.on("join_room")
    def join_room_event(data):
        """
        data = {
            "token": "ABC123",
            "username": "Jogador",
            "avatar": 1
        }
        """
        token = data.get("token")
        username = data.get("username")
        avatar = data.get("avatar")

        game_service = GameService(current_app.db, socketio)
        sucesso, partida = game_service.entrar_partida(token, username, avatar)

        if not sucesso:
            socketio.emit("error", {"msg": partida})
            return

        join_room(token)
        print(f"👤 {username} entrou na sala {token}")

        # Atualiza lista da sala
        socketio.emit(
            "atualizacao_sala",
            {"players": partida["players"], "settings": partida},
            room=token
        )

    # -------------------- Jogador pronto --------------------
    @socketio.on("player_ready")
    def player_ready(data):
        token = data.get("token")
        username = data.get("username")
        ready = data.get("ready", False)

        game_service = GameService(current_app.db, socketio)
        partida = game_service.games.get(token)
        if not partida:
            socketio.emit("error", {"msg": "Partida não encontrada"}, room=token)
            return

        # Atualiza status do jogador
        for p in partida["players"]:
            if p["name"] == username:
                p["isReady"] = ready

        # Emite atualização da sala
        socketio.emit(
            "atualizacao_sala",
            {"players": partida["players"], "settings": partida},
            room=token
        )

        # ====================
        # LÓGICA DE INÍCIO
        # ====================
        humanos = [p for p in partida["players"] if not p["name"].startswith("BOT_")]
        modo = partida.get("modo", "normal")  # 'normal' ou 'bots'

        # Se jogar contra bots e humano clicou pronto → iniciar automaticamente
        if modo == "bots" and len(humanos) == 1 and humanos[0]["isReady"]:
            iniciar_partida_com_bots(token, socketio, game_service)
            return

        # Se todos humanos estão prontos → inicia partida
        if game_service.todos_prontos(token):
            iniciar_partida(token, socketio, game_service)

# ==========================
# FUNÇÃO PARA INICIAR PARTIDA NORMAL
# ==========================
def iniciar_partida(token, socketio, game_service):
    partida = game_service.games.get(token)
    if not partida:
        socketio.emit("error", {"msg": "Não foi possível iniciar a partida"}, room=token)
        return

    # Inicializa o estado do jogo (posição dos jogadores, cartas etc.)
    game_state = game_service.iniciar_partida(token)

    # Emite para todos na sala que a partida começou
    socketio.emit("iniciar_partida", game_state, room=token)
    print(f"🎮 Partida {token} iniciada!")

# ==========================
# FUNÇÃO PARA INICIAR PARTIDA COM BOTS
# ==========================
def iniciar_partida_com_bots(token, socketio, game_service, countdown=3):
    partida = game_service.games.get(token)
    if not partida:
        socketio.emit("error", {"msg": "Não foi possível iniciar a partida"}, room=token)
        return

    # Marca a partida como iniciada para evitar duplicidade
    partida["started"] = True

    # Emite contagem regressiva para front
    socketio.emit("game_starting", {"countdown": countdown}, room=token)

    def delayed_start():
        time.sleep(countdown)
        # Adiciona bots se necessário
        max_players = partida.get("max_jogadores", 4)
        num_bots = max_players - len(partida["players"])
        for i in range(num_bots):
            partida["players"].append({
                "name": f"BOT_{i+1}",
                "avatar_id": 100 + i,
                "avatar_url": "/static/img/bot-avatar.png",
                "isReady": True,
                "isHost": False
            })

        # Inicializa o estado do jogo
        game_state = game_service.iniciar_partida(token)

        # Emite para todos na sala que a partida começou
        socketio.emit("iniciar_partida", game_state, room=token)
        print(f"🎮 Partida {token} iniciada com {num_bots} bots!")

    Thread(target=delayed_start).start()
