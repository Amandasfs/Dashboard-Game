# backend/app/sockets/events.py
from flask_socketio import join_room, leave_room
from flask import current_app
from threading import Thread
import time
from app.extensions import game_service

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
        from flask import request
        
        # Usa a instância global do game_service
        import app.extensions
        gs = app.extensions.game_service
        
        if gs is None:
            from app.services.game_service import GameService
            from app.extensions import socketio as sio
            gs = GameService(current_app.db, sio)
            app.extensions.game_service = gs
        
        token = data.get("token")
        username = data.get("username")
        avatar = data.get("avatar")

        sucesso, partida = gs.entrar_partida(token, username, avatar)

        if not sucesso:
            socketio.emit("error", {"msg": partida})
            return

        # Entra na sala usando o request.sid do socket atual
        join_room(token, sid=request.sid)
        print(f"👤 {username} entrou na sala {token} (SID: {request.sid})")
        
        # Debug: mostra o modo da partida
        modo = partida.get("modo", "multi")
        print(f"🔍 [JOIN ROOM] Modo da partida: {modo}")

        # Atualiza lista da sala
        socketio.emit(
            "atualizacao_sala",
            {"players": partida["players"], "settings": partida},
            room=token
        )

    # -------------------- Jogador pronto --------------------
    @socketio.on("player_ready")
    def player_ready(data):
        # Usa a instância global do game_service
        import app.extensions
        gs = app.extensions.game_service
        
        if gs is None:
            from app.services.game_service import GameService
            from app.extensions import socketio as sio
            gs = GameService(current_app.db, sio)
            app.extensions.game_service = gs
        
        token = data.get("token")
        username = data.get("username")
        ready = data.get("ready", False)

        partida = gs.games.get(token)
        if not partida:
            socketio.emit("error", {"msg": "Partida não encontrada"}, room=token)
            return

        # Atualiza status do jogador
        for p in partida["players"]:
            if p["name"] == username:
                p["isReady"] = ready

        # ====================
        # LÓGICA DE INÍCIO
        # ====================
        modo = partida.get("modo", "multi")  # 'multi' ou 'bot'
        print(f"🔍 [DEBUG] Modo da partida: {modo}, Ready: {ready}, Token: {token}")

        # Se jogar contra bots e humano clicou pronto → iniciar automaticamente
        if modo == "bot" and ready:
            print(f"🤖 [BOT MODE] Iniciando partida com bots imediatamente!")
            # Inicia imediatamente quando qualquer humano clica em pronto no modo bot
            iniciar_partida_com_bots(token, socketio, gs)
            return

        # Emite atualização da sala
        socketio.emit(
            "atualizacao_sala",
            {"players": partida["players"], "settings": partida},
            room=token
        )

        # Se todos humanos estão prontos → inicia partida (modo multi)
        if modo == "multi" and gs.todos_prontos(token):
            iniciar_partida(token, socketio, gs)

    # -------------------- Puxar Carta --------------------
    @socketio.on("puxar_carta")
    def puxar_carta(data):
        # Usa a instância global do game_service
        import app.extensions
        gs = app.extensions.game_service
        
        if gs is None:
            from app.services.game_service import GameService
            from app.extensions import socketio as sio
            gs = GameService(current_app.db, sio)
            app.extensions.game_service = gs
        
        token = data.get("game_code") or data.get("token")
        nome = data.get("nome") or data.get("username")
        
        if not token:
            socketio.emit("error", {"msg": "Token da partida não fornecido"})
            return
        
        partida = gs.games.get(token)
        if not partida:
            socketio.emit("error", {"msg": "Partida não encontrada"})
            return
        
        # Sorteia uma carta
        carta = gs.sortear_carta()
        
        if not carta:
            socketio.emit("error", {"msg": "Nenhuma carta disponível"})
            return
        
        # Salva como carta atual da partida
        partida["carta_atual"] = carta
        
        # Envia a carta para o jogador
        socketio.emit("nova_carta", {
            "question": carta.get("question", ""),
            "options": carta.get("options", []),
            "difficulty": carta.get("difficulty", "easy"),
            "time": carta.get("time", 60),
            "answer": carta.get("answer", 0)
        }, room=token)
        
        print(f"🎴 [CARD] Carta enviada para partida {token}")

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
    
    # Garante que game_code está no estado
    if game_state:
        game_state["game_code"] = token

    # Emite para todos na sala que a partida começou
    socketio.emit("iniciar_partida", game_state or {"game_code": token}, room=token)
    print(f"🎮 Partida {token} iniciada!")

# ==========================
# FUNÇÃO PARA INICIAR PARTIDA COM BOTS
# ==========================
def iniciar_partida_com_bots(token, socketio, game_service, countdown=3):
    partida = game_service.games.get(token)
    if not partida:
        socketio.emit("error", {"msg": "Não foi possível iniciar a partida"}, room=token)
        return

    # Verifica se já foi iniciada
    if partida.get("started"):
        print(f"⚠️ [BOT MODE] Partida {token} já foi iniciada, ignorando...")
        return

    # Marca a partida como iniciada para evitar duplicidade
    partida["started"] = True
    print(f"🤖 [BOT MODE] Iniciando partida {token} com bots (countdown: {countdown}s)")

    # Emite contagem regressiva para front
    print(f"📤 [BOT MODE] Emitindo 'game_starting' para sala {token}")
    socketio.emit("game_starting", {"countdown": countdown}, room=token)
    print(f"✅ [BOT MODE] Evento 'game_starting' emitido!")

    def delayed_start():
        time.sleep(countdown)
        # Adiciona bots se necessário
        max_players = partida.get("max_jogadores", 4)
        num_bots = max_players - len(partida["players"])
        for i in range(num_bots):
            partida["players"].append({
                "name": f"BOT_{i+1}",
                "avatar": 100 + i,
                "avatar_url": "/static/img/bot-avatar.png",
                "posicao": 0,
                "pontos": 0,
                "vida_extra": 0,
                "isReady": True
            })

        # Inicializa o estado do jogo
        game_state = game_service.iniciar_partida(token)
        
        # Garante que game_code está no estado
        if game_state:
            game_state["game_code"] = token
        
        # Emite para todos na sala que a partida começou
        payload = game_state or {"game_code": token}
        print(f"📤 [BOT MODE] Emitindo 'iniciar_partida' para sala {token} com dados:", payload)
        
        # Emite o evento - socketio funciona em threads
        try:
            socketio.emit("iniciar_partida", payload, room=token)
            print(f"✅ [BOT MODE] Evento 'iniciar_partida' emitido!")
        except Exception as e:
            print(f"❌ [BOT MODE] Erro ao emitir evento: {e}")
        
        print(f"🎮 Partida {token} iniciada com {num_bots} bots!")

    Thread(target=delayed_start).start()
