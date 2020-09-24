import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import regularizers
from tensorflow.keras.layers import Dense, Add, Activation

import numpy as np
import os
import time

import config


class NeuralNetwork():
    """ 
        This neural network is copied from 
        https://github.com/farmersrice/saltzero/blob/master/nn_implementations/NeuralNetTensorflow.py
        and https://github.com/blanyal/alpha-zero with a little modification.
        It is just for testing the implementation of my program, I may change the architecture in the future.
    """
    def __init__(self):
        self.model = None
        self.new_network()

    def new_network(self):
        def resnet_block(x):
            identity = x
            x = Dense(1024, activation='relu', kernel_regularizer=regularizers.l2(config.c))(x)
            x = Dense(1024, kernel_regularizer=regularizers.l2(config.c))(x)  # no activation
            x = Add()([x, identity])
            x = Activation('relu')(x)

            return x

        # Input shape is 81(player1) + 81(player2) + 81(legal_moves, i.e. [0,0,0,1,1,0,...]) + 1(current player - 1)
        visible = keras.layers.Input(shape=(81+81+81+1))
        x = Dense(1024, activation='relu', kernel_regularizer=regularizers.l2(config.c))(visible)

        # # 10 resnet blocks
        # for _ in range(4):
        #     x = resnet_block(x)

        policy_hidden = Dense(256, activation='relu', kernel_regularizer=regularizers.l2(config.c))(x)
        policy_output = Dense(81, activation='softmax', kernel_regularizer=regularizers.l2(config.c), name='policy')(policy_hidden)

        value_hidden = Dense(256, activation='relu', kernel_regularizer=regularizers.l2(config.c))(x)
        value_output = Dense(1, activation='tanh', kernel_regularizer=regularizers.l2(config.c), name='value')(value_hidden)

        self.model = keras.models.Model(inputs=visible, outputs=[policy_output, value_output])

        opt = keras.optimizers.SGD(learning_rate=config.learning_rate, momentum=config.momentum)
        # opt = keras.optimizers.Adam(learning_rate = config.learning_rate)

        self.model.compile(loss={'policy': 'categorical_crossentropy', 'value': 'mean_squared_error'},
                           optimizer=opt,
                           metrics=['categorical_accuracy', 'mse'], loss_weights=[1, 1])

        print(self.model.summary())

    def train(self, training_data, validation_data):
        """ Trains the model """
        board = []
        action_prob = []
        value = []
        for data in training_data:
            board.append(data[0])
            action_prob.append(data[1])
            value.append(data[2])
        board = np.array(board)
        action_prob = np.array(action_prob)
        value = np.array(value)

        v_board = []
        v_action_prob = []
        v_value = []
        for v_data in validation_data:
            v_board.append(data[0])
            v_action_prob.append(data[1])
            v_value.append(data[2])
        v_board = np.array(v_board)
        v_action_prob = np.array(v_action_prob)
        v_value = np.array(v_value)
        # print(board.shape)
        # print(action_prob.shape)
        # print(value.shape)

        return self.model.fit(board, {'policy': action_prob, 'value': value}, epochs=config.epochs, validation_data=(v_board, {'policy': v_action_prob, 'value': v_value}))

    def predict(self, board_array):
        """ Return the predicted action and value given a board """
        # keras model need batch size, this reshape means a batch of 1 data
        # action_prob, value = self.model.predict(board_array.reshape(1, -1))
        action_prob, value = self.model(board_array.reshape(1, -1), training = False)
        return np.array(action_prob).reshape(-1), value

    def save_model(self, filename="current_model.h5"):
        """Saves the network model at the given file path.

        Args:
            filename: A string representing the model name.
        """
        # Create directory if it doesn't exist.
        if not os.path.exists(config.model_directory):
            os.mkdir(config.model_directory)

        file_path = config.model_directory + filename

        print("Saving model:", filename, "at", config.model_directory)
        self.model.save(file_path)

    def load_model(self, filename="current_model.h5"):
        """Loads the network model at the given file path.

        Args:
            filename: A string representing the model name.
        """
        file_path = config.model_directory + filename

        print("Loading model:", filename, "from", config.model_directory)
        self.model = tf.keras.models.load_model(file_path)

# net = NeuralNetwork()
# net.predict(np.zeros(81))
