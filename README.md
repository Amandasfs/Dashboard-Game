# Board Algorithm Game

**Projeto:** Jogo de tabuleiro gamificado para praticar técnicas de programação e algoritmos.

## Fase 1 — Início e Preparação
Objetivo: estabelecer a estrutura mínima da aplicação e expor a rota `/health`.

### Tecnologias (Fase 1)
- Python 3.11+
- FastAPI (backend)
- Uvicorn (ASGI server)
- Pluggy (sistema de plugins - preparado)
- Streamlit (frontend — fase 2)
- supabase (banco — fases posteriores)
- Docker (fase 5)

### Como rodar localmente
1. Crie virtualenv e ative:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

### Faze 2- Logica e implementação inicial.
acesso ao docs depois de rodar localmente, use o doc pra testar a funcionalidade:
http://127.0.0.1:8000/docs#/

Os .json pra teste do backend está em testes.txt copie do body das requisições e teste as rotas