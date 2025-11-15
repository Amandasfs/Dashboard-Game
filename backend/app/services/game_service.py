# backend/app/services/game_service.py
import random
from datetime import datetime, timedelta
from bson import ObjectId

class GameService:
    def __init__(self, db, socketio):
        self.db = db
        self.socketio = socketio
        self.games = {}  # partidas em memória: game_code -> info da partida

    def criar_partida(self, host_user, max_jogadores=4, duracao=15):
        """
        Cria uma nova partida
        """
        game_code = str(random.randint(1000, 9999))
        partida = {
            "host": host_user,
            "players": [],
            "max_jogadores": max_jogadores,
            "duracao": duracao,  # minutos
            "start_time": None,
            "tabuleiro": self.gerar_tabuleiro(),
            "turno": 0,  # índice do jogador atual
            "finished": False
        }
        self.games[game_code] = partida
        return game_code

    def entrar_partida(self, game_code, jogador):
        """
        Adiciona um jogador à partida
        """
        partida = self.games.get(game_code)
        if not partida:
            return False, "Partida não existe"
        if len(partida["players"]) >= partida["max_jogadores"]:
            return False, "Partida cheia"
        partida["players"].append({
            "name": jogador,
            "posicao": 0,
            "pontos": 0,
            "vida_extra": 0
        })
        return True, partida

    def gerar_tabuleiro(self):
        """
        Cria o tabuleiro circular com casas especiais
        """
        tabuleiro = []
        for i in range(30):  # 30 casas, exemplo
            casa = {"index": i, "tipo": "normal"}
            if i in [3, 7, 12, 18]:  # casas 10 pontos
                casa["tipo"] = "10pontos"
            elif i in [5, 14]:  # casas vida extra
                casa["tipo"] = "vida_extra"
            elif i in [8, 16, 24]:  # casas desafio 20 pontos
                casa["tipo"] = "20pontos"
            tabuleiro.append(casa)
        return tabuleiro

    def sortear_carta(self, dificuldade=None):
        """
        Sorteia uma carta do MongoDB de acordo com a dificuldade
        """
        query = {}
        if dificuldade:
            query["difficulty"] = dificuldade
        cards = list(self.db.cards.find(query))
        if not cards:
            return None
        return random.choice(cards)

    def calcular_movimento(self, jogador, carta, resposta_correta):
        """
        Calcula a movimentação de acordo com a RN-01 a RN-03
        """
        movimento = 0
        pontos = 0
        vida = jogador["vida_extra"]

        if resposta_correta:
            if carta["difficulty"] == "easy":
                movimento = 2
            elif carta["difficulty"] == "medium":
                movimento = 4
            else:
                movimento = 6
        else:
            if vida > 0:
                # utiliza a vida extra
                jogador["vida_extra"] -= 1
                movimento = 0
            else:
                if carta.get("timeout", False):
                    movimento = -1
                else:
                    if carta["difficulty"] == "easy":
                        movimento = -1  # metade de 2 casas = 1
                    elif carta["difficulty"] == "medium":
                        movimento = -2  # metade de 4 casas
                    else:
                        movimento = -3  # metade de 6 casas

        jogador["posicao"] = (jogador["posicao"] + movimento) % len(self.games["tabuleiro"])  # circular
        return jogador

    def verificar_casa_especial(self, jogador, tabuleiro):
        """
        Aplica regras de casas especiais (10p, 20p, vida extra)
        """
        pos = jogador["posicao"]
        casa = tabuleiro[pos]
        tipo = casa["tipo"]

        if tipo == "10pontos":
            # 50% chance de pegar pontos ou nada (pegadinha)
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
        Alterna para o próximo jogador
        """
        partida = self.games.get(game_code)
        if not partida:
            return None
        partida["turno"] = (partida["turno"] + 1) % len(partida["players"])
        return partida["players"][partida["turno"]]

    def enviar_pergunta_socket(self, game_code):
        """
        Envia a pergunta atual via Socket.IO para todos os jogadores
        """
        partida = self.games.get(game_code)
        if not partida:
            return

        jogador = partida["players"][partida["turno"]]
        carta = self.sortear_carta()  # sorteia carta
        self.socketio.emit(
            "nova_pergunta",
            {
                "player": jogador["name"],
                "question": carta["question"],
                "options": carta["options"],
                "time": 60  # segundos
            },
            room=game_code
        )
