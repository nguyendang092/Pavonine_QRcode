from flask import Flask
from flask_socketio import SocketIO # type: ignore

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/main')
    socketio.init_app(app)
    return app,socketio
