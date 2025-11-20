# backend/app/services/card_service.py
class CardService:
    def __init__(self, db):
        self.collection = db.cards  # coleção MongoDB

    # Antes: def add_card(self, question, answer, difficulty):
    def add_card(self, question, options, answer, difficulty):
        card = {
            "question": question,
            "options": options,
            "answer": answer,
            "difficulty": difficulty
        }
        result = self.collection.insert_one(card)
        card["_id"] = str(result.inserted_id)
        return card
