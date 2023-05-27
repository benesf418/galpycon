import pygame
from network import Network
from Game import Game
from Planet import Planet
from constants import *
from pygame import Vector2

class Client():
    def __init__(self):
        self.network = Network()
        if not self.network.connected:
            exit()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("GalPycon")
        self.color: pygame.Color = None
        self.game: Game = None
        self.selectedPlanetIndex: int = -1
        self.run()

    def drawPlanetSelection(self, source: Planet, target: Planet):
        direction: Vector2 = (target.position - source.position).normalize()
        lineStart = source.position + direction * source.radius
        lineEnd = target.position - direction * (target.radius + 6)
        pygame.draw.polygon(self.screen, self.color,(lineStart, lineEnd), 4)
        pygame.draw.circle(self.screen, self.color, target.position, target.radius + 6, 4)

    def redrawWindow(self, screen):
        screen.fill(BACKGROUND_COLOR)
        for drawable in self.game.get_drawable_objects():
            drawable.draw(screen)
        # print(selectedPlanet)
        if self.selectedPlanetIndex != -1:
            mousePos = pygame.mouse.get_pos()
            planetIndexMousePos = self.game.getPlanetIndexOnPosition(mousePos)
            if planetIndexMousePos != -1 and planetIndexMousePos != self.selectedPlanetIndex:
                self.drawPlanetSelection(self.game.planets[self.selectedPlanetIndex], self.game.planets[planetIndexMousePos])
        pygame.display.update()


    def run(self):
        run = True
        self.color = self.network.getP()
        self.game = self.network.send('get')
        clock = pygame.time.Clock()
        print(self.color)

        while run:
            clock.tick(60)
            self.game.updateShips()
            self.game.planets = self.network.send('get').planets

            #send ships that other players have sent locally
            for shipUpdate in self.network.send('getShipUpdates'):
                self.game.sendShips(shipUpdate[0], shipUpdate[1], shipUpdate[2])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    planetIndexOnMousePos = self.game.getPlanetIndexOnPosition(pygame.mouse.get_pos())
                    if planetIndexOnMousePos != -1 and self.game.planets[planetIndexOnMousePos].color == self.color:
                        print('selected planet')
                        self.selectedPlanetIndex = planetIndexOnMousePos
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.selectedPlanetIndex != -1:
                        planetIndexOnMousePos = self.game.getPlanetIndexOnPosition(pygame.mouse.get_pos())
                        if planetIndexOnMousePos != -1 and planetIndexOnMousePos != self.selectedPlanetIndex:
                            #self.game.sendShips(self.game.planets[self.selectedPlanetIndex], self.game.planets[planetIndexOnMousePos])
                            self.network.send([self.selectedPlanetIndex, planetIndexOnMousePos])
                            self.game.sendShips(self.selectedPlanetIndex, planetIndexOnMousePos)
                    self.selectedPlanetIndex = -1
                    print('deselecting')
            
            self.redrawWindow(self.screen)

Client()