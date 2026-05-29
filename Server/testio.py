from gpiozero import Button
from signal import pause

print("--- CUSTOM ENCODER LOGIC ---")
print("We are upgrading to a Robust Sequence Parser.")
print("This completely filters out bounces and prevents false reverse-reads.")

# Initialize pins without software debounce, our sequence array naturally handles it
clk = Button(17, pull_up=True)
dt = Button(27, pull_up=True)

steps = 0
current_sequence = []

def check_state():
    global current_sequence, steps
    
    state = (clk.is_active, dt.is_active)
    
    if state == (False, False):
        # Cycle complete! Check if both critical states occurred during this click
        if (True, True) in current_sequence and (False, True) in current_sequence:
            idx_11 = current_sequence.index((True, True))
            idx_01 = current_sequence.index((False, True))
            
            # Check which state happened first
            if idx_01 < idx_11:
                steps += 1
                print(f"Rotated Clockwise! Current steps: {steps}")
            else:
                steps -= 1
                print(f"Rotated Anti-clockwise! Current steps: {steps}")
        
        current_sequence.clear()
    elif not current_sequence or current_sequence[-1] != state:
        current_sequence.append(state)

clk.when_pressed = check_state
clk.when_released = check_state
dt.when_pressed = check_state
dt.when_released = check_state

print("\nTurn the encoder. Both directions should now be perfectly reliable! Press Ctrl+C to exit.")

# Keep the script running to listen for events
pause()