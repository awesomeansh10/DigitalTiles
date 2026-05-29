from gpiozero import Button
from signal import pause

print("--- CUSTOM ENCODER LOGIC ---")
print("Your output shows the encoder is mechanically skipping a state (1 0).")
print("gpiozero's built-in RotaryEncoder strictly requires all 4 states and rejects skipped ones.")
print("This custom logic fixes it by using a forgiving 'Clock and Data' approach.")

# Initialize pins as standard buttons with a small software debounce
clk = Button(17, pull_up=True, bounce_time=0.005)
dt = Button(27, pull_up=True, bounce_time=0.005)

steps = 0

def on_dt_pressed():
    global steps
    # When DT (Pin 27) goes active (to GND), we check the state of CLK (Pin 17)
    if clk.is_active:
        steps -= 1
        print(f"Rotated Anti-clockwise! Current steps: {steps}")
    else:
        steps += 1
        print(f"Rotated Clockwise! Current steps: {steps}")

dt.when_pressed = on_dt_pressed

print("\nTurn the encoder. Both directions should now work! Press Ctrl+C to exit.")

# Keep the script running to listen for events
pause()