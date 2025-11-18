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

    Terminal-mode client implemented as a clean state machine.

    States:
        DISCOVER     – find server via UDP broadcast
        CONNECT      – set up sockets and send join request
        WAIT_JOIN    – wait for 'joined <username>' confirmation
        WAIT_START   – wait for first 'update' & 'turn' messages
        MY_TURN      – prompt user for move; send move/resign
        WAIT_UPDATE  – waiting for other player's move
        GAME_OVER    – print result and exit
    """

    # -------------------------------
    # State enumeration
    # -------------------------------

    DISCOVER, CONNECT, WAIT_JOIN, WAIT_START, MY_TURN, WAIT_UPDATE, GAME_OVER = range(7)

    state = DISCOVER
    running = True
    username = None

    context = None
    pub_socket = None
    sub_socket = None

    server_ip = None
    port_to_clients = None
    port_from_clients = None

    my_turn = False

    print("=== Tic Tac Toe Client ===")

    try:
        while running:

            # ============================================================
            # STATE: DISCOVER — find the server by asking the user
            # ============================================================
            if state == DISCOVER:
                server_ip = input("Enter the server IP address: ").strip() 
                port_to_clients = int(input("Enter the port number of server -> client: ").strip())
                port_from_clients = int(input("Enter the port number of client -> server: ").strip())
                state = CONNECT
                continue

            # ============================================================
            # STATE: CONNECT — set up sockets and send join request
            # ============================================================
            if state == CONNECT:
                username = input("Enter your username: ").strip()

                context = zmq.Context()
                pub_socket = context.socket(zmq.PUB)
                sub_socket = context.socket(zmq.SUB)

                pub_socket.connect(f"tcp://{server_ip}:{port_from_clients}")
                sub_socket.connect(f"tcp://{server_ip}:{port_to_clients}")

                sub_socket.setsockopt_string(zmq.SUBSCRIBE, "server/")

                print("Connecting to server...")
                time.sleep(0.5)
                send_client_message(pub_socket, f"request join {username}")

                state = WAIT_JOIN
                continue

            # ============================================================
            # NON-BLOCKING MESSAGE RECEPTION (shared by most states)
            # ============================================================
            msg = None
            try:
                msg = sub_socket.recv_string(flags=zmq.NOBLOCK)
            except zmq.Again:
                pass

            # If a message was received, parse it into tokens.
            if msg:
                tokens = msg.split()
                if len(tokens) >= 2 and tokens[0] == "server/":
                    cmd = tokens[1]
                else:
                    cmd = None
            else:
                cmd = None

            # ============================================================
            # STATE: WAIT_JOIN — waiting for server confirmation
            # ============================================================
            if state == WAIT_JOIN:
                if cmd == "joined":
                    print(f"Player joined: {tokens[-1]}")
                    if tokens[-1] == username:
                        print("You have successfully joined the game.")
                        state = WAIT_START
                elif cmd == "error":
                    print("Server error before start.")
                    state = GAME_OVER
                time.sleep(0.05)
                continue

            # ============================================================
            # STATE: WAIT_START — waiting for first board update + turn
            # ============================================================
            if state == WAIT_START:
                if cmd == "update":
                    board = msg.split("update ", 1)[1]
                    print("\nGame Board:\n" + board)
                elif cmd == "turn":
                    player_turn = tokens[2]
                    my_turn = player_turn == username
                    if my_turn:
                        state = MY_TURN
                    else:
                        state = WAIT_UPDATE
                elif cmd == "error":
                    print("Server error — disconnecting.")
                    state = GAME_OVER
                time.sleep(0.05)
                continue

            # ============================================================
            # STATE: MY_TURN — prompt user for move or resign
            # ============================================================
            if state == MY_TURN:
                move = input("Enter your move (col row) or 'resign': ").strip().lower()
                if move == "resign":
                    send_client_message(pub_socket, f"resign {username}")
                    state = GAME_OVER
                    continue

                try:
                    col, row = map(int, move.split())
                    if 0 <= col <= 2 and 0 <= row <= 2:
                        send_client_message(pub_socket, f"{col} {row} {username}")
                        state = WAIT_UPDATE
                    else:
                        print("Move must be between 0 and 2.")
                except:
                    print("Invalid move. Must be 'col row' or 'resign'.")
                continue

            # ============================================================
            # STATE: WAIT_UPDATE — waiting for opponent move
            # ============================================================
            if state == WAIT_UPDATE:
                if cmd == "update":
                    board = msg.split("update ", 1)[1]
                    print("\nGame Board:\n" + board)

                elif cmd == "turn":
                    player_turn = tokens[2]
                    my_turn = player_turn == username
                    if my_turn:
                        state = MY_TURN

                elif cmd == "won":
                    print(f"Game Over! Winner: {tokens[2]}")
                    state = GAME_OVER

                elif cmd == "draw":
                    print("Game ended in a draw.")
                    state = GAME_OVER

                elif cmd == "error":
                    print("Server error — disconnecting.")
                    state = GAME_OVER

                time.sleep(0.05)
                continue

            # ============================================================
            # STATE: GAME_OVER — exit loop
            # ============================================================
            if state == GAME_OVER:
                running = False
                continue

    except KeyboardInterrupt:
        print("\nExiting game...")
        if pub_socket and username:
            send_client_message(pub_socket, f"resign {username}")

    finally:
        if pub_socket:
            pub_socket.close()
        if sub_socket:
            sub_socket.close()
        if context:
            context.term()



if __name__ == "__main__":
    main()