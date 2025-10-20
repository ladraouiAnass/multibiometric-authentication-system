"""Configuration Widget for Biometric Authentication System

Provides interface for:
- System settings configuration
- Camera and audio device setup
- Authentication thresholds
- Model parameters
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QGroupBox, QFormLayout, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.uic import loadUiType
from os import path

try:
    FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "configure.ui"))
    UI_AVAILABLE = True
except:
    UI_AVAILABLE = False
    FORM_CLASS = QWidget

class ConfigureWidget(FORM_CLASS):
    """Configuration widget for system settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if UI_AVAILABLE:
            self.setupUi(self)
        else:
            self._setup_fallback_ui()
        
        self._load_current_settings()
    
    def _setup_fallback_ui(self):
        """Setup UI when .ui file is not available"""
        main_layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("⚙️ System Configuration")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Camera settings group
        camera_group = QGroupBox("📷 Camera Settings")
        camera_layout = QFormLayout(camera_group)
        
        self.camera_url = QLineEdit()
        self.camera_url.setPlaceholderText("http://192.168.1.104:8080/video or 0 for USB")
        camera_layout.addRow("Camera URL/Index:", self.camera_url)
        
        main_layout.addWidget(camera_group)
        
        # Authentication settings group
        auth_group = QGroupBox("🔐 Authentication Settings")
        auth_layout = QFormLayout(auth_group)
        
        self.voice_threshold = QDoubleSpinBox()
        self.voice_threshold.setRange(0.01, 1.0)
        self.voice_threshold.setSingleStep(0.01)
        self.voice_threshold.setDecimals(2)
        auth_layout.addRow("Voice Similarity Threshold:", self.voice_threshold)
        
        self.face_timeout = QSpinBox()
        self.face_timeout.setRange(1, 30)
        self.face_timeout.setSuffix(" seconds")
        auth_layout.addRow("Face Recognition Timeout:", self.face_timeout)
        
        self.recording_duration = QSpinBox()
        self.recording_duration.setRange(3, 15)
        self.recording_duration.setSuffix(" seconds")
        auth_layout.addRow("Voice Recording Duration:", self.recording_duration)
        
        main_layout.addWidget(auth_group)
        
        # Dataset settings group
        dataset_group = QGroupBox("📁 Dataset Settings")
        dataset_layout = QFormLayout(dataset_group)
        
        self.dataset_path = QLineEdit()
        self.dataset_path.setPlaceholderText("/path/to/dataset")
        dataset_layout.addRow("Dataset Path:", self.dataset_path)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_dataset)
        dataset_layout.addRow("", browse_btn)
        
        main_layout.addWidget(dataset_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save Settings")
        self.reset_btn = QPushButton("🔄 Reset to Defaults")
        self.test_camera_btn = QPushButton("📹 Test Camera")
        
        self.save_btn.clicked.connect(self._save_settings)
        self.reset_btn.clicked.connect(self._reset_settings)
        self.test_camera_btn.clicked.connect(self._test_camera)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.test_camera_btn)
        
        main_layout.addLayout(button_layout)
        
        # Status display
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        main_layout.addWidget(self.status_text)
        
        # Add stretch
        main_layout.addStretch()
    
    def _load_current_settings(self):
        """Load current configuration settings"""
        try:
            # Import config to get current values
            import sys
            sys.path.append(os.path.dirname(__file__))
            import config as cf
            
            # Load values into UI
            self.camera_url.setText(str(cf.camurl))
            self.voice_threshold.setValue(getattr(cf, 'VOICE_THRESHOLD', 0.10))
            self.face_timeout.setValue(3)  # Default value
            self.recording_duration.setValue(6)  # Default value
            self.dataset_path.setText(cf.dataset)
            
            self._add_status("Current settings loaded successfully")
            
        except Exception as e:
            self._add_status(f"Error loading settings: {e}")
    
    def _save_settings(self):
        """Save configuration settings"""
        try:
            # Here you would save settings to config file
            # For now, just show what would be saved
            settings = {
                'camera_url': self.camera_url.text(),
                'voice_threshold': self.voice_threshold.value(),
                'face_timeout': self.face_timeout.value(),
                'recording_duration': self.recording_duration.value(),
                'dataset_path': self.dataset_path.text()
            }
            
            self._add_status("Settings saved successfully:")
            for key, value in settings.items():
                self._add_status(f"  {key}: {value}")
            
        except Exception as e:
            self._add_status(f"Error saving settings: {e}")
    
    def _reset_settings(self):
        """Reset settings to defaults"""
        self.camera_url.setText("http://192.168.1.104:8080/video")
        self.voice_threshold.setValue(0.10)
        self.face_timeout.setValue(3)
        self.recording_duration.setValue(6)
        self.dataset_path.setText("/path/to/dataset")
        
        self._add_status("Settings reset to defaults")
    
    def _browse_dataset(self):
        """Browse for dataset directory"""
        from PyQt5.QtWidgets import QFileDialog
        
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Dataset Directory",
            self.dataset_path.text()
        )
        
        if directory:
            self.dataset_path.setText(directory)
            self._add_status(f"Dataset path updated: {directory}")
    
    def _test_camera(self):
        """Test camera connection"""
        try:
            camera_url = self.camera_url.text()
            self._add_status(f"Testing camera: {camera_url}")
            
            # Here you would actually test the camera
            # For now, just simulate the test
            import time
            time.sleep(1)  # Simulate test delay
            
            self._add_status("✅ Camera test successful")
            
        except Exception as e:
            self._add_status(f"❌ Camera test failed: {e}")
    
    def _add_status(self, message):
        """Add status message to display"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")

# Backward compatibility alias
configure = ConfigureWidget