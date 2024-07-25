from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models import Record

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    timestamp = data.get('timestamp')

    new_record = Record(timestamp=timestamp)
    db.session.add(new_record)
    db.session.commit()

    return jsonify({"status": "success", "timestamp": timestamp})
