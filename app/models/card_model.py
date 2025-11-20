# backend/app/models/card_model.py
class CardModel:
    def __init__(self, question, options, answer, difficulty):
        self.question = question
        self.options = options
        self.answer = answer
        self.difficulty = difficulty
