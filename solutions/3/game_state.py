"""The is a class to hold the state of the game.
It contains the '_board' which is a list of lists of unicode chars
and '_current_player' who is the symbol 'X' or 'O'. 

Following good python style, the _variable means that variable is not intended to be 
read or written to by an external user, but rather modified by means of 'setter' and 'getter' functions."""
class GameState:
    def __init__(self):
        """This is the function that creates the class as a new game state"""
        # 3x3 board initialized with spaces for empty
        self._board = [[' ' for _ in range(3)] for _ in range(3)]
        self._current_player = 'X'  # X always starts

    def get_board(self):
        """ Getter for board """
        return self._board

    def set_board(self, x):
        """ Setter for board """
        self._board = x

    def get_current_player(self):
        """This is a 'getter' function that provides the current player's symbol """
        return self._current_player

    def set_current_player(self, x):
        """ Setter for player """
        self._current_player = x

    def make_move(self, col, row):
        """Attempt to make a move. Return True if valid, False otherwise."""
        if 0 <= row < 3 and 0 <= col < 3 and self._board[row][col] == ' ':
            # Mark the board
            self._board[row][col] = self._current_player
            # Switch player
            self._current_player = 'O' if self._current_player == 'X' else 'X'
            return True
        return False

    def inspect_win(self):
        """Check for three in a row horizontally, vertically, or diagonally."""
        
        # Quick rename for easy typing-out below
        b = self._board
        # Each one of these is a possible winning state
        lines = [
            # Rows
            [b[0][0], b[0][1], b[0][2]],
            [b[1][0], b[1][1], b[1][2]],
            [b[2][0], b[2][1], b[2][2]],
            # Columns
            [b[0][0], b[1][0], b[2][0]],
            [b[0][1], b[1][1], b[2][1]],
            [b[0][2], b[1][2], b[2][2]],
            # Diagonals
            [b[0][0], b[1][1], b[2][2]],
            [b[0][2], b[1][1], b[2][0]]
        ]

        # Check each winning state lines
        for line in lines:
            # Make sure location is not a space, and has three of a kind
            if line[0] != ' ' and all(cell == line[0] for cell in line):
                return True
        return False

    def draw(self):
        """Return a string representation of the board using Unicode grid lines."""
        
        # Build up the string in pieces with smaller strings for each row
        rows = []
        for r in range(3):
            # Print the characters within the designated spaces, separated by unicode vertical bars
            rows.append(f" {self._board[r][0]} │ {self._board[r][1]} │ {self._board[r][2]} ")
            if r < 2:
                # Add a horizontal line with bars in between
                rows.append("───┼───┼───")
        # Make on big string from the rows of strings
        return "\n".join(rows)

