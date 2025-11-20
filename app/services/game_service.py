# backend/app/services/game_service.py
import random
import uuid
from threading import Timer
from datetime import datetime

class GameService:
    def __init__(self, db, socketio):
        self.db = db
        self.socketio = socketio
        self.games = {}  # game_code -> partida

    # -----------------------------------------
    # Criação e entrada na partida
    # -----------------------------------------
    def criar_partida(self, host_user, max_jogadores=4, duracao=15, modo="multi"):
        game_code = str(random.randint(1000, 9999))
        partida = {
            "host": host_user,
            "players": [],
            "max_jogadores": max_jogadores,
            "duracao": duracao,
            "modo": modo,  # "multi" ou "bot"
            "start_time": None,
            "turno": 0,
            "finished": False,
            "tabuleiro": self.gerar_tabuleiro(),
            "carta_atual": None,
            "started": False
        }
        self.games[game_code] = partida
        return game_code

    def entrar_partida(self, game_code, jogador, avatar):
        partida = self.games.get(game_code)
        if not partida:
            return False, "Partida não existe"
        if len(partida["players"]) >= partida["max_jogadores"]:
            return False, "Partida cheia"

        partida["players"].append({
            "id": str(uuid.uuid4()),
            "name": jogador,
            "avatar": avatar,
            "avatar_url": f"/static/img/avatar-{avatar}.png",
            "posicao": 0,
            "pontos": 0,
            "vida_extra": 0,
            "is_bot": False,
            "isReady": False
        })
        return True, partida

    # -----------------------------------------
    # Tabuleiro e cartas
    # -----------------------------------------
    def gerar_tabuleiro(self):
        tabuleiro = []
        for i in range(30):
            tipo = "normal"
            if i in [3, 7, 12, 18]:
                tipo = "10pontos"
            elif i in [5, 14]:
                tipo = "vida_extra"
            elif i in [8, 16, 24]:
                tipo = "20pontos"
            tabuleiro.append({"index": i, "tipo": tipo})
        return tabuleiro

    def sortear_carta(self, dificuldade=None):
        query = {}
        if dificuldade:
            query["difficulty"] = dificuldade
        cards = list(self.db.cards.find(query))
        if not cards:
            return None
        return random.choice(cards)

    # -----------------------------------------
    # Mecânica do jogo
    # -----------------------------------------
    def calcular_movimento(self, game_code, jogador, carta, resposta_correta):
        partida = self.games.get(game_code)
        if not partida:
            return
        tabuleiro = partida["tabuleiro"]
        tamanho = len(tabuleiro)
        movimento = 0

        if resposta_correta:
            movimento = {"easy": 2, "medium": 4, "hard": 6}.get(carta["difficulty"], 2)
        else:
            if jogador.get("vida_extra", 0) > 0:
                jogador["vida_extra"] -= 1
                movimento = 0
            else:
                if carta.get("timeout"):
                    movimento = -1
                else:
                    movimento = {"easy": -1, "medium": -2, "hard": -3}.get(carta["difficulty"], -1)

        jogador["posicao"] = (jogador["posicao"] + movimento) % tamanho
        return jogador

    def verificar_casa_especial(self, jogador, tabuleiro):
        pos = jogador["posicao"]
        tipo = tabuleiro[pos]["tipo"]
        if tipo == "10pontos":
            if random.choice([True, False]):
                jogador["pontos"] += 10
        elif tipo == "20pontos":
            jogador["pontos"] += 20
            jogador["vida_extra"] += 1
        elif tipo == "vida_extra":
            jogador["vida_extra"] += 1
        return jogador

    def proximo_turno(self, game_code):
        partida = self.games.get(game_code)
        if not partida or len(partida["players"]) == 0:
            return None
        partida["turno"] = (partida["turno"] + 1) % len(partida["players"])
        return partida["players"][partida["turno"]]

    def todos_prontos(self, game_code):
        partida = self.games.get(game_code)
        if not partida:
            return False
        humanos = [p for p in partida["players"] if not p.get("is_bot")]
        if len(humanos) == 0:
            return False
        return all(p.get("isReady", False) for p in humanos)

    # -----------------------------------------
    # Início de partida
    # -----------------------------------------
    def iniciar_partida(self, game_code):
        partida = self.games.get(game_code)
        if not partida:
            return None

        # Adiciona bots automaticamente se modo bot
        if partida.get("modo") == "bot":
            self.adicionar_bots(game_code)

        partida["start_time"] = datetime.now()
        partida["turno"] = 0
        partida["started"] = True

        for jogador in partida["players"]:
            jogador["posicao"] = 0
            jogador["pontos"] = 0
            jogador["vida_extra"] = 0
            if "isReady" not in jogador:
                jogador["isReady"] = True  # bots sempre prontos

        # Se o primeiro jogador for bot, aciona
        primeiro = partida["players"][0]
        if primeiro.get("is_bot"):
            self.acionar_bot(game_code)

        return {
            "game_code": game_code,
            "players": partida["players"],
            "tabuleiro": partida["tabuleiro"],
            "turno_atual": partida["players"][0]["name"]
        }

    # -----------------------------------------
    # SocketIO
    # -----------------------------------------
    def enviar_pergunta_socket(self, game_code):
        partida = self.games.get(game_code)
        if not partida:
            return
        jogador = partida["players"][partida["turno"]]
        carta = self.sortear_carta()
        if not carta:
            return
        partida["carta_atual"] = carta
        self.socketio.emit(
            "nova_pergunta",
            {
                "player": jogador["name"],
                "question": carta["question"],
                "options": carta["options"],
                "time": carta.get("time", 60)
            },
            room=game_code
        )

    # -----------------------------------------
    # BOTS
    # -----------------------------------------
    def adicionar_bots(self, game_code):
        partida = self.games.get(game_code)
        if not partida:
            return False, "Partida inexistente"

        max_jog = partida["max_jogadores"]
        atual = len(partida["players"])
        faltam = max_jog - atual
        if faltam <= 0:
            return True, "Nenhum bot necessário"

        for i in range(faltam):
            bot_nome = f"Bot {i+1}"
            bot = {
                "id": str(uuid.uuid4()),
                "name": bot_nome,
                "avatar": f"bot_{i+1}",
                "avatar_url": f"/static/img/avatars/bot_{i+1}.png",
                "posicao": 0,
                "pontos": 0,
                "vida_extra": 0,
                "is_bot": True,
                "isReady": True
            }
            partida["players"].append(bot)
        return True, f"{faltam} bots adicionados"

    def acionar_bot(self, game_code):
        partida = self.games.get(game_code)
        if not partida:
            return
        jogador = partida["players"][partida["turno"]]
        if not jogador.get("is_bot"):
            return
        delay = random.uniform(1.0, 3.0)
        Timer(delay, lambda: self.resposta_bot(game_code, jogador)).start()

    def resposta_bot(self, game_code, bot):
        partida = self.games.get(game_code)
        if not partida:
            return
        carta = partida.get("carta_atual")
        if not carta:
            return
        # 80% chance de acertar
        if random.random() <= 0.8:
            resposta = carta["answer"]
        else:
            opcoes = [0,1,2,3]
            opcoes.remove(carta["answer"])
            resposta = random.choice(opcoes)
        resposta_correta = carta["answer"] == resposta
        self.calcular_movimento(game_code, bot, carta, resposta_correta)
        self.verificar_casa_especial(bot, partida["tabuleiro"])
        proximo = self.proximo_turno(game_code)
        self.socketio.emit(
            "atualizacao_jogo",
            {
                "players": partida["players"],
                "turno_atual": proximo["name"]
            },
            room=game_code
        )
        self.enviar_pergunta_socket(game_code)
