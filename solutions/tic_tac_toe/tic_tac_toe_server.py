"""
Tic-tac-toe server (terminal) with UDP discovery and ZMQ PUB/SUB transport.

This module implements a simple terminal-oriented tic-tac-toe server intended
for local network testing and learning.  It provides:

- UDP broadcast of server information (IP and ports) so clients can discover
  the server without prior configuration.
- ZeroMQ PUB socket to publish server events (game board updates, turns,
  results) to all clients.
- ZeroMQ SUB socket to receive client-originated commands (join requests,
  moves, resignations) with a small topic-prefixing protocol.
- A straightforward single-threaded game loop that manages a single two-
  player game at a time and enforces move/turn rules via GameState.

Design notes:
- Discovery: a background thread continuously broadcasts a short text line
  on a well-known UDP port (default 41110). The payload contains the token
  "server_info" followed by the server IP and the two ZMQ ports used.
  Clients listen for this broadcast to learn where to connect.
- Messaging protocol:
    * Server messages are sent with topic "server/" followed by a command:
        - "server/ joined <username>"
        - "server/ update <ascii-board-drawing>"
        - "server/ turn <username>"
        - "server/ won <username>"
        - "server/ draw"
        - "server/ error <reason>"
    * Client messages are expected to be sent with topic "client/" and a
      payload such as:
        - "client/ request join <username>"
        - "client/ <col> <row> <username>"
        - "client/ resign <username>"
- Game arbitration: when two distinct players have joined, the server
  constructs a GameState, randomly assigns play order, and mediates moves.
  Invalid moves are treated as immediate loss for the submitting player.
- This implementation is intentionally simple and synchronous for clarity;
  production servers should add robust error handling, authentication, and
  persistent state as needed.
"""
import zmq
import socket
import time
from threading import Thread
from game_state import GameState
import random
import sys


def get_local_ip():
    """
    Return a reasonable local IPv4 address for this host.

    The function attempts to open a UDP socket and connect to an external
    IP (Google DNS 8.8.8.8) to discover the default outbound interface's
    address. This is a common, non-invasive technique that does not actually
    send packets to the remote host.

    Returns:
        str: detected local IP (e.g. "192.168.1.5") or "127.0.0.1" on failure.

    Notes:
        - This method is not guaranteed to return the address that other hosts
          will use to reach this machine in complex multi-homed setups, but it
          is sufficient for local/LAN examples and tests.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to an external address; no packets are sent for UDP connect.
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Fall back to loopback in the unlikely event of error.
        return "127.0.0.1"


def broadcast_ip(broadcast_ip, broadcast_port, server_ip, port_to_clients, port_from_clients, stop_flag):
    """
    Thread target that repeatedly broadcasts server discovery information.

    This function runs in a tight but throttled loop (sleep 1s) and sends a
    whitespace-separated text payload to the provided broadcast address/port.

    Payload format:
        "broadcast/ server_info <server_ip> <port_to_clients> <port_from_clients>"

    Parameters:
        broadcast_ip (str): broadcast address, e.g. "255.255.255.255".
        broadcast_port (int): UDP port chosen for discovery (e.g. 41110).
        server_ip (str): IP address clients should use to connect to ZMQ sockets.
        port_to_clients (int|str): port where server publishes updates (PUB).
        port_from_clients (int|str): port where server listens for client PUBs (SUB).
        stop_flag (dict): a dict with key "stop"; when set to True thread exits.

    Notes:
        - The function intentionally keeps the payload simple and human-readable.
        - stop_flag is a mutable dict to allow caller to signal thread shutdown.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Enable broadcast on the socket so it can send to the broadcast address.
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Continue broadcasting until the main thread sets stop_flag["stop"] = True.
    while not stop_flag.get("stop", False):
        payload = f"broadcast/ server_info {server_ip} {port_to_clients} {port_from_clients}"
        try:
            sock.sendto(payload.encode("utf-8"), (broadcast_ip, broadcast_port))
        except Exception:
            # Ignore transient send errors; keep trying.
            pass
        time.sleep(1)

    sock.close()


def send_server_message(pub_socket, message_string):
    """
    Helper to publish a server message with the standard topic prefix.

    This centralizes the message formatting so all outgoing server messages
    follow the "server/ <payload>" convention.

    Parameters:
        pub_socket (zmq.Socket): ZMQ PUB socket bound to clients.
        message_string (str): payload to send after the "server/" topic.
    """
    pub_socket.send_string(f"server/ {message_string}")


def main():
    """
    Main server entry point.

    Responsibilities:
        - Create ZMQ context and bind a PUB socket (to clients) and a SUB
          socket (for client messages).
        - Start the UDP discovery broadcast thread.
        - Accept client join requests until two unique players connect.
        - Manage the turn-based game loop: receive moves, validate them via
          GameState, broadcast updates, and report results.
        - Cleanly close sockets and stop the broadcast thread on exit.

    Runtime behavior:
        - The server blocks waiting for client messages on its SUB socket.
        - When two players are present, a GameState instance is created and
          players are randomly shuffled to decide who plays first.
        - Each valid move results in an "update" broadcast and a "turn"
          broadcast for the next player; wins/draws result in "won"/"draw".

    If the server is started with the flag "--no_broadcast" it will not advertise its location
    def main():

    States:
        WAITING_FOR_PLAYERS  – lobby state until 2 unique players join
        START_GAME           – initializes GameState and assigns first turn
        WAITING_FOR_MOVE     – waits for a valid message from the current player
        PROCESS_MOVE         – validates and applies move; checks win/draw
        GAME_OVER            – broadcasts result and exits loop
    """

    # ---------------------------
    # Initial Setup (unchanged)
    # ---------------------------
    context = zmq.Context()

    auto_discover = "--no_broadcast" not in sys.argv[1:]
    port_to_broadcast = 41110
    port_to_clients = 41111
    port_from_clients = 41112

    server_ip = get_local_ip()

    pub_socket = context.socket(zmq.PUB)
    sub_socket = context.socket(zmq.SUB)

    pub_socket.bind(f"tcp://*:{port_to_clients}")
    sub_socket.bind(f"tcp://*:{port_from_clients}")
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "client/")

    stop_flag = {"stop": False}
    if auto_discover:
        print(f"Server broadcasting information for {server_ip}")
        broadcaster = Thread(
            target=broadcast_ip,
            args=("255.255.255.255",
                  port_to_broadcast,
                  server_ip,
                  port_to_clients,
                  port_from_clients,
                  stop_flag)
        )
        broadcaster.daemon = True
        broadcaster.start()

    # ---------------------------
    # State Machine Variables
    # ---------------------------
    WAITING_FOR_PLAYERS = "WAITING_FOR_PLAYERS"
    START_GAME          = "START_GAME"
    WAITING_FOR_MOVE    = "WAITING_FOR_MOVE"
    PROCESS_MOVE        = "PROCESS_MOVE"
    GAME_OVER           = "GAME_OVER"

    state = WAITING_FOR_PLAYERS

    players = []
    turn_index = 0
    game = None
    last_message = None  # storage for the move/resign just received

    print("Waiting for two players to join...")

    try:
        while True:

            # =====================================================
            # ---------------- WAITING_FOR_PLAYERS ----------------
            # =====================================================
            if state == WAITING_FOR_PLAYERS:
                msg = sub_socket.recv_string()
                tokens = msg.split()
                if not tokens:
                    continue

                if tokens[1] == "request" and tokens[2] == "join":
                    username = tokens[3]
                    if username not in players:
                        players.append(username)
                        send_server_message(pub_socket, f"joined {username}")
                        print(f"{username} joined the game.")

                    if len(players) == 2:
                        state = START_GAME
                    continue

                # A resign during lobby resets lobby.
                if tokens[1] == "resign":
                    print("Resignation received during lobby; resetting lobby.")
                    players = []
                    continue

            # =====================================================
            # ---------------------- START_GAME -------------------
            # =====================================================
            if state == START_GAME:
                game = GameState()
                random.shuffle(players)
                turn_index = 0

                print("Both players connected. Starting game!")
                send_server_message(pub_socket, f"update {str(game)}")
                send_server_message(pub_socket, f"turn {players[turn_index]}")

                state = WAITING_FOR_MOVE
                continue

            # =====================================================
            # -------------------- WAITING_FOR_MOVE ---------------
            # =====================================================
            if state == WAITING_FOR_MOVE:
                msg = sub_socket.recv_string()
                tokens = msg.split()
                last_message = tokens   # pass message to next state

                # Resignation is handled immediately
                if tokens[1] == "resign":
                    username = tokens[2]
                    print(f"{username} resigned.")
                    winner = players[1] if username == players[0] else players[0]
                    send_server_message(pub_socket, f"won {winner}")
                    state = GAME_OVER
                    continue

                # Moves must have 4 tokens: client/ col row username
                if len(tokens) == 4:
                    state = PROCESS_MOVE
                    continue

                # Ignore any other input
                continue

            # =====================================================
            # --------------------- PROCESS_MOVE -----------------
            # =====================================================
            if state == PROCESS_MOVE:
                try:
                    col = int(last_message[1])
                    row = int(last_message[2])
                    username = last_message[3]

                    # Enforce whose turn it is
                    if username != players[turn_index]:
                        state = WAITING_FOR_MOVE
                        continue

                    # Apply the move
                    valid = game.make_move(col, row)
                    if not valid:
                        winner = players[1] if username == players[0] else players[0]
                        send_server_message(pub_socket, f"won {winner}")
                        print(f"Invalid move by {username}. {winner} wins!")
                        state = GAME_OVER
                        continue

                    # Board update
                    send_server_message(pub_socket, f"update {str(game)}")

                    # Win check
                    if game.inspect_win():
                        winner = players[turn_index]
                        send_server_message(pub_socket, f"won {winner}")
                        print(f"{winner} wins!")
                        state = GAME_OVER
                        continue

                    # Draw check
                    if game.inspect_draw():
                        send_server_message(pub_socket, "draw")
                        print("Game ended in a draw.")
                        state = GAME_OVER
                        continue

                    # Next turn
                    turn_index = 1 - turn_index
                    send_server_message(pub_socket, f"turn {players[turn_index]}")

                    state = WAITING_FOR_MOVE

                except Exception as e:
                    print("Error processing move:", e)
                    send_server_message(pub_socket, "error disconnect")
                    state = GAME_OVER

                continue

            # =====================================================
            # ---------------------- GAME_OVER --------------------
            # =====================================================
            if state == GAME_OVER:
                break

    except KeyboardInterrupt:
        print("Server shutting down gracefully.")
        send_server_message(pub_socket, "error disconnect")

    except Exception as e:
        print(f"Server error: {e}")
        send_server_message(pub_socket, "error disconnect")

    finally:
        stop_flag["stop"] = True
        time.sleep(0.1)
        pub_socket.close()
        sub_socket.close()
        context.term()


if __name__ == "__main__":
    main()
