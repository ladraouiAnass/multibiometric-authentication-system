from flask import Flask, render_template, request, jsonify
import sys
import os
current_dir = os.path.dirname(__file__)
config_dir = os.path.join(current_dir, '../../')
sys.path.append(config_dir)
from deploy.decision import *


app = Flask(__name__)

@app.route('/msg')
def index(msg):
    return render_template('index.html',message=msg)

@app.route('/save_image', methods=['POST'])
def save_image():
    try:
        # Get image data from request
        image_data = request.json['imageData']

        # Save image to file
        with open('captured_image.png', 'wb') as f:
            f.write(image_data.split(',')[1].decode('base64'))

        return jsonify({'success': True, 'message': 'Image saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/welcome/name')
def welcome(nom):
    return render_template("index1.html",name=nom)
    
@app.route("/login")
def login():
    verification = initializemodeles()
    persons = process_faces()
    if len(persons)!=0:
        allow,speaker = process_voice(verification)
        if allow:
            if speaker!="Unknown" and speaker in persons:
                return welcome(speaker)
    else:
        message = "can't connect !"
        return index(message)
    


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
