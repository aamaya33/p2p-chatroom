# P2P Chatroom  

A peer-to-peer (P2P) chat application built to test networking concepts and for a class mini-hackathon.  

## Features  
- **Real-time messaging** – Chat between peers on different ports.  
- **Basic terminal UI** – Simple but functional interface.  
- **Offline messaging (WIP)** – Future goal: Store messages when a peer disconnects and deliver them upon reconnection (similar to WhatsApp).  

## Limitations  
- Uses Python (GIL limits threading efficiency).  
- Tested only locally (`localhost`).  

## How to Run  
1. Ensure Python 3 is installed.  
2. Run:  
   ```sh
   python3 p2p.py <IP> <PORT>

Example (local testing) 

python3 p2p.py 127.0.0.1 5000 (Warning: port 1234 has weird firewalls going on with it and can't be connected to.)

##Future Work 

- Offline message storage
- Bettor Error Handling
- Multi-machine testing
