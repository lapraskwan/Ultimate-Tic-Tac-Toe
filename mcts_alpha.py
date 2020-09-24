from mcts_solver import MCTSSolver, MCTSSolverNode
import config

import numpy as np
import tensorflow as tf
import math
import time
import utils

class MCTSAlpha(MCTSSolver):
    def __init__(self, root_game_state, player_id, net):
        self.root_node = MCTSAlphaNode(root_game_state, None, None, player_id, net)
        # self.root_node.expand()
        # Player id of the agent, not the current player of each node
        self.player_id = player_id
        self.net = net

    def get_prob(self):
        """ Return the probability of selection for child nodes of root nodes """
        action_prob = np.zeros(81)
        for i in range(81):
            move = utils.index_to_move(i)
            if move not in self.root_node.game_state.get_legal_moves():
                action_prob[i] = 0
            else:
                for child in self.root_node.child_nodes:
                    if child.move == move:
                        action_prob[i] = child.visited_times / self.root_node.visited_times
        return action_prob

    def get_avg_reward(self):
        """ Return the probability of selection for child nodes of root nodes """
        avg_reward = np.zeros(81)
        for i in range(81):
            move = utils.index_to_move(i)
            if move not in self.root_node.game_state.get_legal_moves():
                avg_reward[i] = -1
            else:
                for child in self.root_node.child_nodes:
                    if child.move == move:
                        if child.visited_times == 0:
                            avg_reward[i] = child.total_reward
                        else:
                            avg_reward[i] = child.total_reward / child.visited_times
        # Normalize avg_reward
        # avg_reward.ptp(0) returns avg_reward.max(0) - avg_reward.min(0), 0 is the axis
        avg_reward_norm = (avg_reward - avg_reward.min(0)) / avg_reward.ptp(0)
        avg_reward_norm = avg_reward_norm / avg_reward_norm.sum(0)
        return avg_reward_norm

    def get_best_node(self, turn, training_mode=False):
        """ Get the best child node (The node with the highest probability) """
        # Select the child's move using a temperature parameter.
        if training_mode and turn < config.temperature_change_turn:
            temperature = config.temperature_start
        else:
            temperature = config.temperature_end

        temperature_exponent = int(1 / temperature)

        # temperature_exponent = 1

        if training_mode and turn < config.temperature_change_turn:
            dirichlet = np.random.dirichlet(config.dirichlet_alpha * np.ones(len(self.root_node.child_nodes)))
            prob_array = []
            visitedtimes = 0
            for index, child_node in enumerate(self.root_node.child_nodes):
                visitedtimes += child_node.visited_times
                prob = (1 - config.epsilon) * (child_node.visited_times / (self.root_node.visited_times - 1)) ** temperature_exponent + config.epsilon * dirichlet[index].tolist()
                prob_array.append(prob)

            # print(visitedtimes)
            # print(self.root_node.visited_times)
            # print(sum(dirichlet))
            best_node = np.random.choice(self.root_node.child_nodes, p=prob_array)
        else:
            best_node = max(self.root_node.child_nodes, key=lambda node: node.visited_times ** temperature_exponent)

        # Handle case where root_node is not expanded
        if best_node is None:
            self.root_node.expand()
            if self.root_node.predicted_value is None:
                self.root_node.set_action_prob_and_predicted_value()

            best_node = max(self.root_node.child_nodes, key=lambda node: node.prob)
        return best_node

    def simulation(self):
        """ Execute one iteration of simulation (selection + expansion + rollout + backpropagation) """
        start_time = time.time()
        target_node = self.selection()
        target_node.expand()
        if target_node.predicted_value is None and target_node.game_state.winner is None:
            target_node.set_action_prob_and_predicted_value()
            action_value = 0
        elif target_node.game_state.winner is not None:
            # Use actual value instead of predicted value (it must be 1 because it is a winning move)
            target_node.predicted_value = 0
            action_value = 1

        reward = target_node.predicted_value + action_value

        if target_node.total_reward != math.inf and target_node.total_reward != -math.inf:
            target_node.back_propagation(reward)
        else:
            reward = target_node.total_reward
            target_node.back_propagation(reward)
        # print("Whole simulation: ",time.time() - start_time)

class MCTSAlphaNode(MCTSSolverNode):
    def __init__(self, game_state, move, parent_node, player_id, net, total_reward=0, visited_times=0):
        a = time.time()
        super().__init__(game_state, move, parent_node, player_id, total_reward=total_reward, visited_times=visited_times)
        self.net = net
        self.prob = 0
        self.predicted_value = None
        # print("Init Node: ", time.time() - a)

    def compute_UCB1(self):
        """ Compute the UCB1 value """
        UCB1 = (self.total_reward / (1 + self.visited_times)) + config.exploration_weight * \
            math.sqrt(self.parent_node.visited_times) / (1 + self.visited_times) * self.prob
        return UCB1

    def set_action_prob_and_predicted_value(self):
        """
        Return the search probability of child nodes and the predicted value of the root node (or all the child?)
        i.e. child_node.visited_times ^ (1/temperature_constant)
        """
        player1_array, player2_array = self.game_state.to_array()
        legal_moves = self.game_state.get_legal_moves()
        legal_moves_array = []
        for i in range(81):
            if utils.index_to_move(i) in legal_moves:
                legal_moves_array.append(1)
            else:
                legal_moves_array.append(0)
        input_array = np.array(player1_array + player2_array + legal_moves_array + [self.game_state.current_player - 1])
        action_prob, predicted_value = self.net.predict(input_array)

        self.predicted_value = np.array(predicted_value).tolist()[0][0]

        # Softmax the probabilities for legal actions
        legal_action_probs = ([], [])  # ([actions], [probs])
        for i in range(81):
            if utils.index_to_move(i) in legal_moves:
                legal_action_probs[0].append(utils.index_to_move(i))
                legal_action_probs[1].append(action_prob[i])

        if len(legal_action_probs[0]) > 0:
            legal_action_probs = (legal_action_probs[0], utils.softmax(np.array(legal_action_probs[1])))

        for child_node in self.child_nodes:
            for index, move in enumerate(legal_action_probs[0]):
                if child_node.move == move:
                    child_node.prob = legal_action_probs[1][index]
            # print(child_node.move, child_node.prob)

    def get_new_node(self, game_state, move, parent_node, player_id, total_reward=0, visited_times=0):
        return MCTSAlphaNode(game_state, move, parent_node, player_id, self.net, total_reward=total_reward, visited_times=visited_times)
