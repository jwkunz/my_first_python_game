"""
This is a simple tic tac toe game played in a local terminal
"""
from game_state import *

# ------------------------
# Simple main game loop
# ------------------------
def play_local_game():
    # Create a new game
    game = GameState()
    # Greet the user
    print("Welcome to Tic Tac Toe!")
    print("Enter moves as: column row\ne.g. 0 0 is top-left; 1 0 is top-center")

    # Game loop
    while True:
        # Draw the new state
        print("\n" + str(game))
        # Ask for a move
        print(f"\nPlayer {game.get_current_player()}'s turn.")
        move = input("Enter your move (col row): ").strip()

        # Validate input
        try:
            col, row = map(int, move.split())
        except ValueError:
            print("Invalid input! Please enter two numbers separated by a space. Valid indexes are {0,1,2}")
            continue

        if not game.make_move(col, row):
            print("Invalid move! Try again. Valid indexes are {0,1,2}")
            continue

        # Check for win
        if game.inspect_win():
            print("\n" + str(game))
            # Remember the winner is the person who just finishe their move
            winner = 'O' if game.get_current_player() == 'X' else 'X'
            print(f"\n🎉 Player {winner} wins!")
            break

        # Check for draw
        if game.inspect_draw():
            print("\n" + str(game))
            print("\nIt's a draw!")
            break

# If this file is called by itself, run the game loop
if __name__ == "__main__":
    play_local_game()
