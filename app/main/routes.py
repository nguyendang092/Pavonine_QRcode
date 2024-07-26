from flask import Flask, render_template, session, send_file
from datetime import datetime, timezone, timedelta
import pytz
import qrcode
from io import BytesIO
from . import main


@main.route('/')
def index():
    qr_creation_time = session.get('qr_creation_time', None)
    return render_template('index.html', qr_creation_time=qr_creation_time)

@main.route('/about')
def about():
    return render_template('about.html')


def generate_qr(url, timestamp):
    qr_content = f"{url},{timestamp}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

@main.route('generate_qr_download')
def generate_qr_download():
    timestamp = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    formatted_timestamp = timestamp.strftime("%Y-%m-%d_%H_%M_%S")
    url = "https://myprojectflask-f4e65bcb2a22.herokuapp.com/main/"
    image = generate_qr(url, formatted_timestamp)
    session['creation_qr'] = formatted_timestamp
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    file_name = f'Pavonine_QRcode_{timestamp.strftime("%Y-%m-%d_%H-%M-%S")}.png'
    return send_file(buffer, mimetype='image/png', as_attachment=True, download_name=file_name)

@main.route('/scan_qr')
def scan_qr():
    creation_time_str = session.get('creation_time')
    if not creation_time_str:
        return render_template('index.html')
    
    creation_time = datetime.fromisoformat(creation_time_str)
    current_time = datetime.now(timezone.utc)
    time_diff = current_time - creation_time

    if time_diff > timedelta(hours=12):
        message = "Thành công! Thời gian quét lớn hơn 12 giờ so với thời gian tạo mã."
    else:
        message = "Thất bại! Thời gian quét chưa đủ 12 giờ so với thời gian tạo mã."

    return render_template('index.html', message=message)