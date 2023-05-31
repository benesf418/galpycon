import pygame
from pygame import Vector2
from constants import *
from Planet import Planet

class Ship:
    def __init__(self, position: Vector2, color: pygame.Color, target_planet_index: int):
        self.position = position
        self.color = color
        self.target_planet_index = target_planet_index
        self.arrived = False
        self.move_direction = Vector2(0, 1)

    def update(self, planets):
        target_planet = planets[self.target_planet_index]
        self.move_direction = (target_planet.position - self.position).normalize()
        new_position = self.position + self.move_direction * SHIP_SPEED * GAME_SPEED
        for planet in planets:
            if planet == target_planet:
                if planet.isInRadius(new_position):
                    self.arrived = True
                    if target_planet.color != self.color:
                        target_planet.ships -= 1
                        if target_planet.ships == 0:
                            target_planet.color = self.color
                        elif target_planet.ships == -1:
                            target_planet.color = self.color
                            target_planet.ships = 1
                    else:
                        target_planet.ships += 1
                    target_planet.generate_surface()
            elif planet.isInRadius(new_position, 9):
                angleToObstacle = self.move_direction.angle_to(planet.position - self.position)
                if (angleToObstacle > 180):
                    angleToObstacle -= 360
                elif angleToObstacle < - 180:
                    angleToObstacle += 360
                if abs(angleToObstacle) < 89:
                    angleToRotate = 90 - abs(angleToObstacle)
                    if angleToObstacle <= 0:
                        self.move_direction = self.move_direction.rotate(angleToRotate)
                    else:
                        self.move_direction = self.move_direction.rotate(-angleToRotate)
                    new_position = self.position + self.move_direction * SHIP_SPEED * GAME_SPEED
        self.position = new_position
            

    
    def draw(self, screen: pygame.Surface):
        surface = pygame.Surface((SHIP_SIZE,SHIP_SIZE))
        surface.fill(BACKGROUND_COLOR)
        surface.set_colorkey(BACKGROUND_COLOR)
        pygame.draw.polygon(surface, self.color,((0,1), (SHIP_SIZE, SHIP_SIZE/2), (0, SHIP_SIZE-1)), 2)
        rotated_surface = pygame.transform.rotate(surface, self.move_direction.angle_to((1, 0)))
        rect = rotated_surface.get_rect()
        screen.blit(rotated_surface, (self.position.x - rect.width/2, self.position.y - rect.height/2))
