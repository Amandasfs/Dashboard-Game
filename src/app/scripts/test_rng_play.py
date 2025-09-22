# scripts/test_rng_play.py
import requests
import random
import time

BASE_URL = "http://127.0.0.1:8000"
session_code = "AB123"  # ajuste
player_id = 1

# pedir carta
r = requests.post(f"{BASE_URL}/score/deal/{session_code}/{player_id}")
print("Deal:", r.status_code, r.text)

# simula resposta rápida
payload = {"answer": "b", "skip": False}
r2 = requests.post(f"{BASE_URL}/score/answer/{session_code}/{player_id}", json=payload)
print("Answer:", r2.status_code, r2.json())
