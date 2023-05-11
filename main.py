import pygame
from sys import exit

pygame.init()

#define constants
from constants import *
from Planet import Planet

#init window
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('Galpycon')
clock = pygame.time.Clock()


background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
background.fill(BACKGROUND_COLOR)

planets = [
    Planet(screen, 300, 300, 30, COLOR_BLUE),
    Planet(screen, 200, 100, 50, COLOR_RED),
    Planet(screen, 500, 250, 40, COLOR_WHITE)
]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    for planet in planets:
        planet.update()

    screen.blit(background, (0,0))
    for planet in planets:
        planet.draw()

    pygame.display.update()
    clock.tick(60)