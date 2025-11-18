"""
Local terminal-based Tic Tac Toe using a clean state machine.
"""

from game_state import *

def play_local_game():
    # -------------------------------
    # State enum
    # -------------------------------
    INIT, DRAW, PROMPT_MOVE, PROCESS_MOVE, CHECK_WIN, CHECK_DRAW, GAME_OVER = range(7)

    state = INIT
    running = True

    game = None
    last_winner = None

    print("=== Terminal Tic Tac Toe (State Machine Edition) ===")

    # -------------------------------
    # Main game loop
    # -------------------------------
    while running:

        # ============================================================
        # INIT — create game and print greeting
        # ============================================================
        if state == INIT:
            game = GameState()
            print("\nWelcome to Tic Tac Toe!")
            print("Enter moves as: column row")
            print("Example: 0 0 is top-left, 1 0 is top-center")
            state = DRAW
            continue

        # ============================================================
        # DRAW — draw board and show whose turn it is
        # ============================================================
        if state == DRAW:
            print("\n" + str(game))
            print(f"\nPlayer {game.get_current_player()}'s turn.")
            state = PROMPT_MOVE
            continue

        # ============================================================
        # PROMPT_MOVE — get move input from player
        # ============================================================
        if state == PROMPT_MOVE:
            move = input("Enter your move (col row): ").strip()

            # Try to parse
            try:
                col, row = map(int, move.split())
                parsed_move = (col, row)
                state = PROCESS_MOVE
            except ValueError:
                print("❌ Invalid input! Enter two numbers between 0 and 2.")
                state = DRAW
            continue

        # ============================================================
        # PROCESS_MOVE — validate & apply the move
        # ============================================================
        if state == PROCESS_MOVE:
            col, row = parsed_move

            # Validate index bounds
            if not (0 <= col <= 2 and 0 <= row <= 2):
                print("❌ Move must use numbers in {0,1,2}. Try again.")
                state = DRAW
                continue

            # Try to make the move
            if not game.make_move(col, row):
                print("❌ Invalid move! That square is taken. Try again.")
                state = DRAW
                continue

            # Move accepted → check for win
            state = CHECK_WIN
            continue

        # ============================================================
        # CHECK_WIN — did the move win the game?
        # ============================================================
        if state == CHECK_WIN:
            if game.inspect_win():
                # The winner is the player who *just* moved
                last_winner = 'O' if game.get_current_player() == 'X' else 'X'
                state = GAME_OVER
            else:
                state = CHECK_DRAW
            continue

        # ============================================================
        # CHECK_DRAW — is the board full?
        # ============================================================
        if state == CHECK_DRAW:
            if game.inspect_draw():
                last_winner = None  # indicates draw
                state = GAME_OVER
            else:
                state = DRAW  # next player's turn
            continue

        # ============================================================
        # GAME_OVER — print result and exit
        # ============================================================
        if state == GAME_OVER:
            print("\n" + str(game))
            if last_winner:
                print(f"\n🎉 Player {last_winner} wins!")
            else:
                print("\n🤝 It's a draw!")
            running = False
            continue


# If run as main, start the state-machine game
if __name__ == "__main__":
    play_local_game()
