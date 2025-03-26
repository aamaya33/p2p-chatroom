import socket as s
import sys
from threading import Thread
from server import *
from datetime import datetime



# TODO: add DB logic to be able to 
# TODO: Add ability to change name as well 
# TODO: add ability to talk to one person at a time? maybe? 
# TODO: add ability to see peers connected -> peers as of now is list of sockets and i need to keep it like that to be able to send messages to the other socket object 
# Alternative: Dictionary {socket: (ip, port)} to keep track of peers and their addresses or we just make a list with addresses and a list with sockets and we keep them in sync
# connected_to_peer function needs to update addresses list  
# TODO: add request to each connection going outwards when connecting for the first time 
# TODO: Remote execution of things? 
# TODO: Make this an API? 

# port 1234 can't be connected to and leads to experiencing false positives

# these will have to become a table in the db, but for later until im able to actually get this to work lol
peers = {}  # {socket: {'ip': ip, 'port': port, 'status': 'online'}}
offline_peers = {}  # {socket: {'ip': ip, 'port': port, 'status': 'offline'}}

def start_server(ip, port, shutdown_event=None):
    """Run a server socket to accept incoming peer connections."""
    server = s.socket(s.AF_INET, s.SOCK_STREAM)
    server.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    server.bind((ip, port))
    server.listen(5)

    server.settimeout(0.5)  # Check for shutdown every 0.5 seconds
    while not shutdown_event.is_set() if shutdown_event else True:
        try:
            conn, addr = server.accept()
            # TODO: check to see if they are in offline to send messages
            peers[conn] = {'ip': addr[0], 'port': addr[1], 'status': 'online'}
            print("\r\033[K", end="") # get rid of the current line and print the new peer connected message
            print(f"\rNew peer connected: {addr}\n(You): ", end="")
            # Start thread to handle messages from new peer
            Thread(target=handle_peer, args=(conn, addr), daemon=True).start()
        except s.timeout:
            continue

def handle_peer(conn, addr):
    """Handle messages from a connected peer."""
    try:
        while True:
            message = conn.recv(2048).decode()
            if message:
                # clear current line to display message and make things flow nicely 
                print("\r\033[K", end="")
                print(f"\r{message}\n(You): ", end="")
                store_inbound_messages(addr, message) # FIXME: when i recieve a message and this is called, it kills the connection between peers
                broadcast(f"<{addr[0]}> {message}", conn)
            else:
                remove_peer(conn)
                break
    except Exception as e:
        print(f"Error handling peer {addr}: {e}")
        remove_peer(conn)

def update_peer_status(conn, status):
    """Update the status of a peer."""

    # this is def too basic, but we'll use it for now
    if status == 'offline' and conn in peers: 
        offline_peers[conn] = peers.pop(conn)
        offline_peers[conn]['status'] = 'offline'
        print("\r\033[K", end="")
        print(f"Peer {offline_peers[conn]['ip']}:{offline_peers[conn]['port']} has gone offline")
    elif status == 'online' and conn in offline_peers:
        peers[conn] = offline_peers.pop(conn)
        peers[conn]['status'] = 'online' 
        print(f"Peer {peers[conn]['ip']}:{peers[conn]['port']} is online")


def broadcast(message, sender_conn):
    """Send message to all peers except the sender."""
    failed = []
    for peer_con in peers.keys():
        # when someone disconnects sender_conn = None -> failed not getting updated 
        if peer_con != sender_conn:
            try:
                peer_con.send(message.encode())
            except: 
                peer_adr = peers.get(peer_con, {})
                failed.append(f"{peer_adr.get('ip', 'Unknown')}: {peer_adr.get('port', 'Unknown')}")
                update_peer_status(peer_con, 'offline')
    
    # if offline_peers: 
    #     for peer_con in offline_peers.keys():

    #         print(f"Failed to send message to peers: {failed}")

def remove_peer(conn):
    """Remove a disconnected peer."""
    update_peer_status(conn, 'offline')

def connect_to_peer(ip, port):
    """Initiate connection to another peer."""
    try:
        sock = s.socket(s.AF_INET, s.SOCK_STREAM)
        sock.connect((ip, port))

        peers[sock] = {'ip': ip, 'port': port, 'status': 'online'}
        print(f"Connected to {ip}:{port}")

        # check to see if the peer was offline 
        if sock in offline_peers: 
            peers[sock] = offline_peers.pop(sock)
        # start new thread for new person 
        Thread(target=handle_peer, args=(sock, (ip, port)), daemon=True).start()
        return sock
        
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def getopenport():
    """Get an open port for the server to listen on."""
    with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
        sock.bind(("", 0))
        return sock.getsockname()[1]


if __name__ == "__main__":
    # Either get ip/port from cmd line or get ip and open port
    if len(sys.argv) == 3:
        ip, port = sys.argv[1], int(sys.argv[2])
    else:
        hostname = s.gethostname()
        ip = s.gethostbyname(hostname)
        port = getopenport()

    indent = "\n" * 35
    print(indent,f"Successfully started. Welcom {ip} listening on port", port, "\n")
    print("Type '/connect <IP> <PORT>' to connect to a peer")
    print("Type '/peers' to list connected peers")
    print("Type '/quit' to exit\n")

    Thread(target=start_server, args=(ip, port), daemon=True).start()
    
    # User input handling
    while True:
        message = input("(You): ")
        if message.lower() == "/quit": # sometimes doesn't work
            break
        # FIXME: Handle other /commands that might not be correct 
        elif message.startswith("/connect"):
            _, *args = message.split()
            if len(args) == 2:
                connect_to_peer(args[0], int(args[1]))
            else:
                print("Invalid format. Use: /connect <IP> <PORT>")
        elif message.startswith("/peers"):
            print("Connected peers: ", peers)
        elif message.startswith("/messages"):
            messages = get_inbound_messages()
            if not messages:
                print("No messages")
            else:
                for idx, (source, message) in enumerate(messages, 1):
                    print(f"  {idx}. From {source}: {message}")
        elif message.startswith("/pending"):
            pending = get_pending_messages()
            if not pending: 
                print("No pending messages")
            else: 
                for idx, (source, message) in enumerate(pending, 1):
                    print(f"  {idx}. To {source}: {message}")
        else:
            broadcast(f"<{ip}> {message}", None)