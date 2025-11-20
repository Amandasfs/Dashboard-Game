// backend/app/static/js/utils.js
// ======================================
// UTILIDADES
// ======================================

// Lê parâmetros da URL
export function getQueryParam(param) {
    const params = new URLSearchParams(window.location.search);
    return params.get(param);
}

// Redirecionar com parâmetros
export function goTo(url, params = {}) {
    const qs = new URLSearchParams(params).toString();
    window.location.href = qs ? `${url}?${qs}` : url;
}

// Exibir erros
export function showError(id, msg) {
    const el = document.getElementById(id);
    if (el) el.textContent = msg;
}

console.log("%cutils.js carregado!", "color:#2196f3");
