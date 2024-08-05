from flask import Flask
from flask_socketio import SocketIO # type: ignore

app = Flask(__name__)
socketio = SocketIO(app)


if __name__ == "__main__":
    socketio.run(app)
