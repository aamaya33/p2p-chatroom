import socket as s
import select
import sys
from threading import Thread

# Global list to track all connected peers
peers = []
# FIXME: add ability to talk to multiple peers at once
def start_server(ip, port):
    """Run a server socket to accept incoming peer connections."""
    server = s.socket(s.AF_INET, s.SOCK_STREAM)
    server.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    server.bind((ip, port))
    server.listen(5)
    # print(f"Listening for peers on {ip}:{port}...")

    while True:
        conn, addr = server.accept()
        peers.append(conn)
        print(f"\nNew peer connected: {addr}")
        # Start thread to handle messages from this peer
        Thread(target=handle_peer, args=(conn, addr), daemon=True).start()

def handle_peer(conn, addr):
    """Handle messages from a connected peer."""
    try:
        while True:
            message = conn.recv(2048).decode()
            if message:
                # clear current line to display message and make things flow nicely 
                print("\r\033[K", end="")
                print(f"\r{message}\n(You): ", end="")
                broadcast(f"<{addr[0]}> {message}", conn)
            else:
                remove_peer(conn)
                break
    except:
        remove_peer(conn)

def broadcast(message, sender_conn):
    """Send message to all peers except the sender."""
    for peer in peers:
        if peer != sender_conn:
            try:
                peer.send(message.encode())
            except: # might have to remove this piece of logic espeically if we want to send messages to peers even when they disconnect
                remove_peer(peer)

def remove_peer(conn):
    """Remove a disconnected peer."""
    if conn in peers:
        peers.remove(conn)
        conn.close()

def connect_to_peer(ip, port):
    """Initiate connection to another peer."""
    try:
        sock = s.socket(s.AF_INET, s.SOCK_STREAM)
        sock.connect((ip, port))
        peers.append(sock)
        print(f"Connected to {ip}:{port}")
        # start new thread for new person 
        Thread(target=handle_peer, args=(sock, (ip, port)), daemon=True).start()
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 p2p.py <IP> <PORT>")
        sys.exit(1)
    ip = sys.argv[1]
    port = int(sys.argv[2])
    print("Successfully started, listening on port", port, "\n")
    print("Type '/connect <IP> <PORT>' to connect to a peer")
    
    # Start server thread
    Thread(target=start_server, args=(ip, port), daemon=True).start()
    
    # User input handling
    while True:
        message = input("(You): ")
        if message.lower() == "/quit":
            break
        elif message.startswith("/connect"):
            _, *args = message.split()
            if len(args) == 2:
                connect_to_peer(args[0], int(args[1]))
            else:
                print("Invalid format. Use: /connect <IP> <PORT>")
        else:
            broadcast(f"<{ip}> {message}", None)