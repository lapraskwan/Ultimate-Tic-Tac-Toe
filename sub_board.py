class SubBoard:
    """
    A class representing a sub board of the ultimate tic tac toe game

    UpperLeft cell is (0, 0), UpperRight cell is (0, 2)
    """
    def __init__(self, board_size = 3):
        self.board_size = board_size
        # None: not yet ended, 0: tie, 1: player 1 is the winner, 2: player 2 is the winner
        self.winner = None
        self.cells = [[None for column in range(self.board_size)] for row in range(self.board_size)]
    
    def make_move(self, player, coor):
        """ If a move is made successfully, return True, else return False """
        if self.winner is not None:
            print("Invalid Board")
            return False
        if any(x not in range(self.board_size) for x in coor):
            print("Move out of boundary")
            return False
        if player != 1 and player != 2:
            print("Invalid Player ID")
            return False
        if self.cells[coor[0]][coor[1]] is not None:
            print("Cell occupied")
            return False

        self.cells[coor[0]][coor[1]] = player
        winner = self.get_winner()
        if winner is not None:
            self.winner = winner
        return True
    
    def get_all_empty_cells(self):
        """ Return a list of empty cells, e.g. [(0,0), (1,2)] """
        empty_cells = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.cells[i][j] is None:
                    empty_cells.append((i, j))
        return empty_cells
    
    def get_winner(self):
        """ Return Winner if game ends (0: draw, 1: player 1, 2: player 2), return None otherwise"""
        diag_1 = []
        diag_2 = []
        for i in range(self.board_size):
            # Row
            if self.cells[i][0] is not None and self.cells[i].count(self.cells[i][0]) == self.board_size:
                return self.cells[i][0]
            # Column
            column = []
            for j in range(self.board_size):
                column.append(self.cells[j][i])
            if column[0] is not None and column.count(column[0]) == self.board_size:
                return column[0]
            # Diagonals
            diag_1.append(self.cells[i][i])
            diag_2.append(self.cells[i][self.board_size - 1 - i])

        if diag_1[0] is not None and diag_1.count(diag_1[0]) == self.board_size:
            return diag_1[0]

        if diag_2[0] is not None and diag_2.count(diag_2[0]) == self.board_size:
            return diag_2[0]
        
        # Game not yet end
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.cells[i][j] is None:
                    return None

        return 0