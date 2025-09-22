from pydantic import BaseModel
from typing import List, Dict, Optional
from models.player import Player


class Card(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    move_spaces: int


class GameSession(BaseModel):
    session_code: str # Sessão que inicia a partida e permite acesso a outros jogadores
    players: List[Player] 
    total_houses: int = 60
    current_turn: Optional[int] = None  # ID do jogador atual
    players_order: List[int] = []  # IDs na ordem de jogo
    positions: Dict[int, int] = {}  # ID do jogador -> posição no tabuleiro
    deck: List[Card] = []  # Cartas embaralhadas
