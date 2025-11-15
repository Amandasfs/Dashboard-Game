# backend/wsgi.py
#!/usr/bin/env python3
from app import create_app
from app.extensions import socketio  # usar extensions

app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
