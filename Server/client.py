import socketio
import time
server_url='http://tiles.anshagarwal.net:1234'
device_id = "Tile0"

def switch_active_node(node_number):
    """
    Connects to the server, sends a command to switch the active node on a device,
    and then disconnects. This function is non-blocking for the main application flow.
    """
    sio = socketio.Client()
    
    # Use a flag to avoid issues with reconnection attempts
    emitted_and_disconnecting = False

    @sio.event
    def connect():
        nonlocal emitted_and_disconnecting
        if emitted_and_disconnecting:
            return

        print("Connected to the Node.js server!")
        print(f"Sending command to switch device '{device_id}' to node number {node_number}")

        sio.emit('python_update', {
            'action': 'switch_node',
            'deviceId': device_id,
            'nodeNumber': node_number
        })
        
        emitted_and_disconnecting = True
        
        def disconnect_task():
            time.sleep(0.1)
            print("Command sent successfully. Disconnecting.")
            sio.disconnect()
            
        sio.start_background_task(disconnect_task)

    @sio.event
    def disconnect():
        print("Disconnected from server.")

    try:
        # Connect to the server. wait_timeout is a safeguard.
        sio.connect(server_url, wait_timeout=10)
        # wait() will block until sio.disconnect() is called.
        sio.wait()
    except socketio.exceptions.ConnectionError as e:
        print(f"Connection failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def connect_nodes(source, target):
    """
    Connects to the server, sends a command to add an edge between two nodes,
    and then disconnects. This function is non-blocking for the main application flow.
    """
    sio = socketio.Client()
    
    # Use a flag to avoid issues with reconnection attempts
    emitted_and_disconnecting = False

    @sio.event
    def connect():
        nonlocal emitted_and_disconnecting
        if emitted_and_disconnecting:
            return

        print("Connected to the Node.js server!")
        print(f"Sending command to connect '{source}' to '{target}'")

        sio.emit('add_edge', {
            'source': source,
            'target': target
        })
        
        emitted_and_disconnecting = True
        
        def disconnect_task():
            time.sleep(0.1)
            print("Command sent successfully. Disconnecting.")
            sio.disconnect()
            
        sio.start_background_task(disconnect_task)

    @sio.event
    def disconnect():
        print("Disconnected from server.")

    try:
        sio.connect(server_url, wait_timeout=10)
        sio.wait()
    except socketio.exceptions.ConnectionError as e:
        print(f"Connection failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def connect_tiles(source, target):
    """
    Connects to the server, sends a command to connect all nodes on a source tile 
    to all nodes on a target tile, and then disconnects.
    """
    sio = socketio.Client()
    
    # Use a flag to avoid issues with reconnection attempts
    emitted_and_disconnecting = False

    @sio.event
    def connect():
        nonlocal emitted_and_disconnecting
        if emitted_and_disconnecting:
            return

        print("Connected to the Node.js server!")
        print(f"Sending command to connect all nodes on tile '{source}' to tile '{target}'")

        sio.emit('connect_tiles', {
            'source': source,
            'target': target
        })
        
        emitted_and_disconnecting = True
        
        def disconnect_task():
            time.sleep(0.1)
            print("Command sent successfully. Disconnecting.")
            sio.disconnect()
            
        sio.start_background_task(disconnect_task)

    @sio.event
    def disconnect():
        print("Disconnected from server.")

    try:
        sio.connect(server_url, wait_timeout=10)
        sio.wait()
    except socketio.exceptions.ConnectionError as e:
        print(f"Connection failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    # This is an example of how to use the function.
    # The script will execute this, and then exit, without hanging.
    
    print("--- Calling function for the first time ---")
    switch_active_node(node_number=0)
    
    time.sleep(1) # Pause for a second to make output readable
    
    print("\n--- Calling function for the second time ---")
    switch_active_node(node_number=1)
    
    print("\n--- Calling function to connect nodes ---")
    connect_nodes(source="Tile0_node_0", target="Tile0_node_1")
    
    print("\n--- Calling function to connect tiles ---")
    connect_tiles(source="Tile0", target="Tile1")

    print("\nScript finished.")
