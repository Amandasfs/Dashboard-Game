# backend/app/services/game_service.py
import random
from bson import ObjectId
from datetime import datetime, timedelta

class GameService:
    def __init__(self, db, socketio):
        self.db = db
        self.socketio = socketio
        self.games = {}  # game_code -> partida

    # -----------------------------------------
    # Criação e entrada na partida
    # -----------------------------------------

    def criar_partida(self, host_user, max_jogadores=4, duracao=15):
        """
        Cria uma partida nova e retorna o código.
        """
        game_code = str(random.randint(1000, 9999))

        partida = {
            "host": host_user,
            "players": [],
            "max_jogadores": max_jogadores,
            "duracao": duracao,
            "start_time": None,
            "turno": 0,
            "finished": False,
            "tabuleiro": self.gerar_tabuleiro(),
            "carta_atual": None
        }

        self.games[game_code] = partida
        return game_code

    def entrar_partida(self, game_code, jogador, avatar):
        """
        Adiciona um jogador à partida existente.
        """
        partida = self.games.get(game_code)
        if not partida:
            return False, "Partida não existe"

        if len(partida["players"]) >= partida["max_jogadores"]:
            return False, "Partida cheia"

        partida["players"].append({
            "name": jogador,
            "avatar": avatar,
            "posicao": 0,
            "pontos": 0,
            "vida_extra": 0
        })

        return True, partida

    # -----------------------------------------
    # Tabuleiro e cartas
    # -----------------------------------------

    def gerar_tabuleiro(self):
        """
        Cria o tabuleiro circular com casas especiais.
        """
        tabuleiro = []
        for i in range(30):
            casa = {"index": i, "tipo": "normal"}

            if i in [3, 7, 12, 18]:
                casa["tipo"] = "10pontos"
            elif i in [5, 14]:
                casa["tipo"] = "vida_extra"
            elif i in [8, 16, 24]:
                casa["tipo"] = "20pontos"

            tabuleiro.append(casa)

        return tabuleiro

    def sortear_carta(self, dificuldade=None):
        """
        Sorteia uma carta do MongoDB.
        """
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
        """
        Calcula movimento e aplica penalidades de acordo com a resposta.
        """
        partida = self.games.get(game_code)
        tabuleiro = partida["tabuleiro"]
        tamanho = len(tabuleiro)

        movimento = 0

        if resposta_correta:
            movimento = {
                "easy": 2,
                "medium": 4,
                "hard": 6
            }.get(carta["difficulty"], 2)

        else:
            # Se tem vida extra, não perde movimento
            if jogador["vida_extra"] > 0:
                jogador["vida_extra"] -= 1
                movimento = 0
            else:
                if carta.get("timeout"):
                    movimento = -1
                else:
                    movimento = {
                        "easy": -1,
                        "medium": -2,
                        "hard": -3
                    }.get(carta["difficulty"], -1)

        # Movimento circular
        jogador["posicao"] = (jogador["posicao"] + movimento) % tamanho
        return jogador

    def verificar_casa_especial(self, jogador, tabuleiro):
        """
        Aplica o efeito da casa especial onde o jogador parou.
        """
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
        """
        Alterna para o próximo jogador.
        """
        partida = self.games.get(game_code)
        if not partida:
            return None

        if len(partida["players"]) == 0:
            return None

        partida["turno"] = (partida["turno"] + 1) % len(partida["players"])
        return partida["players"][partida["turno"]]

    # -----------------------------------------
    # SocketIO
    # -----------------------------------------

    def enviar_pergunta_socket(self, game_code):
        """
        Sorteia carta, salva como carta_atual e envia via socket.
        """
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
