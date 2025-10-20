"""Main Window for Biometric Authentication GUI

Provides tabbed interface for:
- Home dashboard
- Model training
- System configuration  
- Door management
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QPushButton, QLineEdit
)
from PyQt5.QtCore import Qt

from configure import ConfigureWidget
from train import TrainWidget
from home import HomeWidget
from door import DoorWidget

class MainWindow(QMainWindow):
    """Main application window with navigation tabs"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._setup_navigation()
        
    def _setup_ui(self):
        """Initialize main window UI components"""
        self.setWindowTitle("Multimodal Biometric Authentication System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_layout = QVBoxLayout(self.central_widget)
        
        # Create navigation button layout
        self.nav_layout = QHBoxLayout()
        self.central_layout.addLayout(self.nav_layout)
        
    def _setup_navigation(self):
        """Setup navigation buttons and initial widget"""
        # Navigation buttons
        self.nav_buttons = {
            'home': QPushButton("🏠 Home"),
            'train': QPushButton("🎯 Training"), 
            'config': QPushButton("⚙️ Configure"),
            'door': QPushButton("🚪 Door Control")
        }
        
        # Connect button signals
        self.nav_buttons['home'].clicked.connect(lambda: self._switch_widget('home'))
        self.nav_buttons['train'].clicked.connect(lambda: self._switch_widget('train'))
        self.nav_buttons['config'].clicked.connect(lambda: self._switch_widget('config'))
        self.nav_buttons['door'].clicked.connect(lambda: self._switch_widget('door'))
        
        # Add buttons to layout
        for button in self.nav_buttons.values():
            button.setMinimumHeight(40)
            self.nav_layout.addWidget(button)
        
        # Initialize with home widget
        self.current_widget = HomeWidget()
        self.central_layout.addWidget(self.current_widget)
        self._update_button_states('home')
        
    def _switch_widget(self, widget_name):
        """Switch to specified widget and update navigation
        
        Args:
            widget_name (str): Name of widget to switch to
        """
        # Widget mapping
        widget_classes = {
            'home': HomeWidget,
            'train': TrainWidget,
            'config': ConfigureWidget,
            'door': DoorWidget
        }
        
        if widget_name not in widget_classes:
            return
            
        # Remove current widget
        if self.current_widget:
            self.central_layout.removeWidget(self.current_widget)
            self.current_widget.deleteLater()
        
        # Create and add new widget
        self.current_widget = widget_classes[widget_name]()
        self.central_layout.addWidget(self.current_widget)
        
        # Update button states
        self._update_button_states(widget_name)
        
    def _update_button_states(self, active_button):
        """Update navigation button enabled/disabled states
        
        Args:
            active_button (str): Name of currently active button
        """
        for name, button in self.nav_buttons.items():
            button.setEnabled(name != active_button)
                    

