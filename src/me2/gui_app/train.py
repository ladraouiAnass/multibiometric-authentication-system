"""Training Widget for Biometric Authentication System

Provides interface for:
- Model training management
- Dataset validation
- Training progress monitoring
- Model performance evaluation
"""

import os
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QProgressBar, QGroupBox,
    QFormLayout, QSpinBox, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.uic import loadUiType
from os import path

# Add parent directory for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))\n
try:
    from modele.train_modele import BiometricTrainer
    TRAINER_AVAILABLE = True
except ImportError:
    TRAINER_AVAILABLE = False

try:
    FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "train.ui"))
    UI_AVAILABLE = True
except:
    UI_AVAILABLE = False
    FORM_CLASS = QWidget

class TrainingThread(QThread):
    """Background thread for model training"""
    
    # Signals for UI updates
    progress_update = pyqtSignal(int)  # Progress percentage
    status_update = pyqtSignal(str)    # Status message
    training_complete = pyqtSignal(bool, str)  # Success, message
    
    def __init__(self, train_faces=True, train_voices=True):
        super().__init__()
        self.train_faces = train_faces
        self.train_voices = train_voices
        self.trainer = None
    
    def run(self):
        """Run training process"""
        try:
            if not TRAINER_AVAILABLE:
                self.training_complete.emit(False, "Training module not available")
                return
            
            self.status_update.emit("Initializing trainer...")
            self.trainer = BiometricTrainer()
            self.progress_update.emit(10)
            
            success_count = 0
            total_tasks = (1 if self.train_faces else 0) + (1 if self.train_voices else 0)
            
            if self.train_faces:
                self.status_update.emit("Training face recognition model...")
                self.progress_update.emit(20)
                
                if self.trainer.train_face_recognition():
                    success_count += 1
                    self.status_update.emit("✅ Face recognition training completed")
                else:
                    self.status_update.emit("❌ Face recognition training failed")
                
                self.progress_update.emit(50)
            
            if self.train_voices:
                self.status_update.emit("Training voice recognition model...")
                self.progress_update.emit(60)
                
                if self.trainer.train_voice_recognition():
                    success_count += 1
                    self.status_update.emit("✅ Voice recognition training completed")
                else:
                    self.status_update.emit("❌ Voice recognition training failed")
                
                self.progress_update.emit(90)
            
            # Cleanup
            self.status_update.emit("Cleaning up temporary files...")
            self.trainer.cleanup_temp_files()
            self.progress_update.emit(100)
            
            # Final result
            if success_count == total_tasks:
                self.training_complete.emit(True, "All models trained successfully!")
            else:
                self.training_complete.emit(False, f"Training completed with {success_count}/{total_tasks} successful")
                
        except Exception as e:
            self.training_complete.emit(False, f"Training error: {str(e)}")

class TrainWidget(FORM_CLASS):
    """Training widget for model management"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if UI_AVAILABLE:
            self.setupUi(self)
        else:
            self._setup_fallback_ui()
        
        self.training_thread = None
        self._setup_connections()
    
    def _setup_fallback_ui(self):
        """Setup UI when .ui file is not available"""
        main_layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🎯 Model Training")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Training options group
        options_group = QGroupBox("Training Options")
        options_layout = QFormLayout(options_group)
        
        self.train_faces_cb = QCheckBox("Train Face Recognition")\n        self.train_faces_cb.setChecked(True)
        options_layout.addRow(self.train_faces_cb)
        
        self.train_voices_cb = QCheckBox("Train Voice Recognition")
        self.train_voices_cb.setChecked(True)
        options_layout.addRow(self.train_voices_cb)
        
        main_layout.addWidget(options_group)
        
        # Dataset info group
        dataset_group = QGroupBox("📁 Dataset Information")
        dataset_layout = QVBoxLayout(dataset_group)
        
        self.dataset_info = QLabel("Click 'Validate Dataset' to check dataset status")
        dataset_layout.addWidget(self.dataset_info)
        
        validate_btn = QPushButton("🔍 Validate Dataset")
        validate_btn.clicked.connect(self._validate_dataset)
        dataset_layout.addWidget(validate_btn)
        
        main_layout.addWidget(dataset_group)
        
        # Training controls
        controls_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🚀 Start Training")
        self.stop_btn = QPushButton("⏹️ Stop Training")
        self.stop_btn.setEnabled(False)
        
        self.start_btn.clicked.connect(self._start_training)
        self.stop_btn.clicked.connect(self._stop_training)
        
        controls_layout.addWidget(self.start_btn)
        controls_layout.addWidget(self.stop_btn)
        
        main_layout.addLayout(controls_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status display
        status_label = QLabel("📋 Training Log")
        status_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(status_label)
        
        self.status_log = QTextEdit()
        self.status_log.setMaximumHeight(200)
        self.status_log.setReadOnly(True)
        main_layout.addWidget(self.status_log)
        
        # Add stretch
        main_layout.addStretch()
        
        # Initial log entry
        self._add_log("Training interface initialized")
    
    def _setup_connections(self):
        """Setup signal connections"""
        pass  # Connections are set up in _setup_fallback_ui
    
    def _validate_dataset(self):
        """Validate dataset structure and content"""
        try:
            import config as cf
            dataset_path = cf.dataset
            
            self._add_log(f"Validating dataset at: {dataset_path}")
            
            if not os.path.exists(dataset_path):
                self._add_log("❌ Dataset directory not found")
                self.dataset_info.setText("❌ Dataset directory not found")
                return
            
            # Count users and samples
            users = []
            total_faces = 0
            total_voices = 0
            
            for user_dir in os.listdir(dataset_path):
                user_path = os.path.join(dataset_path, user_dir)
                if not os.path.isdir(user_path):
                    continue
                
                users.append(user_dir)
                
                # Count face images
                faces_dir = os.path.join(user_path, "faces")
                if os.path.exists(faces_dir):
                    face_files = [f for f in os.listdir(faces_dir) 
                                if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                    total_faces += len(face_files)
                
                # Count voice samples
                voices_dir = os.path.join(user_path, "voices")
                if os.path.exists(voices_dir):
                    voice_files = [f for f in os.listdir(voices_dir) 
                                 if f.lower().endswith(('.wav', '.mp3', '.flac'))]
                    total_voices += len(voice_files)
            
            # Update info display
            info_text = f"""✅ Dataset Valid
Users: {len(users)}
Face Images: {total_faces}
Voice Samples: {total_voices}"""
            
            self.dataset_info.setText(info_text)
            self._add_log(f"Dataset validation complete: {len(users)} users, {total_faces} faces, {total_voices} voices")
            
        except Exception as e:
            error_msg = f"Dataset validation error: {e}"
            self.dataset_info.setText(f"❌ {error_msg}")
            self._add_log(error_msg)
    
    def _start_training(self):
        """Start model training process"""
        if self.training_thread and self.training_thread.isRunning():
            return
        
        # Check training options
        train_faces = self.train_faces_cb.isChecked()
        train_voices = self.train_voices_cb.isChecked()
        
        if not train_faces and not train_voices:
            self._add_log("❌ Please select at least one training option")
            return
        
        # Update UI state
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start training thread
        self.training_thread = TrainingThread(train_faces, train_voices)
        self.training_thread.progress_update.connect(self.progress_bar.setValue)
        self.training_thread.status_update.connect(self._add_log)
        self.training_thread.training_complete.connect(self._training_finished)
        
        self._add_log("🚀 Starting training process...")
        self.training_thread.start()
    
    def _stop_training(self):
        """Stop training process"""
        if self.training_thread and self.training_thread.isRunning():
            self._add_log("⏹️ Stopping training...")
            self.training_thread.terminate()
            self.training_thread.wait()
            self._training_finished(False, "Training stopped by user")
    
    def _training_finished(self, success, message):
        """Handle training completion"""
        # Update UI state
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        # Log result
        if success:
            self._add_log(f"🎉 {message}")
        else:
            self._add_log(f"⚠️ {message}")
    
    def _add_log(self, message):
        """Add message to training log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        self.status_log.append(log_entry)
        
        # Keep log size manageable
        text = self.status_log.toPlainText()
        lines = text.split('\n')
        if len(lines) > 100:
            self.status_log.setPlainText('\n'.join(lines[-100:]))
    
    def closeEvent(self, event):
        """Clean up when widget is closed"""
        if self.training_thread and self.training_thread.isRunning():
            self.training_thread.terminate()
            self.training_thread.wait()
        event.accept()

# Backward compatibility alias
train = TrainWidget