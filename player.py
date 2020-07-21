from main_board import MainBoard
from monte_carlo_tree_search import MCTS
import sys
import random
import re

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
        coor_format = re.compile('\d,\d')
        while True:
            print("Legal sub-boards:", self.main_board.allowed_sub_boards)
            while True:
                input_1 = input("Please input the coordinate of a sub-board: ")
                if coor_format.match(input_1) is None:
                    print("Invalid format. Expected format: 2,2")
                    continue
                main_board_coor_x, main_board_coor_y = map(int, input_1.split(','))
                break

            while True:
                input_2 = input("Please input the coordinate of a cell in the sub-board: ")
                if coor_format.match(input_2) is None:
                    print("Invalid format. Expected format: 2,2")
                    continue
                sub_board_coor_x, sub_board_coor_y = map(int, input_2.split(','))
                break

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
    def __init__(self, main_board, player_id):
        super().__init__(main_board, player_id)
        self.tree = MCTS(self.main_board, 2, self.player_id)
        self.best_node = None
    
    def get_opponent_move(self):
        if self.best_node is None:
            return None
        for x_main in range(self.main_board.board_size):
            for y_main in range(self.main_board.board_size):
                for x_sub in range(self.main_board.board_size):
                    for y_sub in range(self.main_board.board_size):
                        if self.best_node.game_state.sub_boards[y_main][x_main].cells[y_sub][x_sub] != self.main_board.sub_boards[y_main][x_main].cells[y_sub][x_sub]:
                            return ((y_main, x_main), (y_sub, x_sub))

    def get_move(self):
        # Update root node to the node after opponent moved
        if not self.tree.root_node.child_nodes:
            self.tree.root_node.expand()
        for node in self.tree.root_node.child_nodes:
            if node.move == self.get_opponent_move():
                self.tree.root_node = node
                node.parent_node = None
                break
        
        # Run simulations
        for _ in range(100):
            self.tree.simulation()

        self.best_node = self.tree.get_best_node()
        best_move = self.best_node.move
        return best_move
    
    def make_move(self, main_board_coor, sub_board_coor):
        """ If a move is made successfully, return True, else return False """
        result = self.main_board.make_move(main_board_coor, sub_board_coor)
        if result:
            # Update self.tree, so that the root node is the chosen child node of the original root node
            self.tree.root_node = self.best_node
            self.tree.root_node.parent_node = None
        return result
