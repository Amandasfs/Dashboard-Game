# backend/populate_cards.py
from app import create_app
from app.services.card_service import CardService

# 1️⃣ Inicializa o app Flask e conecta ao DB
app = create_app()

# 2️⃣ Lista de cartas com alternativas
cards = [
    # ------------------ FÁCIL ------------------
    {
        "question": "O que é uma Máquina de Turing?",
        "options": [
            "Um modelo matemático que manipula símbolos em uma fita de acordo com regras.",
            "Um tipo de algoritmo de ordenação.",
            "Uma linguagem de programação.",
            "Uma rede neural."
        ],
        "answer": 0,
        "difficulty": "easy"
    },
    {
        "question": "O que significa uma linguagem ser decidível?",
        "options": [
            "Existe uma MT que sempre decide se uma palavra pertence à linguagem.",
            "Não existe MT que resolva a linguagem.",
            "É uma linguagem natural.",
            "É impossível de reconhecer."
        ],
        "answer": 0,
        "difficulty": "easy"
    },
    {
        "question": "O que é uma configuração de uma Máquina de Turing?",
        "options": [
            "O estado atual, a posição da cabeça e o conteúdo da fita.",
            "O algoritmo de ordenação da MT.",
            "O tamanho da fita da MT.",
            "A quantidade de entradas válidas."
        ],
        "answer": 0,
        "difficulty": "easy"
    },
    {
        "question": "Qual é a função da fita em uma Máquina de Turing?",
        "options": [
            "Armazenar símbolos e permitir leitura/escrita pela cabeça de leitura.",
            "Determinar a saída do algoritmo.",
            "Controlar os estados da MT.",
            "Registrar erros do programa."
        ],
        "answer": 0,
        "difficulty": "easy"
    },
    {
        "question": "O que é um estado de aceitação?",
        "options": [
            "Um estado em que a MT para e aceita a entrada.",
            "O estado inicial da MT.",
            "Um estado que reinicia a MT.",
            "O estado que rejeita a entrada."
        ],
        "answer": 0,
        "difficulty": "easy"
    },
    {
        "question": "O que significa uma máquina ser determinística?",
        "options": [
            "Para cada estado e símbolo lido, existe apenas uma ação possível.",
            "Pode escolher aleatoriamente o próximo estado.",
            "Pode executar várias ações ao mesmo tempo.",
            "Sempre erra ao processar a entrada."
        ],
        "answer": 0,
        "difficulty": "easy"
    },
    {
        "question": "O que significa uma máquina não-determinística?",
        "options": [
            "Pode haver múltiplas ações possíveis para um mesmo estado e símbolo.",
            "Ela sempre segue apenas uma regra por vez.",
            "É impossível de simular por uma MT determinística.",
            "Não possui estado inicial."
        ],
        "answer": 0,
        "difficulty": "easy"
    },
    {
        "question": "O que é a cabeça de leitura/escrita?",
        "options": [
            "É o componente que lê símbolos da fita e escreve novos símbolos.",
            "É o contador de estados da MT.",
            "É o conjunto de regras da MT.",
            "É o tamanho da fita da MT."
        ],
        "answer": 0,
        "difficulty": "easy"
    },
    {
        "question": "O que é a função de transição?",
        "options": [
            "Define as regras que a MT segue: próximo estado, símbolo a escrever e direção da cabeça.",
            "Define a quantidade de passos que a MT fará.",
            "Determina se a MT aceita ou rejeita.",
            "Controla a velocidade de processamento da MT."
        ],
        "answer": 0,
        "difficulty": "easy"
    },
    {
        "question": "O que é um estado inicial?",
        "options": [
            "O estado em que a MT começa a processar a entrada.",
            "Um estado que finaliza a MT.",
            "O estado que nunca é usado.",
            "Um estado que apenas escreve símbolos."
        ],
        "answer": 0,
        "difficulty": "easy"
    },

    # ------------------ MÉDIO ------------------
    {
        "question": "Explique a diferença entre problemas decidíveis e indecidíveis.",
        "options": [
            "Decidíveis podem ser resolvidos por uma MT que sempre termina; indecidíveis não.",
            "Indecidíveis podem ser resolvidos mais rápido que decidíveis.",
            "Decidíveis não têm algoritmo, indecidíveis têm.",
            "Não há diferença prática entre eles."
        ],
        "answer": 0,
        "difficulty": "medium"
    },
    {
        "question": "O que é a Máquina de Turing Universal?",
        "options": [
            "Uma MT que pode simular qualquer outra MT com entrada adequada.",
            "Uma MT que só aceita linguagens simples.",
            "Uma MT que não possui estados.",
            "Uma MT que funciona aleatoriamente."
        ],
        "answer": 0,
        "difficulty": "medium"
    },
    {
        "question": "Defina o Problema da Parada (Halting Problem).",
        "options": [
            "Determinar se uma MT para ou roda para sempre em uma entrada específica.",
            "Encontrar a entrada que maximiza a MT.",
            "Medir a velocidade de execução da MT.",
            "Calcular o número de estados de uma MT."
        ],
        "answer": 0,
        "difficulty": "medium"
    },
    {
        "question": "Explique o conceito de configuração instantânea em uma MT.",
        "options": [
            "É o estado atual, a posição da cabeça e o conteúdo da fita em um momento específico.",
            "É a função de transição da MT.",
            "É a quantidade de fitas usadas.",
            "É o total de passos executados."
        ],
        "answer": 0,
        "difficulty": "medium"
    },
    {
        "question": "Como a Máquina de Turing Universal simula outra MT?",
        "options": [
            "Ela lê a descrição da MT e a entrada, simulando passo a passo as transições da MT original.",
            "Ela cria uma MT nova do zero.",
            "Ela ignora a entrada da MT original.",
            "Ela apenas copia a fita da MT original."
        ],
        "answer": 0,
        "difficulty": "medium"
    },
    {
        "question": "Por que algumas linguagens são indecidíveis?",
        "options": [
            "Porque não existe MT que termine sempre e decida se uma palavra pertence à linguagem.",
            "Porque a MT não consegue ler símbolos.",
            "Porque todas as MTs são determinísticas.",
            "Porque a fita da MT é limitada."
        ],
        "answer": 0,
        "difficulty": "medium"
    },
    {
        "question": "O que significa uma linguagem ser recursiva?",
        "options": [
            "Existe uma MT que decide se qualquer palavra pertence ou não à linguagem, sempre terminando.",
            "A linguagem não tem algoritmo associado.",
            "É uma linguagem que não pode ser computada.",
            "É uma linguagem que sempre aceita qualquer palavra."
        ],
        "answer": 0,
        "difficulty": "medium"
    },
    {
        "question": "O que significa uma linguagem ser recursivamente enumerável?",
        "options": [
            "Existe uma MT que aceita todas as palavras da linguagem, mas pode não parar para palavras que não pertencem.",
            "Todas as palavras são rejeitadas.",
            "A linguagem não tem MT associada.",
            "Existe uma MT que rejeita todas as palavras."
        ],
        "answer": 0,
        "difficulty": "medium"
    },
    {
        "question": "Como problemas podem ser transformados para provar indecidibilidade?",
        "options": [
            "Usando redução de um problema indecidível para outro.",
            "Ignorando o problema original.",
            "Simplificando a MT.",
            "Usando apenas a fita da MT."
        ],
        "answer": 0,
        "difficulty": "medium"
    },
    {
        "question": "O que é uma MT com múltiplas fitas?",
        "options": [
            "Uma MT que possui mais de uma fita para leitura e escrita, podendo simular mais rápido certas operações.",
            "Uma MT que só usa uma fita virtual.",
            "Uma MT que não possui cabeça de leitura.",
            "Uma MT que ignora símbolos da fita."
        ],
        "answer": 0,
        "difficulty": "medium"
    },

    # ------------------ DIFÍCIL ------------------
    {
        "question": "Explique por que o Problema da Parada é indecidível.",
        "options": [
            "Se fosse decidível, poderíamos construir uma MT que contradiz a si mesma, gerando paradoxo.",
            "Porque nenhuma MT funciona corretamente.",
            "Porque todas as MTs são determinísticas.",
            "Porque a fita é infinita."
        ],
        "answer": 0,
        "difficulty": "hard"
    },
    {
        "question": "Como se relaciona o conceito de redutibilidade com indecidibilidade?",
        "options": [
            "Se A se reduz a B e B é decidível, então A também é decidível; caso contrário, podemos provar indecidibilidade.",
            "Redutibilidade não tem relação com indecidibilidade.",
            "Redutibilidade resolve todos os problemas.",
            "Redutibilidade só serve para linguagens fáceis."
        ],
        "answer": 0,
        "difficulty": "hard"
    },
    {
        "question": "Explique a relação entre linguagens recursivas e recursivamente enumeráveis.",
        "options": [
            "Toda linguagem recursiva é recursivamente enumerável, mas nem toda recursivamente enumerável é recursiva.",
            "São exatamente a mesma coisa.",
            "Nenhuma linguagem recursiva é enumerável.",
            "Recursivamente enumeráveis são sempre decidíveis."
        ],
        "answer": 0,
        "difficulty": "hard"
    },
    {
        "question": "Como provar que uma linguagem é indecidível?",
        "options": [
            "Normalmente se reduz um problema indecidível conhecido para a linguagem em questão.",
            "Tentando todas as entradas possíveis.",
            "Executando a MT infinitamente.",
            "Usando apenas a fita da MT."
        ],
        "answer": 0,
        "difficulty": "hard"
    },
    {
        "question": "O que é a MT de Turing Universal e por que é importante?",
        "options": [
            "É a MT que pode simular qualquer MT; importante para formalizar computabilidade.",
            "É a MT que ignora outras MTs.",
            "É a MT que não aceita nenhuma palavra.",
            "É a MT que aceita todas as palavras sem regras."
        ],
        "answer": 0,
        "difficulty": "hard"
    },
    {
        "question": "Explique o conceito de diagonalização de Cantor em computabilidade.",
        "options": [
            "É usado para provar que certos conjuntos ou problemas são não computáveis, como o Halting Problem.",
            "É um método para organizar a fita da MT.",
            "É uma regra de transição da MT.",
            "É uma técnica de ordenação."
        ],
        "answer": 0,
        "difficulty": "hard"
    },
    {
        "question": "O que significa uma função ser computável?",
        "options": [
            "Existe uma MT que, dada a entrada, produz a saída correta e termina.",
            "É uma função que não pode ser calculada.",
            "É uma função que não termina nunca.",
            "É uma função que depende da sorte."
        ],
        "answer": 0,
        "difficulty": "hard"
    },
    {
        "question": "Qual a diferença entre problemas de decisão e problemas de função?",
        "options": [
            "Problemas de decisão retornam sim/não; problemas de função retornam um valor ou saída complexa.",
            "Problemas de decisão sempre falham.",
            "Problemas de função são sempre indecidíveis.",
            "Não existe diferença prática."
        ],
        "answer": 0,
        "difficulty": "hard"
    },
    {
        "question": "Como a indecidibilidade do Problema da Parada afeta outras linguagens?",
        "options": [
            "Muitas linguagens derivadas do Halting Problem também são indecidíveis.",
            "Todas as linguagens se tornam decidíveis.",
            "Não afeta outras linguagens.",
            "Todas as linguagens se tornam recursivas."
        ],
        "answer": 0,
        "difficulty": "hard"
    },
    {
        "question": "Explique a relação entre MT determinísticas e não-determinísticas.",
        "options": [
            "MT não-determinísticas podem ter múltiplas escolhas; toda MT não-determinística pode ser simulada por uma determinística.",
            "MT determinísticas não podem ser simuladas.",
            "MT não-determinísticas não podem aceitar nenhuma palavra.",
            "MT determinísticas e não-determinísticas são iguais em todos os aspectos."
        ],
        "answer": 0,
        "difficulty": "hard"
    }
]

# 3️⃣ Inserir as cartas no MongoDB
with app.app_context():
    service = CardService(app.db)
    for c in cards:
        service.add_card(c["question"], c["options"], c["answer"], c["difficulty"])

print("Cartas adicionadas com sucesso!")
