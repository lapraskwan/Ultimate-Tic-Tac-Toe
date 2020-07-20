from main_board import MainBoard
from monte_carlo_tree_search import MCTS
import sys
import random

class Player:
    def __init__(self, main_board):
        self.main_board = main_board

    def make_move(self, main_board_coor, sub_board_coor):
        """ If a move is made successfully, return True, else return False """
        result = self.main_board.make_move(self.main_board.current_player, main_board_coor, sub_board_coor)
        return result

class RandomPlayer(Player):
    def get_move(self):
        legal_moves = self.main_board.get_legal_moves()
        return random.choice(legal_moves)

class HumanPlayer(Player):
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
    def get_move(self):
        # print('===================================')
        tree = MCTS(self.main_board, 2)
        for _ in range(1000):
            # print('-------------------------')
            tree.simulation()
        best_move = tree.get_best_node().move
        return best_move