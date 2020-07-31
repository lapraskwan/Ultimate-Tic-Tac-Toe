from main_board import MainBoard
from monte_carlo_tree_search import MCTS
from mc_rave import MCRAVE
from heuristic_mc_rave import HMCRAVE
from mcts_solver import MCTSSolver
import sys
import random
import re
from copy import deepcopy
import time
import math

class Player:
    """
    Represents a player who make moves to play the game
    """
    def __init__(self, main_board):
        self.main_board = main_board

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

    User should input two strings with a format of [0-2],[0,2], e.g. 1,2, representing the main board coor and the sub board coor
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
    def __init__(self, main_board, player_id, num_of_simulation = 100, time_limit = None):
        super().__init__(main_board)
        # To check whether this player has won in a simulation
        self.player_id = player_id
        self.num_of_simulation = num_of_simulation
        self.time_limit = time_limit
        self.tree = MCTS(deepcopy(self.main_board), 2, self.player_id)
        self.best_node = self.tree.root_node
    
    def get_opponent_move(self):
        for x_main in range(self.main_board.board_size):
            for y_main in range(self.main_board.board_size):
                for x_sub in range(self.main_board.board_size):
                    for y_sub in range(self.main_board.board_size):
                        if self.best_node.game_state.sub_boards[y_main][x_main].cells[y_sub][x_sub] != self.main_board.sub_boards[y_main][x_main].cells[y_sub][x_sub]:
                            return ((y_main, x_main), (y_sub, x_sub))
        return None

    def get_move(self):
        start_time = time.time()
        # Update root node to the node after opponent moved
        if not self.tree.root_node.child_nodes:
            self.tree.root_node.expand()
        for node in self.tree.root_node.child_nodes:
            if node.move == self.get_opponent_move():
                self.tree.root_node = node
                self.tree.root_node.parent_node = None
                break
        # Run simulations
        if self.num_of_simulation != 0:
            for _ in range(self.num_of_simulation):
                if self.time_limit is not None and time.time() - start_time >= self.time_limit:
                    break
                self.tree.simulation()

        self.best_node = self.tree.get_best_node()
        best_move = self.best_node.move
        end_time = time.time()
        # print(self.player_id, end_time - start_time)
        return best_move
    
    def make_move(self, main_board_coor, sub_board_coor):
        """ If a move is made successfully, return True, else return False """
        result = self.main_board.make_move(main_board_coor, sub_board_coor)
        if result:
            # Update self.tree, so that the root node is the chosen child node of the original root node
            # At this moment, opponent is the current_player
            self.tree.root_node = self.best_node
            self.tree.root_node.parent_node = None
        return result

class MCRAVEPlayer(MCTSPlayer):
    def __init__(self, main_board, player_id, num_of_simulation=100, time_limit=None):
        super().__init__(main_board, player_id, num_of_simulation=num_of_simulation, time_limit=time_limit)
        self.tree = MCRAVE(deepcopy(self.main_board), 2, self.player_id)

class HMCRAVEPlayer(MCTSPlayer):
    def __init__(self, main_board, player_id, num_of_simulation=100, time_limit=None):
        super().__init__(main_board, player_id, num_of_simulation=num_of_simulation, time_limit=time_limit)
        self.tree = HMCRAVE(deepcopy(self.main_board), 2, self.player_id)

class MCTSSolverPlayer(MCTSPlayer):
    def __init__(self, main_board, player_id, num_of_simulation=100, time_limit=None):
        super().__init__(main_board, player_id, num_of_simulation=num_of_simulation, time_limit=time_limit)
        self.tree = MCTSSolver(deepcopy(self.main_board), 2, self.player_id)

    def get_move(self):
        start_time = time.time()
        # Update root node to the node after opponent moved
        if not self.tree.root_node.child_nodes:
            self.tree.root_node.expand()
        for node in self.tree.root_node.child_nodes:
            if node.move == self.get_opponent_move():
                self.tree.root_node = node
                self.tree.root_node.parent_node = None
                break
        # Run simulations
        if self.num_of_simulation != 0:
            for _ in range(self.num_of_simulation):
                if self.time_limit is not None and time.time() - start_time >= self.time_limit:
                    break
                for child_node in self.tree.root_node.child_nodes:
                    # Early stop
                    if child_node.total_reward == math.inf:
                        return child_node.move
                self.tree.simulation()

        self.best_node = self.tree.get_best_node()
        best_move = self.best_node.move
        end_time = time.time()
        # print(self.player_id, end_time - start_time)
        return best_move