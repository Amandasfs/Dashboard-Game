# app.py
from flask import Flask, send_from_directory, jsonify, request, session
from flask_session import Session
import random
from pathlib import Path

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = "troque_essa_chave_para_uma_secreta_e_complexa"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# -------------------------
# PERGUNTAS (usei sua lista original com difficulties)
# -------------------------
QUESTIONS = [
    # EASY (10)
    {"id": 1, "question": "O que é uma Máquina de Turing?", "options": [
        "Um modelo matemático que manipula símbolos em uma fita de acordo com regras.",
        "Um tipo de algoritmo de ordenação.",
        "Uma linguagem de programação.",
        "Uma rede neural."
    ], "answer": 0, "difficulty": "easy"},
    {"id": 2, "question": "O que significa uma linguagem ser decidível?", "options": [
        "Existe uma MT que sempre decide se uma palavra pertence à linguagem.",
        "Não existe MT que resolva a linguagem.",
        "É uma linguagem natural.",
        "É impossível de reconhecer."
    ], "answer": 0, "difficulty": "easy"},
    {"id": 3, "question": "O que é uma configuração de uma Máquina de Turing?", "options": [
        "O estado atual, a posição da cabeça e o conteúdo da fita.",
        "O algoritmo de ordenação da MT.",
        "O tamanho da fita da MT.",
        "A quantidade de entradas válidas."
    ], "answer": 0, "difficulty": "easy"},
    {"id": 4, "question": "Qual é a função da fita em uma Máquina de Turing?", "options": [
        "Armazenar símbolos e permitir leitura/escrita pela cabeça de leitura.",
        "Determinar a saída do algoritmo.",
        "Controlar os estados da MT.",
        "Registrar erros do programa."
    ], "answer": 0, "difficulty": "easy"},
    {"id": 5, "question": "O que é um estado de aceitação?", "options": [
        "Um estado em que a MT para e aceita a entrada.",
        "O estado inicial da MT.",
        "Um estado que reinicia a MT.",
        "O estado que rejeita a entrada."
    ], "answer": 0, "difficulty": "easy"},
    {"id": 6, "question": "O que significa uma máquina ser determinística?", "options": [
        "Para cada estado e símbolo lido, existe apenas uma ação possível.",
        "Pode escolher aleatoriamente o próximo estado.",
        "Pode executar várias ações ao mesmo tempo.",
        "Sempre erra ao processar a entrada."
    ], "answer": 0, "difficulty": "easy"},
    {"id": 7, "question": "O que significa uma máquina não-determinística?", "options": [
        "Pode haver múltiplas ações possíveis para um mesmo estado e símbolo.",
        "Ela sempre segue apenas uma regra por vez.",
        "É impossível de simular por uma MT determinística.",
        "Não possui estado inicial."
    ], "answer": 0, "difficulty": "easy"},
    {"id": 8, "question": "O que é a cabeça de leitura/escrita?", "options": [
        "É o componente que lê símbolos da fita e escreve novos símbolos.",
        "É o contador de estados da MT.",
        "É o conjunto de regras da MT.",
        "É o tamanho da fita da MT."
    ], "answer": 0, "difficulty": "easy"},
    {"id": 9, "question": "O que é a função de transição?", "options": [
        "Define as regras que a MT segue: próximo estado, símbolo a escrever e direção da cabeça.",
        "Define a quantidade de passos que a MT fará.",
        "Determina se a MT aceita ou rejeita.",
        "Controla a velocidade de processamento da MT."
    ], "answer": 0, "difficulty": "easy"},
    {"id": 10, "question": "O que é um estado inicial?", "options": [
        "O estado em que a MT começa a processar a entrada.",
        "Um estado que finaliza a MT.",
        "O estado que nunca é usado.",
        "Um estado que apenas escreve símbolos."
    ], "answer": 0, "difficulty": "easy"},

    # MEDIUM (20)
    {"id": 11, "question": "Explique a diferença entre problemas decidíveis e indecidíveis.", "options": [
        "Decidíveis podem ser resolvidos por uma MT que sempre termina; indecidíveis não.",
        "Indecidíveis podem ser resolvidos mais rápido que decidíveis.",
        "Decidíveis não têm algoritmo, indecidíveis têm.",
        "Não há diferença prática entre eles."
    ], "answer": 0, "difficulty": "medium"},
    {"id": 12, "question": "O que é a Máquina de Turing Universal?", "options": [
        "Uma MT que pode simular qualquer outra MT com entrada adequada.",
        "Uma MT que só aceita linguagens simples.",
        "Uma MT que não possui estados.",
        "Uma MT que funciona aleatoriamente."
    ], "answer": 0, "difficulty": "medium"},
    {"id": 13, "question": "Defina o Problema da Parada (Halting Problem).", "options": [
        "Determinar se uma MT para ou roda para sempre em uma entrada específica.",
        "Encontrar a entrada que maximiza a MT.",
        "Medir a velocidade de execução da MT.",
        "Calcular o número de estados de uma MT."
    ], "answer": 0, "difficulty": "medium"},
    {"id": 14, "question": "Explique o conceito de configuração instantânea em uma MT.", "options": [
        "É o estado atual, a posição da cabeça e o conteúdo da fita em um momento específico.",
        "É a função de transição da MT.",
        "É a quantidade de fitas usadas.",
        "É o total de passos executados."
    ], "answer": 0, "difficulty": "medium"},
    {"id": 15, "question": "Como a Máquina de Turing Universal simula outra MT?", "options": [
        "Ela lê a descrição da MT e a entrada, simulando passo a passo as transições da MT original.",
        "Ela cria uma MT nova do zero.",
        "Ela ignora a entrada da MT original.",
        "Ela apenas copia a fita da MT original."
    ], "answer": 0, "difficulty": "medium"},
    {"id": 16, "question": "Por que algumas linguagens são indecidíveis?", "options": [
        "Porque não existe MT que termine sempre e decida se uma palavra pertence à linguagem.",
        "Porque a MT não consegue ler símbolos.",
        "Porque todas as MTs são determinísticas.",
        "Porque a fita da MT é limitada."
    ], "answer": 0, "difficulty": "medium"},
    {"id": 17, "question": "O que significa uma linguagem ser recursiva?", "options": [
        "Existe uma MT que decide se qualquer palavra pertence ou não à linguagem, sempre terminando.",
        "A linguagem não tem algoritmo associado.",
        "É uma linguagem que não pode ser computada.",
        "É uma linguagem que sempre aceita qualquer palavra."
    ], "answer": 0, "difficulty": "medium"},
    {"id": 18, "question": "O que significa uma linguagem ser recursivamente enumerável?", "options": [
        "Existe uma MT que aceita todas as palavras da linguagem, mas pode não parar para palavras que não pertencem.",
        "Todas as palavras são rejeitadas.",
        "A linguagem não tem MT associada.",
        "Existe uma MT que rejeita todas as palavras."
    ], "answer": 0, "difficulty": "medium"},
    {"id": 19, "question": "Como problemas podem ser transformados para provar indecidibilidade?", "options": [
        "Usando redução de um problema indecidível para outro.",
        "Ignorando o problema original.",
        "Simplificando a MT.",
        "Usando apenas a fita da MT."
    ], "answer": 0, "difficulty": "medium"},
    {"id": 20, "question": "O que é uma MT com múltiplas fitas?", "options": [
        "Uma MT que possui mais de uma fita para leitura e escrita, podendo simular mais rápido certas operações.",
        "Uma MT que só usa uma fita virtual.",
        "Uma MT que não possui cabeça de leitura.",
        "Uma MT que ignora símbolos da fita."
    ], "answer": 0, "difficulty": "medium"},

    # HARD (30)
    {"id": 21, "question": "Explique por que o Problema da Parada é indecidível.", "options": [
        "Se fosse decidível, poderíamos construir uma MT que contradiz a si mesma, gerando paradoxo.",
        "Porque nenhuma MT funciona corretamente.",
        "Porque todas as MTs são determinísticas.",
        "Porque a fita é infinita."
    ], "answer": 0, "difficulty": "hard"},
    {"id": 22, "question": "Como se relaciona o conceito de redutibilidade com indecidibilidade?", "options": [
        "Se A se reduz a B e B é decidível, então A também é decidível; caso contrário, podemos provar indecidibilidade.",
        "Redutibilidade não tem relação com indecidibilidade.",
        "Redutibilidade resolve todos os problemas.",
        "Redutibilidade só serve para linguagens fáceis."
    ], "answer": 0, "difficulty": "hard"},
    {"id": 23, "question": "Explique a relação entre linguagens recursivas e recursivamente enumeráveis.", "options": [
        "Toda linguagem recursiva é recursivamente enumerável, mas nem toda recursivamente enumerável é recursiva.",
        "São exatamente a mesma coisa.",
        "Nenhuma linguagem recursiva é enumerável.",
        "Recursivamente enumeráveis são sempre decidíveis."
    ], "answer": 0, "difficulty": "hard"},
    {"id": 24, "question": "Como provar que uma linguagem é indecidível?", "options": [
        "Normalmente se reduz um problema indecidível conhecido para a linguagem em questão.",
        "Tentando todas as entradas possíveis.",
        "Executando a MT infinitamente.",
        "Usando apenas a fita da MT."
    ], "answer": 0, "difficulty": "hard"},
    {"id": 25, "question": "O que é a MT de Turing Universal e por que é importante?", "options": [
        "É a MT que pode simular qualquer MT; importante para formalizar computabilidade.",
        "É a MT que ignora outras MTs.",
        "É a MT que não aceita nenhuma palavra.",
        "É a MT que aceita todas as palavras sem regras."
    ], "answer": 0, "difficulty": "hard"},
    {"id": 26, "question": "Explique o conceito de diagonalização de Cantor em computabilidade.", "options": [
        "É usado para provar que certos conjuntos ou problemas são não computáveis, como o Halting Problem.",
        "É um método para organizar a fita da MT.",
        "É uma regra de transição da MT.",
        "É uma técnica de ordenação."
    ], "answer": 0, "difficulty": "hard"},
    {"id": 27, "question": "O que significa uma função ser computável?", "options": [
        "Existe uma MT que, dada a entrada, produz a saída correta e termina.",
        "É uma função que não pode ser calculada.",
        "É uma função que não termina nunca.",
        "É uma função que depende da sorte."
    ], "answer": 0, "difficulty": "hard"},
    {"id": 28, "question": "Qual a diferença entre problemas de decisão e problemas de função?", "options": [
        "Problemas de decisão retornam sim/não; problemas de função retornam um valor ou saída complexa.",
        "Problemas de decisão sempre falham.",
        "Problemas de função são sempre indecidíveis.",
        "Não existe diferença prática."
    ], "answer": 0, "difficulty": "hard"},
    {"id": 29, "question": "Como a indecidibilidade do Problema da Parada afeta outras linguagens?", "options": [
        "Muitas linguagens derivadas do Halting Problem também são indecidíveis.",
        "Todas as linguagens se tornam decidíveis.",
        "Não afeta outras linguagens.",
        "Todas as linguagens se tornam recursivas."
    ], "answer": 0, "difficulty": "hard"},
    {"id": 30, "question": "Explique a relação entre MT determinísticas e não-determinísticas.", "options": [
        "MT não-determinísticas podem ter múltiplas escolhas; toda MT não-determinística pode ser simulada por uma determinística.",
        "MT determinísticas não podem ser simuladas.",
        "MT não-determinísticas não podem aceitar nenhuma palavra.",
        "MT determinísticas e não-determinísticas são iguais em todos os aspectos."
    ], "answer": 0, "difficulty": "hard"},
]

# map id -> question for quick lookup
QUESTIONS_MAP = {q["id"]: q for q in QUESTIONS}

# question value by difficulty
VALUE_BY_DIFFICULTY = {
    "easy": 10,
    "medium": 20,
    "hard": 30
}

WIN_SCORE = 100

# -------------------------
# Helpers
# -------------------------
def reset_game_state():
    session["used_ids"] = []
    session["user_score"] = 0
    session["bot_score"] = 0
    session["user_lives"] = 3
    session["rounds_played"] = 0
    session.modified = True

def pick_random_question():
    used = set(session.get("used_ids", []))
    available = [q for q in QUESTIONS if q["id"] not in used]
    if not available:
        return None
    question = random.choice(available)
    used.add(question["id"])
    session["used_ids"] = list(used)
    session.modified = True
    # return question without answer key
    return {"id": question["id"], "question": question["question"], "options": question["options"], "difficulty": question["difficulty"]}

def apply_score_change(player: str, difficulty: str, correct: bool):
    """player = 'user' or 'bot'"""
    value = VALUE_BY_DIFFICULTY.get(difficulty, 10)
    half = value // 2
    if player == "user":
        if correct:
            session["user_score"] = session.get("user_score", 0) + value
        else:
            # perde metade do valor e uma vida
            session["user_score"] = max(0, session.get("user_score", 0) - half)
            session["user_lives"] = session.get("user_lives", 3) - 1
    else:
        if correct:
            session["bot_score"] = session.get("bot_score", 0) + value
        else:
            session["bot_score"] = max(0, session.get("bot_score", 0) - half)
    session.modified = True

def check_winner_after_move():
    """Retorna 'user' / 'bot' / None se alguém alcançou WIN_SCORE."""
    if session.get("user_score", 0) >= WIN_SCORE:
        return "user"
    if session.get("bot_score", 0) >= WIN_SCORE:
        return "bot"
    return None

# -------------------------
# Routes
# -------------------------
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/start", methods=["POST"])
def api_start():
    reset_game_state()
    q = pick_random_question()
    return jsonify({
        "ok": True,
        "question": q,
        "user_score": session["user_score"],
        "bot_score": session["bot_score"],
        "user_lives": session["user_lives"]
    })

@app.route("/api/answer", methods=["POST"])
def api_answer():
    payload = request.get_json()
    if not payload:
        return jsonify({"ok": False, "error": "Payload inválido"}), 400

    qid = payload.get("id")
    selected = payload.get("selected")  # index 0..3 or -1 for timeout

    if qid is None or selected is None:
        return jsonify({"ok": False, "error": "Campos 'id' e 'selected' são obrigatórios"}), 400

    if qid not in QUESTIONS_MAP:
        return jsonify({"ok": False, "error": "Pergunta não encontrada"}), 404

    # get original question (contains answer and difficulty)
    question = QUESTIONS_MAP[qid]
    difficulty = question.get("difficulty", "easy")
    correct_index = question["answer"]

    # determine user correctness (selected == -1 => timeout => considered wrong)
    user_correct = (selected == correct_index)

    # apply user scoring & lives
    if selected == -1:
        user_correct = False

    apply_score_change("user", difficulty, user_correct)

    user_result = {
        "correct": user_correct,
        "correct_index": correct_index,
        "selected": selected
    }

    # check if user reached win score -> immediate win (bot não joga)
    winner = check_winner_after_move()
    if winner == "user":
        session.modified = True
        return jsonify({
            "ok": True,
            "user_result": user_result,
            "bot_result": {"did_play": False},
            "user_score": session.get("user_score", 0),
            "bot_score": session.get("bot_score", 0),
            "user_lives": session.get("user_lives", 0),
            "game_over": True,
            "winner": "user",
            "next_question": None
        })

    # if user lost all lives -> game over immediately
    if session.get("user_lives", 0) <= 0:
        return jsonify({
            "ok": True,
            "user_result": user_result,
            "bot_result": {"did_play": False},
            "user_score": session.get("user_score", 0),
            "bot_score": session.get("bot_score", 0),
            "user_lives": session.get("user_lives", 0),
            "game_over": True,
            "winner": "bot",
            "next_question": None
        })

    # -----------------------
    # TURN DO BOT (sorteia outra pergunta)
    # -----------------------
    # pick bot question (different from used)
    bot_q = pick_random_question()
    bot_result = {"did_play": False}
    if bot_q is not None:
        # bot selects random option index
        bot_selected = random.randrange(len(bot_q["options"]))
        # bot correct with 50% chance
        bot_hits = random.random() < 0.5
        # But to be consistent, if bot_hits is True we can set bot_selected = correct_index of original question id
        # Need original question (with answer) from QUESTIONS_MAP
        bot_original = QUESTIONS_MAP[bot_q["id"]]
        if bot_hits:
            bot_selected = bot_original["answer"]
        # apply bot scoring
        apply_score_change("bot", bot_original.get("difficulty", "easy"), bot_hits)
        bot_result = {
            "did_play": True,
            "qid": bot_q["id"],
            "question": bot_q["question"],
            "selected": bot_selected,
            "correct": bot_hits,
            "correct_index": bot_original["answer"],
            "difficulty": bot_original.get("difficulty", "easy")
        }

    # check winner after bot move
    winner = check_winner_after_move()
    game_over = False
    if winner is not None:
        game_over = True

    # prepare next question for user (if any and not game over)
    next_q = None
    if not game_over:
        next_q = pick_random_question()

    return jsonify({
        "ok": True,
        "user_result": user_result,
        "bot_result": bot_result,
        "user_score": session.get("user_score", 0),
        "bot_score": session.get("bot_score", 0),
        "user_lives": session.get("user_lives", 0),
        "game_over": game_over,
        "winner": winner,
        "next_question": next_q
    })

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    # debug True facilita desenvolvimento; remova em produção
    app.run(debug=True, port=5000)
