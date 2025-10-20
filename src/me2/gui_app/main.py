"""Main GUI Application Entry Point

Launches the PyQt5-based desktop interface for multimodal
biometric authentication system management.
"""

import sys
from PyQt5.QtWidgets import QApplication
from window import MainWindow

def main():
    """Initialize and run the GUI application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Multimodal Biometric Authentication")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Start event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    