from flask import Flask
from .main import main as main_blueprint

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'
    app.register_blueprint(main_blueprint, url_prefix='/main')
    return app
