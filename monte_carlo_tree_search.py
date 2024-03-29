from copy import deepcopy
import math
import random

from main_board import MainBoard
import config

class MCTS:
    """
    Represents the Monte Carlo Search Tree
    """
    def __init__(self, root_game_state, player_id):
        self.root_node = Node(root_game_state, None, None, player_id)
        self.root_node.expand()
        # Player id of the agent, not the current player of each node
        self.player_id = player_id

    def selection(self):
        """
        Return the leave node with the best UCB1 along the path
        """
        node = self.root_node
        while node.child_nodes:
            # best_node = None
            # max_UCB1 = None
            # for child_node in node.child_nodes:
            #     ucb1 = child_node.compute_UCB1()
            #     if best_node is None and max_UCB1 is None:
            #         best_node = child_node
            #         max_UCB1 = ucb1
            #     else:
            #         if ucb1 > max_UCB1:
            #             max_UCB1 = ucb1
            #             best_node = child_node
            # node = best_node
            node = max(node.child_nodes, key=lambda node: node.compute_UCB1())
        return node

    def get_best_node(self):
        """ Get the best child node of root node. Used for making the real move. """
        best_node = None
        max_reward = None
        for node in self.root_node.child_nodes:
            if node.visited_times != 0:
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
        reward = target_node.rollout()
        target_node.back_propagation(reward)

class Node:
    """
    Represents a node in the tree formed during the MCTS
    """
    def __init__(self, game_state, move, parent_node, player_id):
        self.total_reward = 0
        self.visited_times = 0
        self.game_state = game_state
        self.move = move
        self.child_nodes = []
        self.parent_node = parent_node
        self.player_id = player_id

    def rollout(self):
        """ 
        Plays a full game from self.game_state with random actions 

        Return the reward. (-1 if leaf node's current player wins, 0 is draw, 1 if leaf node's current player losses)
        """
        game_state_copy = deepcopy(self.game_state)
        while game_state_copy.winner is None:
            legal_moves = game_state_copy.get_legal_moves()
            main_board_coor, sub_board_coor = random.choice(legal_moves)
            game_state_copy.make_move(main_board_coor, sub_board_coor)
        if game_state_copy.winner == self.game_state.current_player:
            # This leaf mode's current player wins
            return -1
        elif game_state_copy.winner == 0:
            return 0
        else:
            return 1

    def expand(self):
        """ Create child nodes """
        if not self.child_nodes:
            legal_moves = self.game_state.get_legal_moves()
            for move in legal_moves:
                child_game_state = deepcopy(self.game_state)
                child_game_state.make_move(move[0], move[1])
                self.child_nodes.append(self.get_new_node(child_game_state, move, self, self.player_id))
    
    def compute_UCB1(self):
        """ Compute the UCB1 value """
        if self.visited_times == 0:
            return math.inf
        UCB1 = (self.total_reward / self.visited_times) + config.exploration_weight * math.sqrt(math.log(self.parent_node.visited_times) / self.visited_times)
        return UCB1

    def back_propagation(self, reward):
        """ Update the visited_times and total_reward of the current node, and also its parent node, until the root node is reached """
        self.visited_times += 1
        self.total_reward += reward
        if self.parent_node is not None:
            self.parent_node.back_propagation(-reward)
    
    def get_new_node(self, game_state, move, parent_node, player_id):
        return Node(game_state, move, parent_node, player_id)
