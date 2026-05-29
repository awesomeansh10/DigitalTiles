from gpiozero import RotaryEncoder, Button
from signal import pause

# Initialize the rotary encoder on GPIO pins 4 and 17
# gpiozero enables internal pull-ups for the RotaryEncoder by default
encoder = RotaryEncoder(17, 27)

# Initialize the button on GPIO pin 0
# pull_up=True enables the internal pull-up resistor (this is also the default)
button = Button(0, pull_up=True)

def on_clockwise():
    print(f"Rotated Clockwise! Current steps: {encoder.steps}")

def on_counter_clockwise():
    print(f"Rotated Anti-clockwise! Current steps: {encoder.steps}")

def on_button_press():
    print("Button was pressed!")

def on_button_release():
    print("Button was released!")

# Assign event handlers
encoder.when_rotated_clockwise = on_clockwise
encoder.when_rotated_counter_clockwise = on_counter_clockwise
button.when_pressed = on_button_press
button.when_released = on_button_release

print("Running test for Rotary Encoder (Pins 4 & 17) and Button (Pin 26)...")
print("Turn the encoder or press the button. Press Ctrl+C to exit.")

# Keep the script running to listen for events
pause()