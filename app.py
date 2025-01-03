import os
import logging
from flask import Flask, request, jsonify, send_file, url_for
import requests
from werkzeug.utils import secure_filename
from flask_cors import CORS
from create_mockups import create_mockups

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    filename='mockup_app.log'
)

# Create Flask application
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'swatches'
MOCKUP_FOLDER = 'mockups'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MOCKUP_FOLDER'] = MOCKUP_FOLDER

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MOCKUP_FOLDER, exist_ok=True)


@app.route("/generate-mockup", methods=["POST"])
def generate_mockup():
    """Handle image uploads and mockup generation"""
    try:
        data = request.get_json()

        if not data or 'image_url' not in data:
            return jsonify({"message": "No image URL provided"}), 400

        image_urls = data['image_url'] if isinstance(
            data['image_url'], list) else [data['image_url']]

        results = create_mockups(image_urls)

        return jsonify({
            "success": True,
            "message": "Image uploaded successfully",
            "data": results
        }), 201

    except RuntimeError as e:
        logging.error(f"Runtime error: {e}")
        return jsonify({"success": False, "message": str(e), "data": None}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"success": False, "message": f"An unexpected error occurred\nError: {e}", "data": None}), 500



# @app.route("/", methods=['GET'])
# def welcome():
#     """Welcome endpoint"""
#     return {
#         "message": "Welcome to the Mockup Generator API",
#         "available_endpoints": [
#             "/upload-images",
#             "/images",
#             "/html",
#             "/upload"
#         ]
#     }


# @app.route("/upload-images", methods=['POST'])
# def upload_images():
#     """Handle image uploads and mockup generation"""
#     try:
#         # Check if images are present
#         if 'images' not in request.files:
#             return {"message": "No file part"}, 400

#         images = request.files.getlist('images')
#         image_urls = []
#         image_names = []

#         # Process each uploaded image
#         for image in images:
#             if image.filename == '':
#                 return {"message": "No selected file"}, 400

#             filename = secure_filename(image.filename)
#             image_names.append(filename)

#             # Save uploaded image
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             image.save(file_path)

#             # Generate image URL
#             image_urls.append(
#                 url_for('get_image', filename=filename, _external=True))

#         # Process mockups concurrently
#         processing_results = create_mockups(image_names)

#         return {
#             "message": "Images uploaded and processed successfully",
#             "image_urls": image_urls,
#             "processing_results": processing_results
#         }

#     except Exception as e:
#         logging.error(f"Upload error: {e}")
#         return {"message": f"Processing error: {str(e)}"}, 500


# @app.route('/images')
# def get_images():
#     """Retrieve generated mockup images"""
#     images = []

#     # Check if mockups directory exists
#     if os.path.exists(app.config['MOCKUP_FOLDER']):
#         for filename in os.listdir(app.config['MOCKUP_FOLDER']):
#             if os.path.isfile(os.path.join(app.config['MOCKUP_FOLDER'], filename)):
#                 image_url = url_for(
#                     'get_image', filename=filename, _external=True)
#                 images.append(image_url)

#     return jsonify({"images": images})


# @app.route('/images/<filename>')
# def get_image(filename):
#     """Serve individual mockup image"""
#     file_path = os.path.join(app.config['MOCKUP_FOLDER'], filename)

#     # Check if file exists
#     if not os.path.exists(file_path):
#         return {"message": "Image not found"}, 404

#     return send_file(file_path)


# @app.route('/html')
# def get_html():
#     """Serve HTML gallery page"""
#     return send_file('index.html')


# @app.route('/upload')
# def get_upload():
#     """Serve upload page"""
#     return send_file('upload_images.html')

# Main application execution
if __name__ == '__main__':
    print("Mockup API is running on http://localhost:8000")
    app.run(debug=True, host='0.0.0.0', port=8000)
