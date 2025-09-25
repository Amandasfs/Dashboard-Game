# src/app/scripts/simulate_existing_match.py
import requests
import random
import time

BASE_URL = "http://127.0.0.1:8000"

# --- Configurações ---
SESSION_CODE = input("Digite o código da sessão existente: ")
TURN_DELAY = 0.5  # segundos entre jogadas

# --- Funções de API ---
def get_state():
    r = requests.get(f"{BASE_URL}/launch/state/{SESSION_CODE}")
    if r.status_code == 200:
        return r.json()
    else:
        raise Exception("Erro ao buscar estado da sessão:", r.text)

def deal_card(player_id):
    payload = {"session_code": SESSION_CODE, "player_id": player_id}
    r = requests.post(f"{BASE_URL}/score/deal", json=payload)
    if r.status_code == 200:
        return r.json()["card"]
    else:
        print(f"Erro ao pedir carta (Jogador {player_id}):", r.json())
        return None

def answer_card(player_id, card, skip=False):
    if not skip:
        answer_key = random.choice(list(card["options"].keys()))
    else:
        answer_key = ""
    payload = {
        "session_code": SESSION_CODE,
        "player_id": player_id,
        "answer": answer_key,
        "skip": skip
    }
    r = requests.post(f"{BASE_URL}/score/answer", json=payload)
    if r.status_code == 200:
        return r.json()
    else:
        print(f"Erro ao responder carta (Jogador {player_id}):", r.json())
        return None

# --- Simulação da partida ---
def simulate_match():
    print(f"Simulando partida existente: {SESSION_CODE}")

    while True:
        state = get_state()
        players = state["players"]
        game_state = state["game_state"]
        current_turn = game_state["current_turn"]

        # Busca o jogador da vez
        player = next((p for p in players if p["id"] == current_turn), None)
        if not player:
            print(f"Jogador {current_turn} não encontrado na sessão.")
            break

        pid = player["id"]
        print(f"\nVez do Jogador {player['name']} (ID {pid})")

        card = deal_card(pid)
        if card:
            print("Carta:", card["question"])
            print("Opções:", card["options"])
            result = answer_card(pid, card)
            if result:
                print("Resultado:", result)

        # verifica se acabou a partida
        if result and result.get("status") in ["winner", "finished_time"]:
            print("\nPartida finalizada!")
            break

        time.sleep(TURN_DELAY)

# --- Execução ---
if __name__ == "__main__":
    simulate_match()
