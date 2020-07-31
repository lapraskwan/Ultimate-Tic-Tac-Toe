from monte_carlo_tree_search import MCTS, Node
import math
from copy import deepcopy
import random

class MCTSSolver(MCTS):
    """
    The total reward of a node becomes +math.inf if it is a proven win for this agent
    The total reward of a node becomes -math.inf if it is a proven loss for this agent
    """
    def __init__(self, root_game_state, exploration_weight, player_id):
        super().__init__(root_game_state, exploration_weight, player_id)
        self.root_node = MCTSSolverNode(root_game_state, None, None, exploration_weight, player_id)
    
    def simulation(self):
        """ Execute one iteration of simulation (selection + expansion + rollout + backpropagation) """
        target_node = self.selection()
        if target_node.visited_times != 0 and target_node.game_state.winner is None:
            target_node.expand()
            target_node = target_node.child_nodes[0]
        if target_node.total_reward != math.inf or target_node.total_reward != -math.inf:
            reward = target_node.rollout()
            if target_node.game_state.current_player == self.player_id:
                target_node.back_propagation(-reward)
            else:
                target_node.back_propagation(reward)
        else:
            reward = target_node.total_reward
            target_node.back_propagation(reward)

class MCTSSolverNode(Node):
    def __init__(self, game_state, move, parent_node, exploration_weight, player_id, total_reward = 0, visited_times = 0):
        super().__init__(game_state, move, parent_node, exploration_weight, player_id)
        self.total_reward = total_reward
        self.visited_times = visited_times

    def back_propagation(self, reward):
        if reward == math.inf:
            # To prove a loss, we need to prove that all children are loss
            for child_node in self.child_nodes:
                if child_node.total_reward != -math.inf:
                    self.total_reward += -1
                    self.visited_times += 1
                    self.parent_node.back_propagation(-1)
                    return
            self.total_reward = reward
            self.visited_times += 1
            self.parent_node.back_propagation(-reward)

        elif reward == -math.inf:
            # To prove a win, we only need one child to be a win
            self.total_reward = reward
            self.visited_times += 1
            self.parent_node.back_propagation(-reward)
            
        else:
            self.visited_times += 1
            self.total_reward += reward
            if self.parent_node is not None:
                self.parent_node.back_propagation(-reward)
    
    def expand(self):
        """ Create child nodes """
        if not self.child_nodes:
            legal_moves = self.game_state.get_legal_moves()
            for move in legal_moves:
                child_game_state = deepcopy(self.game_state)
                child_game_state.make_move(move[0], move[1])
                if child_game_state.winner is not None and child_game_state.winner != 0:
                    total_reward = math.inf
                    visited_times = 1
                    # print("Terminal Node Reached in Search Tree:", child_game_state.winner)
                else:
                    total_reward = 0
                    visited_times = 0
                self.child_nodes.append(self.get_new_node(child_game_state, move, self, self.exploration_weight, self.player_id, total_reward, visited_times))
    
    def get_new_node(self, game_state, move, parent_node, exploration_weight, player_id, total_reward, visited_times):
        return MCTSSolverNode(game_state, move, parent_node, exploration_weight, player_id, total_reward, visited_times)
