import { initSocket } from "/static/js/socket.js";

const token = new URLSearchParams(window.location.search).get("token");
const username = localStorage.getItem("username") || "Jogador";
const avatar_id = parseInt(localStorage.getItem("selectedAvatar") || 1);

if (!token || !username) window.location.href = "/home";

// ELEMENTOS
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
let partidaIniciada = false;
let cartaAtual = null;

// ==================== TABULEIRO ====================
export function createBoard() {
    boardEl.innerHTML = "";
    for(let i=0;i<64;i++){
        const cell = document.createElement("div");
        cell.classList.add("cell");
        cell.dataset.pos = i;
        boardEl.appendChild(cell);
    }
}
createBoard();

// ==================== SOCKET ====================
const socket = initSocket(token, username, avatar_id);

function animatePawn(pawn, fromCell, toCell){
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

function renderBoard(state){
    gameState = state;
    turnInfo.textContent = `Vez de: ${state.turno_atual}`;

    const oldPawns = document.querySelectorAll(".pawn");
    oldPawns.forEach(p=>p.remove());

    state.players.forEach((p,i)=>{
        const cell = document.querySelector(`[data-pos="${p.posicao}"]`);
        if(!cell) return;

        const pawn = document.createElement("div");
        pawn.classList.add("pawn", playerColors[i]);
        pawn.style.background = `url('/static/img/avatars/avatar_${p.avatar_id}.png') center/cover`;

        const name = document.createElement("div");
        name.classList.add("player-name");
        name.textContent = p.nome;
        pawn.appendChild(name);

        // Animação de movimento
        animatePawn(pawn, boardEl, cell);

        cell.appendChild(pawn);
    });
}

function updatePlayersList(players){
    playersList.innerHTML = "";
    players.forEach((p,i)=>{
        const div = document.createElement("div");
        div.classList.add("player-item");
        div.innerHTML = `<div class="player-avatar" style="border-color:${["#ff6b6b","#6aff6a","#00d0ff","#ffd700"][i]};background:url('/static/img/avatars/avatar_${p.avatar_id}.png') center/cover"></div>
        <div class="player-details"><div class="player-name-info">${p.nome}</div><div class="player-position">Posição: ${p.posicao+1}</div></div>`;
        playersList.appendChild(div);
    });
}

// ==================== CARTAS ====================
drawCardBtn.addEventListener("click",()=>{
    socket.emit("puxar_carta",{token,nome:username});
    drawCardBtn.disabled = true;
});

socket.on("nova_carta",(data)=>{
    cartaAtual = data;
    cardModal.style.display = "block";
    cardQuestion.textContent = data.question || "Pergunta não disponível";
    cardOptions.innerHTML = "";
    (data.options||[]).forEach((opt,i)=>{
        const btn = document.createElement("button");
        btn.textContent = opt;
        btn.className = "btn-pixel";
        btn.onclick = ()=>{
            socket.emit("responder_pergunta",{token,player:username,resposta:i,carta:cartaAtual});
            cardModal.style.display = "none";
            drawCardBtn.disabled = false;
        };
        cardOptions.appendChild(btn);
    });
});

closeCard.addEventListener("click",()=>{ cardModal.style.display="none"; });

// ==================== SOCKET UPDATES ====================
socket.on("update_game",(state)=>{ renderBoard(state); updatePlayersList(state.players); });
socket.on("game_started",(state)=>{ partidaIniciada=true; renderBoard(state); updatePlayersList(state.players); });
