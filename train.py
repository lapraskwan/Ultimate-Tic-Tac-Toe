"""
For every iteration:
    self play a certain number of games against itself (current model) to get training data
    save current model
    train to get new model
    evaluate (New model play against current model)
    if win rate of new model > certain percentage:
        current model = new model
"""
from main_board import MainBoard
from mcts_alpha import MCTSAlpha
from player import MCTSAlphaPlayer
import config
from neural_network import NeuralNetwork
import utils
import os
import time
import matplotlib.pyplot as plt
import random
import copy

import numpy as np

class Train:
    """
    A Class for training the neural network using MCTS

    Codes are modified from https://github.com/blanyal/alpha-zero
    """

    def __init__(self, net):
        self.net = net
        self.eval_net = NeuralNetwork()  # initialize a new net

    def start(self, training_data, validation_data):
        """ Start the training """
        loss_history = []
        validation_loss_history = []
        policy_loss_history = []
        value_loss_history = []

        min_loss = 100
        for i in range(config.iteration):
            print("Iteration", i + 1)

            # training_data = []  # list to store self play states, action_prob and win/draw/lose

            for j in range(config.games_per_iteration):
                print("Start Training Self-Play Game", j + 1)
                start_time = time.time()
                game_state = MainBoard(config.board_size)  # Create a fresh clone for each game.
                self.self_play(game_state, training_data, validation_data)
                end_time = time.time()
                print("Used time: ", end_time - start_time)

            # # Save the current neural network model.
            # self.net.save_model()

            # # Load the recently saved model into the evaluator network.
            # self.eval_net.load_model()

            print(len(training_data))
            print(len(validation_data))

            # Shuffle the training_data
            training_data_copy = copy.deepcopy(training_data)
            validation_data_copy = copy.deepcopy(validation_data)
            random.shuffle(training_data_copy)
            random.shuffle(validation_data_copy)

            # Train the network using self play values.
            
            history = self.net.train(training_data_copy, validation_data_copy)

            current_loss = history.history['loss'][-1]
            current_validation_loss = history.history['val_loss'][-1]
            current_policy_loss = history.history['policy_loss'][-1]
            current_value_loss = history.history['value_loss'][-1]

            loss_history.append(current_loss)
            validation_loss_history.append(current_validation_loss)
            policy_loss_history.append(current_policy_loss)
            value_loss_history.append(current_value_loss)

            # print(training_data[-1])
            # print(self.net.predict(training_data[-1][0]))

            # Cut out half of the training data every 100 games
            if (i + 1) % 20 == 0:
                training_data = training_data[int(len(training_data) / 4):]
                validation_data = validation_data[int(len(validation_data) / 4):]
            # if (i + 1) % 100 == 0:
            #     x = [i for i in range(len(loss_history))]
            #     plt.plot(x, loss_history, label='loss')
            #     plt.plot(x, validation_loss_history, label='validation_loss')
            #     plt.plot(x, policy_loss_history, label='policy_loss')
            #     plt.plot(x, value_loss_history, label='value_loss')
            #     plt.legend(loc='upper right')
            #     plt.xlabel("Iteration")
            #     plt.ylabel("Loss")
            #     plt.title("Loss vs. Iteration")
            #     plt.show()

            # wins, draws, losses = self.evaluate(current_net=self.net, eval_net=self.eval_net)

            # print("wins: ", wins)
            # print("draws: ", draws)
            # print("losses: ", losses)

            # num_games = wins + losses

            # if num_games == 0:
            #     win_rate = 0
            # else:
            #     win_rate = wins / num_games

            # print("win rate:", win_rate)

            # # if win_rate > config.eval_win_rate:
            # if wins > losses:
            #     # Save current model as the best model.
            #     print("New model saved as best model.")
            #     self.net.save_model("best_model.h5")
            # else:
            #     print("New model discarded and previous model loaded.")
            #     # Discard current model and use previous best model.
            #     self.net.load_model()
            if (i + 1) % 100 == 0:
                self.net.save_model("model" + str(i+1) + ".h5")
            if current_loss < min_loss:
                self.net.save_model("best_model.h5")
                min_loss = current_loss
                print("Updated best_model.h5!!!!!")

        # Check for saved loss history
        if os.path.exists(config.model_directory + 'loss_history.npy'):
            previous_loss_history = np.load(config.model_directory + 'loss_history.npy')
        else:
            previous_loss_history = []
            print("No saved loss history, creating new loss_history.npy file.")
        # Save loss history
        loss_history = np.array(loss_history)
        full_loss_history = np.concatenate((previous_loss_history, loss_history))
        np.save(config.model_directory + 'loss_history.npy', full_loss_history)

        # Check for saved validation loss history
        if os.path.exists(config.model_directory + 'validation_loss_history.npy'):
            previous_validation_loss_history = np.load(config.model_directory + 'validation_loss_history.npy')
        else:
            previous_validation_loss_history = []
            print("No saved validation loss history, creating new validation_loss_history.npy file.")
        # Save history
        validation_loss_history = np.array(validation_loss_history)
        full_validation_loss_history = np.concatenate((previous_validation_loss_history, validation_loss_history))
        np.save(config.model_directory + 'validation_loss_history.npy', full_validation_loss_history)

        x = [i for i in range(len(full_loss_history))]
        plt.plot(x, full_loss_history, label='loss')
        plt.plot(x, full_validation_loss_history, label='validation_loss')
        plt.legend(loc='upper right')
        plt.xlabel("Iteration")
        plt.ylabel("Loss")
        plt.title("Loss vs. Iteration (Full History)")
        plt.show()

        x = [i + len(previous_loss_history) for i in range(len(loss_history))]
        plt.plot(x, loss_history, label='loss')
        plt.plot(x, validation_loss_history, label='validation_loss')
        plt.legend(loc='upper right')
        plt.xlabel("Iteration")
        plt.ylabel("Loss")
        plt.title("Loss vs. Iteration (Current Training Phase)")
        plt.show()

        # Check for saved policy loss history
        if os.path.exists(config.model_directory + 'policy_loss_history.npy'):
            previous_policy_loss_history = np.load(config.model_directory + 'policy_loss_history.npy')
        else:
            previous_policy_loss_history = []
            print("No saved policy loss history, creating new policy_loss_history.npy file.")
        # Save loss history
        policy_loss_history = np.array(policy_loss_history)
        full_policy_loss_history = np.concatenate((previous_policy_loss_history, policy_loss_history))
        np.save(config.model_directory + 'policy_loss_history.npy', full_policy_loss_history)

        # Check for saved value loss history
        if os.path.exists(config.model_directory + 'value_loss_history.npy'):
            previous_value_loss_history = np.load(config.model_directory + 'value_loss_history.npy')
        else:
            previous_value_loss_history = []
            print("No saved value loss history, creating new value_loss_history.npy file.")
        # Save history
        value_loss_history = np.array(value_loss_history)
        full_value_loss_history = np.concatenate((previous_value_loss_history, value_loss_history))
        np.save(config.model_directory + 'value_loss_history.npy', full_value_loss_history)

        x = [i for i in range(len(full_policy_loss_history))]
        plt.plot(x, full_policy_loss_history, label='policy_loss')
        plt.plot(x, full_value_loss_history, label='value_loss')
        plt.legend(loc='upper right')
        plt.xlabel("Iteration")
        plt.ylabel("Loss")
        plt.title("Loss (policy and value) vs. Iteration (Full History)")
        plt.show()

        x = [i + len(previous_policy_loss_history) for i in range(len(policy_loss_history))]
        plt.plot(x, policy_loss_history, label='policy_loss')
        plt.plot(x, value_loss_history, label='value_loss')
        plt.legend(loc='upper right')
        plt.xlabel("Iteration")
        plt.ylabel("Loss")
        plt.title("Loss (policy and value) vs. Iteration (Current Training Phase)")
        plt.show()

        print("Finished training for " + str(config.iteration) + " iterations, please find the trained models in google drive.")
    
    def self_play(self, game_state, training_data, validation_data):
        temp_data = []

        player_1 = MCTSAlphaPlayer(game_state, 1, self.net)
        player_2 = MCTSAlphaPlayer(game_state, 2, self.net)

        current_player = player_1
        while game_state.winner is None:
            main_board_coor, sub_board_coor = current_player.get_move(True)
            action_prob = current_player.get_prob()

            legal_moves = game_state.get_legal_moves()
            legal_moves_array = []
            for i in range(81):
                if utils.index_to_move(i) in legal_moves:
                    legal_moves_array.append(1)
                else:
                    legal_moves_array.append(0)

            # The array to be input into the neural network
            player1_array, player2_array = game_state.to_array()
            input_array = player1_array + player2_array + legal_moves_array + [game_state.current_player - 1]
            temp_data.append([np.array(input_array), np.array(action_prob), 0])
            
            current_player.make_move(main_board_coor, sub_board_coor)
            current_player = player_1 if current_player == player_2 else player_2
        
        if game_state.winner == 0:
            value = 0
        elif game_state.winner == 1:
            # Player 1 is the winner, temp_data[1] is the first move played by player 1,
            # so temp_data[1][2] should have a value of 1,
            # and temp_data[0][2] should have a value of -1
            value = -1
        else:
            # Same as above
            value = 1
        
        index = len(temp_data)
        for data in temp_data:
            data[2] = value
            value = -value
            if random.random() <= 0.8:
                training_data.append(data)
            else:
                validation_data.append(data)
            
            index -= 1
            if index <= 1:
                print(data)
                print(self.net.predict(data[0]))

    def evaluate(self, current_net, eval_net):
        win = 0
        draw = 0
        loss = 0

        for i in range(config.number_of_eval_games):
            print("Starting evaluation game: " + str(i))
            start_time = time.time()
            game_state = MainBoard(config.board_size)
            # i % 2 + 1 is equal to 1 when i is odd, and 2 when i is even
            # int(2 / x) is 1 when x is 2, 2 when x is 1
            # This is to ensure both players are played as player 1 and 2 for the same number of times
            player_1 = MCTSAlphaPlayer(game_state, i % 2 + 1, current_net)
            player_2 = MCTSAlphaPlayer(game_state, int(2 / (i % 2 + 1)), eval_net)

            if i % 2 + 1 == 1:
                current_player = player_1
            else:
                current_player = player_2

            while game_state.winner is None:
                main_board_coor, sub_board_coor = current_player.get_move()
                current_player.make_move(main_board_coor, sub_board_coor)
                current_player = player_1 if current_player == player_2 else player_2

            if game_state.winner == i % 2 + 1:
                print("AI wins!")
                win += 1
            elif game_state.winner == 0:
                print("It's a draw.")
                draw += 1
            else:
                print("AI loses.")
                loss += 1
            end_time = time.time()
            print("Used Time: ", end_time - start_time)

        return win, draw, loss

############################################################################################
net = NeuralNetwork()

# Initialize the network with the best model.
if config.load_model:
    file_path = config.model_directory + "best_model.h5"
    if os.path.exists(file_path):
        net.load_model("best_model.h5")
    else:
        print("Trained model doesn't exist. Starting from scratch.")
else:
    print("Trained model not loaded. Starting from scratch.")

# Create the replay buffer
training_data = []  # list to store self play states, action_prob and win/draw/lose
validation_data = []

train = Train(net)
train.start(training_data, validation_data)
