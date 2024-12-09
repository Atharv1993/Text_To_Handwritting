from flask import Flask, request, jsonify
from flask_cors import CORS
import os

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
        return jsonify({'message': 'File uploaded successfully', 'text': extracted_text,"filename": file.filename}), 200




#Text Extraction functions
from PyPDF2 import PdfReader
from docx import Document

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

from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

HANDWRITING_FONT = 'D:\pjts\HandWriting\HandWriting_Font\QEDavidReid.ttf'  
OUTPUT_FOLDER = 'output'
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route('/generate-handwriting', methods=['POST'])
def generate_handwriting():
    try:
        # Get the text from the request
        text = request.json.get('text')
        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Split text into lines
        lines = text.split('\n')

        # Generate handwritten images for each line
        images = []
        for line in lines:
            img = create_handwriting_image(line)
            images.append(img)

        # Combine images into a PDF
        output_path = os.path.join(OUTPUT_FOLDER, 'handwritten_output.pdf')
        save_images_as_pdf(images, output_path)

        return jsonify({"message": "Handwritten document generated successfully", "output_path": output_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

from PIL import Image, ImageDraw, ImageFont

def create_handwriting_image(text, width=800, line_height=50, line_spacing=10):
    """Generate an image of handwritten text with proper wrapping and spacing."""
    
    # Create a new image with white background
    img = Image.new('RGB', (width, 1000), color='white')  # Start with a larger height
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype('D:\pjts\HandWriting\HandWriting_Font\QEDavidReid.ttf', size=48)  # Use your handwriting font
    except IOError:
        raise Exception("Handwriting font file not found or invalid. Make sure 'handwriting.ttf' exists.")

    # Split text into words and wrap it into lines
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        text_width, text_height = draw.textbbox((0, 0), test_line, font=font)[2:4]
        if text_width <= width - 20:  # 20-pixel padding
            current_line = test_line
        else:
            if current_line:  # Avoid adding an empty line
                lines.append(current_line)
            current_line = word

    # Add the last line
    if current_line:
        lines.append(current_line)
    
    # Calculate the total height needed for all lines
    total_height = len(lines) * (line_height + line_spacing)
    
    # Resize the image if needed
    if total_height > img.height:
        img = img.resize((width, total_height), Image.Resampling.LANCZOS)  # Use LANCZOS for resampling
        draw = ImageDraw.Draw(img)
    
    # Draw each line on the image
    y = 10  # Start drawing 10 pixels from the top
    for line in lines:
        draw.text((10, y), line, font=font, fill='black')  # 10-pixel left padding
        y += line_height + line_spacing

    return img


def save_images_as_pdf(images, output_path):
    """Combine images into a PDF."""
    pdf = FPDF()
    for img in images:
        img_path = os.path.join(OUTPUT_FOLDER, 'temp.jpg')
        img.save(img_path)

        # Add image to PDF
        pdf.add_page()
        pdf.image(img_path, x=10, y=10, w=190)  # Adjust positioning and size as needed
        os.remove(img_path)

    pdf.output(output_path)




if __name__ == '__main__':
    app.run(debug=True)
