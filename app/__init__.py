from flask import Flask
from .main import main as main_blueprint

app = Flask(__name__)
app.register_blueprint(main_blueprint, url_prefix='/main')
