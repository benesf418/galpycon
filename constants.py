import pygame
pygame.init()

SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600

GAME_SPEED: float = 1
PLANET_PRODUCTION_SPEED: float = 1
SHIP_SPEED: float = 0.5

SHIP_COUNTER_FONT = pygame.font.SysFont('consolas', 25)

COLOR_BLACK = pygame.Color(0, 0, 0, 255)
COLOR_RED = pygame.Color(255, 0, 0, 255)
COLOR_BLUE = pygame.Color(0, 0, 255, 255)
COLOR_YELLOW = pygame.Color(255, 255, 0, 255)
COLOR_WHITE = pygame.Color(255, 255, 255, 255)

BACKGROUND_COLOR: pygame.Color = COLOR_BLACK
COLOR_SHIP_COUNTER: pygame.Color = COLOR_WHITE
COLOR_NEUTRAL: pygame.Color = COLOR_WHITE

SHIP_SIZE: int = 14

NETWORK_PORT = 5555