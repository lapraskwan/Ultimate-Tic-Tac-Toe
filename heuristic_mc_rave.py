from monte_carlo_tree_search import MCTS, Node
import math
from copy import deepcopy
import random


class HMCRAVE(MCTS):
    def __init__(self, root_game_state, exploration_weight, player_id):
        super().__init__(root_game_state, exploration_weight, player_id)
        self.root_node = HMCRAVENode(root_game_state, None, None, exploration_weight, player_id)

    def get_best_node(self):
        """ Get the best child node """
        best_node = None
        max_reward = None
        for node in self.root_node.child_nodes:
            # Compute_UCB1() may return infinity if both are 0, for exploration, but we should ignore this node since it's not visited at all
            if node.visited_times == 0:
                continue
            reward = node.total_reward / node.visited_times
            if best_node is None and max_reward is None:
                best_node = node
                max_reward = reward
            else:
                if reward > max_reward:
                    max_reward = reward
                    best_node = node
        if best_node is None:
            return self.root_node.child_nodes[0]
        return best_node

    def simulation(self):
        """ Execute one iteration of simulation (selection + expansion + rollout + backpropagation) """
        target_node = self.selection()
        if target_node.visited_times != 0 and target_node.game_state.winner is None:
            target_node.expand()
            target_node = target_node.child_nodes[0]
        reward, action_sequence = target_node.rollout()
        if target_node.game_state.current_player == self.player_id:
            target_node.back_propagation(-reward, action_sequence)
        else:
            target_node.back_propagation(reward, action_sequence)


class HMCRAVENode(Node):
    def __init__(self, game_state, move, parent_node, exploration_weight, player_id, mc_value=0, mc_count=0):
        super().__init__(game_state, move, parent_node, exploration_weight, player_id)
        # Map of tuples: { action: (amaf_count, amaf_value) }
        self.action_amaf_count_value_map = {}
        self.total_reward = mc_value
        self.visited_times = mc_count

    def rollout(self):
        """ 
        Plays a full game from self.game_state with random actions 

        Return the reward. (1 if this agent wins, 0 is draw, -1 if this agent losses)
        Return all the performed actions.
        """
        action_sequence = []
        game_state_copy = deepcopy(self.game_state)
        while game_state_copy.winner is None:
            # Get current_player before move is make
            current_player = game_state_copy.current_player
            legal_moves = game_state_copy.get_legal_moves()
            main_board_coor, sub_board_coor = random.choice(legal_moves)
            game_state_copy.make_move(main_board_coor, sub_board_coor)
            # Only append actions made by this AI
            if current_player == self.player_id:
                action_sequence.append((main_board_coor, sub_board_coor))
        if game_state_copy.winner == self.player_id:
            # This agent wins
            return 1, action_sequence
        elif game_state_copy.winner == 0:
            return 0, action_sequence
        else:
            return -1, action_sequence

    def compute_UCB1(self):
        """ Compute the modified UCB1 value """
        amaf_count = self.parent_node.action_amaf_count_value_map[self.move][0]
        amaf_value = self.parent_node.action_amaf_count_value_map[self.move][1]

        if self.visited_times == 0:
            # UCB1 = amaf_value / amaf_count
            return math.inf
        beta = amaf_count / (self.visited_times + amaf_count + 4 * self.visited_times * amaf_count * 0.2)
        if amaf_count == 0:
            UCB1 = self.total_reward / self.visited_times + self.exploration_weight * \
                math.sqrt(math.log(self.parent_node.visited_times) / self.visited_times)
        else:
            UCB1 = (1 - beta) * (self.total_reward / self.visited_times) + beta * (amaf_value / amaf_count) + \
                self.exploration_weight * math.sqrt(math.log(self.parent_node.visited_times) / self.visited_times)

        return UCB1

    def back_propagation(self, reward, action_sequence):
        """ Update the visited_times and total_reward of the current node, and also its parent node, until the root node is reached """
        self.visited_times += 1
        self.total_reward += reward
        for action in action_sequence:
            # All legal moves of a node are initiated with 0 amaf count and value, we can ignore the action here if
            # it if not in self.action_amaf_count_value_map. Because only direct child moves are affected by the
            # amaf values in this algorithm.
            if action in self.action_amaf_count_value_map:
                new_amaf_count = self.action_amaf_count_value_map[action][0] + 1
                new_amaf_value = self.action_amaf_count_value_map[action][1] + reward
                self.action_amaf_count_value_map[action] = (new_amaf_count, new_amaf_value)
            # As mentioned above, this can be ignored
            # else:
            #     self.action_amaf_count_value_map[action] = (1, reward)
        if self.parent_node is not None:
            self.parent_node.back_propagation(-reward, action_sequence)

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
