import pygame
from pygame import Vector2
from constants import *
from Planet import Planet

class Ship:
    position: Vector2
    color: pygame.Color
    targetPlanetIndex: int
    moveDirection: Vector2
    arrived: bool

    def __init__(self, position: Vector2, color: pygame.Color, targetPlanetIndex: int):
        self.position = position
        self.color = color
        self.targetPlanetIndex = targetPlanetIndex
        self.arrived = False
        self.moveDirection = Vector2(0, 1)
        
        

    def update(self, planets):
        targetPlanet = planets[self.targetPlanetIndex]
        self.moveDirection = (targetPlanet.position - self.position).normalize()
        newPosition = self.position + self.moveDirection * SHIP_SPEED * GAME_SPEED
        for planet in planets:
            if planet == targetPlanet:
                if planet.isInRadius(newPosition):
                    self.arrived = True
                    if targetPlanet.color != self.color:
                        targetPlanet.ships -= 1
                        if targetPlanet.ships == 0:
                            targetPlanet.color = self.color
                        elif targetPlanet.ships == -1:
                            targetPlanet.color = self.color
                            targetPlanet.ships = 1
                    else:
                        targetPlanet.ships += 1
                    targetPlanet.generate_surface()
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
            

    
    def draw(self, screen: pygame.Surface):
        surface = pygame.Surface((SHIP_SIZE,SHIP_SIZE))
        surface.fill((0,0,0))
        surface.set_colorkey((0, 0, 0))
        pygame.draw.polygon(surface, self.color,((0,1), (SHIP_SIZE, SHIP_SIZE/2), (0, SHIP_SIZE-1)), 2)
        rotatedSurface = pygame.transform.rotate(surface, self.moveDirection.angle_to((1, 0)))
        rect = rotatedSurface.get_rect()
        screen.blit(rotatedSurface, (self.position.x - rect.width/2, self.position.y - rect.height/2))