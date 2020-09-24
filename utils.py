import numpy as np


def softmax(x):
    probs = np.exp(x - np.max(x))
    probs /= np.sum(probs)
    return probs


def index_to_move(i):
    main_board_x = int(i / 27)
    if main_board_x == 3:
        move = ((2, 2), (2, 2))
    else:
        main_board_y = int((i - 27 * main_board_x) / 9)
        if main_board_y == 3:
            move = ((main_board_x, 2), (2, 2))
        else:
            sub_board_x = int((i - 27 * main_board_x - 9 * main_board_y) / 3)
            if sub_board_x == 3:
                move = ((main_board_x, main_board_y), (2, 2))
            else:
                sub_board_y = int((i - 27 * main_board_x - 9 * main_board_y - 3 * sub_board_x))
                move = ((main_board_x, main_board_y), (sub_board_x, sub_board_y))
    return move
