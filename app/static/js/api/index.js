// ======================================
// INDEX.JS — AGREGA E REEXPORTA TUDO
// ======================================

// Configurações / constantes
export { API } from "../config.js";

// Utils
export {
    getQueryParam,
    goTo,
    showError
} from "../utils.js";

// Auth
export {
    loginUser,
    registerUser
} from "../auth.js";

// Game
export {
    createGame,
    joinGame
} from "../game.js";

// Socket
export {
    initSocket,
    sendAnswer,
    onGameUpdate,
    onSocketError
} from "../socket.js";

console.log("%cindex.js carregado!", "color:#ff9800");
