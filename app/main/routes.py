import os
from flask import render_template, session, request, redirect, url_for, Blueprint
from datetime import datetime
from PIL import ImageDraw, ImageFont, Image
import pytz
import qrcode 
import base64
from . import main
from app import socketio

UPLOAD_FOLDER = 'path/to/storage'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def update_content():
    socketio.emit('refresh', {'data: New content'}, broadcast=True)
    return "Nội dung mới đã được update"

@main.route('/')
def index():
    qr_creation_time = session.get('qr_creation_time', None)
    return render_template('index.html', qr_creation_time=qr_creation_time)

@main.route('/about')
def about():
    return render_template('about.html')

def generate_qr(url):
    from PIL import Image, ImageDraw, ImageFont
    import qrcode

    canvas_width, canvas_height = 945, 591
    qr_size = 472

    # Tạo QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Resize ảnh QR
    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
    # Tạo canvas trắng
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")

    # Dán QR code vào giữa canvas
    qr_position = ((canvas_width - qr_size) // 2, (canvas_height - qr_size) // 2)
    canvas.paste(qr_img, qr_position)

    # Ghi text dưới ảnh
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    # Lấy timestamp từ URL
    try:
        timestamp = url.split('data=')[-1]
    except:
        timestamp = "unknown"

    text = f'Pavonine_QRcode_{timestamp}'
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((canvas_width - text_width) / 2, canvas_height - text_height - 10)

    draw.text(text_position, text, font=font, fill='black')

    return canvas
 

#def create_1x2_qr_layout(url):
    # Generate two QR codes
    qr_image_1 = generate_qr(url)
    qr_image_2 = generate_qr(url)

    # Create an empty image with twice the width of one QR code image to hold both in 1x2 layout
    total_width = qr_image_1.width 
    total_height = qr_image_1.height
    layout_image = Image.new("RGB", (total_width, total_height), "white")

    # Paste both QR images side by side
    layout_image.paste(qr_image_1, (0, 0))
    layout_image.paste(qr_image_2, (qr_image_1.width, 0))

    return layout_image


@main.route('/generate_qr_download')
def generate_qr_download():
    timestamp = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    formatted_timestamp = timestamp.strftime('%Y%m%d%H%M%S')
    url = f"https://pavocode-0c322a491d91.herokuapp.com/main/scan_qr/{formatted_timestamp}"
    qr_name = f'Pavonine_QRcode_{formatted_timestamp}.png'
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
        time_diff_minutes = time_diff.total_seconds() / 60
        if time_diff_hours > 12:
            message = "Mã QR đã đủ 12 giờ. Vui lòng chuyển công đoạn tiếp theo"
        else:
            remaining_hours = 11 - int(time_diff_hours)
            remaining_minutes = 60 - int(time_diff_minutes % 60)
            message = f"Mã QR chưa đủ 12 giờ. Vui lòng đợi thêm {remaining_hours} giờ: {remaining_minutes} phút"
    except ValueError:
            message = "Mã QR bị lỗi. Vui lòng tạo lại mã QR."

    return render_template('scan_qr.html', message=message, data=timestamp)
