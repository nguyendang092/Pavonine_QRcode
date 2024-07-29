from flask import Flask, render_template, session, send_file,request,redirect
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
    qr_content = f"{url}?data={timestamp}"
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
    url = "https://myprojectflask-f4e65bcb2a22.herokuapp.com/main/scan_qr"
    image = generate_qr(url, formatted_timestamp)
    session['creation_qr'] = formatted_timestamp
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    file_name = f'Pavonine_QRcode_{timestamp.strftime("%Y-%m-%d_%H-%M-%S")}.png'
    return send_file(buffer, mimetype='image/png', as_attachment=True, download_name=file_name)

@main.route('/scan_qr')
def scan_qr():
    data = request.args.get('data')
    if data:
        # Ví dụ: chuyển đổi dữ liệu thành thời gian hoặc URL
        qr_creation_time = data  # hoặc parse data nếu cần
        redirect_url = f"https://myprojectflask-f4e65bcb2a22.herokuapp.com/main/scan_qr?timestamp={qr_creation_time}"
        return redirect(redirect_url)
    else:
        message = "No data in URL."
        return render_template('scan_qr.html', message=message)
