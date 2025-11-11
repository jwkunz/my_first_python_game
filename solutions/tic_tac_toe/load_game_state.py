from game_state import *

# New: parse a board string produced by draw() and return a GameState or None
def load_game_string(s):
    """Parse a board string created by draw() and return a GameState or None on failure."""
    lines = s.splitlines()
    # Expect exactly 5 lines: row, separator, row, separator, row
    if len(lines) != 5:
        return None
    # Check separator lines
    if lines[1] != "───┼───┼───" or lines[3] != "───┼───┼───":
        return None

    allowed = {'X', 'O', ' '}
    rows_parsed = []
    # Data lines are 0,2,4
    for idx in (0, 2, 4):
        line = lines[idx]
        # Expected format: " {c} │ {c} │ {c} " (length 11)
        if len(line) != 11:
            return None
        # Check expected separator characters and spaces
        if line[0] != ' ' or line[2] != ' ' or line[4] != ' ' or line[6] != ' ' or line[8] != ' ' or line[10] != ' ':
            return None
        if line[3] != '│' or line[7] != '│':
            return None
        c1, c2, c3 = line[1], line[5], line[9]
        if c1 not in allowed or c2 not in allowed or c3 not in allowed:
            return None
        rows_parsed.append([c1, c2, c3])

    # Validate counts of X and O
    flat = [c for row in rows_parsed for c in row]
    x_count = flat.count('X')
    o_count = flat.count('O')
    if not (x_count == o_count or x_count == o_count + 1):
        return None

    # Helper to check win for a player
    def is_winner(b, p):
        # rows
        for r in range(3):
            if all(b[r][c] == p for c in range(3)):
                return True
        # cols
        for c in range(3):
            if all(b[r][c] == p for r in range(3)):
                return True
        # diags
        if b[0][0] == p and b[1][1] == p and b[2][2] == p:
            return True
        if b[0][2] == p and b[1][1] == p and b[2][0] == p:
            return True
        return False

    x_win = is_winner(rows_parsed, 'X')
    o_win = is_winner(rows_parsed, 'O')
    # Both cannot win
    if x_win and o_win:
        return None
    # If X won, X must have one more move than O
    if x_win and x_count != o_count + 1:
        return None
    # If O won, counts must be equal
    if o_win and x_count != o_count:
        return None

    # Create GameState and populate internal data
    game = GameState()
    game.set_board(rows_parsed)
    # Decide whose turn it is now: X moves when counts equal, else O
    next_player = 'X' if x_count == o_count else 'O'
    game.set_current_player(next_player)
    return game

def _run_test(name, s, expect_valid):
    res = load_game_string(s)
    ok = (res is not None) == expect_valid
    status = "PASS" if ok else "FAIL"
    print(f"{name}: {status} (expected_valid={expect_valid}, got_valid={res is not None})")
    if res is not None:
        # try to show a little info about the loaded state without assuming too much API
        player = getattr(res, "current_player", None) or getattr(res, "get_current_player", lambda: None)()
        board = getattr(res, "board", None)
        print("  current_player:", player)
        if board:
            for r in board:
                print("  ", r)
    print()

if __name__ == "__main__":
    # valid: empty board
    s_empty = (
        "   │   │   \n"
        "───┼───┼───\n"
        "   │   │   \n"
        "───┼───┼───\n"
        "   │   │   "
    )
    _run_test("empty board", s_empty, True)

    # valid: X moved center
    s_x_center = (
        "   │   │   \n"
        "───┼───┼───\n"
        "   │ X │   \n"
        "───┼───┼───\n"
        "   │   │   "
    )
    _run_test("X in center", s_x_center, True)

    # invalid: both players have winning lines
    s_both_win = (
        " X │ X │ X \n"
        "───┼───┼───\n"
        "   │   │   \n"
        "───┼───┼───\n"
        " O │ O │ O "
    )
    _run_test("both win", s_both_win, False)

    # invalid: bad separator line
    s_bad_sep = (
        "   │   │   \n"
        "-----------\n"
        "   │   │   \n"
        "───┼───┼───\n"
        "   │   │   "
    )
    _run_test("bad separator", s_bad_sep, False)

    # invalid: O has more moves than X
    s_o_more = (
        " O │   │   \n"
        "───┼───┼───\n"
        "   │   │   \n"
        "───┼───┼───\n"
        "   │   │   "
    )
    _run_test("O more than X", s_o_more, False)