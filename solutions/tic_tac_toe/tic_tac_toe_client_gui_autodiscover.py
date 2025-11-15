"""
Tic-tac-toe client GUI using PyQt5 and ZeroMQ for networking.

This module implements a simple graphical client for a tic-tac-toe server.
It provides:
- A clickable 3x3 board rendered with large labels.
- A small information panel for entering a username and controlling the session.
- A terminal-like text area for status messages from the client and server.
- Discovery of a server via UDP broadcast, and communication via ZeroMQ PUB/SUB.

Protocol notes (as used by this client):
- The client listens for UDP broadcasts that include a "server_info" token and ports.
- After connecting, the client sends messages prefixed with a "client/" topic.
- The client subscribes to messages with topic "server/" and expects tokens such as:
    - "server/ update <board_string>"  where <board_string> is the ASCII board block
    - "server/ turn <username>"
    - "server/ joined <username>"
    - "server/ won <username>"
    - "server/ draw"
    - "server/ error"

Board representation:
- Internally the GUI expects a 9-character string for simplified drawing:
    - Characters are 'X', 'O', or '_' (underscore for empty)
    - The string is read left-to-right, top-to-bottom (row-major).
- The server may send a multi-line drawn board; this client extracts the
  "update " tail and prints it verbatim to the terminal.

This file focuses on being clear and educational; functions include
verbose inline documentation to help future maintainers understand the
flow of UI events and network interactions.
"""

import sys
import zmq
import time
import socket
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QMouseEvent


# -----------------------------
# Clickable label for board cells
# -----------------------------
class ClickableLabel(QLabel):
    """
    A QLabel subclass that represents one square on the tic-tac-toe board.

    Each ClickableLabel stores its board coordinates (row, col) and emits a
    'clicked' Qt signal when the user left-clicks it. The label is styled and
    sized for clear, touch-friendly interaction (large font, bold, centered).

    Signals:
        clicked(int col, int row): emitted on left mouse-press with coordinates.
    """
    clicked = pyqtSignal(int, int)  # row, col

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
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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

    Responsibilities:
    - Build and layout UI components (information panel, terminal, board).
    - Discover server via UDP broadcast and connect with ZeroMQ sockets.
    - Maintain a simple state machine for connecting, joining, and playing.
    - Poll for server messages at a regular interval using QTimer.
    - Queue and send user moves to the server.

    Attributes:
        game_state (str): textual state of the internal state machine.
        target_frame_rate_ms (int): QTimer interval in milliseconds.
        running (bool): whether the main loop is active; used when closing.
        click_queue (list): queued user clicks (col, row) awaiting submission.
        pub_socket, sub_socket: ZeroMQ sockets created on connect.
        username (str): local player's username once submitted.
    """

    # Simple state defaults. The state machine transitions are handled in game_loop().
    game_state = "CONNECTING"
    target_frame_rate_ms = 100
    running = True
    click_queue = []
    pub_socket = None
    sub_socket = None
    username = ""

    def __init__(self):
        """
        Initialize the main window and start the repeating game loop.

        This method:
        - Sets a window title and minimum size suitable for the layout.
        - Builds the UI by composing the information, terminal, and board panels.
        - Starts a QTimer that periodically calls game_loop() for processing.
        """
        super().__init__()
        self.setWindowTitle("Tic Tac Toe Client GUI")

        # Start with a reasonable minimum size instead of maximized so it's usable
        # on a variety of display sizes and in automated testing.
        self.setMinimumSize(600, 600)

        self.build_layout()
        self.start_main_game_loop()

    # -----------------------------------
    # Build all panels
    # -----------------------------------
    def build_layout(self):
        """
        Compose the top-level layout for the window.

        The UI is organized vertically:
        - information panel (username, submit, resign)
        - terminal panel (status label + message console)
        - touch panel (3x3 grid of ClickableLabel cells)
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
        and controls the high-level game actions (new game, resign).

        Returns:
            QHBoxLayout: the composed widget layout to be added to the main UI.
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

        Args:
            enabled (bool): True to enable inputs, False to disable.
        """
        for w in self.information_panel_widgets:
            w.setEnabled(enabled)

    # -----------------------------------
    # Touch Panel (tic tac toe board)
    # -----------------------------------
    def build_touch_panel(self):
        """
        Create a 3x3 grid of ClickableLabel widgets representing the game board.

        Each label is connected to handle_cell_clicked which places the click in
        a local queue for later processing by the state machine.

        Returns:
            QGridLayout: ready-to-add grid containing the 3x3 board.
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
            self.board_labels.append(row)

        return grid

    def handle_cell_clicked(self, col, row):
        """
        Handler called when a ClickableLabel emits a clicked signal.

        The click is enqueued to click_queue so it can be processed by the
        game state machine during the next timer tick. Immediate UI feedback
        is provided via the terminal panel.

        Args:
            col (int): clicked column index (0-2).
            row (int): clicked row index (0-2).
        """
        self.click_queue.append((col, row))
        # Game logic will go here soon; for now, echo the coordinates.
        self.terminal_print(f"Cell clicked: Column {col}, Row {row}")

    def draw_game_string(self, game_state: str):
        """
        Simple board renderer that accepts a compact 9-character string.

        The expected format is 9 characters: each is 'X', 'O', or '_' for empty.
        Characters are applied in row-major order across the 3x3 board.

        Args:
            game_state (str): a 9-character string representing the board.

        Notes:
            - This function is intentionally permissive about the source of the
              string; calling code should validate it before passing if needed.
            - If the string is invalid length, an error is printed and the
              function returns without changing the display.
        """
        if len(game_state) != 9:
            print("ERROR: Invalid game string")
            return

        for i, ch in enumerate(game_state):
            r, c = divmod(i, 3)
            # Render underscore as an empty label for ergonomics.
            self.board_labels[r][c].setText("" if ch == "_" else ch)

    # -----------------------------------
    # Terminal Panel
    # -----------------------------------
    def build_terminal_panel(self):
        """
        Construct a vertical layout containing:
        - a top row with a connection status label and a 'New Game' button
        - a QTextEdit used as a read-only terminal to present messages.

        Returns:
            QVBoxLayout: the assembled terminal panel layout.
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

        Args:
            text (str): text to append to the QTextEdit terminal.
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

        Ensures sockets are closed cleanly and, if a game is running, sends a
        resign message to the server before closing the PUB socket.
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

        Expected forms:
            - ['server/', 'won', '<username>']
            - ['server/', 'draw']
            - ['server/', 'error']

        The method prints relevant messages to the terminal and marks the
        GUI as not running when the game is over.
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

        The server-side protocol expects the client to send "resign <username>"
        and this client prefixes messages with "client/" when sending.
        """
        self.send_client_message(f"resign {self.username}")

    def set_game_over(self):
        """
        Mark the local state as game-over and provide console feedback.

        This will stop the main polling loop and prompt the user to close the GUI.
        """
        self.terminal_print("The game is over.  Please close the GUI.")
        self.running = False

    def send_client_message(self, message_string):
        """
        Send a client-originating message over the PUB socket with the required topic.

        Args:
            message_string (str): the payload to send after the 'client/' topic.
        """
        # The server expects the topic "client/" followed by the message body.
        self.pub_socket.send_string(f"client/ {message_string}")

    def discover_server(self, port, timeout=10):
        """
        Listen for a UDP broadcast to discover the server's IP and ports.

        Args:
            port (int): UDP port to bind to for discovery messages.
            timeout (int): seconds to wait before giving up.

        Returns:
            tuple: (server_ip, port_to_clients, port_from_clients) where the
                   latter two are strings extracted from the broadcast payload.
        """
        # Create a UDP socket for discovery broadcasts.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Allow quick rebinds for repeated local testing.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind on all interfaces so broadcasts on any active NIC are seen.
        sock.bind(("", port))

        self.terminal_print(
            "Searching for Tic-Tac-Toe server via LAN broadcast...")
        start = time.time()
        server_ip = None

        # Block in short increments until timeout: this keeps the UI responsive.
        while time.time() - start < timeout:
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
                    break
            except:
                # Sleep briefly to avoid busy-waiting; exceptions commonly occur due to timeouts.
                time.sleep(0.5)

        sock.close()
        return server_ip, port_to_clients, port_from_clients

    def start_main_game_loop(self):
        """
        Start a QTimer that periodically calls game_loop() to process UI and network events.

        Using a timer keeps the UI responsive while allowing simple polling-style networking.
        """
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        # 100 ms interval: approximately 10 updates per second, sufficient for this client.
        self.timer.start(self.target_frame_rate_ms)

    def game_loop(self):
        """
        Primary state machine for the client.

        The method implements a sequence of states:
        - CONNECTING: discover server and set up ZeroMQ sockets
        - WAIT_NEW_GAME: wait for user to press New Game
        - WAIT_USER_NAME: wait for user to submit their username
        - WAIT_TO_PLAY: handle incoming server messages until it's this player's turn
        - GET_USER_MOVE: wait for a click and send it as a move

        The loop also handles socket timeouts, message parsing, and transitions
        driven by buttons, clicks, and server events.
        """
        if self.running == False:
            return

        if self.game_state == "CONNECTING":
            # Initial connecting state: find server, then establish ZMQ PUB/SUB sockets.
            self.set_status_searching()
            self.set_information_panel_enable(False)
            self.port_to_broadcast = 41110
            server_ip, port_to_clients, port_from_clients = self.discover_server(
                self.port_to_broadcast)
            if not server_ip:
                # Discovery failed: show error and stop attempting to proceed.
                self.set_status_error()
                self.terminal_print("No server found. Exiting.")
                return

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
                    board = msg.split(sep="update ")[1]
                    self.terminal_print("\nGame Board:\n" + board)
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
    sys.exit(app.exec_())