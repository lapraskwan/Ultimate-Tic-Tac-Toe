from copy import deepcopy
import math
import random
from main_board import MainBoard

class MCTS:
    def __init__(self, root_game_state, exploration_weight):
        self.root_node = Node(root_game_state, None, False, None, exploration_weight)
        self.root_node.expand()
        self.exploration_weight = exploration_weight
    
    def selection(self):
        """
        Return the leave node with the best UCB1 along the path
        """
        # print("Selection")
        node = self.root_node
        while node.child_nodes:
            best_node = None
            max_UCB1 = None
            for node in node.child_nodes:
                # print("ucb1: ", node.compute_UCB1())
                if best_node == None and max_UCB1 == None:
                    best_node = node
                    max_UCB1 = node.compute_UCB1()
                else:
                    ucb1 = node.compute_UCB1()
                    if ucb1 > max_UCB1:
                        max_UCB1 = ucb1
                        best_node = node
            node = best_node
            # print("Max UCB1: ", max_UCB1)
        return node
    
    def get_best_node(self):
        # print("Getting Best Move")
        best_node = None
        max_reward = None
        for node in self.root_node.child_nodes:
            if best_node == None and max_reward == None:
                best_node = node
                max_reward = node.total_reward / node.visited_times
            else:
                reward = node.total_reward / node.visited_times
                if reward > max_reward:
                    max_UCB1 = reward
                    best_node = node
        # print("Max Reward: ", max_reward)
        return best_node
    
    def simulation(self):
        target_node = self.selection()
        # print("Target node visited times: ", target_node.visited_times)
        if target_node.visited_times != 0 and target_node.game_state.winner is None:
            target_node.expand()
            target_node = target_node.child_nodes[0]
        reward = target_node.rollout()
        # print("Reward of rollout: ", reward)
        target_node.back_propagation(reward)

class Node:
    def __init__(self, game_state, move, is_opponent_turn, parent_node, exploration_weight):
        self.total_reward = 0
        self.visited_times = 0
        self.game_state = game_state
        self.move = move
        self.child_nodes = []
        self.parent_node = parent_node
        self.is_opponent_turn = is_opponent_turn
        self.exploration_weight = exploration_weight

    def rollout(self):
        game_state_copy = deepcopy(self.game_state)
        while game_state_copy.winner is None:
            legal_moves = game_state_copy.get_legal_moves()
            main_board_coor, sub_board_coor = random.choice(legal_moves)
            game_state_copy.make_move(game_state_copy.current_player, main_board_coor, sub_board_coor)
        # print("Winner: ", game_state_copy.winner)
        if game_state_copy.winner == 1:
            # Opponent wins
            # print("Rollout reward: 1")
            return 1
        elif game_state_copy.winner == 0:
            # print("Rollout reward: 0")
            return 0
        else:
            # print("Rollout reward: -1")
            return -1

    def expand(self):
        if not self.child_nodes:
            legal_moves = self.game_state.get_legal_moves()
            for move in legal_moves:
                child_game_state = deepcopy(self.game_state)
                child_game_state.make_move(child_game_state.current_player, move[0], move[1])
                self.child_nodes.append(Node(child_game_state, move, not self.is_opponent_turn, self, self.exploration_weight))
            # print("Created number of children: ", len(self.child_nodes))

    def compute_UCB1(self):
        if self.visited_times == 0:
            return math.inf
        UCB1 = (self.total_reward / self.visited_times) + self.exploration_weight * math.sqrt(math.log(self.parent_node.visited_times) / self.visited_times)
        return UCB1

    def back_propagation(self, reward):
        self.visited_times += 1
        self.total_reward += reward
        # print("Updated Visited times: ", self.visited_times)
        # print("Updated total reward: ", self.total_reward)
        if self.parent_node is not None:
            self.parent_node.back_propagation(reward)

# board = MainBoard()
# # tree = MCTS(board, 2)
# node = Node(board, None, False, None, 2)
# node.expand()
# node.child_nodes[0].rollout()