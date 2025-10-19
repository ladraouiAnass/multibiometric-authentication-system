"""Flask Web Application for Multimodal Biometric Authentication

Provides web interface for facial and voice recognition authentication.
Supports real-time biometric verification with dual-factor authentication.
"""

from flask import Flask, render_template, request, jsonify
import sys
import os
import base64

# Add parent directory to path for imports
current_dir = os.path.dirname(__file__)
config_dir = os.path.join(current_dir, '../../')
sys.path.append(config_dir)

from deploy.decision import initialize_models, process_faces, process_voice

app = Flask(__name__)

@app.route('/msg')
def index(msg):
    """Display main page with message"""
    return render_template('index.html', message=msg)

@app.route('/save_image', methods=['POST'])
def save_image():
    """Save captured image from webcam"""
    try:
        image_data = request.json['imageData']
        # Decode base64 image data
        image_bytes = base64.b64decode(image_data.split(',')[1])
        
        with open('captured_image.png', 'wb') as f:
            f.write(image_bytes)
            
        return jsonify({'success': True, 'message': 'Image saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/welcome/<name>')
def welcome(name):
    """Welcome page for authenticated users"""
    return render_template("index1.html", name=name)

@app.route("/login")
def login():
    """Main authentication endpoint - combines face and voice recognition"""
    try:
        # Initialize voice recognition model
        verification = initialize_models()
        
        # Process facial recognition
        recognized_faces = process_faces()
        
        if recognized_faces:
            # Process voice recognition
            voice_allowed, speaker = process_voice(verification)
            
            if voice_allowed and speaker != "Unknown" and speaker in recognized_faces:
                return welcome(speaker)
            else:
                message = "Authentication failed: Face and voice don't match"
        else:
            message = "No recognized faces detected"
            
        return index(message)
        
    except Exception as e:
        return index(f"Authentication error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
