import pygame
import math
from pygame import Vector2
from constants import *
from Planet import Planet
from ship import Ship

class Game:
    planets: list[Planet]
    ships: list[Ship]

    def __init__(self) -> None:
        pygame.init()
        self.planets = [
            Planet(300, 300, 30, COLOR_BLUE),
            Planet(200, 100, 50, COLOR_RED),
            Planet(500, 250, 40, COLOR_NEUTRAL),
            Planet(400, 500, 50, COLOR_YELLOW),
            Planet(650, 200, 50, COLOR_NEUTRAL)
        ]
        self.ships = []

    def update(self) -> None:
        self.updatePlanets()
        self.updateShips()
        
    def get_drawable_objects(self) -> list:
        return self.planets + self.ships
    
    def sendShips(self, sourcePlanetIndex: int, targetPlanetIndex: int, amount: int = None):
        source = self.planets[sourcePlanetIndex]
        target = self.planets[targetPlanetIndex]
        if amount is not None:
            shipCount = amount
        else:
            shipCount = round(source.ships/2)
            if shipCount > source.ships:
                shipCount -= 1
            source.ships -= shipCount
        source.generate_surface()
        planetPos = source.position
        direction:Vector2 = (target.position - planetPos).normalize()
        distance = source.radius
        degreeStep = 360/(2*3.14*(distance/(SHIP_SIZE+4)))
        direction = direction.rotate(-degreeStep*shipCount/2)
        degreeCounter = 0
        for i in range(0, shipCount):
            pos = planetPos + direction * distance
            direction = direction.rotate(degreeStep)
            degreeCounter += degreeStep
            if degreeCounter >= 360:
                degreeCounter = 0
                distance += SHIP_SIZE
                degreeStep = 360/(2*3.14*(distance/(SHIP_SIZE+4)))
            self.ships.append(Ship(pos, source.color, targetPlanetIndex))
    
    def getPlanetIndexOnPosition(self, position: Vector2) -> int:
        for i in range(len(self.planets)):
            if self.planets[i].isInRadius(position):
                return i
        return -1
    
    def updatePlanets(self):
        for planet in self.planets:
            planet.update()
    
    def updateShips(self):
        for ship in self.ships:
            ship.update(self.planets)
            if ship.arrived:
                self.ships.remove(ship)
