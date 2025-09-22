# api/launch.py
from fastapi import APIRouter, HTTPException
from models.player import Player
import os
import json
import random
import string
import time

router = APIRouter()

BASE_DIR = "data/sessions"

def generate_code(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_path(session_code):
    return os.path.join(BASE_DIR, session_code)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def load_json(file_path):
    if not os.path.exists(file_path):
        return [] if "players" in file_path else {}
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# ---------- NOVA ROTA DE STATUS ----------
@router.get("/")
async def launch_status():
    return {"status": "ok", "message": "Backend Launch ativo!"}

# ---------- CRIAR SESSÃO ----------
@router.post("/create")
async def create_session(player: Player):
    code = generate_code()
    path = get_path(code)
    ensure_dir(path)

    player_data = player.dict()
    player_data["id"] = 1
    save_json(os.path.join(path, "players.json"), [player_data])

    total_houses = 60
    special_count = random.randint(15, 20)
    special_houses = sorted(random.sample(range(1, total_houses + 1), k=special_count))

    game_state = {
        "players_order": [1],       # ordem inicial já com jogador 1
        "current_turn": 1,           # jogador 1 começa
        "positions": {"1": 0},
        "deck": [],
        "scores": {"1": 0},
        "total_houses": total_houses,
        "special_houses": special_houses,
        "start_time": None,
        "end_time": None,
        "last_deal": {}
    }
    save_json(os.path.join(path, "game_state.json"), game_state)

    return {"message": "Sessão criada!", "session_code": code, "jogador": player_data, "special_houses": special_houses}

# ---------- ADICIONAR JOGADOR ----------
@router.post("/join/{code}")
async def join_session(code: str, player: Player):
    path = get_path(code)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")

    players_file = os.path.join(path, "players.json")
    players = load_json(players_file)

    if len(players) >= 4:
        raise HTTPException(status_code=400, detail="Máximo de 4 jogadores por sessão.")

    for p in players:
        if p["email"] == player.email:
            raise HTTPException(status_code=400, detail="E-mail já usado.")
        if p["pawn"] == player.pawn:
            raise HTTPException(status_code=400, detail="Peão já escolhido.")

    new_id = players[-1]["id"] + 1
    new_player = player.dict()
    new_player["id"] = new_id
    players.append(new_player)
    save_json(players_file, players)

    game_state_file = os.path.join(path, "game_state.json")
    game_state = load_json(game_state_file)
    game_state["positions"][str(new_id)] = 0
    game_state["scores"][str(new_id)] = 0

    # Atualiza ordem e turno se houver pelo menos 2 jogadores e ainda não definido
    if len(players) >= 2 and not game_state["players_order"]:
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

# ---------- OBTER ESTADO ----------
@router.get("/state/{code}")
async def get_state(code: str):
    path = get_path(code)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    game_file = os.path.join(path, "game_state.json")
    players_file = os.path.join(path, "players.json")
    return {
        "players": load_json(players_file),
        "game_state": load_json(game_file)
    }

# ---------- INICIAR PARTIDA ----------
@router.post("/start/{code}")
async def start_game(code: str):
    path = get_path(code)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    players_file = os.path.join(path, "players.json")
    game_file = os.path.join(path, "game_state.json")

    players = load_json(players_file)
    game = load_json(game_file)

    if len(players) < 2:
        raise HTTPException(status_code=400, detail="É necessário pelo menos 2 jogadores para iniciar.")

    now = int(time.time())
    game["start_time"] = now
    game["end_time"] = now + 15 * 60  # 15 minutos
    save_json(game_file, game)

    return {"message": "Partida iniciada!", "start_time": game["start_time"], "end_time": game["end_time"]}
