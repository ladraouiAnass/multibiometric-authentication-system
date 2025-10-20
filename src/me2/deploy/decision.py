"""Core Authentication Decision Module

Implements multimodal biometric authentication combining:
- Facial recognition using FaceNet embeddings
- Voice recognition using ECAPA-TDNN speaker verification
- Real-time processing with configurable thresholds
"""

import os
import sys
import time

import pickle
import subprocess as cmd

import cv2
import imutils
import face_recognition
import sounddevice as sd
import soundfile as sf
from imutils.video import VideoStream, FPS
from speechbrain.inference.speaker import SpeakerRecognition

# Add config path
current_dir = os.path.dirname(__file__)
config_dir = os.path.join(current_dir, '../')
sys.path.append(config_dir)
import gui_app.config as cf

# Authentication thresholds
VOICE_SIMILARITY_THRESHOLD = 0.10
FACE_RECOGNITION_TIMEOUT = 3.0
VOICE_RECORDING_DURATION = 6.0

def initialize_models():
    """Initialize speaker recognition model
    
    Returns:
        SpeakerRecognition: Configured ECAPA-TDNN model
    """
    model_path = f"{cf.me2}/deploy/pretrained_models/spkrec-ecapa-voxceleb"
    verification = SpeakerRecognition.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb", 
        savedir=model_path
    )
    return verification

def process_faces():
    """Process facial recognition from video stream
    
    Captures frames for specified duration and identifies known faces
    using pre-trained FaceNet embeddings with cosine similarity.
    
    Returns:
        set: Unique names of recognized individuals
    """
    recognized_persons = []
    current_name = "Unknown"
    
    # Load pre-trained face encodings
    encodings_path = f"{cf.me2}/deploy/embeddings/encodings_faces.pickle"
    print("Loading face encodings...")
    
    try:
        with open(encodings_path, "rb") as f:
            face_data = pickle.load(f)
    except FileNotFoundError:
        print(f"Face encodings not found at {encodings_path}")
        return set()
    
    # Initialize video stream
    video_stream = VideoStream(cf.camurl).start()
    time.sleep(2.0)  # Allow camera to warm up
    
    fps_counter = FPS().start()
    start_time = time.time()
    
    # Process frames for specified duration
    while (time.time() - start_time) < FACE_RECOGNITION_TIMEOUT:
        frame = video_stream.read()
        if frame is None:
            continue
            
        # Preprocess frame
        frame = imutils.resize(frame, width=500)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces and compute encodings
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        # Match faces against known encodings
        for encoding in face_encodings:
            matches = face_recognition.compare_faces(face_data["encodings"], encoding)
            name = "Unknown"
            
            if True in matches:
                # Find best match using voting
                matched_indices = [i for i, match in enumerate(matches) if match]
                name_counts = {}
                
                for i in matched_indices:
                    candidate_name = face_data["names"][i]
                    name_counts[candidate_name] = name_counts.get(candidate_name, 0) + 1
                
                name = max(name_counts, key=name_counts.get)
                
                # Add new recognition
                if current_name != name:
                    current_name = name
                    recognized_persons.append(name)
                    print(f"Recognized: {name}")
        
        fps_counter.update()
    
    # Cleanup
    fps_counter.stop()
    print(f"Face recognition completed - Elapsed: {fps_counter.elapsed():.2f}s, FPS: {fps_counter.fps():.2f}")
    cv2.destroyAllWindows()
    video_stream.stop()
    
    return set(recognized_persons)

def record_audio():
    """Record audio sample for voice recognition
    
    Records audio for specified duration at 44.1kHz sample rate.
    
    Returns:
        str: Path to recorded audio file
    """
    sample_rate = 44100
    duration = VOICE_RECORDING_DURATION
    
    print(f"Recording audio for {duration} seconds...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2)
    sd.wait()  # Wait for recording to complete
    
    # Ensure cache directory exists
    cache_dir = f"{cf.me2}/deploy/cachaud"
    os.makedirs(cache_dir, exist_ok=True)
    
    audio_path = f"{cache_dir}/recorded_audio.wav"
    sf.write(audio_path, recording, sample_rate)
    
    return audio_path

def extract_voice_embedding(audio_path, verification_model):
    """Extract voice embedding from audio file
    
    Args:
        audio_path (str): Path to audio file
        verification_model: SpeakerRecognition model
        
    Returns:
        torch.Tensor: Voice embedding vector
    """
    waveform = verification_model.load_audio(audio_path)
    batch = waveform.unsqueeze(0)
    embedding = verification_model.encode_batch(batch, None, normalize=False)
    return embedding

def process_voice(verification_model):
    """Process voice recognition and speaker identification
    
    Records audio sample and compares against stored voice embeddings
    using cosine similarity with configurable threshold.
    
    Args:
        verification_model: SpeakerRecognition model
        
    Returns:
        tuple: (is_authenticated, speaker_name)
    """
    # Record new audio sample
    audio_path = record_audio()
    
    try:
        # Extract embedding from recorded audio
        current_embedding = extract_voice_embedding(audio_path, verification_model)
        
        # Load stored voice embeddings
        embeddings_path = f"{cf.me2}/deploy/embeddings/encodings_voices.pickle"
        with open(embeddings_path, "rb") as f:
            stored_embeddings = pickle.load(f)
        
        # Find best match
        max_similarity = 0
        identified_speaker = "Unknown"
        is_authenticated = False
        
        for user_data in stored_embeddings:
            username = user_data[0]
            user_embeddings = user_data[1]
            
            for stored_embedding in user_embeddings:
                similarity = verification_model.similarity(stored_embedding, current_embedding)
                
                if similarity > VOICE_SIMILARITY_THRESHOLD and similarity > max_similarity:
                    max_similarity = similarity
                    identified_speaker = username
                    is_authenticated = True
        
        print(f"Voice recognition: {identified_speaker} (similarity: {max_similarity:.3f})")
        
    except Exception as e:
        print(f"Voice processing error: {e}")
        is_authenticated = False
        identified_speaker = "Unknown"
    
    finally:
        # Cleanup audio files
        _cleanup_audio_files([audio_path])
    
    return is_authenticated, identified_speaker

def get_database_voices():
    """Retrieve voice samples from dataset directory
    
    Returns:
        list: Tuples of (username, list_of_voice_file_paths)
    """
    database_path = cf.dataset
    if not os.path.exists(database_path):
        print(f"Dataset path not found: {database_path}")
        return []
    
    voices_labeled = []
    
    for user in os.listdir(database_path):
        user_path = os.path.join(database_path, user)
        voices_path = os.path.join(user_path, "voices")
        
        if os.path.exists(voices_path):
            voice_files = [
                os.path.join(voices_path, voice) 
                for voice in os.listdir(voices_path)
                if voice.endswith(('.wav', '.mp3', '.flac'))
            ]
            if voice_files:
                voices_labeled.append((user, voice_files))
    
    return voices_labeled

def _cleanup_audio_files(file_paths):
    """Clean up temporary audio files
    
    Args:
        file_paths (list): List of file paths to remove
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not remove {file_path}: {e}")
    
    # Also clean up any .wav files in the main directory
    try:
        cleanup_cmd = cmd.Popen(
            [f"rm -f {cf.me2}/*.wav"], 
            stdout=cmd.PIPE, 
            stderr=cmd.PIPE, 
            shell=True
        )
        cleanup_cmd.wait()
    except Exception as e:
        print(f"Warning: Cleanup command failed: {e}")

def authenticate_user(face_names, voice_speaker):
    """Combine face and voice authentication results
    
    Args:
        face_names (set): Set of recognized face names
        voice_speaker (str): Identified voice speaker
        
    Returns:
        tuple: (is_authenticated, authenticated_user)
    """
    if not face_names or voice_speaker == "Unknown":
        return False, "Unknown"
    
    # Check if voice matches any recognized face
    if voice_speaker in face_names:
        return True, voice_speaker
    
    return False, "Mismatch"
