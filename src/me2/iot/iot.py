"""IoT Integration Module for Smart Door Control

Provides hardware interfaces for:
- Servo motor control via GPIO (Raspberry Pi)
- Arduino communication via serial
- Door status monitoring
- Smart lock integration
"""

import time
import random
import logging
from typing import Optional, Tuple

try:
    from gpiozero import Servo
    import serial
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("GPIO/Serial libraries not available - running in simulation mode")

# Hardware configuration
SERVO_GPIO_PIN = 17
ARDUINO_PORT = '/dev/ttyACM0'  # Linux
# ARDUINO_PORT = 'COM3'  # Windows
BAUD_RATE = 9600
SERVO_TIMEOUT = 1.0

class DoorController:
    """Smart door controller with servo and Arduino integration"""
    
    def __init__(self):
        self.servo = None
        self.arduino_connection = None
        self._door_status = "closed"
        self._initialize_hardware()
    
    def _initialize_hardware(self):
        """Initialize servo and Arduino connections"""
        if not GPIO_AVAILABLE:
            logging.info("Running in simulation mode")
            return
            
        try:
            # Initialize servo
            self.servo = Servo(SERVO_GPIO_PIN)
            logging.info(f"Servo initialized on GPIO pin {SERVO_GPIO_PIN}")
        except Exception as e:
            logging.error(f"Failed to initialize servo: {e}")
    
    def set_servo_angle(self, angle: float) -> bool:
        """Set servo to specific angle
        
        Args:
            angle (float): Servo angle (-1 to 1)
            
        Returns:
            bool: Success status
        """
        if not self.servo:
            logging.warning("Servo not available - simulating movement")
            time.sleep(SERVO_TIMEOUT)
            return True
            
        try:
            self.servo.value = angle
            time.sleep(SERVO_TIMEOUT)
            return True
        except Exception as e:
            logging.error(f"Servo control failed: {e}")
            return False
    
    def communicate_with_arduino(self, command: bytes = b's') -> bool:
        """Send command to Arduino via serial
        
        Args:
            command (bytes): Command to send
            
        Returns:
            bool: Success status
        """
        if not GPIO_AVAILABLE:
            logging.info(f"Simulating Arduino command: {command}")
            return True
            
        try:
            with serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1) as ser:
                time.sleep(2)  # Arduino initialization time
                ser.write(command)
                logging.info(f"Command sent to Arduino: {command}")
                return True
        except Exception as e:
            logging.error(f"Arduino communication failed: {e}")
            return False
    
    def open_door(self) -> str:
        """Open the smart door
        
        Returns:
            str: Door status after operation
        """
        logging.info("Opening door...")
        
        # Method 1: Direct servo control
        if self.set_servo_angle(1.0):  # Full open position
            self._door_status = "opened"
        
        # Method 2: Arduino control (alternative)
        # if self.communicate_with_arduino(b'o'):
        #     self._door_status = "opened"
        
        logging.info(f"Door status: {self._door_status}")
        return self._door_status
    
    def close_door(self) -> str:
        """Close the smart door
        
        Returns:
            str: Door status after operation
        """
        logging.info("Closing door...")
        
        # Method 1: Direct servo control
        if self.set_servo_angle(-1.0):  # Full closed position
            self._door_status = "closed"
        
        # Method 2: Arduino control (alternative)
        # if self.communicate_with_arduino(b'c'):
        #     self._door_status = "closed"
        
        logging.info(f"Door status: {self._door_status}")
        return self._door_status
    
    def get_door_status(self) -> str:
        """Get current door status
        
        In a real implementation, this would read from sensors.
        Currently returns simulated status for testing.
        
        Returns:
            str: Current door status ('opened' or 'closed')
        """
        # Simulate sensor reading
        if not GPIO_AVAILABLE:
            return random.choice(["opened", "closed"])
        
        return self._door_status
    
    def cleanup(self):
        """Clean up hardware resources"""
        if self.servo:
            self.servo.close()
        if self.arduino_connection:
            self.arduino_connection.close()

# Global door controller instance
_door_controller = DoorController()

# Legacy function interfaces for backward compatibility
def initialize_servo():
    """Legacy function - use DoorController class instead"""
    return _door_controller.servo

def get_status_of_door() -> str:
    """Get current door status"""
    return _door_controller.get_door_status()

def open_door() -> str:
    """Open the door"""
    return _door_controller.open_door()

def close_door() -> str:
    """Close the door"""
    return _door_controller.close_door()

def turn_servo_motor() -> bool:
    """Legacy servo control function"""
    return _door_controller.set_servo_angle(1.0)

# Aliases for backward compatibility
getStatusofDoor = get_status_of_door
openDoor = open_door
closeDoor = close_door
turnservomotorf = turn_servo_motor