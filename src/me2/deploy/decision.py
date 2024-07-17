from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import os
import sys
current_dir = os.path.dirname(__file__)
config_dir = os.path.join(current_dir, '../')
sys.path.append(config_dir)
import gui_app.config as cf
from scipy.spatial.distance import cosine
from speechbrain.inference.speaker import SpeakerRecognition
import time
import sounddevice as sd
import soundfile as sf
import subprocess as cmd


def initializemodeles():
     verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir=f"{cf.me2}/deploy/pretrained_models/spkrec-ecapa-voxceleb")
     return verification

def process_faces():
    viewed_presons = []
    currentname = "unknown"
    encodingsP = f"{cf.me2}/deploy/embeddings/encodings_faces.pickle"
    print("loading encodings + face detector...")
    with open(encodingsP,"rb") as f:
        data = pickle.load(f)
    vs = VideoStream(cf.camurl).start()
    time.sleep(2.0)
    fps = FPS().start()
    
    start_time = time.time()
    while (time.time() - start_time) < 3:  # Run for 5 seconds
        frame = vs.read()
        frame = imutils.resize(frame, width=500)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(frame)
        encodings = face_recognition.face_encodings(frame, boxes)
        names = []
        for encoding in encodings:
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown"
            if True in matches:
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1
                name = max(counts, key=counts.get)
                if currentname != name:
                    currentname = name
                    viewed_presons.append(currentname)
                    print(currentname)
            names.append(name)
        # for ((top, right, bottom, left), name) in zip(boxes, names):
        #     cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 225), 2)
        #     y = top - 15 if top - 15 > 15 else top + 15
        #     cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, .8, (0, 255, 255), 2)
        # cv2.imshow("Facial Recognition is Running", frame)
        # key = cv2.waitKey(1) & 0xFF
        # if key == ord("q"):
        #     break
        fps.update()
    fps.stop()
    print(" elapsed time: {:.2f}".format(fps.elapsed()))
    print(" approx. FPS: {:.2f}".format(fps.fps()))
    cv2.destroyAllWindows()
    vs.stop()
    return set(viewed_presons)


def takeAudio():
    generated = ""
    fs = 44100 
    duree = 6
    enregistrement = sd.rec(int(duree * fs), samplerate=fs, channels=2)
    sd.wait()
    chemin =f"{cf.me2}/deploy/cachaud/recorded_audio.wav"
    sf.write(chemin, enregistrement, fs)
    return chemin


def prepare_voice_embeddings(voice_path,verification):
    waveform_x = verification.load_audio(voice_path)
    batch_x = waveform_x.unsqueeze(0)
    emb1 = verification.encode_batch(batch_x, None, normalize=False)
    return emb1

def process_voices(names_set,verification):
    print("recording...")
    new_voice_path = takeAudio()
    embexist = prepare_voice_embeddings(new_voice_path,verification)
    max_score = 0
    usr = "Unknown"
    prediction_final = False
    with open(f"{cf.me2}/deploy/embeddings/encodings_voices.pickle", "rb") as f:
          embeddings = pickle.load(f)
    for user_embeddings in embeddings:
            user = user_embeddings[0]
            for emb in user_embeddings[1]:
                score = verification.similarity(emb, embexist)
                prediction = score > 0.10
                if score > max_score and prediction:
                    max_score = score
                    usr = user
                    prediction_final=prediction
    remove = cmd.Popen([f"rm {cf.me2}/*.wav"],stdout=cmd.PIPE,stderr=cmd.PIPE,shell=True)
    time.sleep(0.1)
    remove = cmd.Popen([f"rm {new_voice_path}"],stdout=cmd.PIPE,stderr=cmd.PIPE,shell=True)
    print(usr)
    return prediction_final,usr 

def process_voice(verification):
    print("recording...")
    new_voice_path = takeAudio()
    embexist = prepare_voice_embeddings(new_voice_path,verification)
    max_score = 0
    usr = "Unknown"
    prediction_final = False
    with open(f"{cf.me2}/deploy/embeddings/encodings_voices.pickle", "rb") as f:
          embeddings = pickle.load(f)
    for user_embeddings in embeddings:
        user = user_embeddings[0]
        for emb in user_embeddings[1]:
            score = verification.similarity(emb, embexist)
            prediction = score > 0.10
            if score > max_score and prediction:
               max_score = score
               usr = user
               prediction_final=prediction
    remove = cmd.Popen([f"rm {cf.src}/me2/*.wav"],stdout=cmd.PIPE,stderr=cmd.PIPE,shell=True)
    time.sleep(0.1)
    remove = cmd.Popen([f"rm {new_voice_path}"],stdout=cmd.PIPE,stderr=cmd.PIPE,shell=True)
    return prediction_final,usr



def get_database_voices():
    database_path = cf.dataset
    users = os.listdir(database_path)
    voices_labeled = []
    for user in users:
        user_path = os.path.join(database_path,user)
        user_voices_path = os.path.join(user_path,"voices")
        user_voices = [ os.path.join(user_voices_path,voice) for voice in os.listdir(user_voices_path)]
        voices_labeled.append((user,user_voices))
    return voices_labeled

def process_v(verification):
    print("recording...")
    new_voice_path = takeAudio()
    # embexist = prepare_voice_embeddings(new_voice_path,verification)
    max_score = 0
    usr = "Unknown"
    prediction_final = False
    with open(f"{cf.me2}/deploy/embeddings/encodings_voices.pickle", "rb") as f:
          embeddings = pickle.load(f)
    embeddings = get_database_voices()
    for user_embeddings in embeddings:
        user = user_embeddings[0]
        for emb in user_embeddings[1]:
            score,prediction = verification.verify_files(emb,new_voice_path)
            if score > max_score and prediction:
               max_score = score
               usr = user
    remove = cmd.Popen([f"rm {cf.src}/me2/*.wav"],stdout=cmd.PIPE,stderr=cmd.PIPE,shell=True)
    time.sleep(0.1)
    remove = cmd.Popen([f"rm {new_voice_path}"],stdout=cmd.PIPE,stderr=cmd.PIPE,shell=True)
    print(f"voice={usr}")
    return prediction,usr
