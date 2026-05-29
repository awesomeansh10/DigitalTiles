from gpiozero import Button
from signal import pause

print("--- RAW ENCODER DEBUG MODE ---")
print("We are reading the raw signals from the pins to see if one is broken.")

# Treat both encoder pins as standard buttons to see exactly what they are doing
pin_A = Button(17, pull_up=True)
pin_B = Button(27, pull_up=True)

def print_pin_states():
    # .value is 1 when connected to GND (active) and 0 when open (pull-up/inactive)
    print(f"Pin 17: {pin_A.value} | Pin 27: {pin_B.value}")

# Trigger the print whenever either pin changes state
pin_A.when_pressed = print_pin_states
pin_A.when_released = print_pin_states
pin_B.when_pressed = print_pin_states
pin_B.when_released = print_pin_states

print("Slowly turn the encoder ONE click in either direction.")
print("You should see BOTH pins alternating between 0 and 1. Press Ctrl+C to exit.")

# Keep the script running to listen for events
pause()