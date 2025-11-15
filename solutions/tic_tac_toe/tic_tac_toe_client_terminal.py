"""
This file contains logic for a remote client to connect to a tic tac toe server and play a game
"""

import zmq
import time
import socket

def discover_server(port, timeout=10):
    """Listen for broadcast messages to discover the server IP."""
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Allow the socket to reuse addresses (helpful when restarting quickly)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind to all interfaces on a chosen port
    sock.bind(("", port))   # "" means INADDR_ANY, so it listens on all interfaces

    print("Searching for Tic-Tac-Toe server via LAN broadcast...")
    start = time.time()
    server_ip = None

    while time.time() - start < timeout:
        try:
            data, addr = sock.recvfrom(1024)  # buffer size 1024 bytes
            string = str(data,'utf-8')
            fields = string.split(" ")
            if fields[1].strip() == "server_info":
                server_ip = fields[2].strip()
                port_to_clients = fields[3].strip()
                port_from_clients = fields[4].strip()
                print(f"Discovered server at {server_ip}")
                break
        except:
            time.sleep(0.5)

    sock.close()
    return server_ip,port_to_clients,port_from_clients

# Wraps the client send message with a topic tag
def send_client_message(pub_socket, message_string):
    pub_socket.send_string(f"client/ {message_string}")

def main():


    port_to_broadcast = 41110

    # Find the server
    server_ip,port_to_clients,port_from_clients = discover_server(port_to_broadcast)
    if not server_ip:
        print("No server found. Exiting.")
        return
    print(f"Found server at {server_ip}")

    # Get the user information
    username = input("Enter your username: ").strip()

    # Setup the sockets
    context = zmq.Context()
    pub_socket = context.socket(zmq.PUB)
    sub_socket = context.socket(zmq.SUB)

    pub_socket.connect(f"tcp://{server_ip}:{port_from_clients}")
    sub_socket.connect(f"tcp://{server_ip}:{port_to_clients}")
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "server/")

    print("Connecting to server...")
    # Give the server time to register you
    time.sleep(0.5)
    send_client_message(pub_socket,f"request join {username}")

    # State variables
    my_turn = False
    running = True

    try:
        while running:
            try:
                # Get messages
                msg = sub_socket.recv_string(flags=zmq.NOBLOCK)

                # Parse
                tokens = msg.split()

                if not tokens:
                    continue

                cmd = tokens[1]

                if cmd == "joined":
                    # Inform player joined game
                    print(f"Player joined: {tokens[-1]}")

                elif cmd == "update":
                    # Get the remaining string as the board string
                    board = msg.split(sep="update ")[1]
                    # Print it
                    print("\nGame Board:\n" + board)

                elif cmd == "turn":
                    # Check if turn and inform user of instructions
                    turn_name = tokens[2]
                    my_turn = (turn_name == username)
                    if my_turn:
                        print("It's your turn!")
                    else:
                        print("Please wait for the other player to make their move")

                elif cmd == "won":
                    # Inform of winner
                    print(f"Game over! Winner: {tokens[2]}")
                    running = False

                elif cmd == "draw":
                    # Inform of draw
                    print("Game ended in a draw.")
                    running = False

                elif cmd == "error":
                    # Inform of error
                    print("Server error — disconnecting.")
                    running = False

            except zmq.Again:
                # Try to listen again
                pass

            # If turn to move
            if my_turn:
                # Get user input and sanatize it
                move = input("Enter your move (col row) or 'resign': ").strip().lower()
                if move == "resign":
                    # Quit message
                    send_client_message(pub_socket,f"resign {username}")
                    # Exit flag
                    running = False
                    break
                try:
                    # Sanatize
                    col, row = map(int, move.split())
                    if 0 <= col <= 2 and 0 <= row <= 2:
                        # Send
                        send_client_message(pub_socket,f"{col} {row} {username}")
                        my_turn = False
                    else:
                        # Redirect user to try again
                        print("Invalid move — must be between 0 and 2.")
                except ValueError:
                    print("Invalid input format. Use two numbers or 'resign'.")

            time.sleep(0.05)

    except KeyboardInterrupt:
        # Quit game
        print("\nExiting game.")
        send_client_message(pub_socket,f"resign {username}")
        running = False        
    finally:
        pub_socket.close()
        sub_socket.close()
        context.term()

if __name__ == "__main__":
    main()
