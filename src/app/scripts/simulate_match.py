# scripts/simulate_match.py
import requests
import random
import time

BASE_URL = "http://127.0.0.1:8000"
TOTAL_HOUSES = 60

session_code = None
players = []

def create_session():
    global session_code
    print("Criando sessão...")
    res = requests.post(f"{BASE_URL}/launch/create", json={
        "name": "Jogador Humano",
        "email": "humano@email.com",
        "password": "123",
        "pawn": "blue"
    })
    data = res.json()
    session_code = data["session_code"]
    players.append(data["jogador"])
    print("Sessão criada:", session_code)
    print("Casas especiais:", data.get("special_houses"))

def join_rnd_player():
    print("Adicionando jogador RNG...")
    res = requests.post(f"{BASE_URL}/launch/join/{session_code}", json={
        "name": "Jogador RNG",
        "email": "rng@email.com",
        "password": "rng123",
        "pawn": "red"
    })
    data = res.json()
    for p in data["jogadores"]:
        if p["email"] == "rng@email.com":
            players.append(p)
    print("Jogador RNG entrou.")

def start_game():
    print("Iniciando partida...")
    res = requests.post(f"{BASE_URL}/launch/start/{session_code}")
    print(res.json())

def get_game_state():
    res = requests.get(f"{BASE_URL}/launch/state/{session_code}")
    return res.json()

def play_turn_api(player):
    pid = player["id"]
    name = player["name"]
    print(f"\nVez de {name} (id={pid})")

    # 1) pedir carta
    r = requests.post(f"{BASE_URL}/score/deal/{session_code}/{pid}")
    if r.status_code != 200:
        print("Erro ao pedir carta:", r.json())
        return False
    card = r.json()["card"]
    print("Carta:", card["question"])
    for k, v in card["options"].items():
        print(f"{k}) {v}")
    # Simula delay pequeno
    time.sleep(random.uniform(0.1, 1.0))

    # 2) responder
    if name == "Jogador RNG":
        # RNG: 20% skip, se não -> 70% acerta
        if random.random() < 0.2:
            payload = {"answer": "", "skip": True}
        else:
            if random.random() < 0.7:
                # responde corretamente
                # encontra a chave correta (servidor não retorna a key 'correct', então para simulação vamos usar heurística: pick B if 'Brasília' etc)
                # Para simplicidade, vamos "adivinhar" com 70% de chance como acertar: enviamos 'b' ou 'a' dependendo do texto
                # Melhor: quando deck é fixo do servidor, nós podemos inferir por frase. Aqui assumimos 70% acerto enviando 'b' (funciona para as cartas de exemplo).
                payload = {"answer": "b", "skip": False}
            else:
                # envia resposta errada aleatória
                payload = {"answer": random.choice(["a", "c", "d"]), "skip": False}
        print(f"[RNG] Resposta: {payload['answer'] or 'SKIP'}")
    else:
        # Jogador humano: para teste, vamos responder sempre 'b' (ou poderia ler input)
        payload = {"answer": "b", "skip": False}
        print(f"[HUMANO SIM] Resposta: {payload['answer']}")

    r2 = requests.post(f"{BASE_URL}/score/answer/{session_code}/{pid}", json=payload)
    if r2.status_code != 200:
        print("Erro ao responder:", r2.json())
        return False
    res = r2.json()
    print("Resultado:", res.get("ação"))
    print("Nova posição:", res.get("posição_atual"))
    print("Pontos:", res.get("pontos"))
    if res.get("status") == "winner":
        print(f"\n🏆 {player['name']} venceu por alcançar a casa final!")
        return True
    if res.get("status") == "finished_time":
        print("\n⏳ Partida terminou por tempo.")
        return True
    return res.get("posição_atual", 0) >= TOTAL_HOUSES

def main():
    create_session()
    join_rnd_player()
    start_game()
    time.sleep(0.5)

    # Trava local dos jogadores (ordem retornada pelo state)
    state = get_game_state()
    players_local = state["players"]
    game_state = state["game_state"]
    order_ids = game_state["players_order"]

    # loop enquanto não terminar
    running = True
    while running:
        state = get_game_state()
        current = state["game_state"]["current_turn"]
        player = next(p for p in players if p["id"] == current)
        fim = play_turn_api(player)
        if fim:
            running = False
            break
        time.sleep(0.5)

if __name__ == "__main__":
    main()
