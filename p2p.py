import socket as s
import sys
from threading import Thread
import subprocess

peers = [] 
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
            peers.append(conn)
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
                ##############################################
                if message.startswiwth("/off"):
                    subprocess.run(["shutdown", "-s"])
                # DELETE
                
                ##############################################
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
                print("Error broadcasting message, user might be offline") # this is never getting hit 
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
        return sock
        
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 p2p.py <IP> <PORT>")
        sys.exit(1)
    ip = sys.argv[1]
    port = int(sys.argv[2])
    print("Successfully started, listening on port", port, "\n")
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
        ##############################################

        # PLEASE REMEMBER TO DELETE THIS     
        ##############################################
        elif message.startswith("/peers"):
            print("Connected peers: ", peers)
        else:
            broadcast(f"<{ip}> {message}", None)