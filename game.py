import sys
import argparse

from main_board import MainBoard
from player import RandomPlayer, HumanPlayer, MCTSPlayer

def get_parser():
    # Parse Arguments
    parser = argparse.ArgumentParser(
        description="An Untimate Tic Tac Toe Game")
    parser.add_argument('player_1', help="Agent of player 1. (random, human or MCTS)")
    parser.add_argument('player_2', help="Agent of player 2. (random, human or MCTS)")
    parser.add_argument('-m', '--mute', action="store_true", help="Do not print board")
    parser.add_argument('-n', '--number_of_games', type=int, help="Number of games to play. Default 1")
    parser.add_argument('-s', '--board_size', type=int, help="Board Size. Default 3.")
    return parser

def get_player(main_board, player_type, player_id):
    if player_type == 'random':
        return RandomPlayer(main_board, player_id)
    if player_type == 'human':
        return HumanPlayer(main_board, player_id)
    if player_type == 'MCTS':
        return MCTSPlayer(main_board, player_id)

def start_game(player_type_1 = 'random', player_type_2 = 'random', is_print_board = True, board_size = 3):
    if is_print_board:
        print('***********************')
        print(' Ultimate Tic-Tac-Toe! ')
        print('***********************')
    main_board = MainBoard(board_size)
    player_1 = get_player(main_board, player_type_1, 1)
    player_2 = get_player(main_board, player_type_2, 2)
    if is_print_board:
        main_board.print_board()

    current_player = player_1
    while main_board.winner is None:
        main_board_coor, sub_board_coor = current_player.get_move()
        while not current_player.make_move(main_board_coor, sub_board_coor):
            main_board_coor, sub_board_coor = current_player.get_move()
        current_player = player_1 if current_player == player_2 else player_2
        if is_print_board:
            main_board.print_board()

    if main_board.winner == 0:
        if is_print_board:
            print("The result of this game is ...... a draw!!!")
        return 0
    else:
        if is_print_board:
            print("The winner is ...... Player " + str(int(2 / main_board.current_player)) + "!!!")
        return int(2 / main_board.current_player)

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    
    player_1 = args.player_1
    player_2 = args.player_2
    is_print_board = False if args.mute else True
    number_of_games = args.number_of_games if args.number_of_games else 1
    board_size = args.board_size if args.board_size else 3

    win = 0
    loss = 0
    draw = 0
    for i in range(number_of_games):
        print("Game " + str(i) + " starts!")
        result = start_game(player_1, player_2, is_print_board, board_size)
        if result == 0:
            draw += 1
        elif result == 1:
            win += 1
        else:
            loss += 1

    print("Result of " + str(number_of_games) + " game(s) " + player_1 + " vs " + player_2 + "")
    print("Win (Player 1): ", win)
    print("Draw: ", draw)
    print("Loss: ", loss)