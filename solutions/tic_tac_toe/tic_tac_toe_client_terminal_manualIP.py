"""
Terminal-mode tic-tac-toe client that connects to a server by manually-entered IP.

This module implements a simple command-line client for playing a tic-tac-toe
game against a server on the local network. Unlike the other client variant
that discovers the server via UDP broadcasts, this script asks the user to
provide the server IP address (and the user's desired username) interactively.

Primary responsibilities:
- Prompt the user for the server IP and username.
- Establish ZeroMQ PUB/SUB sockets connected to the server's known ports.
- Send a join request to the server and participate in turn-based play.
- Display textual board updates and simple status messages received from the server.
- Allow the user to submit moves (col row) or type "resign" to quit.

Protocol summary (as expected by the server used in the accompanying examples):
- Outgoing client messages (sent on the PUB socket) take the forms:
    * "request join <username>"
    * "<col> <row> <username>"         (a move)
    * "resign <username>"
- Incoming server messages on the SUB socket are simple whitespace-separated
  command lines such as:
    * "joined <username>"
    * "update <ascii-board-drawing...>"
    * "turn <username>"
    * "won <username>"
    * "draw"
    * "error"

Notes and assumptions:
- This client connects to TCP ports 41111 (server PUB -> clients) and
  41112 (server SUB <- clients) by default; these ports are hard-coded to
  match the sample server used by this project.
- The SUB socket is configured to subscribe to all messages (empty topic),
  because some server examples send messages without a topic prefix.
- The implementation uses non-blocking recv on the SUB socket together with
  a small sleep in the main loop to remain responsive while waiting for I/O.
- This module is intended for manual use from a terminal and performs
  blocking reads for user input when it is the player's turn.
"""
import zmq
import time


def main():
    """
    Start the terminal client and manage the interactive game session.

    Flow:
    1. Prompt the user for the server IP and a username.
    2. Create a ZMQ Context and connect:
         - PUB socket -> tcp://<server_ip>:41111 (send commands to server)
         - SUB socket -> tcp://<server_ip>:41112 (receive server updates)
    3. Send "request join <username>" to register with the server.
    4. Enter a loop that:
         - non-blocking receives server messages and handles them (update, turn, won, draw, error)
         - when it becomes this client's turn, prompt the user for a move or 'resign'
         - validates user input and sends moves to server in the required format
    5. Cleanly close sockets and terminate the ZMQ context on exit.

    Behaviour and edge-cases:
    - The SUB socket is polled with zmq.NOBLOCK; when no message is available,
      zmq.Again is raised and the loop continues.
    - When this client is in 'my_turn' state it will block on input() until the
      user responds; this design simplifies the terminal interaction model.
    - If the user enters invalid input, they are prompted again without notifying
      the server; only valid moves or 'resign' are sent.
    - KeyboardInterrupt (Ctrl-C) triggers a graceful resign notification before exit.

    This function interacts directly with the terminal and does not return any
    value; it exits when the game ends or the user quits.
    """
    context = zmq.Context()

    # Prompt the user for the server IP and their desired username.
    # .strip() trims accidental surrounding whitespace.
    server_ip = input("Enter the server IP address: ").strip()
    username = input("Enter your username: ").strip()

    # Create and connect the PUB socket to the server's "incoming from clients" port.
    # The server in the example binds a PUB socket at tcp://*:41111 for distributing updates;
    # clients publish to the complementary port so the server can receive them.
    pub_socket = context.socket(zmq.PUB)
    pub_socket.connect(f"tcp://{server_ip}:41111")

    # Create and connect the SUB socket to receive server messages.
    # The SUB socket subscribes to the empty string to receive all topics/messages.
    sub_socket = context.socket(zmq.SUB)
    sub_socket.connect(f"tcp://{server_ip}:41112")
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    print("Connecting to server...")
    # Sleep briefly to allow the server to process the new connection in simple setups.
    time.sleep(0.5)

    # Send a join request announcing the username to the server.
    # The server expects a "request join <username>" form to register the player.
    pub_socket.send_string(f"request join {username}")

    # Local state used by the main loop.
    my_turn = False   # True when the server indicates it is this client's turn
    running = True    # Flag to keep the main loop running

    try:
        while running:
            try:
                # Try to read a message from the server without blocking.
                # If no message is available, zmq.Again is raised and we fall through.
                msg = sub_socket.recv_string(flags=zmq.NOBLOCK)

                # Tokenize the incoming message for simple command parsing.
                tokens = msg.split()

                if not tokens:
                    # Defensive: skip empty messages.
                    continue

                # Many server examples send command tokens at the start of the line.
                # Parse cmd as the first token and handle the known commands.
                cmd = tokens[0]

                if cmd == "joined":
                    # Notification that a player joined; tokens[-1] holds the name.
                    print(f"Player joined: {tokens[-1]}")

                elif cmd == "update":
                    # The 'update' message contains a multi-line ascii board after the token.
                    # Using str.split(sep="update ", 1)[1] extracts the rest of the message.
                    board = msg.split(sep="update ")[1]
                    print("\nGame Board:\n" + board)

                elif cmd == "turn":
                    # Server announces whose turn it currently is.
                    # Compare that name to our username to set local my_turn flag.
                    # tokens[1] is expected to be the username in this message format.
                    turn_name = tokens[1]
                    my_turn = (turn_name == username)
                    if my_turn:
                        print("It's your turn!")
                    else:
                        print("Please wait for the other player to make their move")

                elif cmd == "won":
                    # Server reports a winner; tokens[1] should be the winner's name.
                    print(f"Game over! Winner: {tokens[1]}")
                    running = False

                elif cmd == "draw":
                    # Draw condition: no winner and no more moves.
                    print("Game ended in a draw.")
                    running = False

                elif cmd == "error":
                    # Server signaled an error condition; disconnect locally.
                    print("Server error — disconnecting.")
                    running = False

            except zmq.Again:
                # No message available right now; normal path. Continue to input handling.
                pass

            # If it's our turn, prompt the user for a move or 'resign'.
            if my_turn:
                # Request input from the user. This call blocks until the user responds.
                move = input("Enter your move (col row) or 'resign': ").strip().lower()
                if move == "resign":
                    # Send a resign notification to the server and exit the game.
                    pub_socket.send_string(f"resign {username}")
                    running = False
                    break
                try:
                    # Expect two integers separated by whitespace: col row
                    col, row = map(int, move.split())
                    # Validate the coordinates are inside 0..2 (3x3 board).
                    if 0 <= col <= 2 and 0 <= row <= 2:
                        # Send the move to the server in the expected "<col> <row> <username>" format.
                        pub_socket.send_string(f"{col} {row} {username}")
                        # After sending a move, the client typically waits for the server
                        # to announce whose turn it is next; set my_turn to False.
                        my_turn = False
                    else:
                        # Notify user of invalid coordinates and allow another attempt.
                        print("Invalid move — must be between 0 and 2.")
                except ValueError:
                    # Input could not be parsed into two integers.
                    print("Invalid input format. Use two numbers or 'resign'.")

            # Small sleep to avoid a tight CPU-consuming loop when idle.
            time.sleep(0.05)

    except KeyboardInterrupt:
        # Handle Ctrl-C gracefully: notify server of resignation before exiting.
        print("\nExiting game.")
        pub_socket.send_string(f"resign {username}")
        running = False
    finally:
        # Ensure ZMQ sockets and context are properly closed on exit.
        pub_socket.close()
        sub_socket.close()
        context.term()


if __name__ == "__main__":
    main()