"""
This file contains logic for a remote client to connect to a tic tac toe server and play a game
"""

import zmq
import time

def main():
    context = zmq.Context()

    # Get the user information
    server_ip = input("Enter the server IP address: ").strip()
    username = input("Enter your username: ").strip()

    # Connect to the server sub port
    pub_socket = context.socket(zmq.PUB)
    pub_socket.connect(f"tcp://{server_ip}:41111")

    # Listen on the response port
    sub_socket = context.socket(zmq.SUB)
    sub_socket.connect(f"tcp://{server_ip}:41112")
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    print("Connecting to server...")
    # Give the server time to register you
    time.sleep(0.5)
    pub_socket.send_string(f"request join {username}")

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

                cmd = tokens[0]

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
                    turn_name = tokens[1]
                    my_turn = (turn_name == username)
                    if my_turn:
                        print("It's your turn!")
                    else:
                        print("Please wait for the other player to make their move")

                elif cmd == "won":
                    # Inform of winner
                    print(f"Game over! Winner: {tokens[1]}")
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
                    pub_socket.send_string(f"resign {username}")
                    # Exit flag
                    running = False
                    break
                try:
                    # Sanatize
                    col, row = map(int, move.split())
                    if 0 <= col <= 2 and 0 <= row <= 2:
                        # Send
                        pub_socket.send_string(f"{col} {row} {username}")
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
        pub_socket.send_string(f"resign {username}")
        running = False        
    finally:
        pub_socket.close()
        sub_socket.close()
        context.term()

if __name__ == "__main__":
    main()