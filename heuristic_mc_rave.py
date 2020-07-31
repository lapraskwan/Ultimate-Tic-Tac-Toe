from mc_rave import MCRAVE, MCRAVENode
import math
from copy import deepcopy
import random


class HMCRAVE(MCRAVE):
    def __init__(self, root_game_state, exploration_weight, player_id):
        super().__init__(root_game_state, exploration_weight, player_id)
        self.root_node = HMCRAVENode(root_game_state, None, None, exploration_weight, player_id)

class HMCRAVENode(MCRAVENode):
    def __init__(self, game_state, move, parent_node, exploration_weight, player_id, mc_value=0, mc_count=0):
        super().__init__(game_state, move, parent_node, exploration_weight, player_id)
        self.total_reward = mc_value
        self.visited_times = mc_count

    def expand(self):
        """ Create child nodes """
        # print("self move: ", self.move)
        if not self.child_nodes:
            legal_moves = self.game_state.get_legal_moves()
            for move in legal_moves:
                # print("Added move: ", move)
                mc_count, mc_value, amaf_count, amaf_value = self.heuristic(move)
                self.action_amaf_count_value_map[move] = (amaf_count, amaf_value)
                child_game_state = deepcopy(self.game_state)
                child_game_state.make_move(move[0], move[1])
                self.child_nodes.append(self.get_new_node(child_game_state, move, self, self.exploration_weight, self.player_id, mc_value=mc_value, mc_count=mc_count))

    def get_new_node(self, game_state, move, parent_node, exploration_weight, player_id, mc_value = 0, mc_count = 0):
        return HMCRAVENode(game_state, move, parent_node, exploration_weight, player_id, mc_value=mc_value, mc_count=mc_count)

    def heuristic(self, move):
        """
        Return mc_count, mc_value, amaf_count, amaf_value

        1. If a move leads to immediate loss, give it -inf value
        2. If a move wins a sub board, give it +10 value
        3. If a move blocks a opponent, give it +8 value
        4. If a move is center give it +2 value
        5. If a move is on the same line of another same color cell, and the same line has no opposing color cell, give it +5
        6. If a move wins the game, give it inf value
        """
        # Only apply heuristics to AI's move
        if self.game_state.current_player != self.player_id:
            return 0, 0, 0, 0

        # Make a move
        game_state_copy = deepcopy(self.game_state)
        game_state_copy.make_move(move[0], move[1])

        # Check win
        if game_state_copy.winner is not None and game_state_copy.winner == self.player_id:
            return 1, math.inf, 1, math.inf

        # Check immediate loss
        legal_moves = game_state_copy.get_legal_moves()
        for move_2 in legal_moves:
            game_state_copy_2 = deepcopy(game_state_copy)
            game_state_copy_2.make_move(move_2[0], move_2[1])
            if game_state_copy_2.winner is not None and game_state_copy_2.winner != self.player_id:
                return 1, -math.inf, 1, -math.inf

        # Wins sub-board
        if game_state_copy.sub_board_values[move[0][0]][move[0][1]] == self.player_id:
            return 1, 1, 1, 10

        # # Blocks opponent winner that sub board
        # game_state_copy_opponent = deepcopy(self.game_state)
        # game_state_copy_opponent.current_player = int(2 / game_state_copy_opponent.current_player)
        # game_state_copy_opponent.make_move(move[0], move[1])
        # if game_state_copy_opponent.sub_board_values[move[0][0]][move[0][1]] == int(2 / self.player_id):
        #     return 1, 1, 1, 8

        # # Center
        # if move[1] == (1, 1):
        #     return 1, 1, 1, 2

        return 0, 0, 0, 0
