from gpiozero import RotaryEncoder, Button
from signal import pause

# Initialize the rotary encoder on GPIO pins 17 and 27
# 3-pin mouse scroll wheel encoders are raw mechanical components.
# WIRING: Left Pin -> GPIO 17, Middle Pin -> GND, Right Pin -> GPIO 27.
# We add a small bounce_time to debounce the mechanical contacts.
# max_steps=0 ensures the encoder can spin infinitely.
encoder = RotaryEncoder(17, 27, max_steps=0, bounce_time=0.005)

# Initialize the button on GPIO pin 0
# pull_up=True enables the internal pull-up resistor (this is also the default)
button = Button(0, pull_up=True, bounce_time=0.01)

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

print("Running test for Rotary Encoder (Pins 17 & 27) and Button (Pin 0)...")
print("NOTE: Ensure the middle pin of the 3-pin encoder is wired to GND.")
print("Turn the encoder or press the button. Press Ctrl+C to exit.")

# Keep the script running to listen for events
pause()