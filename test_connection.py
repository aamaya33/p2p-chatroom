import pytest
import socket
import time
import os
import sqlite3
from threading import Thread, Event
from p2p import start_server, connect_to_peer, getopenport, broadcast, update_peer_status
from server import get_pending_messages, get_inbound_messages, mark_message_as_read

@pytest.fixture(scope="function")
def clean_db():
    """Remove test database before tests"""
    if os.path.exists("messages.db"):
        # Just clean the tables instead of deleting the DB
        conn = sqlite3.connect("messages.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM outbound_messages")
        cursor.execute("DELETE FROM inbound_messages")
        conn.commit()
        conn.close()
    yield
    # No cleanup needed after tests

@pytest.fixture(scope="function")
def server_fixture(clean_db):
    """Fixture to start a server for testing."""
    ip = "127.0.0.1"
    port = find_free_port()
    shutdown_event = Event()
    
    server_thread = Thread(target=start_server, args=(ip, port, shutdown_event), daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(0.2)
    
    yield (ip, port, shutdown_event)
    
    # Cleanup
    shutdown_event.set()
    time.sleep(0.2)

def find_free_port():
    """Find an available port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

def test_connect_to_peer(server_fixture):
    """Test basic connection to a peer."""
    ip, port, _ = server_fixture
    
    # Connect to server
    client = connect_to_peer(ip, port)
    assert client is not None, "Connection to peer failed"

    # Verify connection works by sending a test message
    test_msg = "TEST_CONNECTION"
    client.send(test_msg.encode())
    time.sleep(0.1)
    
    # Clean up
    client.close()

def test_message_exchange(server_fixture, clean_db):
    """Test sending and receiving messages between peers."""
    ip, port, _ = server_fixture
    
    # Create a client that connects to our server
    client = connect_to_peer(ip, port)
    assert client is not None, "Connection to peer failed"
    
    # Set up a receiving socket to simulate another peer
    receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver_port = find_free_port()
    receiver.bind(("127.0.0.1", receiver_port))
    receiver.listen(1)
    receiver.settimeout(1)
    
    # Connect to the receiver from the client
    connect_to_peer("127.0.0.1", receiver_port)
    
    # Accept the connection
    conn, _ = receiver.accept()
    
    # Send test message
    test_msg = "<127.0.0.1> TEST_MESSAGE"
    client.send(test_msg.encode())
    
    # Wait for message processing
    time.sleep(0.2)
    
    # Check if message was stored in database
    messages = get_inbound_messages()
    assert len(messages) > 0, "Message was not stored in the database"
    
    # Clean up
    conn.close()
    receiver.close()
    client.close()

def test_offline_messaging(server_fixture, clean_db):
    """Test storing messages when peer is offline and delivering them when they come back online."""
    ip, port, shutdown_event = server_fixture
    
    # Create the first peer
    client = connect_to_peer(ip, port)
    assert client is not None, "Connection to peer failed"
    
    # Get info about the peer
    peer_ip = "127.0.0.1"  # We know this is localhost in tests
    
    # Simulate peer going offline
    client.close()
    time.sleep(0.2)
    
    # Broadcast message to offline peer
    message = f"<{ip}> Message to offline peer"
    broadcast(message)
    
    # Check if message was stored as pending
    pending = get_pending_messages()
    assert len(pending) > 0, "Message was not stored for offline peer"
    
    # Client reconnects
    new_client = connect_to_peer(ip, port)
    assert new_client is not None, "Reconnection failed"
    time.sleep(0.2)
    
    # Clean up
    new_client.close()

def test_multiple_connections(server_fixture):
    """Test handling multiple peer connections."""
    ip, port, _ = server_fixture
    
    # Connect multiple clients
    clients = []
    for _ in range(3):
        client = connect_to_peer(ip, port)
        assert client is not None, "Connection to peer failed"
        clients.append(client)
    
    # Make sure all connections are active
    for i, client in enumerate(clients):
        test_msg = f"TEST_FROM_CLIENT_{i}"
        client.send(test_msg.encode())
    
    time.sleep(0.2)
    
    # Clean up
    for client in clients:
        client.close()

if __name__ == "__main__":
    pytest.main(["-v"])