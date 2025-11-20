// backend/app/static/js/socket.js

// ======================================
// SOCKET.IO - Fluxo Sala de Espera / Tabuleiro
// ======================================

let socket = null;

/**
 * Inicializa o Socket.IO
 * @param {string|null} game_code - Código da sala
 * @param {string|null} username - Nome do jogador
 * @param {number} avatarId - ID do avatar
 * @returns {Socket} socket
 */
export function initSocket(game_code = null, username = null, avatarId = 1) {
    if (!socket) {
        if (typeof io === "undefined") {
            console.error("Socket.IO não foi carregado. Verifique o <script> no HTML!");
            return null;
        }

        socket = io(); // inicializa cliente
        console.log("%cSocket conectado!", "color:#4caf50");

        socket.on("connect", () => console.log("Conectado ao servidor!"));
        socket.on("disconnect", () => console.log("Desconectado do servidor!"));
    }

    // entrar na sala somente após conexão
    if (socket && game_code && username) {
        socket.emit("join_room", {
            token: game_code,
            username: username,
            avatar: avatarId
        });
    }

    return socket;
}

// ====================================================================
// ---------------------- EVENTOS DA SALA DE ESPERA -------------------
// ====================================================================

export function onWaitingRoomUpdate(callback) {
    const s = initSocket();
    if (!s) return;
    s.on("atualizacao_sala", callback);
}

export function playerReady(game_code, username, isReady = true) {
    const s = initSocket();
    if (!s) return;
    s.emit("player_ready", {
        token: game_code,
        username: username,
        ready: isReady
    });
}

// ====================================================================
// ------------------------- INÍCIO DE PARTIDA -------------------------
// ====================================================================

export function onGameStarting(callback) {
    const s = initSocket();
    if (!s) return;
    s.on("game_starting", callback);
}

export function onStartGame(callback) {
    const s = initSocket();
    if (!s) return;
    s.on("iniciar_partida", callback);
}

// ====================================================================
// ----------------------------- TABULEIRO ------------------------------
// ====================================================================

// Atualização geral do jogo (posição dos peões, rodada, pontuação)
export function onGameUpdate(callback) {
    const s = initSocket();
    if (!s) return;
    s.on("atualizacao_jogo", callback);
}

// Quando um jogador deve puxar uma carta
export function onDrawCard(callback) {
    const s = initSocket();
    if (!s) return;
    s.on("puxar_carta_servidor", callback);
}

// Quando o servidor envia a carta puxada
export function onCardReceived(callback) {
    const s = initSocket();
    if (!s) return;
    s.on("carta_enviada", callback);
}

// Movimento do peão no tabuleiro
export function onPawnMove(callback) {
    const s = initSocket();
    if (!s) return;
    s.on("mover_peao", callback);
}

// ====================================================================
// ------------------------- AÇÕES DO JOGADOR ---------------------------
// ====================================================================

// Jogador solicita puxar carta
export function drawCard(game_code, username) {
    const s = initSocket();
    if (!s) return;

    s.emit("puxar_carta", {
        game_code: game_code,
        nome: username
    });
}

// Jogador envia resposta
export function sendAnswer(game_code, player, respostaIndex, cardObj) {
    const s = initSocket();
    if (!s) return;

    s.emit("responder_pergunta", {
        game_code: game_code,
        player: {
            id: player.id,
            nome: player.username,
            avatar_id: player.avatar_id,
            avatar_url: player.avatar_url
        },
        resposta: respostaIndex,
        carta: cardObj
    });
}

// ====================================================================
// ------------------------------ ERROS --------------------------------
// ====================================================================

export function onSocketError(callback) {
    const s = initSocket();
    if (!s) return;
    s.on("error", callback);
}

console.log("%csocket.js carregado!", "color:#2196f3");
