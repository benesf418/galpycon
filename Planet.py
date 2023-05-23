import pygame
from pygame import Vector2
from constants import *

class Planet:
    screen: pygame.Surface
    position: Vector2
    radius: int
    surface: pygame.Surface
    color: pygame.Color
    ships: int

    def __init__(self, screen: pygame.Surface, x: int, y: int , radius: str, color: pygame.Color, startingShips = 0):
        self.screen = screen
        self.position = Vector2(x, y)
        self.color = color
        self.radius = radius
        self.surface = pygame.Surface((radius*2, radius*2))
        self.frameCounter = 0
        self.ships = startingShips
        self.generate_surface()

    def generate_surface(self):
        self.surface.fill((0,0,0,0))
        pygame.draw.circle(self.surface, self.color, (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.surface, (30,30,30), (self.radius, self.radius), self.radius - 5)
        text = SHIP_COUNTER_FONT.render(str(self.ships), True, COLOR_SHIP_COUNTER)
        self.surface.blit(text, text.get_rect(center = self.surface.get_rect().center))

    def update(self):
        if self.color == COLOR_NEUTRAL:
            return
        self.frameCounter += self.radius * PLANET_PRODUCTION_SPEED * GAME_SPEED
        if self.frameCounter >= 2500:
            self.frameCounter -= 2500
            self.ships += 1
            self.generate_surface()

    
    def draw(self):
        self.screen.blit(self.surface, (self.position.x - self.radius, self.position.y - self.radius))
    
    def isInRadius(self, pos: Vector2, extendRadius: float = 0) -> bool:
        distance = (pos - self.position).length()
        return distance <= self.radius + extendRadius