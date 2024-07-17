# import the necessary packages
from imutils import paths
import numpy as np
import face_recognition
#import argparse
import pickle
import cv2
import os
import subprocess as cmd
import sys
current_dir = os.path.dirname(__file__)
config_dir = os.path.join(current_dir, '../')
sys.path.append(config_dir)
import gui_app.config as cf
from speechbrain.inference.speaker import SpeakerRecognition
import time

def train_faces():
    # our images are located in the dataset folder
    print("[INFO] start processing faces...")
    imagePaths = list(paths.list_images(f"{cf.dataset}"))
    # initialize the list of known encodings and known names
    knownEncodings = []
    knownNames = []
    # loop over the image paths
    for (i, imagePath) in enumerate(imagePaths):
        # extract the person name from the image path
        print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))
        name = imagePath.split(os.path.sep)[-3]
        # load the input image and convert it from RGB (OpenCV ordering) to dlib ordering (RGB)
        image = cv2.imread(imagePath)
        if image is None:
            print(f"Error: Unable to load image {imagePath}")
            continue
        print(f"[INFO] native image shape: {image.shape}, dtype: {image.dtype}")
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # detect the (x, y)-coordinates of the bounding boxes corresponding to each face in the input image
        print(f"[INFO] Converted image shape: {rgb.shape}, dtype: {rgb.dtype}")
        # Check if the image is in the correct format
        if rgb.dtype != 'uint8':
            print(f"Error: Image {imagePath} is not 8-bit")
            continue
        # Ensure the image is contiguous in memory
        rgb = np.ascontiguousarray(rgb)
        print(f"[INFO] Image is contiguous: {rgb.flags['C_CONTIGUOUS']}")
        print("face localisation")
        #rgb = np.ascontiguousarray(rgb[:, :, ::-1])
        boxes = face_recognition.face_locations(rgb, model="cnn")
        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb, boxes)
        # loop over the encodings
        for encoding in encodings:
            # add each encoding + name to our set of known names and encodings
            knownEncodings.append(encoding)
            knownNames.append(name)

    # dump the facial encodings + names to disk
    print("[INFO] serializing encodings...")
    data = {"encodings": knownEncodings, "names": knownNames}
    with open(f"{cf.me2}/deploy/embeddings/encodings_faces.pickle", "wb") as f:
        pickle.dump(data, f)

def initializemodeles():
    verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir=f"{cf.me2}/deploy/pretrained_models/spkrec-ecapa-voxceleb")
    return verification

def get_database_voices():
    database_path = cf.dataset
    users = os.listdir(database_path)
    voices_labeled = []
    for user in users:
        user_path = os.path.join(database_path, user)
        user_voices_path = os.path.join(user_path, "voices")
        user_voices = [os.path.join(user_voices_path, voice) for voice in os.listdir(user_voices_path)]
        voices_labeled.append((user, user_voices))
    return voices_labeled

def prepare_voice_embeddings(voice_path):
    waveform_x = verification.load_audio(voice_path)
    batch_x = waveform_x.unsqueeze(0)
    emb1 = verification.encode_batch(batch_x, None, normalize=False)
    return emb1

def train_voices(verification):
    database_paths = get_database_voices()
    embeddings = []
    for user_voices in database_paths:
        user = user_voices[0]
        user_embeddings = []
        for existing_audio_path in user_voices[1]:
            emb1 = prepare_voice_embeddings(existing_audio_path)
            user_embeddings.append(emb1)
        embeddings.append((user, user_embeddings))
    with open(f"{cf.src}/me2/deploy/embeddings/encodings_voices.pickle", "wb") as f:
        pickle.dump(embeddings, f)

if __name__ == "__main__":
    verification = initializemodeles()
    train_faces()
    print("faces encoded successfully")
    print("training voices...")
    train_voices(verification)
    print("voices encoded successfully")
    remove = cmd.Popen([f"rm {cf.me2}/*.wav"], stdout=cmd.PIPE, stderr=cmd.PIPE, shell=True)
    time.sleep(0.1)

