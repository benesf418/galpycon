import pygame
import math
from sys import exit
from pygame import Vector2

pygame.init()

from constants import *
from Planet import Planet
from ship import Ship

#init window
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('Galpycon')
clock = pygame.time.Clock()


background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
background.fill(BACKGROUND_COLOR)

playerColor = COLOR_BLUE

planets = [
    Planet(300, 300, 30, playerColor),
    Planet(200, 100, 50, COLOR_RED),
    Planet(500, 250, 40, COLOR_NEUTRAL),
    Planet(400, 500, 50, COLOR_NEUTRAL),
    Planet(650, 200, 50, COLOR_NEUTRAL)
]

ships = []

targetPlanetSource: Planet = None

def sendShips(source: Planet, target: Planet):
    shipCount = round(source.ships/2)
    if shipCount > source.ships:
        shipCount -= 1
    source.ships -= shipCount
    source.generate_surface()
    planetPos = source.position
    targetPlanet = target
    direction:Vector2 = (targetPlanet.position - planetPos).normalize()
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
        ships.append(Ship(pos, source.color, target, planets))

def drawPlanetSelection(source: Planet, target: Planet, color = playerColor):
    direction: Vector2 = (target.position - source.position).normalize()
    lineStart = source.position + direction * source.radius
    lineEnd = target.position - direction * (target.radius + 6)
    pygame.draw.polygon(screen, color,(lineStart, lineEnd), 4)
    pygame.draw.circle(screen, color, target.position, target.radius + 6, 4)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for planet in planets:
                if planet.isInRadius(pos) and planet.color == playerColor:
                    targetPlanetSource = planet
        
        if event.type == pygame.MOUSEBUTTONUP:
            if targetPlanetSource is not None:
                pos = pygame.mouse.get_pos()
                planetChosen: bool = False
                for planet in planets:
                    if planet.isInRadius(pos) and targetPlanetSource is not planet:
                        sendShips(targetPlanetSource, planet)
            targetPlanetSource = None        

    for planet in planets:
        planet.update()
    for ship in ships:
        ship.update()
        if ship.arrived:
            ships.remove(ship)

    screen.blit(background, (0,0))

    for planet in planets:
        planet.draw(screen)
    for ship in ships:
        ship.draw(screen)

    if targetPlanetSource is not None:
        mousePos = pygame.mouse.get_pos()
        for planet in planets:
            if planet is targetPlanetSource:
                continue
            if planet.isInRadius(mousePos):
                drawPlanetSelection(targetPlanetSource, planet)

    pygame.display.update()
    clock.tick(60)