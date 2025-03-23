import socket as s
import select
import sys


# Create a socket object
server = s.socket(s.AF_INET, s.SOCK_STREAM)
server.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1) 

if len(sys.argv) != 3:
    print("Usage: python3 server.py <port>")
    sys.exit(1)

# Get ip and port to bind the server 
IP_addr = str(sys.argv[1])
PORT_num = int(sys.argv[2])

server.bind((IP_addr, PORT_num))

server.listen(5) # server listens to 5 clients

clients = []

def client_thread(conn, addr):
    conn.send("PeePoo")

    # Revieve data from client
    while True:
        try:
            message = conn.recv(2048)
            if message:
                print("<" + addr[0] + "> " + message)

                # Send data to all clients
                message_to_send = "<" + addr[0] + "> " + message
                broadcast(message_to_send, conn)
            else:
                remove(conn) 
        except: 
            continue