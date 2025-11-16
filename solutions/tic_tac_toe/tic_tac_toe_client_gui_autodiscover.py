"""
Tic-tac-toe client GUI converted from PyQt5 to PySide6.

Original file: tic_tac_toe_client_gui_autodiscover.py
Converted imports and small Qt API differences for PySide6.
"""

import sys
import zmq
import time
import socket
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPalette, QColor, QMouseEvent


# -----------------------------
# Clickable label for board cells
# -----------------------------
class ClickableLabel(QLabel):
    """
    A QLabel subclass that represents one square on the tic-tac-toe board.

    Signals:
        clicked(int col, int row): emitted on left mouse-press with coordinates.
    """
    clicked = Signal(int, int)  # row, col

    def __init__(self, col, row):
        """
        Initialize a ClickableLabel for a given board column and row.

        Args:
            col (int): column index on board (0-2).
            row (int): row index on board (0-2).
        """
        super().__init__()
        self.row = row
        self.col = col
        # Visual configuration appropriate for a 3x3 board on small/large screens.
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Arial", 48, QFont.Bold))
        self.setStyleSheet("border: 2px solid black;")
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handle mouse press events.

        Emits the 'clicked' signal for left-button presses so the GUI controller
        can enqueue the click and handle moves asynchronously.
        """
        if event.button() == Qt.LeftButton:
            # Intentionally emit (col, row) to match the rest of the UI expectations.
            self.clicked.emit(self.col, self.row)


# -----------------------------
# Main GUI Window
# -----------------------------
class TicTacToeGUI(QWidget):
    """
    The main application window and controller for the tic-tac-toe client.

    Attributes:
        game_state (str): textual state of the internal state machine.
        target_frame_rate_ms (int): QTimer interval in milliseconds.
        running (bool): whether the main loop is active; used when closing.
        click_queue (list): queued user clicks (col, row) awaiting submission.
        pub_socket, sub_socket: ZeroMQ sockets created on connect.
        username (str): local player's username once submitted.
    """

    # Simple state defaults.
    game_state = "INITIALIZE"
    target_frame_rate_ms = 100
    running = True
    click_queue = []
    pub_socket = None
    sub_socket = None
    username = ""

    def __init__(self):
        """
        Initialize the main window and start the repeating game loop.
        """
        super().__init__()
        self.setWindowTitle("Tic Tac Toe Client GUI")

        # Start with a reasonable minimum size instead of maximized so it's usable
        # on a variety of display sizes and in automated testing.
        self.setMinimumSize(400,300)

        self.build_layout()
        self.start_main_game_loop()
        self.setStyleSheet("background-color: darkslategray; color:white")

    # -----------------------------------
    # Build all panels
    # -----------------------------------
    def build_layout(self):
        """
        Compose the top-level layout for the window.
        """
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.build_information_panel())
        main_layout.addLayout(self.build_terminal_panel())
        main_layout.addLayout(self.build_touch_panel())
        self.setLayout(main_layout)

    # -----------------------------------
    # Top Panel
    # -----------------------------------
    def build_information_panel(self):
        """
        Construct the top information panel where the user enters their name
        and controls the high-level game actions.
        """
        layout = QHBoxLayout()

        # Label + input for username, and two buttons: Submit and Resign.
        self.name_label = QLabel("Enter your name:")
        self.name_input = QLineEdit()
        self.submit_button = QPushButton("Submit")
        # Use checkable buttons so the UI loop can detect clicks by reading state.
        self.submit_button.setCheckable(True)
        self.resign_button = QPushButton("Resign")
        self.resign_button.setCheckable(True)

        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.resign_button)

        # Keep a reference list so the panel can be enabled/disabled as a unit.
        self.information_panel_widgets = [
            self.name_label,
            self.name_input,
            self.submit_button,
            self.resign_button
        ]

        return layout

    def set_information_panel_enable(self, enabled: bool):
        """
        Enable or disable the widgets in the information panel.
        """
        for w in self.information_panel_widgets:
            w.setEnabled(enabled)

    # -----------------------------------
    # Touch Panel (tic tac toe board)
    # -----------------------------------
    def build_touch_panel(self):
        """
        Create a 3x3 grid of ClickableLabel widgets representing the game board.
        """
        grid = QGridLayout()
        self.board_labels = []

        for r in range(3):
            row = []
            for c in range(3):
                # Note: ClickableLabel expects (col, row) ordering in constructor.
                label = ClickableLabel(r, c)
                label.clicked.connect(self.handle_cell_clicked)
                grid.addWidget(label, r, c)
                row.append(label)
                label.setStyleSheet("background-color: lightslategray;")
            self.board_labels.append(row)

        return grid

    def handle_cell_clicked(self, col, row):
        """
        Handler called when a ClickableLabel emits a clicked signal.
        """
        self.click_queue.append((col, row))
        # Game logic will go here soon; for now, echo the coordinates.
        self.terminal_print(f"Cell clicked: Column {col}, Row {row}")

    def draw_game_string(self, game_board_string: str):
        """
        Simple board renderer that accepts the terminal friendly game board string
        """
        idx = 1
        
        for row in range(3):
            for col in range(3):
                mark = game_board_string[idx]
                # Render underscore as an empty label for ergonomics.
                self.board_labels[row][col].setText(mark)
                idx += 4
            idx += 12

    # -----------------------------------
    # Terminal Panel
    # -----------------------------------
    def build_terminal_panel(self):
        """
        Construct a vertical layout containing status and a terminal console.
        """
        outer = QVBoxLayout()
        top_row = QHBoxLayout()

        # Connection status label: initial text and style set to searching.
        self.status_label = QLabel("searching")
        self.set_status_searching()

        # New Game button is checkable to allow the state machine to detect click.
        self.new_game_btn = QPushButton("New Game")
        self.new_game_btn.setCheckable(True)

        # Use a black background and bright foreground for readability of the status.
        self.status_label.setAutoFillBackground(True)
        palette = self.status_label.palette()
        palette.setColor(QPalette.Window, QColor("black"))
        self.status_label.setPalette(palette)

        top_row.addWidget(self.status_label)
        top_row.addWidget(self.new_game_btn)

        # Terminal is read-only and uses a monospace font to preserve alignment.
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont("Courier", 12))

        # Initial welcome message in the terminal console.
        self.terminal_print("Welcome to tic tac toe version 1.0.0")

        outer.addLayout(top_row)
        outer.addWidget(self.terminal)
        return outer

    # Terminal print
    def terminal_print(self, text: str):
        """
        Append a line of text to the on-screen terminal.
        """
        self.terminal.append(text)

    # Connection status helpers
    def set_status_searching(self):
        """Set the status label indicating the client is searching for a server."""
        self.status_label.setText("searching")
        self.status_label.setStyleSheet("color: yellow; font-weight: bold;")

    def set_status_connected(self):
        """Set the status label indicating the client is connected to a server."""
        self.status_label.setText("connected")
        self.status_label.setStyleSheet(
            "color: lightgreen; font-weight: bold;")

    def set_status_error(self):
        """Set the status label indicating a connection error occurred."""
        self.status_label.setText("connection error")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def closeEvent(self, event):
        """
        Handle the window close event.
        """
        if self.pub_socket is not None:
            if self.running:
                self.resign()
            self.pub_socket.close()
        if self.sub_socket is not None:
            self.sub_socket.close()
        # Accept the close to allow the application to exit.
        event.accept()

    # -----------------------------------
    # Simple Main Game Loop
    # -----------------------------------
    def handle_game_over_tokens(self, tokens):
        """
        Process tokens received from the server representing a game-over event.
        """
        if tokens[1] == "won":
            # Inform of winner
            self.terminal_print(f"Game over! Winner: {tokens[2]}")
            self.set_game_over()
        elif tokens[1] == "draw":
            # Inform of draw
            self.terminal_print("Game ended in a draw.")
            self.set_game_over()
        elif tokens[1] == "error":
            # Inform of error
            self.terminal_print("Server error — disconnecting.")
            self.set_game_over()
        else:
            # Unknown token: ignore but do not crash
            pass

    def resign(self):
        """
        Send a resign command to the server on behalf of the local player.
        """
        self.send_client_message(f"resign {self.username}")

    def set_game_over(self):
        """
        Mark the local state as game-over and provide console feedback.
        """
        self.terminal_print("The game is over.  Please close the GUI.")
        self.running = False

    def send_client_message(self, message_string):
        """
        Send a client-originating message over the PUB socket with the required topic.
        """
        # The server expects the topic "client/" followed by the message body.
        self.pub_socket.send_string(f"client/ {message_string}")

    def discover_server(self, port, timeout=1):
        """
        Listen for a UDP broadcast to discover the server's IP and ports.
        """
        # Create a UDP socket for discovery broadcasts.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Allow quick rebinds for repeated local testing.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)
        # Bind on all interfaces so broadcasts on any active NIC are seen.
        sock.bind(("", port))
        start = time.time()
        server_ip = None

        try:
            data, addr = sock.recvfrom(1024)  # buffer size 1024 bytes
            string = str(data, 'utf-8')
            fields = string.split(" ")
            # Expect a message shaped like: "<whatever> server_info <ip> <port_to_clients> <port_from_clients>"
            if fields[1].strip() == "server_info":
                server_ip = fields[2].strip()
                port_to_clients = fields[3].strip()
                port_from_clients = fields[4].strip()
                self.terminal_print(f"Discovered server at {server_ip}")
        except:
            server_ip = None
            port_to_clients = None
            port_from_clients = None

        sock.close()
        return server_ip, port_to_clients, port_from_clients

    def start_main_game_loop(self):
        """
        Start a QTimer that periodically calls game_loop() to process UI and network events.
        """
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        # 100 ms interval: approximately 10 updates per second, sufficient for this client.
        self.timer.start(self.target_frame_rate_ms)

    def game_loop(self):
        """
        Primary state machine for the client.
        """
        if self.running == False:
            return
        if self.game_state == "INITIALIZE":
            self.set_status_searching()
            self.terminal_print(
            "Searching for Tic-Tac-Toe server's LAN broadcast...")
            self.game_state = "CONNECTING"
        if self.game_state == "CONNECTING":
            # Initial connecting state: find server, then establish ZMQ PUB/SUB sockets.
            self.set_information_panel_enable(False)
            self.port_to_broadcast = 41110
            server_ip, port_to_clients, port_from_clients = self.discover_server(
                self.port_to_broadcast,timeout=1.0)
            if server_ip is not None:
                self.terminal_print(f"Found server at {server_ip}")

                # Create a ZMQ context and sockets for publishing client messages and
                # subscribing to server updates.
                self.context = zmq.Context()
                self.pub_socket = self.context.socket(zmq.PUB)
                self.sub_socket = self.context.socket(zmq.SUB)

                # Connect sockets using the addresses learned from discovery broadcast.
                self.pub_socket.connect(f"tcp://{server_ip}:{port_from_clients}")
                self.sub_socket.connect(f"tcp://{server_ip}:{port_to_clients}")
                # Only accept messages sent with topic "server/".
                self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "server/")
                # Make recv non-blocking with a short timeout to keep the UI responsive.
                self.sub_socket.setsockopt(zmq.RCVTIMEO, self.target_frame_rate_ms)

                self.set_status_connected()

                self.terminal_print("Press 'New Game' to begin")
                self.set_information_panel_enable(True)

                self.game_state = "WAIT_NEW_GAME"

        elif self.game_state == "WAIT_NEW_GAME":
            # User has clicked New Game -> ask for username
            if self.new_game_btn.isChecked():
                self.new_game_btn.setChecked(False)
                self.terminal_print("Enter your user name and press submit")
                self.game_state = "WAIT_USER_NAME"

        elif self.game_state == "WAIT_USER_NAME":
            # Submit button clicked -> send join request to server
            if self.submit_button.isChecked():
                self.submit_button.setChecked(False)
                self.username = self.name_input.text()
                if self.username:
                    self.send_client_message(f"request join {self.username}")
                    self.game_state = "WAIT_TO_PLAY"
                else:
                    self.terminal_print("Invalid username string")

            pass
        elif self.game_state == "WAIT_TO_PLAY":
            # Normal play state: send resigns, poll for server messages.
            if self.resign_button.isChecked():
                self.resign_button.setChecked(False)
                self.resign()
            # Try to receive a message from the server without blocking
            try:
                msg = self.sub_socket.recv_string(flags=zmq.NOBLOCK)
                tokens = msg.split()
                if tokens[1] == "joined":
                    # Inform player joined game
                    self.terminal_print(f"Player joined: {tokens[-1]}")
                elif tokens[1] == "update":
                    # Display the remainder of the message after the 'update ' token.
                    board_game_string = msg.split(sep="update ")[1]
                    self.draw_game_string(board_game_string)
                    #self.terminal_print("\nGame Board:\n" + board)
                elif tokens[1] == "turn":
                    # Server instructs whose turn it is. If it's this client, enter GET_USER_MOVE.
                    turn_name = tokens[2]
                    my_turn = (turn_name == self.username)
                    if my_turn:
                        self.terminal_print(
                            "Your turn. Please touch a square to make a move.")
                        # Reset any stale clicks and enter the move collection state.
                        self.click_queue = []
                        self.game_state = "GET_USER_MOVE"
                    else:
                        self.terminal_print(
                            "Please wait for your opponent to make a move.")
                else:
                    # Handle end-of-game and other tokens through a helper.
                    self.handle_game_over_tokens(tokens)
            except zmq.Again:
                # No message available; continue without failing.
                pass

        elif self.game_state == "GET_USER_MOVE":
            # In this state we expect to have a queued click to send as a move.
            if len(self.click_queue) > 0:
                (row, col) = self.click_queue[0]
                # Clear out pending clicks once one is used.
                self.click_queue = []
                # Format the move as "<col> <row> <username>" — server expects this.
                self.send_client_message(f"{col} {row} {self.username}")
                self.game_state = "WAIT_TO_PLAY"
            else:
                # If no click yet, watch for an explicit resign or urgent messages.
                if self.resign_button.isChecked():
                    self.resign_button.setChecked(False)
                    self.resign()
                try:
                    msg = self.sub_socket.recv_string(flags=zmq.NOBLOCK)
                    tokens = msg.split()
                    self.handle_game_over_tokens(tokens)
                except zmq.Again:
                    pass
        else:
            # Unknown state: do nothing to avoid crashes. This is defensive.
            pass
        # Trigger a repaint so GUI elements reflect any changes shortly.
        self.repaint()


# -----------------------------
# Run GUI
# -----------------------------
if __name__ == "__main__":
    # Standard Qt application bootstrap. The script blocks until the window closes.
    app = QApplication(sys.argv)
    gui = TicTacToeGUI()
    gui.show()
    sys.exit(app.exec())
