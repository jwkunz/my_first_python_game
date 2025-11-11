#!/usr/bin/env python3
import zmq
import threading
import sys
import time
import socket
import re
import select

def get_local_ip():
    """Attempt to determine the local IP address of the current host."""
    try:
        # connect to a dummy address (won't actually send data)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Unable to determine local IP"

def wait_for_keypress():
    """Pause until user presses a key."""
    print("\nPress any key to exit and try again later...")
    # Works on most terminals
    sys.stdin.read(1)
    sys.exit(1)

def listener(sub_socket):
    """Continuously listen for messages on the SUB socket."""
    while True:
        try:
            msg = sub_socket.recv_string(flags=zmq.NOBLOCK)
            print(f"\nPartner: {msg}")
            print("> ", end="", flush=True)
        except zmq.Again:
            time.sleep(0.05)
        except zmq.ZMQError as e:
            print(f"\n[ERROR] Subscription socket error: {e}")
            wait_for_keypress()

def validate_ip(ip):
    """Validate IPv4 format."""
    pattern = re.compile(
        r"^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
        r"(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$"
    )
    return bool(pattern.match(ip))

def main():
    print("=== Type2Talk: Simple ZMQ Two-Way Chat ===\n")

    # Display current host IP for convenience
    local_ip = get_local_ip()
    print(f"Your local IP address: {local_ip}")
    print("You may need to give this IP to your partner.\n")

    # Ask for configuration
    config = ""
    while config not in ["A", "B"]:
        config = input("Enter configuration (A/B): ").strip().upper()
        if config not in ["A", "B"]:
            print("Invalid choice. Please enter 'A' or 'B'.\n")

    # Ask for partner IP
    partner_ip = ""
    while not validate_ip(partner_ip):
        partner_ip = input("Enter partner IP address (e.g., 192.168.1.20): ").strip()
        if not validate_ip(partner_ip):
            print("Invalid IP address. Please enter a valid IPv4 address.\n")

    # Set up ports based on configuration
    if config == "A":
        pub_port, sub_port = 7150, 7151
    else:
        pub_port, sub_port = 7151, 7150

    print(f"\nConfiguration {config} selected.")
    print(f"Publishing on port {pub_port}, subscribing to {partner_ip}:{sub_port}")
    print("Attempting to initialize sockets...")

    context = zmq.Context()

    try:
        # Create PUB socket
        pub_socket = context.socket(zmq.PUB)
        pub_socket.bind(f"tcp://*:{pub_port}")
    except zmq.ZMQError as e:
        print(f"\n[ERROR] Could not bind publisher socket on port {pub_port}: {e}")
        wait_for_keypress()

    try:
        # Create SUB socket
        sub_socket = context.socket(zmq.SUB)
        sub_socket.connect(f"tcp://{partner_ip}:{sub_port}")
        sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    except zmq.ZMQError as e:
        print(f"\n[ERROR] Could not connect to subscriber socket at {partner_ip}:{sub_port}: {e}")
        wait_for_keypress()

    print("\nSockets successfully initialized.")
    print("Type messages and press Enter to send.")
    print("Press Ctrl+C to quit.\n")

    # Start background listener thread
    listener_thread = threading.Thread(target=listener, args=(sub_socket,), daemon=True)
    listener_thread.start()

    try:
        print("> ", end="", flush=True)
        while True:
            # Use select to detect available stdin input
            readable, _, _ = select.select([sys.stdin], [], [], 0.1)
            if readable:
                msg = sys.stdin.readline().strip()
                if msg:
                    try:
                        pub_socket.send_string(msg)
                    except zmq.ZMQError as e:
                        print(f"\n[ERROR] Could not send message: {e}")
                        wait_for_keypress()
    except KeyboardInterrupt:
        print("\nExiting chat... Goodbye.")
    finally:
        pub_socket.close()
        sub_socket.close()
        context.term()


if __name__ == "__main__":
    main()
