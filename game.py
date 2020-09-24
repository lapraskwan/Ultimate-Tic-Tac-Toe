import matplotlib.pyplot as plt
import sys
import os
import argparse
import time

from main_board import MainBoard
from player import RandomPlayer, HumanPlayer, MCTSPlayer, MCRAVEPlayer, HMCRAVEPlayer, MCTSSolverPlayer, MCTSAlphaPlayer
import config
from neural_network import NeuralNetwork


def get_parser():
    # Parse Arguments
    parser = argparse.ArgumentParser(description="An Untimate Tic Tac Toe Game")

    parser.add_argument('player_1',
                        help="Agent of player 1. (random, human, mcts, mctss, mcrave or hmcrave)",
                        choices=['random', 'human', 'mcts', 'mctss', 'mctsa', 'mcrave', 'hmcrave'])

    parser.add_argument('player_2',
                        help="Agent of player 2. (random, human, mcts, mctss, mcrave or hmcrave)",
                        choices=['random', 'human', 'mcts', 'mctss', 'mctsa', 'mcrave', 'hmcrave'])

    parser.add_argument('-m',
                        '--mute',
                        help="Do not print board",
                        action="store_true",
                        default=config.mute)

    parser.add_argument('-n',
                        '--number_of_games',
                        help="Number of games to play",
                        type=int,
                        default=config.number_of_games)

    parser.add_argument('-b',
                        '--board_size',
                        help="Board Size. Default 3.",
                        type=int,
                        default=config.board_size)

    parser.add_argument('-s',
                        '--number_of_simulations',
                        help="Number of simulations per move.",
                        type=int,
                        default=config.number_of_simulations)

    parser.add_argument('-t',
                        '--time_limit',
                        help="Time limit per move.",
                        type=float,
                        default=config.time_limit)
    return parser


def get_player(main_board, player_type, player_id, number_of_simulations=config.number_of_simulations, time_limit=config.time_limit, net=None):
    if player_type == 'random':
        return RandomPlayer(main_board)
    if player_type == 'human':
        return HumanPlayer(main_board)
    if player_type == 'mcts':
        return MCTSPlayer(main_board, player_id, number_of_simulations, time_limit)
    if player_type == 'mcrave':
        return MCRAVEPlayer(main_board, player_id, number_of_simulations, time_limit)
    if player_type == 'hmcrave':
        return HMCRAVEPlayer(main_board, player_id, number_of_simulations, time_limit)
    if player_type == 'mctss':
        return MCTSSolverPlayer(main_board, player_id, number_of_simulations, time_limit)
    if player_type == 'mctsa':
        return MCTSAlphaPlayer(main_board, player_id, net, num_of_simulation=number_of_simulations, time_limit=time_limit)

def start_game(player_type_1='random', player_type_2='random', mute=config.mute, board_size=config.board_size, number_of_simulations=config.number_of_simulations, time_limit=config.time_limit, net=None):
    if not mute:
        print('***********************')
        print(' Ultimate Tic-Tac-Toe! ')
        print('***********************')
    main_board = MainBoard(board_size)
    player_1 = get_player(main_board, player_type_1, 1, number_of_simulations, time_limit, net)
    player_2 = get_player(main_board, player_type_2, 2, number_of_simulations, time_limit, net)
    if not mute:
        main_board.print_board()

    current_player = player_1
    while main_board.winner is None:
        main_board_coor, sub_board_coor = current_player.get_move()
        # print(current_player.tree.root_node.action_prob_dict)
        # for child_node in current_player.tree.root_node.child_nodes:
        #     print(child_node.total_reward)
        while not current_player.make_move(main_board_coor, sub_board_coor):
            main_board_coor, sub_board_coor = current_player.get_move()
        current_player = player_1 if current_player == player_2 else player_2
        if not mute:
            main_board.print_board()

    if main_board.winner == 0:
        if not mute:
            print("The result of this game is ...... a draw!!!")
        return 0
    else:
        if not mute:
            print("The winner is ...... Player " + str(int(2 / main_board.current_player)) + "!!!")
        return int(2 / main_board.current_player)

def main():
    parser = get_parser()
    args = parser.parse_args()

    player_1 = args.player_1
    player_2 = args.player_2
    mute = args.mute
    number_of_games = args.number_of_games
    board_size = args.board_size
    number_of_simulations = args.number_of_simulations
    time_limit = args.time_limit

    net = NeuralNetwork()
    # Initialize the network with the best model.
    file_path = config.model_directory + "best_model.h5"
    if os.path.exists(file_path):
        # The following error is showed if I train the network in Google Colab and then use it on my own machine:
        # 'This TensorFlow binary is optimized with Intel(R) MKL-DNN to use the following CPU instructions 
        # in performance critical operations:  SSE4.1 SSE4.2 AVX AVX2 FMA
        # To enable them in non-MKL-DNN operations, rebuild TensorFlow with the appropriate compiler flags.'
        # So after a little bit of google-ing I added the following line.
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        net.load_model("best_model.h5")
    else:
        print("Trained model doesn't exist. Using random weights.")

    win = 0
    loss = 0
    draw = 0
    for i in range(number_of_games):
        print("Game " + str(i) + " starts!")
        start_game_time = time.time()
        result = start_game(player_1, player_2, mute, board_size, number_of_simulations, time_limit, net)
        print("Game Time: ", time.time() - start_game_time)
        if result == 0:
            draw += 1
        elif result == 1:
            win += 1
        else:
            loss += 1

    print("Result of " + str(number_of_games) + " game(s) " + player_1 + " vs " + player_2 + "")
    if number_of_simulations:
        print("Number of simulations per move: ", number_of_simulations)
    if time_limit:
        print("Time limit per move: ", time_limit)
    print("Win (Player 1): ", win)
    print("Draw: ", draw)
    print("Loss: ", loss)


if __name__ == "__main__":
    main()
