# backend/app/sockets/events.py
def socketio_events(socketio):
    
    @socketio.on("connect")
    def on_connect():
        print("Cliente conectado!")
    
    @socketio.on("disconnect")
    def on_disconnect():
        print("Cliente desconectado!")
    
    @socketio.on("ping")
    def handle_ping(data):
        print("Recebido:", data)
        socketio.emit("pong", {"msg": "pong do servidor"})
