from flask import render_template, session, send_file,request,redirect, url_for
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import pytz
import qrcode
import base64
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
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    font_path = "app/static/font/FS PFBeauSansPro-XThinItalic.ttf"
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf",16)
    text = f'Pavonine_QRcode_{timestamp}' 
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    qr_width, qr_height = img.size
    text_position = ((qr_width - text_width) / 2, qr_height - text_height - 10)
    draw.text(text_position, text, font=font, fill='black')
    return img

@main.route('generate_qr_download')
def generate_qr_download():
    timestamp = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    url = "https://myprojectflask-f4e65bcb2a22.herokuapp.com/main/scan_qr"
    qr_name = f'Pavonine_QrCode_{formatted_timestamp}'
    image = generate_qr(url, formatted_timestamp)
    session['creation_qr'] = formatted_timestamp
    session['qr_name'] = qr_name
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    session['qr_image'] = buffer.getvalue()
    return redirect(url_for('main.qr_info'))

@main.route('/qr_info')
def qr_info():
    qr_image = session.get('qr_image')
    creation_time = session.get('creation_qr')
    qr_name = session.get('qr_name')
    print("Creation Time:", creation_time)

    if not qr_image or not creation_time:
        return "QR code not found", 404
    qr_image_base64 = base64.b64encode(qr_image).decode('utf-8')
    return render_template('qr_info.html', qr_image=qr_image_base64, creation_time=creation_time, qr_name=qr_name)

@main.route('/scan_qr')
def scan_qr():
    creation_time_str = session.get('creation_qr')
    scan_time = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    data = request.args.get('data')
    if data:
        creartion_qr = datetime.strptime(creation_time_str,'%Y-%m-%d %H:%M:%S')
        time_diff = scan_time - creartion_qr
        time_diff_hour = time_diff.total_seconds()/3600
        if time_diff_hour > 12:
            message = "Mã QR đã đủ 12 giờ. Vui lòng chuyển công đoạn tiếp theo"
            return render_template('scan_qr.html', message=message)
        else:
            message = "Mã QR chưa đủ 12 giờ. Vui lòng đợi thêm {scan_time} - {creartion_qr}"
    else:
        message = "No data in URL."
        return render_template('scan_qr.html', message=message)
