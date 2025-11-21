// ================================
//  SCRIPT DO JOGO - ATUALIZADO PARA CARD
// ================================
let currentQuestion = null;
let timer = null;
let timeLeft = 15;
let isUserTurn = true;
let playing = false;

const timerEl = document.getElementById("timer");
const questionEl = document.getElementById("questionText");
const optionsBox = document.getElementById("card-options"); // <- alterado
const botTurnBox = document.getElementById("bot-turn-box");
const startBtn = document.getElementById("startBtn");
const messages = document.getElementById("messages");
const userScoreEl = document.getElementById("userScore");
const botScoreEl = document.getElementById("botScore");
const userLivesEl = document.getElementById("userLives");
const difficultyTag = document.getElementById("difficultyTag");

// evento de iniciar
startBtn.addEventListener("click", () => {
    if (!playing) startGame();
    else restartGame();
});

// ================================
//  INÍCIO DE JOGO
// ================================
async function startGame() {
    messages.textContent = "";
    startBtn.disabled = true;
    startBtn.textContent = "Jogando...";
    playing = true;
    isUserTurn = true;

    const res = await fetch("/api/start", { method: "POST" });
    const data = await res.json();

    if (!data.ok) {
        messages.textContent = data.error || "Erro ao iniciar.";
        startBtn.disabled = false;
        startBtn.textContent = "Iniciar Jogo";
        playing = false;
        return;
    }

    updateHud(data.user_score, data.bot_score, data.user_lives);

    currentQuestion = data.question;
    renderQuestion(currentQuestion);
    startTimer();
}

// ================================
//  RENDERIZA PERGUNTA DO TURNO
// ================================
function renderQuestion(q) {
    botTurnBox.style.display = "none";
    optionsBox.innerHTML = "";
    difficultyTag.textContent = q?.difficulty?.toUpperCase() || "—";

    if (!q) {
        questionEl.textContent = "Sem mais perguntas.";
        timerEl.textContent = "";
        startBtn.disabled = false;
        startBtn.textContent = "Reiniciar";
        playing = false;
        return;
    }

    questionEl.textContent = q.question;

    q.options.forEach((op, idx) => {
        const btn = document.createElement("button");
        btn.className = "option-btn";
        btn.textContent = op;
        btn.onclick = () => {
            if (!playing || !isUserTurn) return;
            stopTimer();
            submitAnswer(idx);
        };

        optionsBox.appendChild(btn);
    });
}

// ================================
//  TIMER DE TURNOS
// ================================
function startTimer() {
    stopTimer();
    timeLeft = 15;
    timerEl.textContent = timeLeft;

    timer = setInterval(() => {
        timeLeft--;
        timerEl.textContent = timeLeft;

        if (timeLeft <= 0) {
            stopTimer();
            if (isUserTurn) submitAnswer(-1); // não respondeu = erro
        }
    }, 1000);
}

function stopTimer() {
    if (timer) {
        clearInterval(timer);
        timer = null;
    }
}

// ================================
//  ENVIA RESPOSTA DO USUÁRIO
// ================================
async function submitAnswer(selectedIndex) {
    if (!currentQuestion) return;

    Array.from(optionsBox.children).forEach(b => b.disabled = true);

    const res = await fetch("/api/answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            id: currentQuestion.id,
            selected: selectedIndex
        })
    });

    const data = await res.json();

    if (!data.ok) {
        messages.textContent = data.error;
        playing = false;
        startBtn.disabled = false;
        startBtn.textContent = "Reiniciar";
        return;
    }

    updateHud(data.user_score, data.bot_score, data.user_lives);

    showUserResult(data.user_result);

    // turno do bot
    isUserTurn = false;
    showBotTurn(data.bot_result);

    if (data.game_over) {
        setTimeout(() => endGame(data.winner), 1500);
        return;
    }

    setTimeout(() => {
        currentQuestion = data.next_question;
        isUserTurn = true;
        renderQuestion(currentQuestion);
        startTimer();
    }, 1500);
}

// ================================
//  RESULTADO DO USUÁRIO
// ================================
function showUserResult(result) {
    const btns = document.querySelectorAll(".option-btn");
    if (!btns.length) return;

    const correctIndex = result.correct_index;

    btns[correctIndex]?.classList.add("correct");

    if (!result.correct) {
        btns.forEach(b => b.classList.add("disabled"));
        messages.textContent = "Você errou!";
    } else {
        messages.textContent = "Você acertou!";
    }
}

// ================================
//  TURNO DO BOT
// ================================
function showBotTurn(bot) {
    if (!bot.did_play) {
        botTurnBox.style.display = "none";
        return;
    }

    botTurnBox.style.display = "block";
    botTurnBox.innerHTML = `
        <h3>Vez do Bot</h3>
        <p><strong>Pergunta:</strong> ${escapeHtml(bot.question)}</p>
        <p><strong>Bot escolheu:</strong> ${escapeHtml(bot.options?.[bot.selected] ?? bot.selected)}</p>
        <p><strong>Resultado:</strong> ${bot.correct ? "Acertou 🎯" : "Errou ❌"}</p>
    `;
}

// ================================
//  HUD DO JOGO
// ================================
function updateHud(u, b, l) {
    userScoreEl.textContent = u;
    botScoreEl.textContent = b;
    userLivesEl.textContent = l;
}

// ================================
//  FINAL DO JOGO
// ================================
function endGame(winner) {
    playing = false;
    stopTimer();

    let text = "Fim do jogo — ";

    if (winner === "user") text += "Você venceu! 🎉";
    else if (winner === "bot") text += "O bot venceu 🤖";
    else text += "Empate.";

    messages.textContent = text;
    startBtn.disabled = false;
    startBtn.textContent = "Reiniciar";
}

// ================================
//  UTILITÁRIO
// ================================
function escapeHtml(str) {
    return String(str)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}
