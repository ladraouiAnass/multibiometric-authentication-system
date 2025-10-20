"""Home Dashboard Widget for Biometric Authentication System

Provides overview and quick access to:
- System status
- Recent authentication logs
- Quick actions
- System statistics
"""

import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QGridLayout, QFrame
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QPalette
from PyQt5.uic import loadUiType
from os import path

try:
    FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "home.ui"))
    UI_AVAILABLE = True
except:
    UI_AVAILABLE = False
    FORM_CLASS = QWidget

class HomeWidget(FORM_CLASS):
    """Home dashboard widget with system overview"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if UI_AVAILABLE:
            self.setupUi(self)
        else:
            self._setup_fallback_ui()
        
        self._setup_dashboard()
        self._setup_timer()
    
    def _setup_fallback_ui(self):
        """Setup UI when .ui file is not available"""
        main_layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🏠 Multimodal Biometric Authentication System")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Status cards layout
        cards_layout = QGridLayout()
        main_layout.addLayout(cards_layout)
        
        # System status card
        self.status_card = self._create_status_card("System Status", "🟢 Online")
        cards_layout.addWidget(self.status_card, 0, 0)
        
        # Authentication stats card
        self.auth_card = self._create_status_card("Today's Authentications", "0")
        cards_layout.addWidget(self.auth_card, 0, 1)
        
        # Models status card
        self.models_card = self._create_status_card("Models Status", "✅ Ready")
        cards_layout.addWidget(self.models_card, 1, 0)
        
        # Door status card
        self.door_card = self._create_status_card("Door Status", "🔒 Closed")
        cards_layout.addWidget(self.door_card, 1, 1)
        
        # Recent activity log
        activity_label = QLabel("📋 Recent Activity")
        activity_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(activity_label)
        
        self.activity_log = QTextEdit()
        self.activity_log.setMaximumHeight(200)
        self.activity_log.setReadOnly(True)
        main_layout.addWidget(self.activity_log)
        
        # Quick actions
        actions_label = QLabel("⚡ Quick Actions")
        actions_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(actions_label)
        
        actions_layout = QHBoxLayout()
        
        self.train_btn = QPushButton("🎯 Train Models")
        self.config_btn = QPushButton("⚙️ Configure")
        self.door_btn = QPushButton("🚪 Door Control")
        
        actions_layout.addWidget(self.train_btn)
        actions_layout.addWidget(self.config_btn)
        actions_layout.addWidget(self.door_btn)
        
        main_layout.addLayout(actions_layout)
        
        # Add stretch to push everything to top
        main_layout.addStretch()
    
    def _create_status_card(self, title, value):
        """Create a status card widget
        
        Args:
            title (str): Card title
            value (str): Card value
            
        Returns:
            QFrame: Styled status card
        """
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setLineWidth(1)
        card.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        title_label.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 14, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
    
    def _setup_dashboard(self):
        """Initialize dashboard with current system information"""
        # Add initial log entries
        self._add_log_entry("System initialized")
        self._add_log_entry("Biometric models loaded")
        self._add_log_entry("Dashboard ready")
        
        # Update initial status
        self._update_system_status()
    
    def _setup_timer(self):
        """Setup timer for periodic updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_system_status)
        self.update_timer.start(10000)  # Update every 10 seconds
    
    def _update_system_status(self):
        """Update system status information"""
        try:
            # Update system status
            self.status_card.value_label.setText("🟢 Online")
            
            # Update models status
            self.models_card.value_label.setText("✅ Ready")
            
            # Update door status (would normally query actual door)
            # For now, show simulated status
            import random
            door_states = ["🔒 Closed", "🔓 Open"]
            # self.door_card.value_label.setText(random.choice(door_states))
            self.door_card.value_label.setText("🔒 Closed")  # Default to closed
            
        except Exception as e:
            self.status_card.value_label.setText("🔴 Error")
            self._add_log_entry(f"Status update error: {e}")
    
    def _add_log_entry(self, message):
        """Add entry to activity log
        
        Args:
            message (str): Log message
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Add to log and scroll to bottom
        self.activity_log.append(log_entry)
        
        # Keep log size manageable (last 50 entries)
        text = self.activity_log.toPlainText()
        lines = text.split('\n')
        if len(lines) > 50:
            self.activity_log.setPlainText('\n'.join(lines[-50:]))
    
    def log_authentication(self, user, success):
        """Log authentication attempt
        
        Args:
            user (str): Username
            success (bool): Authentication result
        """
        status = "✅ Success" if success else "❌ Failed"
        self._add_log_entry(f"Authentication {status}: {user}")
        
        # Update authentication counter
        current_count = int(self.auth_card.value_label.text())
        self.auth_card.value_label.setText(str(current_count + 1))
    
    def closeEvent(self, event):
        """Clean up when widget is closed"""
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
        event.accept()

# Backward compatibility alias
home = HomeWidget