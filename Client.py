import pygame
from network import Network
from Game import Game
from Planet import Planet
from constants import *
from pygame import Vector2
from Lobby import Lobby
from Button import Button
from math import floor
import random

class Client:
    def __init__(self, screen: pygame.display, network: Network):
        # self.server_ip = server_ip
        # self.network = Network()
        # self.network.connect(self.server_ip)
        # if not self.network.connected:
        #     print(f'failed to connect to {server_ip}')
        #     return
        self.network = network
        self.color = self.network.getColor()
        self.screen = screen
        self.game: Game = None
        self.selectedPlanetIndex: int = -1
        self.button_back = Button('back to main menu', Vector2(SCREEN_WIDTH/2, 600))
        self.button_back_game = Button('back to main menu', Vector2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100))
        self.button_ready = Button('ready', Vector2(SCREEN_WIDTH/2, 410))
        self.ready = False
        self.running = True
        self.count_down_length: float = 5.5
        self.count_down: float = self.count_down_length
        self.star_positions: list[Vector2] = []
        self.star_sizes: list[int] = []
        for i in range(STAR_COUNT):
            self.star_positions.append(Vector2(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)))
            self.star_sizes.append(random.randint(STAR_SIZE_MIN, STAR_SIZE_MAX))
        self.stars_surface: pygame.Surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.stars_surface.fill(BACKGROUND_COLOR)
        for i in range(len(self.star_positions)):
            star_position = self.star_positions[i]
            star_size = self.star_sizes[i]
            self.stars_surface.blit(
                pygame.font.SysFont('consolas', star_size).render('x', True, (50 + star_size*10, 50 + star_size*10, 50 + star_size*10, 255) ),
                star_position
            )
        self.run()


    def drawPlanetSelection(self, source: Planet, target: Planet):
        direction: Vector2 = (target.position - source.position).normalize()
        lineStart = source.position + direction * source.radius
        lineEnd = target.position - direction * (target.radius + 6)
        pygame.draw.polygon(self.screen, self.color, (lineStart, lineEnd), 4)
        pygame.draw.circle(self.screen, self.color, target.position, target.radius + 6, 4)


    def redrawWindow(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.screen.blit(self.stars_surface, (0, 0))
        for drawable in self.game.get_drawable_objects():
            drawable.draw(self.screen)
        # print(selectedPlanet)
        if self.selectedPlanetIndex != -1:
            mousePos = pygame.mouse.get_pos()
            planetIndexMousePos = self.game.getPlanetIndexOnPosition(mousePos)
            if planetIndexMousePos != -1 and planetIndexMousePos != self.selectedPlanetIndex:
                self.drawPlanetSelection(self.game.planets[self.selectedPlanetIndex], self.game.planets[planetIndexMousePos])
        
        if self.game.winner_color != None:
            winner_text = 'winner: '
            winner_text_full = winner_text + self.game.winner_nick
            winner_text_size = FONT.size(winner_text_full)
            winner_text_background = pygame.Surface((winner_text_size[0] + 20, winner_text_size[1] + 20))
            winner_text_background.set_alpha(200)
            winner_text_background.fill(BACKGROUND_COLOR)
            self.screen.blit(winner_text_background, (SCREEN_WIDTH/2 - winner_text_size[0]/2 - 10, SCREEN_HEIGHT/2 - winner_text_size[1]/2 - 10))
            # pygame.draw.rect(self.screen, (0, 0, 0, 120), 
            #     (SCREEN_WIDTH/2 - winner_text_size[0]/2 - 10, SCREEN_HEIGHT/2 - winner_text_size[1]/2 - 10, winner_text_size[0] + 20, winner_text_size[1] + 20)
            # )
            self.screen.blit(
                FONT.render(winner_text, True, COLOR_WHITE),
                (SCREEN_WIDTH/2 - winner_text_size[0]/2, SCREEN_HEIGHT/2 - winner_text_size[1]/2)
            )
            self.screen.blit(
                FONT.render(self.game.winner_nick, True, self.game.winner_color),
                (SCREEN_WIDTH/2 - winner_text_size[0]/2 + FONT.size(winner_text)[0], SCREEN_HEIGHT/2  - winner_text_size[1]/2)
            )
            self.button_back_game.draw(self.screen)
        pygame.display.update()
    

    def draw_lobby(self, lobby: Lobby):
        #captions
        self.screen.fill(BACKGROUND_COLOR)
        lobby_name = lobby.get_player(lobby.lobby_leader_id)['nick']+'\'s lobby'
        self.screen.blit(
            FONT.render(lobby_name, True, COLOR_WHITE),
            (SCREEN_WIDTH/2 - FONT.size(lobby_name)[0]/2, 50)
        )
        players_caption = f'players ({lobby.players_connected}/{lobby.players_max}):'
        self.screen.blit(
            FONT.render(players_caption, True, COLOR_WHITE),
            (SCREEN_WIDTH/2 - FONT.size(players_caption)[0]/2, 120)
        )

        #list players in lobby
        player_name_y = 160
        for player in lobby.player_list:
            nick = player['nick']
            player_color = player['color']
            self.screen.blit(
                FONT.render(nick, True, player_color),
                    (SCREEN_WIDTH/2 - FONT.size(nick)[0]/2, player_name_y)
            )
            if player['ready']:
                self.screen.blit(
                FONT.render('√', True, COLOR_GREEN),
                    (SCREEN_WIDTH/2 + FONT.size(nick)[0]/2 + 7, player_name_y)
                )
            player_name_y += FONT.size(nick)[1] + 10
        for color in lobby.available_colors:
            self.screen.blit(
                FONT.render('---', True, color),
                    (SCREEN_WIDTH/2 - FONT.size('---')[0]/2, player_name_y)
            )
            player_name_y += FONT.size(nick)[1] + 10
        
        #countdown if all players are ready
        if self.count_down != self.count_down_length:
            countdown_text = f'starting in {floor(self.count_down)}'
            self.screen.blit(
                FONT.render(countdown_text, True, COLOR_WHITE),
                    (SCREEN_WIDTH/2 - FONT.size(countdown_text)[0]/2, 320)
            )
        
        #ready/not ready buttons
        self.button_ready.draw(self.screen)

        #back to menu button
        self.button_back.draw(self.screen)

        pygame.display.update()

    def run(self):
        clock = pygame.time.Clock()

        while self.running:
            clock.tick(60)

            #get update from server
            update = self.network.send('get')
            if update == False:
                return self.end()
            
            #lobby stage
            if type(update) is Lobby:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        self.end()
                        return
                    
                    # if event.type == pygame.KEYDOWN:
                    #     if event.key == pygame.K_SPACE:
                    #         # print('trying to start')
                    #         self.network.send('start')
                    #         if update.get_player(self.network.player_id) == update.lobby_leader_id:
                    #             self.network.send('start')

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        #back to menu button
                        if self.button_back.detect_hover():
                            self.end()
                            return
                        #ready button
                        elif self.button_ready.detect_hover():
                            self.ready = not self.ready
                            if self.ready:
                                self.button_ready.force_color = COLOR_GRAY
                                self.network.send('ready')
                            else:
                                self.button_ready.force_color = None
                                self.network.send('notReady')
                
                #return to menu of loby leader has left
                if not update.get_player(update.lobby_leader_id):
                    self.end()
                    return
                
                #check if all players are ready and if so, start countdown
                all_ready = True
                for player in update.player_list:
                    if not player['ready']:
                        all_ready = False
                if all_ready:
                    self.count_down -= 1/60
                else:
                    self.count_down = self.count_down_length
                
                if self.count_down <= 0:
                    self.network.send('start')
                
                self.draw_lobby(update)
                continue
            
            #first game init
            if self.game is None:
                self.game = update

            #update moving ships locally
            self.game.updateShips()
            self.game.planets = update.planets
            self.game.winner_color = update.winner_color
            self.game.winner_nick = update.winner_nick

            #send ships that other players have sent locally
            shipUpdates = self.network.send('getShipUpdates')
            if shipUpdates:
                for shipUpdate in shipUpdates:
                    self.game.sendShips(shipUpdate[0], shipUpdate[1], shipUpdate[2])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.end()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.end()
                        return
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game.winner_color == None:
                        planetIndexOnMousePos = self.game.getPlanetIndexOnPosition(pygame.mouse.get_pos())
                        if planetIndexOnMousePos != -1 and self.game.planets[planetIndexOnMousePos].color == self.color:
                            self.selectedPlanetIndex = planetIndexOnMousePos
                    elif self.button_back_game.detect_hover():
                        self.end()
                        return
                
                #deselecting planets and sending ships
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.selectedPlanetIndex != -1:
                        planetIndexOnMousePos = self.game.getPlanetIndexOnPosition(pygame.mouse.get_pos())
                        if planetIndexOnMousePos != -1 and planetIndexOnMousePos != self.selectedPlanetIndex:
                            self.network.send([self.selectedPlanetIndex, planetIndexOnMousePos])
                            self.game.sendShips(self.selectedPlanetIndex, planetIndexOnMousePos)
                    self.selectedPlanetIndex = -1
            
            self.redrawWindow()
    
    def end(self):
        self.running = False
