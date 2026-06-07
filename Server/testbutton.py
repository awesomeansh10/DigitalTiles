from gpiozero import Button
from signal import pause

def button_pressed():
    print("Button on GPIO 26 pressed!")

def button_released():
    print("Button on GPIO 26 released!")

if __name__ == '__main__':
    print("Testing GPIO 26 button. Press Ctrl+C to exit.")
    
    # Initialize the button on GPIO 26 with an internal pull-up resistor
    test_button = Button(26, pull_up=True)
    
    test_button.when_pressed = button_pressed
    test_button.when_released = button_released
    
    # Keep the script running to listen for events
    pause()