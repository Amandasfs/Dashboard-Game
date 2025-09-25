# api/score.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
import random
import time

router = APIRouter()
BASE_DIR = "data/sessions"

# --- MODELS ---

class PlayAnswer(BaseModel):
    answer: str = ""  # opcional: 'a'/'b'/'c'/'d'
    skip: bool = False

class PlayerAction(BaseModel):
    session_code: str
    player_id: int

class AnswerCard(PlayerAction, PlayAnswer):
    pass

# --- UTILS ---

def get_paths(session_code):
    session_path = os.path.join(BASE_DIR, session_code)
    if not os.path.exists(session_path):
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    return os.path.join(session_path, "players.json"), os.path.join(session_path, "game_state.json")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def generate_deck():
    raw_cards = [
        {"question": "Quem foi o criador da Máquina de Turing?",
         "options": ["John von Neumann", "Alan Turing", "Claude Shannon", "Kurt Gödel"],
         "correct_answer": "Alan Turing"},
        {"question": "Qual foi o principal objetivo de Alan Turing ao criar o conceito de Máquina de Turing?",
         "options": ["Resolver o problema da criptografia durante a Segunda Guerra Mundial",
                     "Definir o limite da computação e formalizar a noção de algoritmo",
                     "Propor um novo sistema de números binários",
                     "Construir o primeiro computador físico"],
         "correct_answer": "Definir o limite da computação e formalizar a noção de algoritmo"},
        {"question": "Durante a Segunda Guerra Mundial, o trabalho de Alan Turing ajudou a quebrar qual código criptográfico?",
         "options": ["Código Enigma", "Código Caesar", "Código Morse", "Código RSA"],
         "correct_answer": "Código Enigma"},
        {"question": "O que significa que a Máquina de Turing é 'universal'?",
         "options": ["Ela pode resolver qualquer problema computacionalmente decidível",
                     "Ela pode simular qualquer outra Máquina de Turing",
                     "Ela é capaz de realizar apenas operações aritméticas simples",
                     "Ela pode ser utilizada para resolver problemas matemáticos avançados"],
         "correct_answer": "Ela pode simular qualquer outra Máquina de Turing"},
        {"question": "O que é o 'Problema da Parada' (Halting Problem)?",
         "options": ["Determinar se um programa vai terminar em um número finito de passos",
                     "Determinar se um programa está executando em tempo exponencial",
                     "Verificar se uma Máquina de Turing está no estado inicial",
                     "Verificar se uma linguagem é regular"],
         "correct_answer": "Determinar se um programa vai terminar em um número finito de passos"}
    ]

    cards = []
    for raw in raw_cards:
        opts = raw["options"][:]
        random.shuffle(opts)
        key_map = dict(zip(["a", "b", "c", "d"], opts))
        correct_letter = next(k for k, v in key_map.items() if v == raw["correct_answer"])
        # Define move_spaces: fácil=2, média=4, difícil=6 (RN-01)
        move_spaces = random.choice([2, 4, 6])
        cards.append({
            "question": raw["question"],
            "options": key_map,
            "correct": correct_letter,
            "move_spaces": move_spaces
        })
    random.shuffle(cards)
    return cards

# --- ROTAS ---

@router.post("/deal")
async def deal_card(action: PlayerAction):
    players_file, game_file = get_paths(action.session_code)
    game = load_json(game_file)

    pid = str(action.player_id)
    if pid not in game["positions"]:
        raise HTTPException(status_code=400, detail="Jogador inválido.")
    if game.get("current_turn") != action.player_id:
        raise HTTPException(status_code=400, detail="Não é a vez deste jogador.")

    now = int(time.time())
    if game.get("start_time") is None or now >= game.get("end_time", 0):
        raise HTTPException(status_code=400, detail="Partida não iniciada ou já terminou.")

    deck = generate_deck()
    used = game.get("used_questions", [])
    available_cards = [c for i, c in enumerate(deck) if i not in used]
    if not available_cards:
        game["used_questions"] = []
        available_cards = deck

    card = random.choice(available_cards)
    card_index = deck.index(card)
    game.setdefault("used_questions", []).append(card_index)
    game.setdefault("last_deal", {})[pid] = {"card": card, "timestamp": now}

    save_json(game_file, game)
    return {
        "card": {
            "question": card["question"],
            "options": card["options"],
            "move_spaces": card["move_spaces"]
        },
        "message": "Carta entregue. Você tem 60 segundos para responder."
    }

@router.post("/answer")
async def answer_card(body: AnswerCard):
    players_file, game_file = get_paths(body.session_code)
    game = load_json(game_file)

    pid = str(body.player_id)
    if pid not in game["positions"]:
        raise HTTPException(status_code=400, detail="Jogador inválido.")

    last = game.get("last_deal", {}).get(pid)
    if not last:
        raise HTTPException(status_code=400, detail="Nenhuma carta entregue a este jogador.")

    now = int(time.time())
    if now - last["timestamp"] > 60:
        body.skip = True  # RN-02: timeout → voltar 1 casa

    card = last["card"]
    current_pos = game["positions"][pid]
    gained_points, move = 0, 0
    action_msg = ""

    # --- RN aplicação ---
    if body.skip:
        move = -1 if current_pos > 0 else 0
        action_msg = "Jogador não respondeu / timeout: voltou 1 casa. (RN-02)"
    else:
        ans = body.answer.lower().strip()
        correct = (ans == card["correct"])

        # Verifica se está em casa especial
        special = game.get("special_houses", {})
        is_special = current_pos in (
            special.get("ten_point_positive", [])
            + special.get("ten_point_traps", [])
            + special.get("life", [])
            + special.get("challenge_20", [])
        )

        # Vida extra ativa (RN-06)
        has_life = game["lives"].get(pid, 0) > 0

        if correct:
            # RN-01: acertou → anda move_spaces
            move = card["move_spaces"]
            gained_points += move
            action_msg = f"Acertou! Avançou {move} casas. (RN-01)"
        else:
            if is_special:
                # RN-07: errar em casa especial não gera punição
                move = 0
                action_msg = "Errou em casa especial: sem punição. (RN-07)"
            elif has_life:
                # Gasta vida para anular punição
                game["lives"][pid] -= 1
                move = 0
                action_msg = "Errou, mas usou a vida extra: sem punição. (RN-06)"
            else:
                # RN-03: erro normal → volta metade
                penalty = card["move_spaces"] // 2
                move = -penalty if current_pos > 0 else 0
                action_msg = f"Errou! Voltou {abs(move)} casas. (RN-03)"

    # Atualiza posição
    new_pos = max(0, min(current_pos + move, game["total_houses"]))
    game["positions"][pid] = new_pos
    game["scores"][pid] = game["scores"].get(pid, 0) + gained_points

    # --- RN casas especiais ---
    specials = game.get("special_houses", {})
    if new_pos in specials.get("ten_point_positive", []):
        game["scores"][pid] += 10
        action_msg += " Caiu em casa +10 pontos. (RN-05)"
    elif new_pos in specials.get("ten_point_traps", []):
        action_msg += " Caiu em casa pegadinha: nada acontece. (RN-05)"
    elif new_pos in specials.get("life", []):
        # RN-08: só ganha se parar exatamente
        game["lives"][pid] = game["lives"].get(pid, 0) + 1
        action_msg += " Ganhou uma vida extra! (RN-06, RN-08)"
    elif new_pos in specials.get("challenge_20", []):
        if not body.skip and body.answer.lower().strip() == card["correct"]:
            game["scores"][pid] += 20
            action_msg += " Acertou desafio: +20 pontos! (RN-04)"
        else:
            action_msg += " Desafio falhado: sem bônus. (RN-04, RN-07)"

    # Limpa carta
    if pid in game.get("last_deal", {}):
        del game["last_deal"][pid]

    # Passa turno
    order = game["players_order"]
    next_index = (order.index(body.player_id) + 1) % len(order)
    game["current_turn"] = order[next_index]

    # Fim da partida
    if now >= game.get("end_time", 0):
        save_json(game_file, game)
        return {
            "ação": action_msg,
            "posição": new_pos,
            "pontos": game["scores"][pid],
            "status": "finished_time"
        }
    if new_pos >= game["total_houses"]:
        save_json(game_file, game)
        return {
            "ação": action_msg,
            "posição": new_pos,
            "pontos": game["scores"][pid],
            "status": "winner",
            "message": f"Jogador {body.player_id} venceu a partida!"
        }

    save_json(game_file, game)
    return {
        "ação": action_msg,
        "posição": new_pos,
        "pontos": game["scores"][pid],
        "vidas": game["lives"][pid],
        "próximo": game["current_turn"]
    }
