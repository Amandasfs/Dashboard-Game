from fastapi import FastAPI
from api import launch, score

app = FastAPI(title="Board Algorithm Game - Backend", version="0.1.0")

@app.get("/")
async def root():
    return {
        "message": "Bem-vindo ao jogo de tabuleiro!",
        "routes": {
            "health": "/health",
            "launch": "/launch"
        }
    }

@app.get("/health") # Fase 1: Rota /health
async def health():
    return {"status": "ok"}

# Entrega fase 2: Rotas pra acessar o launch e o /score
app.include_router(launch.router, prefix="/launch", tags=["Launch"])
app.include_router(score.router, prefix="/score", tags=["Score"])
