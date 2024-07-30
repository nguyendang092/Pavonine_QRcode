import os
from flask import render_template, session, request, redirect, url_for, Blueprint
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import pytz
import qrcode
import base64
from io import BytesIO
from . import main
import urllib.parse

UPLOAD_FOLDER = 'path/to/storage'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@main.route('/')
def index():
    qr_creation_time = session.get('qr_creation_time', None)
    return render_template('index.html', qr_creation_time=qr_creation_time)

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
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    timestamp = url.split('data=')[-1]
    text = f'Pavonine_QRcode_{timestamp}' 
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    qr_width, qr_height = img.size
    text_position = ((qr_width - text_width) / 2, qr_height - text_height - 10)
    draw.text(text_position, text, font=font, fill='black')
    return img

@main.route('/generate_qr_download')
def generate_qr_download():
    timestamp = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    formatted_timestamp = timestamp.strftime('%Y%m%d%H%M%S')
    name_qrcode = timestamp.strftime('%Y_%m_%d %H_%M_%S')
    url = f"https://myprojectflask-f4e65bcb2a22.herokuapp.com/main/scan_qr/{formatted_timestamp}"
    qr_name = f'Pavonine_QrCode_{name_qrcode}.png'
    qr_path = os.path.join(UPLOAD_FOLDER, qr_name)
    image = generate_qr(url)
    image.save(qr_path, format="PNG")

    session['qr_creation_time'] = formatted_timestamp
    session['qr_image_path'] = qr_path
    return redirect(url_for('main.qr_info'))

@main.route('/qr_info')
def qr_info():
    qr_image_path = session.get('qr_image_path')
    creation_time = session.get('qr_creation_time')
    data = request.args.get('data')
    qr_name = os.path.basename(qr_image_path) if qr_image_path else None


    if not qr_image_path or not creation_time:
        return "QR code not found", 404

    with open(qr_image_path, "rb") as img_file:
        qr_image_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    return render_template('qr_info.html', qr_image=qr_image_base64, creation_time=creation_time,qr_name=qr_name, data=data)

@main.route('/scan_qr/<timestamp>')
def scan_qr(timestamp):
    if not timestamp:
        return render_template('scan_qr.html', message="Timestamp is missing in the URL.", data=None)
    scan_time = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    try:
        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        creation_qr = tz.localize(datetime.strptime(timestamp, '%Y%m%d%H%M%S'))
        time_diff = scan_time - creation_qr
        time_diff_hours = time_diff.total_seconds() / 3600
        if time_diff_hours > 12:
            message = "Mã QR đã đủ 12 giờ. Vui lòng chuyển công đoạn tiếp theo"
        else:
            message = f"Mã QR chưa đủ 12 giờ. Vui lòng đợi thêm {12 - time_diff_hours:.2f} giờ"
    except ValueError:
            message = "Invalid timestamp format."
    else:
        message = "No data in URL."
    return render_template('scan_qr.html', message=message, data=timestamp)
