from flask import Flask


app = Flask(__name__)
app.register_blueprint( url_prefix='/main')
