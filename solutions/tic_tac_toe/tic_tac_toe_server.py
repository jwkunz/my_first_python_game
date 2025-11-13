"""
This file contains logic to manage two users playing a tic tac toe game
"""

import zmq
import socket
import time
from game_state import GameState 
import random

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def main():
    context = zmq.Context()

    # Socket for receiving player messages
    sub_socket = context.socket(zmq.SUB)
    sub_socket.bind("tcp://*:41111")
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    # Socket for sending updates
    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind("tcp://*:41112")

    print(f"Server running at IP: {get_local_ip()}")
    print("Waiting for two players to join...")

    players = []
    game = None
    turn_index = 0

    try:
        while True:
            msg = sub_socket.recv_string()
            tokens = msg.split()
            if not tokens:
                continue

            cmd = tokens[0]

            # Handle join requests
            if cmd == "request" and len(tokens) >= 3 and tokens[1] == "join":
                username = tokens[2]
                if username not in players:
                    players.append(username)
                    pub_socket.send_string(f"joined {username}")
                    print(f"{username} joined the game.")
                if len(players) == 2 and game is None:
                    game = GameState()
                    print("Both players connected. Starting game!")
                    # Randomly pick teams
                    random.seed(time.time_ns())
                    random.shuffle(players)
                    pub_socket.send_string(f"update {str(game)}")
                    pub_socket.send_string(f"turn {players[turn_index]}")
                continue

            # Ignore if game hasn't started
            if not game or len(players) < 2:
                continue

            # Handle resignations
            if cmd == "resign" and len(tokens) == 2:
                username = tokens[1]
                if username in players:
                    winner = players[1] if username == players[0] else players[0]
                    pub_socket.send_string(f"won {winner}")
                    print(f"{username} resigned. {winner} wins!")
                    break

            # Handle moves
            if len(tokens) == 3:
                try:
                    col = int(tokens[0])
                    row = int(tokens[1])
                    username = tokens[2]

                    if username != players[turn_index]:
                        continue  # ignore move from wrong player

                    valid = game.make_move(col, row)
                    if not valid:
                        # Invalid move submission is automatic loss
                        winner = players[1] if username == players[0] else players[0]
                        pub_socket.send_string(f"won {winner}")
                        print(f"{username} resigned. {winner} wins!")
                        break

                    # Send updated game
                    pub_socket.send_string(f"update {str(game)}")

                    # Check for win
                    if game.inspect_win():
                        # Inform
                        winner = players[turn_index]
                        pub_socket.send_string(f"won {winner}")
                        print(f"{winner} wins!")
                        break

                    # Check for draw
                    if game.inspect_draw():
                        # Inform
                        pub_socket.send_string("draw")
                        print("Game ended in a draw.")
                        break

                    # Next turn
                    turn_index = 1 - turn_index
                    pub_socket.send_string(f"turn {players[turn_index]}")

    # Disconnect on all exceptions
                except Exception as e:
                    print("Error processing move:", e)
                    pub_socket.send_string("error disconnect")
                    break

    except KeyboardInterrupt:
        print("Server shutting down gracefully.")
        pub_socket.send_string("error disconnect")
    except Exception as e:
        print(f"Server error: {e}")
        pub_socket.send_string("error disconnect")
    finally:
        sub_socket.close()
        pub_socket.close()
        context.term()

if __name__ == "__main__":
    main()
