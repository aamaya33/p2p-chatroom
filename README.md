# P2P Chatroom  
[![Python Tests](https://github.com/aamaya33/p2p-chatroom/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/aamaya33/p2p-chatroom/actions/workflows/python-package-conda.yml)


A peer-to-peer (P2P) chat application built to test networking concepts and for a class mini-hackathon.  

## Features  
- **Real-time messaging** – Chat between peers on different ports.  
- **Basic terminal UI** – Simple but functional interface.  
- **Offline messaging** – Store messages when a peer disconnects and deliver them upon reconnection (similar to WhatsApp).  

## Limitations  
- Uses Python (GIL limits threading efficiency).  

## How to Run  
1. Ensure Python 3 is installed.  
2. If you want to specify which port you want to use or run it locally, use:  
   ```sh
   python3 p2p.py <IP> <PORT>
3. Or you can just run and automatically assign a port by using:
   ```sh
   python3 p2p.py

Example (local testing) 

python3 p2p.py 127.0.0.1 5000 (Warning: port 1234 has weird firewalls going on with it and can't be connected to.)

## Future Work 

- Encryption
- More robust offline sending logic
- API
