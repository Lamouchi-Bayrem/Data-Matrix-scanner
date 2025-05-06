from flask import Flask, request, jsonify, render_template, send_from_directory
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename
import uuid
from ultralytics import YOLO
from pyzbar.pyzbar import decode as pyzbar_decode
import pylibdmtx

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Load YOLO model (keep this in your project directory)
MODEL_PATH = 'best.pt'  # Your trained YOLO model
model = YOLO(MODEL_PATH)

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def decode_datamatrix(image):
    """Decode Data Matrix using libdmtx"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    messages = libdmtx.decode(gray)
    results = []
    
    for msg in messages:
        data = msg.data.decode('utf-8')
        rect = msg.rect
        points = [
            (rect.left, rect.top),
            (rect.left + rect.width, rect.top),
            (rect.left + rect.width, rect.top + rect.height),
            (rect.left, rect.top + rect.height)
        ]
        
        results.append({
            'type': 'DATA-MATRIX',
            'data': data,
            'points': points,
            'rect': {
                'left': rect.left,
                'top': rect.top,
                'width': rect.width,
                'height': rect.height
            }
        })
    
    return results

def detect_and_decode(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None, "Could not read the image file"

        # Detect codes with YOLO
        results = model(image)
        detections = []
        
        for result in results:
            for box in result.boxes:
                # Get bounding box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                
                if confidence < 0.5:  # Confidence threshold
                    continue
                
                # Crop the detected code
                cropped = image[y1:y2, x1:x2]
                
                # Decode based on type
                if class_name == 'qr-code':
                    decoded = pyzbar_decode(cropped)
                    code_type = 'QR-CODE'
                elif class_name == 'data-matrix':
                    decoded = decode_datamatrix(cropped)
                    code_type = 'DATA-MATRIX'
                else:
                    continue
                
                if not decoded:
                    continue
                
                # Adjust coordinates to original image
                for obj in decoded:
                    detections.append({
                        'type': code_type,
                        'data': obj['data'],
                        'points': [(x1 + p[0], y1 + p[1]) for p in obj['points']],
                        'rect': {
                            'left': x1 + obj['rect']['left'],
                            'top': y1 + obj['rect']['top'],
                            'width': obj['rect']['width'],
                            'height': obj['rect']['height']
                        },
                        'confidence': confidence
                    })
        
        # Draw on image
        for detection in detections:
            points = np.array(detection['points'], dtype=np.int32)
            cv2.polylines(image, [points], True, (0, 255, 0), 2)
            cv2.putText(image, 
                       f"{detection['type']}: {detection['data']}", 
                       (detection['rect']['left'], detection['rect']['top'] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Save processed image
        processed_filename = f"processed_{str(uuid.uuid4())}.jpg"
        processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
        cv2.imwrite(processed_path, image)
        
        return detections, processed_filename
    
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/decode', methods=['POST'])
def decode_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        results, processed_filename = detect_and_decode(filepath)
        
        if results is None:
            return jsonify({'error': processed_filename}), 500
        
        return jsonify({
            'results': results,
            'processed_image': processed_filename
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/uploads/<filename>')
def serve_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    except FileNotFoundError:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)