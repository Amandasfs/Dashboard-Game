# api/launch.py
from fastapi import APIRouter, HTTPException
from models.player import Player
import os
import json
import random
import string
import time
from typing import List

router = APIRouter()

BASE_DIR = "data/sessions"

TOTAL_HOUSES = 60
TEN_POINT_TOTAL = 8          # RN-05 total (4 positivos + 4 pegadinhas)
TEN_POINT_POSITIVE = 4
TEN_POINT_TRAPS = 4
LIFE_HOUSES = 2              # RN-06 (2 casas de vida extra)
CHALLENGE_HOUSES = 5         # RN-04 casas de desafio (+20 pts)
# Note: you can tune CHALLENGE_HOUSES count if you prefer other number

def generate_code(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_path(session_code):
    return os.path.join(BASE_DIR, session_code)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def load_json(file_path):
    if not os.path.exists(file_path):
        return [] if "players" in file_path else {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def pick_unique_houses(total, exclude: List[int] = None):
    """Helper: pick `total` unique houses from 1..TOTAL_HOUSES excluding given ones."""
    exclude = set(exclude or [])
    pool = [i for i in range(1, TOTAL_HOUSES + 1) if i not in exclude]
    return sorted(random.sample(pool, k=total))


@router.get("/")
async def launch_status():
    return {"status": "ok", "message": "Backend Launch ativo!"}


@router.post("/create")
async def create_session(player: Player):
    """
    Cria uma sessão (não inicia o jogo). Não inicia `players_order` até que haja >= 2 jogadores.
    Gera todas as casas especiais conforme RN.
    """
    code = generate_code()
    path = get_path(code)
    ensure_dir(path)

    # Salvando jogador inicial
    player_data = player.dict()
    player_data["id"] = 1
    save_json(os.path.join(path, "players.json"), [player_data])

    # Gera casas especiais sem sobreposição:
    used = set()

    # casas de 10 pontos (positivas)
    ten_positive = pick_unique_houses(TEN_POINT_POSITIVE, exclude=used)
    used.update(ten_positive)

    # casas de 10 pontos (pegadinhas)
    ten_traps = pick_unique_houses(TEN_POINT_TRAPS, exclude=used)
    used.update(ten_traps)

    # casas que concedem vida extra
    life_houses = pick_unique_houses(LIFE_HOUSES, exclude=used)
    used.update(life_houses)

    # casas de desafio (20 pontos se acertar)
    challenge_houses = pick_unique_houses(CHALLENGE_HOUSES, exclude=used)
    used.update(challenge_houses)

    # Construir estrutura de casas especiais (por categoria)
    special_houses = {
        "ten_point_positive": ten_positive,
        "ten_point_traps": ten_traps,
        "life": life_houses,
        "challenge_20": challenge_houses
    }

    # Estado inicial do jogo
    game_state = {
        # players_order será definido quando houver >=2 jogadores (no /join)
        "players_order": [],
        "current_turn": None,
        # positions: map de id_str -> posição (0 = start)
        "positions": {"1": 0},
        # scores: map id_str -> pontos
        "scores": {"1": 0},
        # vidas por jogador: 0 ou 1 (a regra RN-06 diz "vida extra" — aqui controlamos por contador)
        "lives": {"1": 0},
        # total casas
        "total_houses": TOTAL_HOUSES,
        # casas especiais agrupadas
        "special_houses": special_houses,
        # marcar início/fim
        "start_time": None,
        "end_time": None,
        # controle de cartas e respostas
        "last_deal": {},
        "used_questions": [],
        # meta: deck pode ser usado pelo /score
        "deck": []
    }

    save_json(os.path.join(path, "game_state.json"), game_state)

    return {
        "message": "Sessão criada!",
        "session_code": code,
        "jogador": player_data,
        "special_houses": special_houses
    }


@router.post("/join/{code}")
async def join_session(code: str, player: Player):
    """
    Adiciona um jogador à sessão. Atualiza positions, scores e lives.
    Quando atingir 2 jogadores, define players_order (embaralhado) e current_turn.
    Permite até 4 jogadores.
    """
    path = get_path(code)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")

    players_file = os.path.join(path, "players.json")
    players = load_json(players_file)

    # validações
    if len(players) >= 4:
        raise HTTPException(status_code=400, detail="Máximo de 4 jogadores por sessão.")

    for p in players:
        if p["email"] == player.email:
            raise HTTPException(status_code=400, detail="E-mail já usado.")
        if p["pawn"] == player.pawn:
            raise HTTPException(status_code=400, detail="Peão já escolhido.")

    # novo jogador
    new_id = players[-1]["id"] + 1
    new_player = player.dict()
    new_player["id"] = new_id
    players.append(new_player)
    save_json(players_file, players)

    # atualiza game_state
    game_state_file = os.path.join(path, "game_state.json")
    game_state = load_json(game_state_file)

    # adiciona posição/score/life
    game_state["positions"][str(new_id)] = 0
    game_state["scores"][str(new_id)] = 0
    game_state["lives"][str(new_id)] = 0

    # se houver pelo menos 2 jogadores, (re)define a ordem e turno
    # --> aqui definimos sempre quando houver >=2 jogadores, para evitar "players_order" preso em [1]
    if len(players) >= 2:
        order = [p["id"] for p in players]
        random.shuffle(order)
        game_state["players_order"] = order
        game_state["current_turn"] = order[0]

    save_json(game_state_file, game_state)

    return {
        "message": "Jogador adicionado!",
        "jogadores": players,
        "ordem": game_state.get("players_order", [])
    }


@router.get("/state/{code}")
async def get_state(code: str):
    """
    Retorna players e game_state completo (útil para simulação/docs).
    """
    path = get_path(code)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    game_file = os.path.join(path, "game_state.json")
    players_file = os.path.join(path, "players.json")
    return {
        "players": load_json(players_file),
        "game_state": load_json(game_file)
    }


@router.post("/start/{code}")
async def start_game(code: str):
    """
    Inicia a partida (seta start_time e end_time = start + 15 minutos).
    Só inicia se houver de 2 a 4 jogadores.
    """
    path = get_path(code)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")

    players_file = os.path.join(path, "players.json")
    game_file = os.path.join(path, "game_state.json")

    players = load_json(players_file)
    game = load_json(game_file)

    if len(players) < 2:
        raise HTTPException(status_code=400, detail="É necessário pelo menos 2 jogadores para iniciar.")
    if len(players) > 4:
        raise HTTPException(status_code=400, detail="Máximo de 4 jogadores permitido.")

    # Se players_order não definido (por algum motivo), define agora
    if not game.get("players_order"):
        order = [p["id"] for p in players]
        random.shuffle(order)
        game["players_order"] = order
        game["current_turn"] = order[0]

    now = int(time.time())
    game["start_time"] = now
    game["end_time"] = now + 15 * 60  # 15 minutos

    save_json(game_file, game)

    return {"message": "Partida iniciada!", "start_time": game["start_time"], "end_time": game["end_time"]}
