from monte_carlo_tree_search import MCTS, Node
import math
from copy import deepcopy
import random

class MCRAVE(MCTS):
    def __init__(self, root_game_state, exploration_weight, player_id):
        self.root_node = MCRAVENode(root_game_state, None, None, exploration_weight, player_id)
        self.root_node.expand()
        self.exploration_weight = exploration_weight
        # Player id of the agent, not the current player of each node
        self.player_id = player_id
    
    def get_best_node(self):
        """ Get the best child node """
        best_node = None
        max_reward = None
        for node in self.root_node.child_nodes:
            # Compute_UCB1() may return infinity if both are 0, for exploration, but we should ignore this node since it's not visited at all
            if node.visited_times == 0 and node.move in self.root_node.action_amaf_count_value_map and self.root_node.action_amaf_count_value_map[node.move][0] == 0:
                continue
            if node.visited_times != 0:
                UCB1 = node.compute_UCB1() - self.exploration_weight * math.sqrt(math.log(self.root_node.visited_times) / node.visited_times)
            else:
                UCB1 = node.compute_UCB1()
            if best_node == None and max_reward == None:
                best_node = node
                max_reward = UCB1
            else:
                if UCB1 > max_reward:
                    max_reward = UCB1
                    best_node = node
        if best_node is None:
            return self.root_node.child_nodes[0]
        return best_node
    
    def simulation(self):
        """ Execute one iteration of simulation (selection + expansion + rollout + backpropagation) """
        target_node = self.selection()
        if target_node.visited_times != 0 and target_node.game_state.winner is None:
            target_node.expand()
            best_node = None
            max_UCB1 = None
            for child_node in target_node.child_nodes:
                if best_node == None and max_UCB1 == None:
                    best_node = child_node
                    max_UCB1 = child_node.compute_UCB1()
                else:
                    ucb1 = child_node.compute_UCB1()
                    if ucb1 > max_UCB1:
                        max_UCB1 = ucb1
                        best_node = child_node
            target_node = best_node
        reward, action_sequence = target_node.rollout()
        target_node.back_propagation(reward, action_sequence)

class MCRAVENode(Node):
    def __init__(self, game_state, move, parent_node, exploration_weight, player_id, mc_value = 0, mc_count = 0):
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
        if self.move in self.parent_node.action_amaf_count_value_map:
            amaf_count = self.parent_node.action_amaf_count_value_map[self.move][0]
            amaf_value = self.parent_node.action_amaf_count_value_map[self.move][1]
        else:
            amaf_count = 0
            amaf_value = 0
        
        if self.visited_times == 0 and amaf_count == 0:
            return math.inf
        beta = amaf_count / (self.visited_times + amaf_count + 4 * self.visited_times * amaf_count * 1)
        if self.visited_times == 0:
            UCB1 = amaf_value / amaf_count
        elif amaf_count == 0:
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
            if action in self.action_amaf_count_value_map:
                new_amaf_count = self.action_amaf_count_value_map[action][0] + 1
                new_amaf_value = self.action_amaf_count_value_map[action][1] + reward
                self.action_amaf_count_value_map[action] = (new_amaf_count, new_amaf_value)
            else:
                self.action_amaf_count_value_map[action] = (1, reward)
        if self.parent_node is not None:
            self.parent_node.back_propagation(reward, action_sequence)

    def expand(self):
        """ Create child nodes """
        if not self.child_nodes:
            legal_moves = self.game_state.get_legal_moves()
            for move in legal_moves:
                child_game_state = deepcopy(self.game_state)
                child_game_state.make_move(move[0], move[1])
                self.child_nodes.append(MCRAVENode(child_game_state, move, self, self.exploration_weight, self.player_id))