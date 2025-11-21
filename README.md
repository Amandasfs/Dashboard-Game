# Quiz: Você vs Bot

Um jogo de perguntas e respostas baseado em **Máquinas de Turing**, onde o usuário compete contra um bot que tem 50% de chance de acertar cada pergunta.

---

## 🧠 Lógica do Jogo

O jogo segue a seguinte lógica:

1. Cada jogador (usuário e bot) responde a uma pergunta por turno.
2. As perguntas têm **dificuldade**: `easy`, `medium` e `hard`.
3. Cada dificuldade tem **pontos diferentes**:
   - Easy: 10 pontos  
   - Medium: 20 pontos  
   - Hard: 30 pontos
4. O usuário tem **3 vidas**.  
   - Resposta errada: perde metade dos pontos da pergunta e 1 vida.  
   - Não responder (timeout): considerado erro.
5. O bot escolhe aleatoriamente uma pergunta e acerta **50% das vezes**.
6. O jogo termina quando:
   - Um jogador atinge **100 pontos** (vitória imediata).  
   - O usuário perde todas as vidas (vitória do bot).  
   - Todas as perguntas são respondidas (vence quem tiver mais pontos).

---

## 🎯 Regras de Negócio

- Perguntas não se repetem no mesmo jogo.
- O turno do usuário vem **primeiro**; o bot joga em seguida.
- O score e as vidas do usuário são persistidos em sessão (Flask `session`).
- O jogo fornece **feedback visual** de acertos e erros:
  - Verde para respostas corretas.
  - Vermelho/desabilitado para respostas incorretas.
- O bot exibe:
  - Pergunta jogada
  - Alternativa escolhida
  - Resultado (Acertou / Errou)
  - Pontos ganhos

---

## 💻 Estrutura do Projeto

quiz-bot/
├─ app.py # Backend Flask
├─ static/
│ ├─ index.html # Frontend
│ ├─ style.css # Estilos
│ └─ script.js # Lógica do jogo
├─ requirements.txt # Dependências Python
└─ README.md


---

## 🚀 Como Rodar a Aplicação

### Pré-requisitos

- Python 3.10+  
- pip  

### Passos

1. Clone o repositório:

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd quiz-bot

Crie um ambiente virtual e ative:
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt

Rode a aplicação:
python app.py

Acesse em: http://localhost:5000
