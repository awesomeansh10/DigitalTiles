import socketio
import time
import serial
import os
from dotenv import load_dotenv
from gpiozero import RotaryEncoder, Button

# Load environment variables from .env file
load_dotenv()

# --- Global Configuration ---
server_url='http://tiles.anshagarwal.net:1234'
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

def connect_tiles(source, target):
    """
    Sends a command to connect all nodes on a source tile to all nodes on a target tile.
    """
    ensure_connection()
    print(f"Sending command to connect all nodes on tile '{source}' to tile '{target}'")
    sio.emit('connect_tiles', {
        'source': source,
        'target': target
    })

def disconnect_tiles(source, target):
    """
    Sends a command to disconnect all nodes on a source tile from all nodes on a target tile.
    """
    ensure_connection()
    print(f"Sending command to disconnect all nodes on tile '{source}' from tile '{target}'")
    sio.emit('disconnect_tiles', {
        'source': source,
        'target': target
    })

def toggle_menu():
    """
    Sends a command to toggle the menu in the drawer.
    """
    ensure_connection()
    print(f"Sending command to toggle menu for device '{device_id}'")
    sio.emit('toggle_menu', {'deviceId': device_id})

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
        encoder = RotaryEncoder(17, 18)
        previous_steps = encoder.steps

        # Initialize the button (assuming GPIO pin 27)
        button1 = Button(27)
        button2 = Button(26)
        button3 = Button(25)
        button4 = Button(24)
        menubutton = Button(22)
        menubutton_was_pressed = False

        # Initialize UART communication
        # Note: '/dev/serial0' is the default serial port on Raspberry Pi. 
        # The 2.0s timeout ensures the script doesn't freeze if no response is received.
        uart = serial.Serial('/dev/serial0', baudrate=9600, timeout=1.0)

        print("\nWaiting for encoder rotation...")
        while True:
            current_steps = encoder.steps
            if current_steps != previous_steps:
                # You can apply a modulo if you have a fixed number of nodes (e.g., current_steps % 4)
                if current_steps < 0:
                    activenode = 1
                else:
                    activenode = current_steps

                switch_active_node(node_number=activenode)
                previous_steps = current_steps
            
            # Check for button click
            if button1.is_pressed and connected_tiles[0] == 0:
                print("\nButton clicked! Transmitting message over UART...")
                uart.write(device_id.encode('utf-8'))
                if uart.in_waiting > 0:
            # 1. Read the raw bytes (e.g., b'Tile1\n')
                    incoming_bytes = uart.read(uart.in_waiting)
                    incoming_string = incoming_bytes.decode('utf-8').strip()       
                    target = incoming_string[4]  # Extract the tile number from the incoming string
                    print(f"Received message: '{incoming_string}' - connecting to {target}")
                    target1 = "Tile"+str(target)
                    connect_tiles(source=device_id, target=target1)
                    connected_tiles[0] = int(target)

            elif not button1.is_pressed and connected_tiles[0] !=0:
                target = "Tile"+str(connected_tiles[0])
                disconnect_tiles(source=device_id, target=target)
                connected_tiles[0] = 0


            if button3.is_pressed and connected_tiles[2] == 0:
                print("\nButton clicked! Transmitting message over UART...")
                uart.write(device_id.encode('utf-8'))
                if uart.in_waiting > 0:
            # 1. Read the raw bytes (e.g., b'Tile1\n')
                    incoming_bytes = uart.read(uart.in_waiting)
                    incoming_string = incoming_bytes.decode('utf-8').strip()       
                    target = incoming_string[4]  # Extract the tile number from the incoming string
                    print(f"Received message: '{incoming_string}' - connecting to {target}")
                    target1 = "Tile"+str(target)
                    connect_tiles(source=device_id, target=target1)
                    connected_tiles[2] = int(target)

            elif not button3.is_pressed and connected_tiles[2] !=0:
                target = "Tile"+str(connected_tiles[2])
                disconnect_tiles(source=device_id, target=target)
                connected_tiles[2] = 0



            if button4.is_pressed and connected_tiles[3] == 0:
                print("\nButton clicked! Transmitting message over UART...")
                uart.write(device_id.encode('utf-8'))
                if uart.in_waiting > 0:
            # 1. Read the raw bytes (e.g., b'Tile1\n')
                    incoming_bytes = uart.read(uart.in_waiting)
                    incoming_string = incoming_bytes.decode('utf-8').strip()       
                    target = incoming_string[4]  # Extract the tile number from the incoming string
                    print(f"Received message: '{incoming_string}' - connecting to {target}")
                    target1 = "Tile"+str(target)
                    connect_tiles(source=device_id, target=target1)
                    connected_tiles[3] = int(target)

            elif not button4.is_pressed and connected_tiles[3] !=0:
                target = "Tile"+str(connected_tiles[3])
                disconnect_tiles(source=device_id, target=target)
                connected_tiles[3] = 0




            if button2.is_pressed and connected_tiles[1] == 0:
                print("\nButton clicked! Transmitting message over UART...")
                uart.write(device_id.encode('utf-8'))
                if uart.in_waiting > 0:
            # 1. Read the raw bytes (e.g., b'Tile1\n')
                    incoming_bytes = uart.read(uart.in_waiting)
                    incoming_string = incoming_bytes.decode('utf-8').strip()       
                    target = incoming_string[4]  # Extract the tile number from the incoming string
                    print(f"Received message: '{incoming_string}' - connecting to {target}")
                    target1 = "Tile"+str(target)
                    connect_tiles(source=device_id, target=target1)
                    connected_tiles[1] = int(target)

            elif not button2.is_pressed and connected_tiles[1] !=0:
                target = "Tile"+str(connected_tiles[1])
                disconnect_tiles(source=device_id, target=target)
                connected_tiles[1] = 0

            # Check for menu button click
            if menubutton.is_pressed and not menubutton_was_pressed:
                toggle_menu()
                menubutton_was_pressed = True
            elif not menubutton.is_pressed:
                menubutton_was_pressed = False
            
            time.sleep(0.3)  # Small delay to prevent high CPU usage

            


    except socketio.exceptions.ConnectionError as e:
        print(f"Connection failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # 6. Disconnect at the end to allow the script to exit cleanly
        if sio.connected:
            sio.disconnect()
