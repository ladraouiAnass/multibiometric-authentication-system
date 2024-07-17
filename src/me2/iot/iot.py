import random
from gpiozero import Servo
import serial

def initializeservo():
    # GPIO pin for servo control
    servo_pin = 17
    # Define the servo object
    servo = Servo(servo_pin)
    return servo

# Function to set the servo angle
def set_angle(angle):
    servo.value = angle
    time.sleep(1)

def turnservomotor():
    node=serial.Serial("COM3",9600)
    num=1
    node.write(num.encode())
    node.write(num.encode())

# Function to communicate with Arduino
def communicate_with_arduino():
    # Define the port for Arduino (modify based on your system)
    arduino_port = '/dev/ttyACM0'
    # Initialize serial communication
    ser = serial.Serial(arduino_port, 9600, timeout=1)
    # Wait for Arduino to initialize
    time.sleep(2)
    # Send signal to Arduino to control servo motor
    ser.write(b's')
    # Close serial connection
    ser.close()

def getStatusofDoor():
    ...
    return random.choice(["opened","closed"])


def turnservomotorf():
    return True
    
def openDoor():
    if turnservomotorf():
       return "opened"
    else:
        return "closed"
    

def closeDoor():
    return "closed"
    
                


                                    
