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
    
    sleep(0.1)
    
    # Verify the server is listening
    assert is_port_open(ip, port), "Server failed to start"
    
    yield (ip, port)

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

def test_message_exchange():
    """Test sending and receiving messages between two peers."""
    # Start two servers on different ports
    ip = "127.0.0.1"
    port1 = find_free_port()
    port2 = find_free_port()
    
    server1_thread = Thread(target=start_server, args=(ip, port1), daemon=True)
    server1_thread.start()
    sleep(0.1)
    
    server2_thread = Thread(target=start_server, args=(ip, port2), daemon=True)
    server2_thread.start()
    sleep(0.1)
    
    # Connect peer2 to peer1
    conn = connect_to_peer(ip, port1)
    assert conn is not None
    
    # Create a test client to connect to peer2 and receive the broadcast
    test_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_client.connect((ip, port2))
    
    # Send a message from peer2 to peer1
    test_msg = "TEST_MESSAGE"
    conn.send(test_msg.encode())
    
    # Receive the broadcasted message on the test client
    response = test_client.recv(1024).decode()
    assert test_msg in response, "Message broadcasting failed"
    
    conn.close()
    test_client.close()
    