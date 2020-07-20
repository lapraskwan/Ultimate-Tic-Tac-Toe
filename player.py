from main_board import MainBoard
from monte_carlo_tree_search import MCTS
import sys
import random

class Player:
    """
    Represents a player who make moves to play the game
    """
    def __init__(self, main_board, player_id):
        self.main_board = main_board
        # Only used in MCTSPlayer to check whether it has won in a simulation
        self.player_id = player_id

    def make_move(self, main_board_coor, sub_board_coor):
        """ If a move is made successfully, return True, else return False """
        result = self.main_board.make_move(main_board_coor, sub_board_coor)
        return result
    
    def get_move(self):
        """ 
        Please overwrite this method

        Return a tuple of main board coordinates and sub board coordinates
        e.g. ( (0, 2), (2, 1) )
        """
        raise NotImplementedError("Function get_move() is not implemented")

class RandomPlayer(Player):
    """
    A player that chooses moves randomly from the legal moves
    """
    def get_move(self):
        legal_moves = self.main_board.get_legal_moves()
        return random.choice(legal_moves)

class HumanPlayer(Player):
    """
    Let the user chooses the moves by typing into the command line.
    """
    def get_move(self):
        while True:
            print("Possible sub-boards:", self.main_board.allowed_sub_boards)
            main_board_coor_x, main_board_coor_y = map(int, input("Please input the coordinate of a sub-board: ").split(','))
            sub_board_coor_x, sub_board_coor_y = map(int, input("Please input the coordinate of a cell in the sub-board: ").split(','))
            input_coor = ((main_board_coor_x, main_board_coor_y), (sub_board_coor_x, sub_board_coor_y))
            if main_board_coor_x in range(self.main_board.board_size) and main_board_coor_y in range(self.main_board.board_size) and sub_board_coor_x in range(self.main_board.board_size) and sub_board_coor_y in range(self.main_board.board_size):
                break
            else:
                print("Invalid move. Coordinates are intergers from 0-" + str(self.main_board.board_size - 1) + ".")
        return input_coor

class MCTSPlayer(Player):
    """
    A player that uses the Monte Carlo Tree Search to choose a move that is more likely to win
    """
    def get_move(self):
        tree = MCTS(self.main_board, 2, self.player_id)
        for _ in range(100):
            tree.simulation()
        best_move = tree.get_best_node().move
        return best_move