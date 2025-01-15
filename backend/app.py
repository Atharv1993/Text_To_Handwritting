from flask import Flask, request, jsonify,send_file
from flask_cors import CORS
import os

#Text Extraction functions
from PyPDF2 import PdfReader
from docx import Document

from PIL import Image, ImageDraw, ImageFont
import tempfile


app = Flask(__name__)
CORS(app)  # Enable cross-origin requests
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Basic Running
@app.route('/')
def home():
    return "File Upload and Text Extraction API is Running"


#-Upload Files Endpoint---------------------------------------------------------------------------------------------------------------
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for upload'}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Extract text from file
        extracted_text = extract_text_from_file(file_path)
        #return jsonify({'message': 'File uploaded successfully', 'text': extracted_text,"filename": file.filename}), 200
        return generate_handwritten_image(extracted_text,file.filename)
        


def extract_text_from_file(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_word(file_path)
    else:
        return "Unsupported file format"

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_word(file_path):
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text


#-Generate a Handwritten Document ---------------------------------------------------------------------------------------------------------------
# Path to the handwriting font
HANDWRITING_FONT = r'D:\pjts\HandWriting\HandWriting_Font\QEDavidReid.ttf'

# Endpoint to generate handwritten image
# @app.route('/generate', methods=['POST'])
def generate_handwritten_image(text,fname):
    try:
        # Get text from the request
        # data = request.get_json()
        # text = data.get('text', '')
        if not text:
            return jsonify({"error": "The input text is empty."}), 400
        
        # Generate the handwritten image
        image = create_handwriting_image(text)

        # Save the image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            temp_path = tmp_file.name
            image.save(temp_path)

        # Send the file to the client
        response = send_file(temp_path, mimetype='image/png',as_attachment=True, 
                             download_name="handwritten.png")
        
        # Remove the temporary file after sending
        @response.call_on_close
        def cleanup():
            os.remove(temp_path)

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Function to create handwriting image
def create_handwriting_image(text, width=1000, line_height=50, line_spacing=10):
    # Create an initial blank image with a white background
    img = Image.new('RGB', (width, 1000), color='white')  # Start with a larger height
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(HANDWRITING_FONT, size=32)
    except IOError:
        raise Exception("Handwriting font file not found or invalid. Make sure the path is correct.")

    lines = []
    for raw_line in text.split('\n'):  # Split text into lines on newline characters
        current_line = ""
        if raw_line == "":
            lines.append(current_line)
            continue
        for word in raw_line.split():  # Handle each word in the line
            test_line = f"{current_line} {word}".strip()
            text_width, text_height = draw.textbbox((0, 0), test_line, font=font)[2:4]
            if text_width <= width - 20:  # 20-pixel padding
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

    # Adjust image height based on total content
    total_height = len(lines) * (line_height + line_spacing)
    if total_height > img.height:
        img = img.resize((width, total_height), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img)

    # Render text onto the image
    y = 10
    for line in lines:
        if line == "":
            y += line_height  # Extra spacing for empty lines (newline)
        else:
            draw.text((10, y), line, font=font, fill='black')  # Replace tab with spaces
            y += line_height + line_spacing

    return img

if __name__ == '__main__':
    app.run(debug=True)
