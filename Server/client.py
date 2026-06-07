import socketio
import time
import os
from dotenv import load_dotenv

try:
    from gpiozero import RotaryEncoder, Button
    from signal import pause
    import pigpio # Replacing hardware serial with pigpio for multi-port software serial
except ImportError:
    print("Required hardware libraries not available. Run: sudo apt-get install pigpio && pip install gpiozero pigpio")

# Load environment variables from .env file
load_dotenv()

# --- Global Configuration ---
server_url = 'http://tiles.anshagarwal.net:1234'
# server_url = 'http://localhost:1234'

device_id = os.environ.get("DEVICE_ID", "Tile1")

# 1. Create a single, persistent client instance
sio = socketio.Client()

# --- Pogo Pin Mesh Configuration ---
# You must wire your pogo pins to these GPIO numbers.
# Remember the crossover rule: Your pogo cables must route TX to RX, and RX to TX!
BAUD_RATE = 9600
PORTS = {
    'left':    {'tx': 20,  'rx': 21,  'connected_to': None, 'cb': None},
    'bottom':  {'tx': 12, 'rx': 7, 'connected_to': None, 'cb': None},
    'right': {'tx': 25, 'rx': 8, 'connected_to': None, 'cb': None},
    'top':   {'tx': 24, 'rx': 23, 'connected_to': None, 'cb': None}
}

# Connect to the local pigpio daemon
pi = pigpio.pi()
if not pi.connected:
    print("Failed to connect to pigpiod. Run 'sudo systemctl start pigpiod'")
    exit()

# --- Socket.io Event Handlers ---
@sio.event
def connect():
    print("Connection established with the server.")

@sio.event
def disconnect():
    print("Disconnected from the server.")

def ensure_connection():
    if not sio.connected:
        print(f"Connecting to {server_url}...")
        try:
            sio.connect(server_url, wait_timeout=10)
        except Exception as e:
            print(f"Socket connection failed: {e}")

def switch_active_node(node_number):
    ensure_connection()
    print(f"Switching device '{device_id}' to node number {node_number}")
    sio.emit('python_update', {
        'action': 'switch_node',
        'deviceId': device_id,
        'nodeNumber': node_number
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
    ensure_connection()
    print(f"Toggling menu for device '{device_id}'")
    sio.emit('toggle_menu', {'deviceId': device_id})


# --- Rotary Encoder Logic ---
steps = 0
current_sequence = []

def check_state():
    global current_sequence, steps
    state = (clk.is_active, dt.is_active)
    
    if state == (False, False):
        if (True, True) in current_sequence and (False, True) in current_sequence:
            idx_11 = current_sequence.index((True, True))
            idx_01 = current_sequence.index((False, True))
            
            if idx_01 < idx_11:
                steps += 1
            else:
                steps -= 1
            
            # Only change the active node when the encoder has moved 2 steps
            if steps % 2 == 0:
                logical_steps = steps // 2
                activenode = abs(logical_steps) + 1
                
                switch_active_node(node_number=activenode)

        current_sequence.clear()
    elif not current_sequence or current_sequence[-1] != state:
        current_sequence.append(state)


# --- Pogo Mesh Networking Logic ---

def execute_handshake(edge):
    """Executes the two-way ID exchange when a connection is made."""
    port = PORTS[edge]
    rx_pin = port['rx']
    tx_pin = port['tx']
    
    print(f"\n[{edge.upper()}] Starting handshake...")

    # 1. Open background listening buffer FIRST so we don't miss their transmission
    try:
        pi.bb_serial_read_open(rx_pin, BAUD_RATE)
    except pigpio.error:
        pi.bb_serial_read_close(rx_pin)
        pi.bb_serial_read_open(rx_pin, BAUD_RATE)

    # 2. Transmit our Device ID
    msg = f"{device_id}\n".encode('utf-8')
    pi.wave_clear()
    pi.wave_add_serial(tx_pin, BAUD_RATE, msg)
    wave_id = pi.wave_create()
    pi.wave_send_once(wave_id)
    
    while pi.wave_tx_busy():
        time.sleep(0.01)

    # 3. Listen for their Device ID
    timeout = time.time() + 1.5
    response = ""
    while time.time() < timeout:
        count, data = pi.bb_serial_read(rx_pin)
        if count > 0:
            response += data.decode('utf-8', errors='ignore')
            if '\n' in response:
                break
        time.sleep(0.01)

    # 4. Handle Result
    if response:
        target = response.strip()
        print(f"[{edge.upper()}] SUCCESS: Connected to {target}")
        port['connected_to'] = target
        connect_tiles(source=device_id, target=target, edge=edge)
    else:
        print(f"[{edge.upper()}] FAILED: Handshake timed out.")
        pi.bb_serial_read_close(rx_pin)

    # 5. After handshake, switch to watching for a physical disconnect (FALLING edge)
    port['cb'] = pi.callback(rx_pin, pigpio.FALLING_EDGE, make_disconnect_callback(edge))


def make_connect_callback(edge):
    """Factory function for RISING edge (Connection) interrupts."""
    def cb(gpio, level, tick):
        if level == 1:
            time.sleep(0.05) # Debounce pogo spring
            if pi.read(gpio) == 1:
                # Disable this interrupt so incoming data doesn't trigger it
                PORTS[edge]['cb'].cancel()
                execute_handshake(edge)
    return cb

def make_disconnect_callback(edge):
    """Factory function for FALLING edge (Disconnection) interrupts."""
    def cb(gpio, level, tick):
        if level == 0:
            time.sleep(0.05) # Debounce
            if pi.read(gpio) == 0:
                print(f"\n[{edge.upper()}] Physical disconnect detected.")
                port = PORTS[edge]
                
                if port['connected_to']:
                    disconnect_tiles(source=device_id, target=port['connected_to'], edge=edge)
                    port['connected_to'] = None
                
                try:
                    pi.bb_serial_read_close(gpio)
                except pigpio.error:
                    pass
                
                # Reset interrupt to watch for a new connection (RISING edge)
                port['cb'].cancel()
                port['cb'] = pi.callback(gpio, pigpio.RISING_EDGE, make_connect_callback(edge))
    return cb

def setup_pogo_ports():
    """Initializes all 4 ports to idle state and sets up connect traps."""
    print("Initializing Pogo Pin Ports...")
    for edge, config in PORTS.items():
        # Set RX to pull-down (0V when empty)
        pi.set_mode(config['rx'], pigpio.INPUT)
        pi.set_pull_up_down(config['rx'], pigpio.PUD_DOWN)
        
        # Set TX to Output and drive HIGH (3.3V)
        pi.set_mode(config['tx'], pigpio.OUTPUT)
        pi.write(config['tx'], 1)
        
        # Trap the RISING edge (0V -> 3.3V)
        config['cb'] = pi.callback(config['rx'], pigpio.RISING_EDGE, make_connect_callback(edge))


if __name__ == '__main__':
    try:
        ensure_connection()

        # Initialize hardware controls
        menubutton = Button(26, pull_up=True)
        clk = Button(17, pull_up=True)
        dt = Button(27, pull_up=True)

        clk.when_pressed = check_state
        clk.when_released = check_state
        dt.when_pressed = check_state
        dt.when_released = check_state
        menubutton.when_pressed = toggle_menu

        # Initialize the smart Pogo Pin mesh network
        setup_pogo_ports()

        print("\nTile is active. Waiting for connections or encoder rotation...")
        pause()

    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Clean up daemons and connections on exit
        for edge, config in PORTS.items():
            if config['cb']:
                config['cb'].cancel()
            try:
                pi.bb_serial_read_close(config['rx'])
            except:
                pass
        pi.stop()
        if sio.connected:
            sio.disconnect()