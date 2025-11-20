// backend/app/static/js/game.js
import { API } from "./config.js";

// ======================================
// GAME API (COMPATÍVEL COM AVATARES)
// ======================================

export async function createGame(host, maxPlayers = 4, duracao = 15, modo = "multi") {
    const payload = {
        host: host.username || host.nome || host,
        max_jogadores: maxPlayers,
        duracao: duracao,
        modo: modo
    };

    const response = await fetch(API.CREATE_GAME, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (!response.ok) throw data.error || "Erro ao criar partida";

    return data;
}

export async function joinGame(gameCode, player) {
    const payload = {
        game_code: gameCode,
        player: {
            id: player.id,
            nome: player.username,
            avatar_id: player.avatar_id,
            avatar_url: player.avatar_url
        }
    };

    const response = await fetch(API.JOIN_GAME, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (!response.ok) throw data.error || "Erro ao entrar na partida";

    return data;
}

console.log("%cgame.js carregado!", "color:#2196f3");
