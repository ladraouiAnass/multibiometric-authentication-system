"""Door Management Widget for Biometric Authentication

Provides GUI interface for:
- Biometric door access control
- Manual door operations
- Guest access management
- Real-time status monitoring
"""

import sys
import os
import time
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit
from PyQt5.QtGui import QFont
from PyQt5.uic import loadUiType
from os import path

# Import IoT and authentication modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from iot.iot import get_status_of_door, open_door, close_door
from deploy.decision import initialize_models, process_faces, process_voice, authenticate_user

class AuthenticationThread(QThread):
    """Background thread for biometric authentication"""
    
    # Signals for UI updates
    status_update = pyqtSignal(str)
    authentication_complete = pyqtSignal(bool, str, str)  # success, user, message
    
    def __init__(self):
        super().__init__()
        self.verification_model = None
    
    def run(self):
        """Run biometric authentication process"""
        try:
            # Initialize models
            self.status_update.emit("Initializing authentication models...")
            self.verification_model = initialize_models()
            
            # Process facial recognition
            self.status_update.emit("Capturing and analyzing facial features...")
            recognized_faces = process_faces()
            
            if not recognized_faces:
                self.authentication_complete.emit(False, "Unknown", "No recognized faces detected")
                return
            
            # Process voice recognition
            self.status_update.emit("Recording and analyzing voice (6 seconds)...")
            voice_allowed, speaker = process_voice(self.verification_model)
            
            # Combine authentication results
            is_authenticated, authenticated_user = authenticate_user(recognized_faces, speaker)
            
            if is_authenticated:
                message = f"Authentication successful for {authenticated_user}"
                self.authentication_complete.emit(True, authenticated_user, message)
            else:
                if speaker == "Unknown":
                    message = "Voice not recognized"
                elif speaker not in recognized_faces:
                    message = f"Face and voice mismatch (voice: {speaker})"
                else:
                    message = "Authentication failed"
                self.authentication_complete.emit(False, speaker, message)
                
        except Exception as e:
            self.authentication_complete.emit(False, "Error", f"Authentication error: {str(e)}")

try:
    FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "door.ui"))
    UI_AVAILABLE = True
except:
    UI_AVAILABLE = False
    FORM_CLASS = QWidget

class DoorWidget(FORM_CLASS):
    """Door control widget with biometric authentication"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if UI_AVAILABLE:
            self.setupUi(self)
        else:
            self._setup_fallback_ui()
        
        self.auth_thread = None
        self._setup_connections()
        self._update_door_status()
        self._setup_status_timer()
    
    def _setup_fallback_ui(self):
        """Setup UI when .ui file is not available"""
        layout = QVBoxLayout(self)
        
        # Status display
        self.status = QLabel("Unknown")
        self.status.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(self.status)
        
        # Current action display
        self.actual = QLabel("Ready")
        layout.addWidget(self.actual)
        
        # Authentication result
        self.cause = QLabel("")
        layout.addWidget(self.cause)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.open = QPushButton("🔓 Biometric Open")
        self.close = QPushButton("🔒 Close Door")
        self.guest = QPushButton("👤 Guest Access")
        
        button_layout.addWidget(self.open)
        button_layout.addWidget(self.close)
        button_layout.addWidget(self.guest)
        
        layout.addLayout(button_layout)
    
    def _setup_connections(self):
        """Setup button connections and signals"""
        self.open.clicked.connect(self._authenticate_and_open)
        self.close.clicked.connect(self._close_door)
        self.guest.clicked.connect(self._guest_access)
    
    def _setup_status_timer(self):
        """Setup timer for periodic status updates"""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_door_status)
        self.status_timer.start(5000)  # Update every 5 seconds
    
    def _update_door_status(self):
        """Update door status display"""
        try:
            current_status = get_status_of_door()
            self.status.setText(current_status.title())
            self._update_button_states(current_status)
        except Exception as e:
            self.status.setText("Error")
            print(f"Status update error: {e}")
    
    def _update_button_states(self, door_status):
        """Update button enabled/disabled states based on door status"""
        if door_status == "closed":
            self.open.setEnabled(True)
            self.close.setEnabled(False)
        elif door_status == "opened":
            self.open.setEnabled(False)
            self.close.setEnabled(True)
        else:
            # Unknown status - enable both for manual control
            self.open.setEnabled(True)
            self.close.setEnabled(True)
    
    def _authenticate_and_open(self):
        """Start biometric authentication process"""
        if self.auth_thread and self.auth_thread.isRunning():
            return  # Authentication already in progress
        
        # Disable buttons during authentication
        self.open.setEnabled(False)
        self.guest.setEnabled(False)
        
        # Clear previous results
        self.cause.setText("")
        
        # Start authentication thread
        self.auth_thread = AuthenticationThread()
        self.auth_thread.status_update.connect(self._update_status)
        self.auth_thread.authentication_complete.connect(self._handle_authentication_result)
        self.auth_thread.start()
    
    def _update_status(self, message):
        """Update status message during authentication"""
        self.actual.setText(message)
    
    def _handle_authentication_result(self, success, user, message):
        """Handle authentication completion"""
        self.actual.setText("")
        self.cause.setText(message)
        
        if success:
            # Open door on successful authentication
            try:
                door_status = open_door()
                self.status.setText(door_status.title())
                self._update_button_states(door_status)
            except Exception as e:
                self.cause.setText(f"Door control error: {e}")
        
        # Re-enable buttons
        self._update_door_status()
        self.guest.setEnabled(True)
    
    def _close_door(self):
        """Close the door"""
        try:
            self.actual.setText("Closing door...")
            door_status = close_door()
            self.status.setText(door_status.title())
            self._update_button_states(door_status)
            self.actual.setText("")
            self.cause.setText("Door closed manually")
        except Exception as e:
            self.cause.setText(f"Error closing door: {e}")
            self.actual.setText("")
    
    def _guest_access(self):
        """Provide guest access (admin override)"""
        try:
            self.cause.setText("Guest access granted (Admin override)")
            self.actual.setText("Opening door...")
            
            door_status = open_door()
            self.status.setText(door_status.title())
            self._update_button_states(door_status)
            
            self.actual.setText("")
        except Exception as e:
            self.cause.setText(f"Guest access error: {e}")
            self.actual.setText("")
    
    def closeEvent(self, event):
        """Clean up when widget is closed"""
        if self.auth_thread and self.auth_thread.isRunning():
            self.auth_thread.terminate()
            self.auth_thread.wait()
        
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
        
        event.accept()

# Backward compatibility alias
door = DoorWidget
    