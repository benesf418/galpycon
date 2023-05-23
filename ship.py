import pygame
from pygame import Vector2
from constants import *
from Planet import Planet

class Ship:
    screen: pygame.Surface
    position: Vector2
    surface: pygame.Surface
    color: pygame.Color
    targetPlanet: Planet
    moveDirection: Vector2
    arrived: bool

    def __init__(self, screen: pygame.Surface, position: Vector2, color: pygame.Color, targetPlanet: Planet, planets):
        self.screen = screen
        self.position = position
        self.color = color
        self.surface = pygame.Surface((SHIP_SIZE,SHIP_SIZE))
        self.surface.fill((0,0,0))
        self.surface.set_colorkey((0, 0, 0))
        pygame.draw.polygon(self.surface, self.color,((0,1), (SHIP_SIZE, SHIP_SIZE/2), (0, SHIP_SIZE-1)), 2)
        self.targetPlanet = targetPlanet
        self.arrived = False
        self.moveDirection = Vector2(0, 1)
        self.planets = planets
        
        

    def update(self):
        self.moveDirection = (self.targetPlanet.position - self.position).normalize()
        newPosition = self.position + self.moveDirection * SHIP_SPEED * GAME_SPEED
        for planet in self.planets:
            if planet == self.targetPlanet:
                if planet.isInRadius(newPosition):
                    self.arrived = True
                    if self.targetPlanet.color != self.color:
                        self.targetPlanet.ships -= 1
                        if self.targetPlanet.ships == 0:
                            self.targetPlanet.color = self.color
                        elif self.targetPlanet.ships == -1:
                            self.targetPlanet.color = self.color
                            self.targetPlanet.ships = 1
                    else:
                        self.targetPlanet.ships += 1
                    self.targetPlanet.generate_surface()
            elif planet.isInRadius(newPosition, 9):
                angleToObstacle = self.moveDirection.angle_to(planet.position - self.position)
                if (angleToObstacle > 180):
                    angleToObstacle -= 360
                elif angleToObstacle < - 180:
                    angleToObstacle += 360
                if abs(angleToObstacle) < 89:
                    angleToRotate = 90 - abs(angleToObstacle)
                    if angleToObstacle <= 0:
                        self.moveDirection = self.moveDirection.rotate(angleToRotate)
                    else:
                        self.moveDirection = self.moveDirection.rotate(-angleToRotate)
                    newPosition = self.position + self.moveDirection * SHIP_SPEED * GAME_SPEED
        self.position = newPosition
            

    
    def draw(self):
        rotatedSurface = pygame.transform.rotate(self.surface, self.moveDirection.angle_to((1, 0)))
        rect = rotatedSurface.get_rect()
        self.screen.blit(rotatedSurface, (self.position.x - rect.width/2, self.position.y - rect.height/2))