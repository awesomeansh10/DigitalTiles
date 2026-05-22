import socketio
import time
import random
import threading

# Create a standard Socket.IO client
sio = socketio.Client()

# A simple transparent 1x1 PNG as a placeholder image
DUMMY_IMAGE = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII="

@sio.event
def connect():
    print("Connected to the Socket.IO server!")
    
    # Generate a random ID for the Python node
    node_id = f"python_node_{random.randint(100, 999)}"
    
    # Emulate the payload sent by drawer.html
    payload = {
        'id': node_id,
        'x': random.randint(100, 500),
        'y': random.randint(100, 500),
        'image': DUMMY_IMAGE
    }
    
    print(f"Emitting 'add_node' for {node_id}")
    sio.emit('add_node', payload)
    
    # Example of delayed edge creation
    def interact():
        time.sleep(2)
        target_id = input(f"\n[{node_id}] Enter a target node ID to connect to (or press Enter to skip): ")
        if target_id.strip():
            sio.emit('add_edge', {'source': node_id, 'target': target_id.strip()})
            print(f"Emitted 'add_edge' from {node_id} to {target_id}")

    threading.Thread(target=interact, daemon=True).start()
    
@sio.event
def disconnect():
    print("Disconnected from server")

if __name__ == '__main__':
    # Adjust the port if your Node.js server uses a different one
    SERVER_URL = 'http://localhost:3000'
    try:
        sio.connect(SERVER_URL)
        sio.wait()
    except Exception as e:
        print(f"Connection failed: {e}")