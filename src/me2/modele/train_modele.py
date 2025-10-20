"""Model Training Module for Biometric Authentication

Trains and generates embeddings for:
- Facial recognition using FaceNet
- Voice recognition using ECAPA-TDNN
- Stores embeddings as pickle files for inference
"""

import os
import sys
import time
import pickle
import subprocess as cmd
from pathlib import Path

import cv2
import numpy as np
import face_recognition
from imutils import paths
from speechbrain.inference.speaker import SpeakerRecognition

# Add config path
current_dir = os.path.dirname(__file__)
config_dir = os.path.join(current_dir, '../')
sys.path.append(config_dir)
import gui_app.config as cf

class BiometricTrainer:
    """Handles training of face and voice recognition models"""
    
    def __init__(self):
        self.face_model = "cnn"  # Use CNN model for better accuracy
        self.voice_model = None
        self._initialize_voice_model()
    
    def _initialize_voice_model(self):
        """Initialize SpeechBrain voice recognition model"""
        try:
            model_path = f"{cf.me2}/deploy/pretrained_models/spkrec-ecapa-voxceleb"
            self.voice_model = SpeakerRecognition.from_hparams(
                source="speechbrain/spkrec-ecapa-voxceleb",
                savedir=model_path
            )
            print("Voice recognition model initialized successfully")
        except Exception as e:
            print(f"Failed to initialize voice model: {e}")
    
    def train_face_recognition(self):
        """Train face recognition model and generate embeddings
        
        Processes all face images in the dataset directory and creates
        FaceNet embeddings for each person.
        """
        print("[INFO] Starting face recognition training...")
        
        # Get all image paths from dataset
        dataset_path = Path(cf.dataset)
        if not dataset_path.exists():
            print(f"Dataset path not found: {dataset_path}")
            return False
        
        image_paths = list(paths.list_images(str(dataset_path)))
        if not image_paths:
            print("No images found in dataset")
            return False
        
        print(f"[INFO] Found {len(image_paths)} images to process")
        
        # Initialize storage for encodings
        known_encodings = []
        known_names = []
        
        # Process each image
        for i, image_path in enumerate(image_paths):
            print(f"[INFO] Processing image {i + 1}/{len(image_paths)}: {Path(image_path).name}")
            
            # Extract person name from directory structure
            person_name = Path(image_path).parent.parent.name
            
            # Load and validate image
            image = cv2.imread(image_path)
            if image is None:
                print(f"[WARNING] Could not load image: {image_path}")
                continue
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Ensure image is in correct format
            if rgb_image.dtype != 'uint8':
                print(f"[WARNING] Image {image_path} is not 8-bit, skipping")
                continue
            
            # Make image contiguous in memory
            rgb_image = np.ascontiguousarray(rgb_image)
            
            try:
                # Detect face locations
                face_locations = face_recognition.face_locations(rgb_image, model=self.face_model)
                
                if not face_locations:
                    print(f"[WARNING] No faces detected in {image_path}")
                    continue
                
                # Generate face encodings
                face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
                
                # Store encodings for each detected face
                for encoding in face_encodings:
                    known_encodings.append(encoding)
                    known_names.append(person_name)
                    print(f"[INFO] Added encoding for {person_name}")
                
            except Exception as e:
                print(f"[ERROR] Failed to process {image_path}: {e}")
                continue
        
        if not known_encodings:
            print("[ERROR] No face encodings generated")
            return False
        
        # Save encodings to pickle file
        print("[INFO] Serializing face encodings...")
        face_data = {
            "encodings": known_encodings,
            "names": known_names
        }
        
        # Ensure embeddings directory exists
        embeddings_dir = Path(cf.me2) / "deploy" / "embeddings"
        embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        encodings_path = embeddings_dir / "encodings_faces.pickle"
        with open(encodings_path, "wb") as f:
            pickle.dump(face_data, f)
        
        print(f"[INFO] Face training completed. Saved {len(known_encodings)} encodings to {encodings_path}")
        return True
    
    def get_voice_dataset(self):
        """Retrieve voice samples from dataset directory
        
        Returns:
            list: Tuples of (person_name, list_of_voice_files)
        """
        dataset_path = Path(cf.dataset)
        if not dataset_path.exists():
            print(f"Dataset path not found: {dataset_path}")
            return []
        
        voice_data = []
        
        for person_dir in dataset_path.iterdir():
            if not person_dir.is_dir():
                continue
            
            voices_dir = person_dir / "voices"
            if not voices_dir.exists():
                print(f"[WARNING] No voices directory for {person_dir.name}")
                continue
            
            # Find all audio files
            voice_files = []
            for ext in ['*.wav', '*.mp3', '*.flac', '*.m4a']:
                voice_files.extend(voices_dir.glob(ext))
            
            if voice_files:
                voice_data.append((person_dir.name, [str(f) for f in voice_files]))
                print(f"[INFO] Found {len(voice_files)} voice samples for {person_dir.name}")
        
        return voice_data
    
    def extract_voice_embedding(self, audio_path):
        """Extract voice embedding from audio file
        
        Args:
            audio_path (str): Path to audio file
            
        Returns:
            torch.Tensor: Voice embedding or None if failed
        """
        try:
            waveform = self.voice_model.load_audio(audio_path)
            batch = waveform.unsqueeze(0)
            embedding = self.voice_model.encode_batch(batch, None, normalize=False)
            return embedding
        except Exception as e:
            print(f"[ERROR] Failed to extract embedding from {audio_path}: {e}")
            return None
    
    def train_voice_recognition(self):
        """Train voice recognition model and generate embeddings
        
        Processes all voice samples in the dataset and creates
        ECAPA-TDNN embeddings for each person.
        """
        if not self.voice_model:
            print("[ERROR] Voice model not initialized")
            return False
        
        print("[INFO] Starting voice recognition training...")
        
        # Get voice dataset
        voice_dataset = self.get_voice_dataset()
        if not voice_dataset:
            print("[ERROR] No voice data found")
            return False
        
        # Generate embeddings for each person
        voice_embeddings = []
        
        for person_name, voice_files in voice_dataset:
            print(f"[INFO] Processing voice samples for {person_name}")
            
            person_embeddings = []
            
            for voice_file in voice_files:
                print(f"[INFO] Processing: {Path(voice_file).name}")
                
                embedding = self.extract_voice_embedding(voice_file)
                if embedding is not None:
                    person_embeddings.append(embedding)
                else:
                    print(f"[WARNING] Failed to process {voice_file}")
            
            if person_embeddings:
                voice_embeddings.append((person_name, person_embeddings))
                print(f"[INFO] Generated {len(person_embeddings)} embeddings for {person_name}")
            else:
                print(f"[WARNING] No valid embeddings for {person_name}")
        
        if not voice_embeddings:
            print("[ERROR] No voice embeddings generated")
            return False
        
        # Save embeddings to pickle file
        print("[INFO] Serializing voice embeddings...")
        
        embeddings_dir = Path(cf.me2) / "deploy" / "embeddings"
        embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        embeddings_path = embeddings_dir / "encodings_voices.pickle"
        with open(embeddings_path, "wb") as f:
            pickle.dump(voice_embeddings, f)
        
        total_embeddings = sum(len(embs[1]) for embs in voice_embeddings)
        print(f"[INFO] Voice training completed. Saved {total_embeddings} embeddings to {embeddings_path}")
        return True
    
    def cleanup_temp_files(self):
        """Clean up temporary audio files"""
        try:
            # Remove any .wav files in the me2 directory
            cleanup_cmd = cmd.Popen(
                [f"rm -f {cf.me2}/*.wav"],
                stdout=cmd.PIPE,
                stderr=cmd.PIPE,
                shell=True
            )
            cleanup_cmd.wait()
            print("[INFO] Temporary files cleaned up")
        except Exception as e:
            print(f"[WARNING] Cleanup failed: {e}")

def main():
    """Main training function"""
    print("=" * 60)
    print("MULTIMODAL BIOMETRIC AUTHENTICATION - MODEL TRAINING")
    print("=" * 60)
    
    trainer = BiometricTrainer()
    
    try:
        # Train face recognition
        print("\n" + "=" * 40)
        print("TRAINING FACE RECOGNITION MODEL")
        print("=" * 40)
        
        face_success = trainer.train_face_recognition()
        if face_success:
            print("✅ Face recognition training completed successfully")
        else:
            print("❌ Face recognition training failed")
        
        # Train voice recognition
        print("\n" + "=" * 40)
        print("TRAINING VOICE RECOGNITION MODEL")
        print("=" * 40)
        
        voice_success = trainer.train_voice_recognition()
        if voice_success:
            print("✅ Voice recognition training completed successfully")
        else:
            print("❌ Voice recognition training failed")
        
        # Overall status
        print("\n" + "=" * 40)
        print("TRAINING SUMMARY")
        print("=" * 40)
        
        if face_success and voice_success:
            print("🎉 All models trained successfully!")
            print("System ready for multimodal authentication")
        else:
            print("⚠️  Some models failed to train")
            print("Check the logs above for details")
    
    except KeyboardInterrupt:
        print("\n[INFO] Training interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Training failed: {e}")
    finally:
        # Cleanup
        trainer.cleanup_temp_files()

if __name__ == "__main__":
    main()