from flask import Flask, render_template, request, jsonify
from rembg import remove
from PIL import Image
import io
import os
import base64

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed'

# Ensure folders exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Save the uploaded image
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(input_path)
        
        # Open the image and remove the background
        with open(input_path, 'rb') as i:
            input_image = i.read()
        
        output_image = remove(input_image)
        
        # Save the processed image
        img = Image.open(io.BytesIO(output_image))
        processed_filename = f"processed_{file.filename.rsplit('.', 1)[0]}.png"
        output_path = os.path.join(PROCESSED_FOLDER, processed_filename)
        img.save(output_path, format='PNG')

        # Convert the processed image to base64
        with open(output_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

        # Return the processed image data
        return jsonify({
            'message': 'Image processed successfully',
            'image': encoded_string,
            'filename': processed_filename
        })

if __name__ == '__main__':
    app.run(debug=True)