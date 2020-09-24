from sub_board import SubBoard
import config

class MainBoard:
    """
    A Class representing the main board

    UpperLeft sub-board is (0, 0), UpperRight sub-board is (0, 2)
    """

    def __init__(self, board_size = config.board_size):
        self.board_size = board_size
        self.sub_board_values = [[None for column in range(self.board_size)] for row in range(self.board_size)]
        self.sub_boards = [[SubBoard(self.board_size) for column in range(self.board_size)] for row in range(self.board_size)]
        self.allowed_sub_boards = [(x, y) for x in range(self.board_size) for y in range(self.board_size)]
        self.winner = None
        self.current_move = 0
        self.current_player = 1

    def make_move(self, main_board_coor, sub_board_coor):
        """ If a move is made successfully, return True, else return False """
        if any(x not in range(self.board_size) for x in main_board_coor) or any(x not in range(self.board_size) for x in sub_board_coor):
            print("Move out of boundary")
            return False
        if main_board_coor not in self.allowed_sub_boards:
            print("Invalid Sub-board")
            return False
        target_sub_board = self.sub_boards[main_board_coor[0]][main_board_coor[1]]
        result = target_sub_board.make_move(self.current_player, sub_board_coor)
        if not result:
            return result
        # A successful move is made
        self.sub_board_values[main_board_coor[0]][main_board_coor[1]] = target_sub_board.winner
        self.update_allowed_sub_boards(sub_board_coor)
        self.current_move += 1
        # If player is 1, then 2/1 is 2; If player is 2, then 2/2 is 1
        self.current_player = int(2 / self.current_player)
        winner = self.get_winner()
        if winner is not None:
            self.winner = winner
        return True

    def update_allowed_sub_boards(self, sub_board_coor):
        """ Updates the allowed_sub_boards for next move """
        if self.sub_board_values[sub_board_coor[0]][sub_board_coor[1]] is None:
            self.allowed_sub_boards = [sub_board_coor]
        else:
            self.allowed_sub_boards = []
            all_sub_boards = [(x, y) for x in range(self.board_size) for y in range(self.board_size)]
            for sub_board in all_sub_boards:
                if self.sub_board_values[sub_board[0]][sub_board[1]] is None:
                    self.allowed_sub_boards.append(sub_board)
        return self.allowed_sub_boards

    def get_winner(self):
        """ Return Winner if game ends (0: draw, 1: player 1, 2: player 2), return None otherwise"""
        diag_1 = []
        diag_2 = []
        for i in range(self.board_size):
            # Row
            if self.sub_board_values[i][0] is not None and self.sub_board_values[i][0] != 0 and self.sub_board_values[i].count(self.sub_board_values[i][0]) == self.board_size:
                return self.sub_board_values[i][0]
            # Column
            column = []
            for j in range(self.board_size):
                column.append(self.sub_board_values[j][i])
            if column[0] is not None and column[0] != 0 and column.count(column[0]) == self.board_size:
                return column[0]
            # Diagonals
            diag_1.append(self.sub_board_values[i][i])
            diag_2.append(self.sub_board_values[i][self.board_size - 1 - i])

        if diag_1[0] is not None and diag_1[0] != 0 and diag_1.count(diag_1[0]) == self.board_size:
            return diag_1[0]

        if diag_2[0] is not None and diag_2[0] != 0 and diag_2.count(diag_2[0]) == self.board_size:
            return diag_2[0]

        # Game not yet end
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.sub_board_values[i][j] is None:
                    return None
        # Draw
        return 0

    def get_legal_moves(self):
        """ Return all legal moves """
        if self.winner is not None:
            return []
        possible_moves = []
        for main_board_coor in self.allowed_sub_boards:
            for cell in self.sub_boards[main_board_coor[0]][main_board_coor[1]].get_all_empty_cells():
                possible_moves.append((main_board_coor, cell))
        return possible_moves

    def print_board(self):
        """ Print out the game state """
        print(('******' + '**' * (self.board_size - 2)) * self.board_size)
        if self.current_move == 0:
            print("      Game Starts!")
        else:
            print('  Move ' + str(self.current_move) + " by Player " + str(int(2 / self.current_player)))
        print(('******' + '**' * (self.board_size - 2)) * self.board_size)
        print(('------' + '--' * (self.board_size - 2)) * self.board_size)
        for y_main in range(self.board_size):
            for y_sub in range(self.board_size):
                for x_main in range(self.board_size):
                    for x_sub in range(self.board_size):
                        value = self.sub_boards[y_main][x_main].cells[y_sub][x_sub]
                        print(value if value is not None else '_', end = '')
                        if x_main == self.board_size - 1 and x_sub == self.board_size - 1 and y_sub == self.board_size - 1:
                            print()
                            print(('------' + '--' * (self.board_size - 2)) * self.board_size)
                        elif x_main == self.board_size - 1 and x_sub == self.board_size - 1:
                            print()
                        elif x_sub == self.board_size - 1:
                            print(' || ', end='')
                        else:
                            print('|', end='')

    def to_array(self):
        array = []
        all_sub_boards = [(x, y) for x in range(self.board_size) for y in range(self.board_size)]
        for subboard_idx in all_sub_boards:
            for y in range(self.board_size):
                for x in range(self.board_size):
                    array.append(self.sub_boards[subboard_idx[0]][subboard_idx[1]].cells[y][x]
                                 if self.sub_boards[subboard_idx[0]][subboard_idx[1]].cells[y][x] is not None else 0)

        player1_array = [1 if x == 1 else 0 for x in array]
        player2_array = [1 if x == 2 else 0 for x in array]
        return player1_array, player2_array
