// ======================================
// API BASE URL
// ======================================

const API = {
    LOGIN: "/api/auth/login",
    REGISTER: "/api/auth/register",
    CREATE_GAME: "/api/game/create",
    JOIN_GAME: "/api/game/join"
};

// ======================================
// UTILIDADES GLOBAIS
// ======================================

// Lê parâmetros da URL
function getQueryParam(param) {
    const params = new URLSearchParams(window.location.search);
    return params.get(param);
}

// Redirecionar com parâmetros
function goTo(url, params = {}) {
    const qs = new URLSearchParams(params).toString();
    window.location.href = qs ? `${url}?${qs}` : url;
}

// Exibir erros na UI
function showError(id, msg) {
    const el = document.getElementById(id);
    if (el) el.textContent = msg;
}

console.log("%capi.js carregado!", "color:#2196f3");
