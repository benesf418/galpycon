import pygame
from pygame import Vector2
from constants import *

class Planet:
    def __init__(self, x: int, y: int , radius: str, color: pygame.Color, startingShips: int = 0):
        self.position = Vector2(x, y)
        self.color = color
        self.radius = radius
        self.frameCounter = 0
        self.ships = startingShips

    def generate_surface(self) -> pygame.Surface:
        surface = pygame.Surface((self.radius*2, self.radius*2))
        surface.set_colorkey(BACKGROUND_COLOR)
        surface.fill((0,0,0,0))
        pygame.draw.circle(surface, self.color, (self.radius, self.radius), self.radius)
        pygame.draw.circle(surface, PLANET_BACKGROUND, (self.radius, self.radius), self.radius - 5)
        text = FONT.render(str(self.ships), True, COLOR_SHIP_COUNTER)
        surface.blit(text, text.get_rect(center = surface.get_rect().center))
        return surface

    def update(self):
        if self.color == COLOR_NEUTRAL:
            return
        self.frameCounter += self.radius * PLANET_PRODUCTION_SPEED * GAME_SPEED
        if self.frameCounter >= 2500:
            self.frameCounter -= 2500
            self.ships += 1
            self.generate_surface()

    
    def draw(self, screen: pygame.Surface):
        screen.blit(self.generate_surface(), (self.position.x - self.radius, self.position.y - self.radius))
    
    def isInRadius(self, pos: Vector2, extendRadius: float = 0) -> bool:
        distance = (pos - self.position).length()
        return distance <= self.radius + extendRadius