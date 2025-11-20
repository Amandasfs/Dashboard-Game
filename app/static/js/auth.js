import { API } from "./config.js";

// ======================================
// AUTH (com suporte a avatar)
// ======================================

export async function loginUser(username, password) {
    const response = await fetch(API.LOGIN, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    if (!response.ok) throw data.error || "Erro no login";

    return data; // já contém id, username, avatar_id e avatar_url
}

export async function registerUser(username, password) {
    const response = await fetch(API.REGISTER, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    if (!response.ok) throw data.error || "Erro no registro";

    return data;
}

console.log("%cauth.js carregado!", "color:#2196f3");
