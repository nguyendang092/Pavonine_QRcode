from flask import render_template, send_file
from . import main
import datetime
import qrcode
from io import BytesIO

@main.route('/')
def index():
    login_time = datetime.datetime.now().strftime(f"%Y-%m-%d - %H:%M:%S")
    return render_template('index.html', login_time=login_time)

@main.route('/about')
def about():
    return render_template('about.html')


def generate_qr(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

@main.route('/qr_code')
def qr_code():
    url = "https://myprojectflask-f4e65bcb2a22.herokuapp.com/main/"
    img = generate_qr(url)
    # Lưu hình ảnh vào bộ nhớ
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")