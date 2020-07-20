"""
UI  Mode
Command line mode

Game:
    1. Initialize Board
    2. Choose players (Human, Random, AI) (Player 1 vs PLlayer 2)
    3. While not end game: 
        player 1 makes move, player 2 makes move...

Player:
    - Get All Possible Moves
    1. Random:
        - Randomly Pick one
    2. Human:
        - User's choice
    3. AI
        - Choose the best move after Monte Carlo Tree Search
"""
from main_board import MainBoard
from player import RandomPlayer, HumanPlayer, MCTSPlayer

def get_player(main_board, player_type):
    if player_type == 'random':
        return RandomPlayer(main_board)
    if player_type == 'human':
        return HumanPlayer(main_board)
    if player_type == 'MCTS':
        return MCTSPlayer(main_board)

def start_game(player_type_1 = 'random', player_type_2 = 'random'):
    # print('***********************')
    # print(' Ultimate Tic-Tac-Toe! ')
    # print('***********************')
    main_board = MainBoard()
    player_1 = get_player(main_board, player_type_1)
    player_2 = get_player(main_board, player_type_2)
    # main_board.print_board()

    current_player = player_1
    while main_board.winner is None:
        main_board_coor, sub_board_coor = current_player.get_move()
        while not current_player.make_move(main_board_coor, sub_board_coor):
            main_board_coor, sub_board_coor = current_player.get_move()
        current_player = player_1 if current_player == player_2 else player_2
        # main_board.print_board()
    if main_board.winner == 0:
        print("The result of this game is ...... a draw!!!")
        return 0
    else:
        print("The winner is ...... Player " + str(int(2 / main_board.current_player)) + "!!!")
        return int(2 / main_board.current_player)

if __name__ == "__main__":
    win = 0
    loss = 0
    draw = 0
    for i in range(1000):
        print("Game " + str(i) + " starts!")
        result = start_game('MCTS', 'random')
        if result == 0:
            draw += 1
        elif result == 1:
            win += 1
        else:
            loss += 1
    print("Result of 50 games MCTS vs Random")
    print("Win: ", win)
    print("Draw: ", draw)
    print("Loss: ", loss)