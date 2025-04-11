import os
from flask import render_template, session, request, redirect, url_for, Blueprint
from datetime import datetime
from PIL import ImageDraw, ImageFont, Image
import pytz
from pathlib import Path
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

def generate_qr(url, timestamp, model, quantity):
    from PIL import Image, ImageDraw, ImageFont
    import qrcode

    canvas_width, canvas_height = 645, 645  # tăng chiều cao thêm
    qr_size = 300

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
    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)

    # Tạo canvas
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    qr_position = ((canvas_width - qr_size) // 2, 10)
    canvas.paste(qr_img, qr_position)

    # In text dưới QR
    draw = ImageDraw.Draw(canvas)

    # Font rõ ràng, dễ thấy hơn
    font_path = Path("static/fonts/robo.ttf")
    try:
        font_big = ImageFont.truetype(str(font_path), 26)
    except:
        font_big = ImageFont.load_default()

    model_text = f'Model: {model}'
    quantity_text = f'Số lượng: {quantity}'

    model_bbox = draw.textbbox((0, 0), model_text, font=font_big)
    quantity_bbox = draw.textbbox((0, 0), quantity_text, font=font_big)

    model_x = (canvas_width - (model_bbox[2] - model_bbox[0])) / 2
    quantity_x = (canvas_width - (quantity_bbox[2] - quantity_bbox[0])) / 2

    model_y = qr_position[1] + qr_size + 10
    quantity_y = model_y + 20  # khoảng cách giữa dòng

    draw.text((model_x, model_y), model_text, font=font_big, fill='black')
    draw.text((quantity_x, quantity_y), quantity_text, font=font_big, fill='black')

    return canvas



@main.route('/generate_qr_download')
def generate_qr_download():
    model = request.args.get('model', 'UnknownModel')
    quantity = request.args.get('quantity', '0')

    timestamp = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    formatted_timestamp = timestamp.strftime('%Y%m%d%H%M%S')

    url = f"https://pavocode-0c322a491d91.herokuapp.com/main/scan_qr/{formatted_timestamp}?model={model}&quantity={quantity}"

    qr_name = f'Pavonine_{formatted_timestamp}.png'
    qr_path = os.path.join(UPLOAD_FOLDER, qr_name)

    image = generate_qr(url, formatted_timestamp, model, quantity)
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
    model = request.args.get('model', 'UnknownModel')
    quantity = request.args.get('quantity', '0')

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
            message = "✅ Mã QR đã đủ 12 giờ. Vui lòng chuyển công đoạn tiếp theo.✅ QR 코드 생성 후 12시간이 지났습니다. 다음 단계로 진행해 주세요."
        else:
            remaining_hours = 11 - int(time_diff_hours)
            remaining_minutes = 60 - int(time_diff_minutes % 60)
            message = f"⏳ Mã QR chưa đủ 12 giờ. Vui lòng đợi thêm {remaining_hours} giờ: {remaining_minutes} phút.⏳ QR 코드 생성 후 12시간이 아직 지나지 않았습니다. {remaining_hours}시간 {remaining_minutes}분 더 기다려 주세요."
    except ValueError:
        message = "❌ Mã QR bị lỗi. Vui lòng tạo lại mã QR.❌ QR 코드에 오류가 있습니다. QR 코드를 다시 생성해 주세요."

    return render_template(
    'scan_qr.html',
    message=message,
    data=timestamp,
    model=model,
    quantity=quantity
)

