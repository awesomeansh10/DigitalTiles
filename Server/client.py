import socketio
import random
import time

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print("Connected to the Node.js server!")
    
    # Example 1: Trigger the 'add_node' function
    node_id = f"python_node_{random.randint(100, 999)}"
    tile_id = "Tile_Python"
    
    print(f"Triggering 'add_node' for {node_id}")
    sio.emit('add_node', {
        'id': node_id,
        'tileId': tile_id,
        'x': random.uniform(100, 400),
        'y': random.uniform(100, 400),
        'image': 'data:,' # Provide a base64 image string here if needed
    })
    
    # Example 3: Send a custom event that drawer.html will listen to
    print("Sending 'python_update' command to change brush color")
    sio.emit('python_update', {
        'action': 'change_color',
        'color': '#a855f7' # Changes brush to purple
    })
    
    # Example 4: Send command to switch active node
    target_device = "Tile0" # Also known as Tile ID
    target_node = 2 # Node number
    print(f"Sending 'python_update' command to switch active node on {target_device} to node number {target_node}")
    sio.emit('python_update', {
        'action': 'switch_node',
        'deviceId': target_device,
        'nodeNumber': target_node
    })

    # Example 2: Trigger the 'add_edge' function to connect nodes
    # sio.emit('add_edge', {'source': node_id, 'target': 'node_1'})

@sio.event
def disconnect():
    print("Disconnected from server")

if __name__ == '__main__':
    # Connect to your Node.js Socket.IO server.
    # Adjust the URL and port (e.g., 3000) to match your server configuration.
    sio.connect('http://tiles.anshagarwal.net:1234')
    
    # Keep the connection alive
    sio.wait()
