import pygame
from constants import *

class Button:
    def __init__(self, text, position: pygame.Vector2):
        self.text = text
        self.position = position
        self.force_color: pygame.Color = None
        text_width, text_height = FONT.size(self.text)
        self.size = pygame.Vector2(text_width + 20, text_height + 20)

    def detect_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] > self.position.x - self.size.x/2 and mouse_pos[0] < self.position.x + self.size.x/2:
            if mouse_pos[1] > self.position.y - self.size.y/2 and mouse_pos[1] < self.position.y + self.size.y/2:
                return True
        return False

    def draw(self, screen: pygame.Surface):
        text_width, text_height = FONT.size(self.text)
        self.size = pygame.Vector2(text_width + 20, text_height + 20)
        color = COLOR_WHITE
        if self.force_color:
            color = self.force_color
        if self.detect_hover():
            color = COLOR_GRAY
        renderedText = FONT.render(self.text, True, color)
        self.surface = pygame.Surface(self.size)
        pygame.draw.polygon(self.surface, color, (
            (0,0), (self.size.x-2, 0), (self.size.xy - pygame.Vector2(2,2)), (0, self.size.y-2)
        ), 2)
        self.surface.blit(renderedText, (10, 10))
        screen.blit(self.surface, self.position - self.size/2)