from pydantic import BaseModel

class Player(BaseModel):
    name: str
    email: str
    password: str
    pawn: str
