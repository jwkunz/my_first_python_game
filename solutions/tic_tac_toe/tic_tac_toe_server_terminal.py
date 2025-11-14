"""
This file contains logic to manage two users playing a tic tac toe game
"""

import zmq
import socket
import time
from threading import Thread
from game_state import GameState 
import random

# Helper function to get the local IP address
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# Service for advertising the server IP address
def broadcast_ip(broadcast_ip, broadcast_port, server_ip, port_to_clients,port_from_clients, stop_flag):
    """Thread function that continuously broadcasts server IP using UDP """
    # UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Broadcast settings
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # Until stop flag received
    while not stop_flag["stop"]:
        # Send this string
        sock.sendto(bytes(f"broadcast/ server_info {server_ip} {port_to_clients} {port_from_clients}",'utf-8'),(broadcast_ip,broadcast_port))
        time.sleep(1)

# Wraps the server send message with a topic tag
def send_server_message(pub_socket, message_string):
    pub_socket.send_string(f"server/ {message_string}")

def main():
    context = zmq.Context()
    port_to_broadcast = 41110
    port_to_clients = 41111
    port_from_clients = 41112

    server_ip = get_local_ip()

    pub_socket = context.socket(zmq.PUB)
    sub_socket = context.socket(zmq.SUB)

    # Bind game sockets
    pub_socket.bind(f"tcp://*:{port_to_clients}")
    sub_socket.bind(f"tcp://*:{port_from_clients}")
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "client/")

    print(f"Server broadcasting information for {server_ip}")

    # Start broadcast thread
    stop_flag = {"stop": False}
    t = Thread(target=broadcast_ip, args=("255.255.255.255", port_to_broadcast, server_ip, port_to_clients, port_from_clients,stop_flag))
    t.daemon = True
    t.start()

    print("Waiting for two players to join...")

    players = []
    game = None
    turn_index = 0

    try:
        while True:
            # Get input
            msg = sub_socket.recv_string()
            tokens = msg.split()
            if not tokens:
                continue

            cmd = tokens[1]

            # Handle join requests
            if cmd == "request" and len(tokens) >= 4 and tokens[2] == "join":
                username = tokens[3]
                if username not in players:
                    players.append(username)
                    send_server_message(pub_socket,f"joined {username}")
                    print(f"{username} joined the game.")
                if len(players) == 2 and game is None:
                    game = GameState()
                    print("Both players connected. Starting game!")
                    # Randomly pick teams
                    random.seed(time.time_ns())
                    random.shuffle(players)
                    send_server_message(pub_socket,f"update {str(game)}")
                    send_server_message(pub_socket,f"turn {players[turn_index]}")
                continue


            # Handle resignations
            if cmd == "resign" and len(tokens) == 3:
                username = tokens[2]
                print(f"{username} resigned")
                if (username in players) and (len(players)==2):
                    winner = players[1] if username == players[0] else players[0]
                    send_server_message(pub_socket,f"won {winner}")
                    print(f"{winner} wins!")
                    break
                else:
                    players = []
                    continue

            # Ignore if game hasn't started
            if not game or len(players) < 2:
                continue

            # Handle moves
            if len(tokens) == 4:
                try:
                    col = int(tokens[1])
                    row = int(tokens[2])
                    username = tokens[3]

                    if username != players[turn_index]:
                        continue  # ignore move from wrong player

                    valid = game.make_move(col, row)
                    if not valid:
                        # Invalid move submission is automatic loss
                        winner = players[1] if username == players[0] else players[0]
                        send_server_message(pub_socket,f"won {winner}")
                        print(f"{username} resigned. {winner} wins!")
                        break

                    # Send updated game
                    send_server_message(pub_socket,f"update {str(game)}")

                    # Check for win
                    if game.inspect_win():
                        # Inform
                        winner = players[turn_index]
                        send_server_message(pub_socket,f"won {winner}")
                        print(f"{winner} wins!")
                        break

                    # Check for draw
                    if game.inspect_draw():
                        # Inform
                        send_server_message(pub_socket,"draw")
                        print("Game ended in a draw.")
                        break

                    # Next turn
                    turn_index = 1 - turn_index
                    send_server_message(pub_socket,f"turn {players[turn_index]}")

    # Disconnect on all exceptions
                except Exception as e:
                    print("Error processing move:", e)
                    send_server_message(pub_socket,"error disconnect")
                    break

    except KeyboardInterrupt:
        print("Server shutting down gracefully.")
        send_server_message(pub_socket,"error disconnect")
    except Exception as e:
        print(f"Server error: {e}")
        send_server_message(pub_socket,"error disconnect")
    finally:
        sub_socket.close()
        pub_socket.close()
        context.term()

if __name__ == "__main__":
    main()
