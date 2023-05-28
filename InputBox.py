# from typing import Any
from Button import Button
import pygame
from constants import *

class InputBox(Button):
    active: bool
    default_text: str

    def __init__(self, text, position: pygame.Vector2) -> None:
        super(InputBox, self).__init__(text, position)
        self.active = False
        self.default_text = text
    
    def handle_input(self, event: pygame.event):
        self.force_color = COLOR_GRAY
        if self.text == self.default_text:
            self.text = ''
        if not super().detect_hover() and event.type == pygame.MOUSEBUTTONDOWN:
            return self.finish_input()
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.finish_input()
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif len(self.text) <= 20:
                    self.text += event.unicode
        if len(self.text) > 0:
            return self.text
        return False
    
    def finish_input(self) -> False:
        if len(self.text) == 0:
            self.text = self.default_text
        self.active = False
        self.force_color = None
        return False
