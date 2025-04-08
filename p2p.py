import socket as s
import sys
from threading import Thread, Event
from server import *
from datetime import datetime


# TODO: Add ability to change name as well 
# TODO: add ability to talk to one person at a time? maybe? 
# TODO: add ability to see peers connected -> peers as of now is list of sockets and i need to keep it like that to be able to send messages to the other socket object 
# Alternative: Dictionary {socket: (ip, port)} to keep track of peers and their addresses or we just make a list with addresses and a list with sockets and we keep them in sync
# connected_to_peer function needs to update addresses list  
# TODO: add request to each connection going outwards when connecting for the first time 
# TODO: Remote execution of things? 
# TODO: Make this an API? 

# port 1234 can't be connected to and leads to experiencing false positives

# these will have to become a table in the db, but for later until im able to actually get this to work lol also wouldn't it be better to keep it locally cached?
# seems like queries could be slow if we have to go to the db every time we want to check if a peer is online or offline
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
            matches = [peer for peer in offline_peers.values() if peer['ip'] == addr[0]]

            if matches:
                peers[conn] = {'ip': addr[0], 'port': addr[1], 'status': 'online'}
                print("\r\033[K", end="")
                print(f"Peer {peers[conn]['ip']}:{peers[conn]['port']} is back online\nYou: ", end="")
                send_pending_messages(source=s.gethostbyname(s.gethostname())) 
                peers[conn]['status'] = 'online'
            else:
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
        print(f"Peer {offline_peers[conn]['ip']}:{offline_peers[conn]['port']} has gone offline\n(You): ", end="")
    elif status == 'online' and conn in offline_peers:
        peers[conn] = offline_peers.pop(conn)
        peers[conn]['status'] = 'online' 
        print(f"Peer {peers[conn]['ip']}:{peers[conn]['port']} is online\n(You): ", end="")


def broadcast(message, sender=None):
    """Send message to all peers except the sender."""
    if peers:
        for peer_con in peers.keys():
            if peer_con != sender: 
                try:
                    peer_con.send(message.encode())
                except: 
                    peer_adr = peers.get(peer_con, {})
                    print(f"Failed to send message to {peer_adr['ip']}:{peer_adr['port']}")
                    update_peer_status(peer_con, 'offline')
    
    elif offline_peers:
        # if there are offline peers 
        # get the IP and store the message to be sent store_pending_message
        for addr in offline_peers.values():
                ip = addr['ip']
                try:
                    store_pending_message(ip, message)
                except Exception as e: 
                    print(f"Failed to store message to {ip}: {e}")
        
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
    
def send_pending_messages(source=None):
    """Send all pending messages to their destinations."""
    pending = get_pending_messages()
    if not pending: 
        return
    
    if source is None:
        source = s.gethostbyname(s.gethostname())
    
    # this isn't the most robust logic ever, but this is good enough for the sake of this project
    for destination, message in pending:
        try:
            broadcast(f"<{source}> {message}")
            mark_message_as_read(destination, message)
        except Exception as e:
            print(f"Error sending pending message: {e}")

def main():
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

    shutdown_event = Event() 
    server_thread = Thread(target=start_server, args=(ip,port,shutdown_event), daemon=True)
    server_thread.start()
    
    # User input handling
    while True:
        message = input("(You): ")
        if message.lower() == "/quit": # sometimes doesn't work
            print("Shutting down...")
            shutdown_event.set()

            # add all connections to offline_peers
            for peer in peers.keys():
                offline_peers[peer] = peers[peer]
                
            # close all connections
            # FIXME: extra you: being printed when closing out
            print("Closing connections...")
            for peer in offline_peers.keys():
                try:
                    if offline_peers[peer]['status'] == 'online':
                        peer.shutdown(s.SHUT_RDWR)
                        peer.close()
                        offline_peers[peer]['status'] = 'offline' # done for the sake of knowing where logic willl be on the db 
                except Exception as e:
                    print(f"Error closing connection: {e}")
                    pass
            
            server_thread.join(timeout=5)
            break
        # FIXME: Handle other /commands that might not be correct 
        elif message.startswith("/connect"):
            _, *args = message.split()
            if len(args) == 2:
                connect_to_peer(args[0], int(args[1]))
            else:
                print("Invalid format. Use: /connect <IP> <PORT>")
        elif message.startswith("/peers"):
            if not peers:
                print("No connected peers")
            else:
                print("Connected peers: ")
                for idx, (peer, details) in enumerate(peers.items(), 1):
                    print(f"  {idx}. {details['ip']}:{details['port']}")
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
            broadcast(f"<{ip}> {message}")

if __name__ == "__main__":
    main()