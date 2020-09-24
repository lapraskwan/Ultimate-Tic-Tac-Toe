import math

mute = False
number_of_games = 1
board_size = 3
number_of_simulations = 2000
time_limit = None
exploration_weight = math.sqrt(2)

learning_rate = 0.05
epochs = 2
iteration = 2
c = 0.0001  # from original
momentum = 0.9  # from original

games_per_iteration = 2
number_of_eval_games = 6
epsilon = 0.25 # Dirchlet
dirichlet_alpha = 0.5
temperature_start = 1
temperature_end = 0.001
temperature_change_turn = 30

eval_win_rate = 0.55
load_model = True
model_directory = './models/'
# batch_size = 32
