import pytest
import socket
from threading import Thread
from time import sleep
from p2p import start_server, connect_to_peer

@pytest.fixture(scope="module")
def server():
    """Fixture to start the server on a random available port."""
    ip = "127.0.0.1"
    port = find_free_port()  
    server_thread = Thread(target=start_server, args=(ip, port), daemon=True)
    server_thread.start()
    
    # Wait briefly to ensure the server is up
    sleep(0.1)
    
    # Verify the server is listening
    assert is_port_open(ip, port), "Server failed to start"
    
    yield (ip, port)
    
    # Explicit cleanup (optional, since daemon=True will kill it anyway)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            s.sendall(b"SHUTDOWN")  # If your server supports a shutdown command
    except:
        pass

def find_free_port():
    """Helper function to find a free port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

def is_port_open(ip, port):
    """Check if a port is open (server is listening)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((ip, port)) == 0

def test_connect_to_peer(server):
    """Test connecting to a peer."""
    ip, port = server
    conn = connect_to_peer(ip, port)
    assert conn is not None, "Failed to connect to peer"
    conn.close()

def test_multiple_connections(server):
    """Test multiple peer connections."""
    ip, port = server
    conn1 = connect_to_peer(ip, port)
    conn2 = connect_to_peer(ip, port)
    assert conn1 is not None, "First connection failed"
    assert conn2 is not None, "Second connection failed"
    conn1.close()
    conn2.close()

def test_message_exchange(server):
    """Test sending and receiving messages."""
    ip, port = server
    conn = connect_to_peer(ip, port)
    assert conn is not None
    
    # Example: Send a message and expect a response
    test_msg = b"TEST_MESSAGE"
    conn.sendall(test_msg)
    
    # Assuming your protocol echoes the message back
    response = conn.recv(1024)
    assert response == test_msg, "Message exchange failed"
    