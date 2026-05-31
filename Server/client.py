import socketio
import time
try:
    import serial
    from gpiozero import RotaryEncoder, Button
    from signal import pause
except ImportError:
    print("Serial library not available.")
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# --- Global Configuration ---
server_url='http://tiles.anshagarwal.net:1234'
# server_url='http://localhost:1234'

device_id = os.environ.get("DEVICE_ID", "Tile1")
connected_tiles = [0,0,0,0]
# 1. Create a single, persistent client instance
sio = socketio.Client()

# 2. Define global event handlers for connect/disconnect events
@sio.event
def connect():
    print("Connection established with the server.")

@sio.event
def disconnect():
    print("Disconnected from the server.")

def ensure_connection():
    """Ensures the client is connected to the server before sending a command."""
    if not sio.connected:
        print(f"Connecting to {server_url}...")
        sio.connect(server_url, wait_timeout=10)

# 3. Refactor functions to simply emit events over the existing connection
def switch_active_node(node_number):
    """
    Sends a command to switch the active node on the configured device.
    """
    ensure_connection()
    print(f"Sending command to switch device '{device_id}' to node number {node_number}")
    sio.emit('python_update', {
        'action': 'switch_node',
        'deviceId': device_id,
        'nodeNumber': node_number
    })

def connect_nodes(source, target):
    """
    Sends a command to add an edge between two nodes.
    """
    ensure_connection()
    print(f"Sending command to connect '{source}' to '{target}'")
    sio.emit('add_edge', {
        'source': source,
        'target': target
    })

def connect_tiles(source, target, edge):
    """
    Sends a command to connect all nodes on a source tile to all nodes on a target tile.
    """
    ensure_connection()
    print(f"Sending command to connect all nodes on tile '{source}' to tile '{target}'")
    sio.emit('connect_tiles', {
        'source': source,
        'target': target
    })
    sio.emit('python_update', {
        'action': 'tile_connected',
        'deviceId': source,
        'targetTile': target,
        'edge': edge
    })

def disconnect_tiles(source, target, edge):
    """
    Sends a command to disconnect all nodes on a source tile from all nodes on a target tile.
    """
    ensure_connection()
    print(f"Sending command to disconnect all nodes on tile '{source}' from tile '{target}'")
    sio.emit('disconnect_tiles', {
        'source': source,
        'target': target
    })
    sio.emit('python_update', {
        'action': 'tile_disconnected',
        'deviceId': source,
        'edge': edge
    })




def toggle_menu():
    """
    Sends a command to toggle the menu in the drawer.
    """
    ensure_connection()
    print(f"Sending command to toggle menu for device '{device_id}'")
    sio.emit('toggle_menu', {'deviceId': device_id})


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
            
            if steps <= 0:
                activenode = abs(steps)
                if activenode == 0:
                    activenode = 1
            else:
                activenode = steps

            switch_active_node(node_number=activenode)

        current_sequence.clear()
    elif not current_sequence or current_sequence[-1] != state:
        current_sequence.append(state)


tileconnections = [0,0,0,0]

def button1_pressed():
    print("\nButton clicked! Transmitting message over UART...")
    uart.write(device_id.encode('utf-8'))
    if uart.in_waiting > 0:
        incoming_bytes = uart.read(uart.in_waiting)
        incoming_string = incoming_bytes.decode('utf-8').strip()       
        target = incoming_string[4]  # Extract the tile number from the incoming string
        print(f"Received message: '{incoming_string}' - connecting to {target}")
        target1 = "Tile"+str(target)
        connect_tiles(source=device_id, target=target1, edge='top')
        tileconnections[0] = int(target)

def button1_released():
    target = "Tile"+str(tileconnections[0])
    disconnect_tiles(source=device_id, target=target, edge='top')
    tileconnections[0] = 0


def button2_pressed():
    print("\nButton clicked! Transmitting message over UART...")
    uart.write(device_id.encode('utf-8'))
    if uart.in_waiting > 0:
        incoming_bytes = uart.read(uart.in_waiting)
        incoming_string = incoming_bytes.decode('utf-8').strip()       
        target = incoming_string[4]  # Extract the tile number from the incoming string
        print(f"Received message: '{incoming_string}' - connecting to {target}")
        target1 = "Tile"+str(target)
        connect_tiles(source=device_id, target=target1, edge='right')
        tileconnections[1] = int(target)

def button2_released():
    target = "Tile"+str(tileconnections[1])
    disconnect_tiles(source=device_id, target=target, edge='right')
    tileconnections[1] = 0


def button3_pressed():
    print("\nButton clicked! Transmitting message over UART...")
    uart.write(device_id.encode('utf-8'))
    if uart.in_waiting > 0:
        incoming_bytes = uart.read(uart.in_waiting)
        incoming_string = incoming_bytes.decode('utf-8').strip()       
        target = incoming_string[4]  # Extract the tile number from the incoming string
        print(f"Received message: '{incoming_string}' - connecting to {target}")
        target1 = "Tile"+str(target)
        connect_tiles(source=device_id, target=target1, edge='bottom')
        tileconnections[2] = int(target)

def button3_released():
    target = "Tile"+str(tileconnections[2])
    disconnect_tiles(source=device_id, target=target, edge='bottom')
    tileconnections[2] = 0



def button4_pressed():
    print("\nButton clicked! Transmitting message over UART...")
    uart.write(device_id.encode('utf-8'))
    if uart.in_waiting > 0:
        incoming_bytes = uart.read(uart.in_waiting)
        incoming_string = incoming_bytes.decode('utf-8').strip()       
        target = incoming_string[4]  # Extract the tile number from the incoming string
        print(f"Received message: '{incoming_string}' - connecting to {target}")
        target1 = "Tile"+str(target)
        connect_tiles(source=device_id, target=target1, edge='left')
        tileconnections[3] = int(target)

def button4_released():
    target = "Tile"+str(tileconnections[3])
    disconnect_tiles(source=device_id, target=target, edge='left')
    tileconnections[3] = 0


if __name__ == '__main__':
    try:
        # 4. Connect once at the start of the script
        ensure_connection()

        # # 5. Call functions to send commands over the open connection
        # print("--- Sending command to switch to node 0 ---")
        # switch_active_node(node_number=0)
        # time.sleep(1) # Pauses are for visual pacing, not for technical reasons
        
        # print("\n--- Sending command to switch to node 1 ---")
        # switch_active_node(node_number=1)
        # time.sleep(1)
        
        # print("\n--- Sending command to connect nodes ---")
        # connect_nodes(source="Tile0_node_0", target="Tile0_node_1")
        # time.sleep(1)
        
        # print("\n--- Sending command to connect tiles ---")
        # connect_tiles(source="Tile0", target="Tile1")
        # time.sleep(1)

        # print("\n--- Sending command to disconnect tiles ---")
        # disconnect_tiles(source="Tile0", target="Tile1")
        # time.sleep(1)

        # print("\nAll commands sent. Script finished.")

        # Initialize the rotary encoder (assuming GPIO pins 17 and 18)
        # Note: You'll need to run this on a Raspberry Pi with the gpiozero library installed.

        # Initialize the button (assuming GPIO pin 27)
        button1 = Button(22, pull_up=True)
        button2 = Button(26, pull_up=True)
        button3 = Button(25, pull_up=True)
        button4 = Button(24, pull_up=True)
        menubutton = Button(0, pull_up=True)
        menubutton_was_pressed = False
        clk = Button(17, pull_up=True)
        dt = Button(27, pull_up=True)

        steps = 0
        current_sequence = []

        # Initialize UART communication
        # Note: '/dev/serial0' is the default serial port on Raspberry Pi. 
        # The 2.0s timeout ensures the script doesn't freeze if no response is received.
        uart = serial.Serial('/dev/serial0', baudrate=9600, timeout=1.0)

        print("\nWaiting for encoder rotation...")
        


        clk.when_pressed = check_state
        clk.when_released = check_state
        dt.when_pressed = check_state
        dt.when_released = check_state


        menubutton.when_pressed = toggle_menu

        button1.when_pressed = button1_pressed
        button1.when_released = button1_released
        button2.when_pressed = button2_pressed
        button2.when_released = button2_released
        button3.when_pressed = button3_pressed
        button3.when_released = button3_released
        button4.when_pressed = button4_pressed
        button4.when_released = button4_released

        pause()


    except socketio.exceptions.ConnectionError as e:
        print(f"Connection failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # 6. Disconnect at the end to allow the script to exit cleanly
        if sio.connected:
            sio.disconnect()
