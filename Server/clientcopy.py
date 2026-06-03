import socketio
import time

# Load environment variables from .env file

# --- Global Configuration ---
server_url='http://127.0.0.1:1234'
device_id = "Tile1"
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
    ensure_connection()
    print(f"Connecting tile '{source}' to tile '{target}' on the {edge} edge")
    sio.emit('connect_tiles', {'source': source, 'target': target})
    sio.emit('python_update', {
        'action': 'tile_connected',
        'deviceId': source,
        'targetTile': target,
        'edge': edge
    })

def disconnect_tiles(source, target, edge):
    ensure_connection()
    print(f"Disconnecting tile '{source}' from tile '{target}' on the {edge} edge")
    sio.emit('disconnect_tiles', {'source': source, 'target': target})
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

if __name__ == '__main__':
    try:
        # 4. Connect once at the start of the script
        ensure_connection()
        for i in range(10):
            input("Press Enter to toggle the menu...")
            toggle_menu()


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
        # disconnect_tiles(source="Tile0", target="Tile1", edge="right")
        # time.sleep(1)

        # print("\nAll commands sent. Script finished.")

        # Initialize the rotary encoder (assuming GPIO pins 17 and 18)
        # Note: You'll need to run this on a Raspberry Pi with the gpiozero library installed.


            


    except socketio.exceptions.ConnectionError as e:
        print(f"Connection failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # 6. Disconnect at the end to allow the script to exit cleanly
        if sio.connected:
            sio.disconnect()
