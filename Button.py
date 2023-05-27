import pygame
from constants import *

class Button:
    text: str
    position: pygame.Vector2
    size: pygame.Vector2

    def __init__(self, text, position: pygame.Vector2):
        self.text = text
        self.position = position
        textWidth, textHeight = FONT.size(self.text)
        self.size = pygame.Vector2(textWidth + 20, textHeight + 20)

    def detect_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] > self.position.x - self.size.x/2 and mouse_pos[0] < self.position.x + self.size.x/2:
            if mouse_pos[1] > self.position.y - self.size.y/2 and mouse_pos[1] < self.position.y + self.size.y/2:
                return True
        return False

    def draw(self, screen: pygame.Surface):
        color = COLOR_WHITE
        if self.detect_hover():
            color = COLOR_GRAY
        renderedText = FONT.render(self.text, True, color)
        self.surface = pygame.Surface(self.size)
        pygame.draw.polygon(self.surface, color, (
            (0,0), (self.size.x-2, 0), (self.size.xy - pygame.Vector2(2,2)), (0, self.size.y-2)
        ), 2)
        self.surface.blit(renderedText, (10, 10))
        screen.blit(self.surface, self.position - self.size/2)