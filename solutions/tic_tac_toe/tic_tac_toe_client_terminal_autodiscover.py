"""
Terminal-mode tic-tac-toe client for the example server.

This module implements a minimal command-line client that can discover a
local tic-tac-toe server via UDP broadcast, connect using ZeroMQ PUB/SUB,
and participate in a game by sending simple textual commands.

Design goals:
- Keep the client simple and easy to read for educational purposes.
- Use UDP broadcast discovery so the client does not need a priori server IP.
- Communicate with the server using topic-prefixed strings:
    * Outgoing: "client/ <payload>"
    * Incoming: messages prefixed with "server/" and a command token.

Protocol notes (as expected by this client and the example server):
- Discovery broadcast payload is expected to include the token "server_info"
  followed by the server IP and two ports: <port_to_clients> <port_from_clients>.
- After discovery:
    - Client connects a PUB socket to port_from_clients (to send to server).
    - Client connects a SUB socket to port_to_clients (to receive from server).
    - Client subscribes to messages starting with topic "server/".
- Typical server commands received via SUB:
    - "server/ joined <username>"
    - "server/ update <board-drawing>"
    - "server/ turn <username>"
    - "server/ won <username>"
    - "server/ draw"
    - "server/ error"

Usage:
    python tic_tac_toe_client_terminal.py

This script is intentionally synchronous and blocking in places (input()),
because it is designed for manual terminal use rather than as a background
service. It uses short sleeps and non-blocking ZMQ recv to remain responsive.
"""
import zmq
import time
import socket


def discover_server(port, timeout=10):
    """
    Listen for a UDP broadcast to discover the server IP and ports.

    The function binds a UDP socket to all interfaces on the provided
    port and waits up to `timeout` seconds for a broadcast message that
    contains the token "server_info". When found, it extracts and returns
    the server IP and two ports encoded in the broadcast payload.

    Expected broadcast format (whitespace-separated):
        <whatever> server_info <server_ip> <port_to_clients> <port_from_clients>

    Parameters:
        port (int): UDP port to bind to for discovery messages.
        timeout (int): Maximum seconds to wait before giving up.

    Returns:
        tuple: (server_ip, port_to_clients, port_from_clients)
            - server_ip (str or None): the discovered server IP (None on timeout).
            - port_to_clients (str): port string server uses to publish updates.
            - port_from_clients (str): port string server expects clients to publish to.

    Notes:
        - The port strings are returned as strings because they are taken
          directly from the broadcast text. Callers may convert to int.
        - This function blocks but uses small sleep intervals to be
          robust in interactive use.
    """
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Allow the socket to reuse addresses (helpful when restarting quickly)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind to all interfaces on a chosen port; "" means INADDR_ANY.
    sock.bind(("", port))

    print("Searching for Tic-Tac-Toe server via LAN broadcast...")
    start = time.time()
    server_ip = None
    port_to_clients = None
    port_from_clients = None

    # Loop until timeout. Use short sleep on exceptions to avoid tight busy-wait.
    while time.time() - start < timeout:
        try:
            data, addr = sock.recvfrom(1024)  # buffer size 1024 bytes
            string = str(data, 'utf-8')
            fields = string.split(" ")
            # Defensive parsing: ensure there are enough fields before indexing.
            if len(fields) >= 5 and fields[1].strip() == "server_info":
                server_ip = fields[2].strip()
                port_to_clients = fields[3].strip()
                port_from_clients = fields[4].strip()
                print(f"Discovered server at {server_ip}")
                break
        except Exception:
            # Most common path: socket blocking or transient network errors.
            # Sleep briefly to keep checks periodic and to avoid high CPU usage.
            time.sleep(0.5)

    sock.close()
    return server_ip, port_to_clients, port_from_clients


def send_client_message(pub_socket, message_string):
    """
    Send a client-originated message via the provided PUB socket with the expected topic.

    The server in this example expects client messages to be sent with the
    "client/" topic prefix followed by a space and the payload. This helper
    centralizes that format so callers only provide the payload.

    Parameters:
        pub_socket (zmq.Socket): a configured ZMQ PUB socket connected to server.
        message_string (str): payload to send (e.g. "request join alice", "resign alice").

    Example:
        send_client_message(pub_socket, "request join alice")
    """
    pub_socket.send_string(f"client/ {message_string}")


def main():
    """
    Terminal-mode main loop: discover server, join, and interact until game ends.

    Flow:
    1. Discover server via UDP broadcast.
    2. Prompt for username and connect PUB/SUB sockets.
    3. Send a "request join <username>" message and enter the game loop.
    4. React to incoming server messages and prompt the user for moves when it's their turn.
    5. Support 'resign' to quit the game and notify the server.

    The loop uses non-blocking SUB recv and short sleeps to remain responsive.
    KeyboardInterrupt (Ctrl-C) is handled to gracefully resign and close sockets.
    """
    port_to_broadcast = 41110

    # Discover server via LAN broadcast. If not found, exit early.
    server_ip, port_to_clients, port_from_clients = discover_server(port_to_broadcast)
    if not server_ip:
        print("No server found. Exiting.")
        return
    print(f"Found server at {server_ip}")

    # Prompt the user for a username (trim whitespace).
    username = input("Enter your username: ").strip()

    # Set up ZeroMQ context and sockets:
    # - PUB socket: used to send client messages to server (connect to port_from_clients).
    # - SUB socket: used to receive server broadcasts/updates (connect to port_to_clients).
    context = zmq.Context()
    pub_socket = context.socket(zmq.PUB)
    sub_socket = context.socket(zmq.SUB)

    # Connect to the discovered endpoints. Use tcp://<ip>:<port>.
    pub_socket.connect(f"tcp://{server_ip}:{port_from_clients}")
    sub_socket.connect(f"tcp://{server_ip}:{port_to_clients}")
    # Only receive messages whose topic begins with "server/".
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "server/")

    print("Connecting to server...")
    # Short sleep gives the server a moment to process a new connection in simple setups.
    time.sleep(0.5)
    # Request to join the game.
    send_client_message(pub_socket, f"request join {username}")

    # State variables for the main loop.
    my_turn = False
    running = True

    try:
        while running:
            try:
                # Attempt to receive an incoming message without blocking.
                # If no message is available, zmq.Again is raised and we continue.
                msg = sub_socket.recv_string(flags=zmq.NOBLOCK)

                # Basic parsing: split into tokens by whitespace.
                tokens = msg.split()
                if not tokens:
                    continue
                cmd = tokens[1]

                if cmd == "joined":
                    # Inform user that a player joined (usually one of the two players).
                    print(f"Player joined: {tokens[-1]}")

                elif cmd == "update":
                    # Server sends a drawn board after 'update '. Preserve formatting.
                    board = msg.split(sep="update ")[1]
                    print("\nGame Board:\n" + board)

                elif cmd == "turn":
                    # Server announces whose turn it is. Compare to local username.
                    turn_name = tokens[2]
                    my_turn = (turn_name == username)
                    if my_turn:
                        print("It's your turn!")
                    else:
                        print("Please wait for the other player to make their move")

                elif cmd == "won":
                    # A player won the game; print winner and stop running.
                    print(f"Game over! Winner: {tokens[2]}")
                    running = False

                elif cmd == "draw":
                    # The game ended in a draw.
                    print("Game ended in a draw.")
                    running = False

                elif cmd == "error":
                    # An error occurred on the server; exit.
                    print("Server error — disconnecting.")
                    running = False

            except zmq.Again:
                # No message available this iteration; proceed to input handling.
                pass

            # If it is this client's turn, prompt user for move or resign.
            if my_turn:
                # Read input; accept "resign" or "<col> <row>".
                move = input("Enter your move (col row) or 'resign': ").strip().lower()
                if move == "resign":
                    # Notify server of resignation and exit the loop.
                    send_client_message(pub_socket, f"resign {username}")
                    running = False
                    break
                try:
                    # Parse two integers separated by whitespace.
                    col, row = map(int, move.split())
                    # Validate the coordinates are within 0..2.
                    if 0 <= col <= 2 and 0 <= row <= 2:
                        send_client_message(pub_socket, f"{col} {row} {username}")
                        # After sending a move, wait for server to reply (no longer my turn).
                        my_turn = False
                    else:
                        print("Invalid move — must be between 0 and 2.")
                except ValueError:
                    # Input not parseable as two integers.
                    print("Invalid input format. Use two numbers or 'resign'.")

            # Small sleep to avoid a tight loop; keeps CPU usage reasonable.
            time.sleep(0.05)

    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl-C: notify server of resignation.
        print("\nExiting game.")
        send_client_message(pub_socket, f"resign {username}")
        running = False
    finally:
        # Ensure sockets and context are closed on exit.
        pub_socket.close()
        sub_socket.close()
        context.term()


if __name__ == "__main__":
    main()