import pygame
from pygame.locals import QUIT
from main_board import MainBoard

class MainBoardGUI(MainBoard):
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    WHITE = (255, 255, 255)

    def __init__(self, board_size = 3):
        super().__init__()
        pygame.init()
        window_surface = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption('Ultimate Tic-Tac-Toe')

        background = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        background.fill(self.WHITE)
        # draw the grid lines
        # vertical lines...
        pygame.draw.line(background, (0, 0, 0), (100, 0), (100, 300), 2)
        pygame.draw.line(background, (0, 0, 0), (200, 0), (200, 300), 2)

        # horizontal lines...
        pygame.draw.line(background, (0, 0, 0), (0, 100), (300, 100), 2)
        pygame.draw.line(background, (0, 0, 0), (0, 200), (300, 200), 2)

        window_surface.blit(background, (0,0))
        pygame.display.update()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type is QUIT:
                    running = False
    
    def init_board(self):
        pygame.init()
        window_surface = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption('Ultimate Tic-Tac-Toe')

        background = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        background.fill(self.WHITE)
        # draw the grid lines
        # vertical lines...
        pygame.draw.line(background, (0, 0, 0), (100, 0), (100, 300), 2)
        pygame.draw.line(background, (0, 0, 0), (200, 0), (200, 300), 2)

        # horizontal lines...
        pygame.draw.line(background, (0, 0, 0), (0, 100), (300, 100), 2)
        pygame.draw.line(background, (0, 0, 0), (0, 200), (300, 200), 2)
MainBoardGUI()
