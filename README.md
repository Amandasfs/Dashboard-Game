# 🎮 Board Algorithm Game

**Desafie suas habilidades de programação e algoritmos em um jogo de tabuleiro gamificado!**

## 📋 Sobre o Projeto

Jogo interativo de tabuleiro para praticar técnicas de programação e resolução de problemas algorítmicos.

## 🚀 Status do Projeto

**Fase 1 - Concluída ✅**
- Estrutura básica do backend com FastAPI
- Rota de health check (`/health`)
- Sistema de plugins preparado
- Documentação interativa da API

## 🛠️ Tecnologias

- **Python 3.11+**
- **FastAPI** - Framework web moderno
- **Uvicorn** - Servidor ASGI
- **Pluggy** - Sistema de plugins

## 💻 Como Executar

### Pré-requisitos
- Python 3.11 ou superior

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/board-algorithm-game.git
cd board-algorithm-game
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .\.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
Acesso
API: http://127.0.0.1:8000

Documentação: http://127.0.0.1:8000/docs

Health Check: http://127.0.0.1:8000/health
