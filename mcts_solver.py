from monte_carlo_tree_search import MCTS, Node
import math

class MCTSSolver(MCTS):
    """
    The total reward of a node becomes +math.inf if it is a proven win for this agent
    The total reward of a node becomes -math.inf if it is a proven loss for this agent
    """
    def selection(self):
        """
        Return the leave node with the best UCB1 along the path
        """
        node = self.root_node
        while node.child_nodes:
            best_node = None
            max_UCB1 = None
            for child_node in node.child_nodes:
                # Cannot use math.inf here, because it is used to represent a winning nodeo
                if child_node.visited_times == 0:
                    best_node = child_node
                    break
                ucb1 = child_node.compute_UCB1()
                if best_node is None and max_UCB1 is None:
                    best_node = child_node
                    max_UCB1 = ucb1
                else:
                    if ucb1 > max_UCB1:
                        max_UCB1 = ucb1
                        best_node = child_node
            node = best_node
        return node

class MCTSSolverNode(Node):
    def __init__(self, game_state, move, parent_node, exploration_weight, player_id, winner = None):
        super().__init__(game_state, move, parent_node, exploration_weight, player_id)
        self.winner = winner
        if self.winner == self.player_id:
            self.total_reward = math.inf
        elif self.winner == int(2/ self.player_id):
            self.total_reward = -math.inf
    
    def rollout(self):
        """ 
        Plays a full game from self.game_state with random actions 

        Return the reward. (1 if this agent wins, 0 is draw, -1 if this agent losses)
        """
        if self.winner == self.player_id:
            return math.inf
        elif self.winner == int(2 / self.player_id):
            return -math.inf

        game_state_copy = deepcopy(self.game_state)
        while game_state_copy.winner is None:
            legal_moves = game_state_copy.get_legal_moves()
            main_board_coor, sub_board_coor = random.choice(legal_moves)
            game_state_copy.make_move(main_board_coor, sub_board_coor)
        if game_state_copy.winner == self.player_id:
            # This agent wins
            return 1
        elif game_state_copy.winner == 0:
            return 0
        else:
            return -1

    def back_propagation(self, reward):
        if reward == math.inf:
            if self.game_state.current_player == int(2 / self.player_id):
                for child_node in self.child_nodes:
                    if child_node.total_reward != reward:
                        self.total_reward += -1
                        self.visited_times += 1
                        self.parent_node.back_propagation(reward)
                        return
            self.winner = self.player_id
            self.total_reward = reward
            self.visited_times += 1
            self.parent_node.back_propagation(reward)

        elif reward == -math.inf:
            if self.game_state.current_player == self.player_id:
                for child_node in self.child_nodes:
                    if child_node.total_reward != reward:
                        self.total_reward += -1
                        self.visited_times += 1
                        self.parent_node.back_propagation(reward)
                        return
            self.winner = int(2/self.player_id)
            self.total_reward = reward
            self.visited_times += 1
            self.parent_node.back_propagation(reward)
            
        else:
            self.visited_times += 1
            self.total_reward += reward
            if self.parent_node is not None:
                self.parent_node.back_propagation(reward)
    
    def expand(self):
        """ Create child nodes """
        if not self.child_nodes:
            legal_moves = self.game_state.get_legal_moves()
            for move in legal_moves:
                child_game_state = deepcopy(self.game_state)
                child_game_state.make_move(move[0], move[1])
                winner = child_game_state.winner
                self.child_nodes.append(Node(child_game_state, move, self, self.exploration_weight, self.player_id, winner))
    
    def compute_UCB1(self):
        if self.winner == self.player_id:
            return math.inf
        elif self.winner == int(2 / self.player_id):
            return -math.inf

        UCB1 = (self.total_reward / self.visited_times) + self.exploration_weight * \
            math.sqrt(math.log(self.parent_node.visited_times) / self.visited_times)
        return UCB1
