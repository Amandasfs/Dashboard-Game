// backend/app/static/js/tabuleiro.js
import { 
    initSocket, 
    drawCard as socketDrawCard, 
    sendAnswer, 
    onGameUpdate, 
    onCardReceived, 
    onStartGame 
} from "/static/js/socket.js";

// ==================== VARIÁVEIS ====================
const token = new URLSearchParams(window.location.search).get("token");
const username = localStorage.getItem("username") || "Jogador";
const avatar_id = parseInt(localStorage.getItem("selectedAvatar") || 1);

if (!token || !username) window.location.href = "/home";

// ELEMENTOS DO DOM
const boardEl = document.getElementById("board");
const cardText = document.getElementById("cardText");
const drawCardBtn = document.getElementById("drawCardBtn");
const turnInfo = document.getElementById("turnInfo");
const playersList = document.getElementById("playersList");
const cardModal = document.getElementById("cardModal");
const cardQuestion = document.getElementById("cardQuestion");
const cardOptions = document.getElementById("cardOptions");
const closeCard = document.getElementById("closeCard");

const playerColors = ["player1","player2","player3","player4"];
let gameState = null;
let cartaAtual = null;

// ==================== TABULEIRO ====================
export function createBoard() {
    boardEl.innerHTML = "";
    for (let i = 0; i < 64; i++) {
        const cell = document.createElement("div");
        cell.classList.add("cell");
        cell.dataset.pos = i;

        if (i === 0) cell.classList.add("start");
        if (i === 63) cell.classList.add("end");

        boardEl.appendChild(cell);
    }
}
createBoard();

// ==================== SOCKET ====================
const socket = initSocket(token, username, avatar_id);

// ==================== FUNÇÕES ====================
function animatePawn(pawn, fromCell, toCell) {
    if (!fromCell || fromCell === toCell) {
        toCell.appendChild(pawn);
        pawn.style.transform = "translate(-50%, -50%)";
        return;
    }

    const fromRect = fromCell.getBoundingClientRect();
    const toRect = toCell.getBoundingClientRect();
    const dx = toRect.left - fromRect.left;
    const dy = toRect.top - fromRect.top;

    pawn.style.transition = "transform 0.5s ease";
    pawn.style.transform = `translate(${dx}px, ${dy}px)`;
    setTimeout(() => {
        toCell.appendChild(pawn);
        pawn.style.transition = "none";
        pawn.style.transform = "translate(-50%, -50%)";
    }, 500);
}

function renderBoard(state) {
    gameState = state;
    turnInfo.textContent = `Vez de: ${state.turno_atual}`;

    document.querySelectorAll(".pawn").forEach(p => p.remove());

    state.players.forEach((p, i) => {
        const cell = document.querySelector(`[data-pos="${p.posicao}"]`);
        if (!cell) return;

        const pawn = document.createElement("div");
        pawn.classList.add("pawn", playerColors[i]);
        pawn.style.background = `url('/static/img/avatars/avatar_${p.avatar_id}.png') center/cover`;

        const name = document.createElement("div");
        name.classList.add("player-name");
        name.textContent = p.nome;
        pawn.appendChild(name);

        const prevCell = p.posicaoAnterior != null ? document.querySelector(`[data-pos="${p.posicaoAnterior}"]`) : null;
        animatePawn(pawn, prevCell, cell);

        cell.appendChild(pawn);
    });

    updatePlayersList(state.players);
}

function updatePlayersList(players) {
    playersList.innerHTML = "";
    players.forEach((p, i) => {
        const div = document.createElement("div");
        div.classList.add("player-item");
        div.innerHTML = `
        <div class="player-avatar" style="border-color:${["#ff6b6b","#6aff6a","#00d0ff","#ffd700"][i]};background:url('/static/img/avatars/avatar_${p.avatar_id}.png') center/cover"></div>
        <div class="player-details">
            <div class="player-name-info">${p.nome}</div>
            <div class="player-position">Posição: ${p.posicao+1}</div>
        </div>`;
        playersList.appendChild(div);
    });
}

// ==================== CARTAS ====================
drawCardBtn.addEventListener("click", () => {
    drawCardBtn.disabled = true;
    cardText.textContent = "Tentando puxar carta...";
    socketDrawCard(token, username);
});

onCardReceived((data) => {
    cartaAtual = data;
    cardText.textContent = data.question || "Pergunta não disponível";

    cardOptions.innerHTML = "";
    (data.options || []).forEach((opt, i) => {
        const btn = document.createElement("button");
        btn.textContent = opt;
        btn.className = "btn-pixel";
        btn.onclick = () => {
            sendAnswer(token, { nome: username, avatar_id }, i, cartaAtual);
            cardModal.classList.remove("active");
            drawCardBtn.disabled = false;
        };
        cardOptions.appendChild(btn);
    });

    cardModal.classList.add("active");
});

closeCard.addEventListener("click", () => {
    cardModal.classList.remove("active");
    drawCardBtn.disabled = false;
});

// ==================== SOCKET UPDATES ====================
onGameUpdate(renderBoard);

onStartGame((state) => {
    renderBoard(state);
});
