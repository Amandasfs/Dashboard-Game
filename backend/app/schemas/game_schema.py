# backend/app/schemas/game_schema.py
from pydantic import BaseModel
from typing import Optional, List


class PlayerSchema(BaseModel):
    name: str
    avatar: int
    posicao: int = 0
    pontos: int = 0
    vida_extra: int = 0


class CasaTabuleiroSchema(BaseModel):
    index: int
    tipo: str   # normal, 10pontos, 20pontos, vida_extra


class CartaSchema(BaseModel):
    _id: str
    question: str
    options: list
    difficulty: str
    time: Optional[int] = 60


class PartidaSchema(BaseModel):
    host: str
    players: List[PlayerSchema]
    max_jogadores: int
    duracao: int
    start_time: Optional[str] = None
    turno: int = 0
    finished: bool = False
    tabuleiro: List[CasaTabuleiroSchema]
    carta_atual: Optional[CartaSchema] = None
