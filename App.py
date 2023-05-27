import pygame
from network import Network
from Game import Game
from Planet import Planet
from constants import *
from pygame import Vector2
from Client import Client
from Button import Button
from network import Network
from _thread import *
from server import Server
import pygame.locals

class App:
    screen: pygame.display
    server: Server

    finding_games: bool

    #main menu
    button_host_game: Button
    button_join_game: Button
    button_exit: Button
    buttons_main_menu: list[Button]

    #join game menu
    button_back: Button
    buttons_join_game_menu: list[Button]

    #found games buttons
    buttons_found_games: list[Button]

    current_menu_buttons: list[Button]

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.locals.RESIZABLE)
        if FULLSCREEN:
            pygame.display.toggle_fullscreen()
        pygame.display.set_caption("GalPycon")
        self.network = Network()

        #main menu
        self.button_host_game = Button('host game', Vector2(SCREEN_WIDTH/2, 240))
        self.button_join_game = Button('join game', Vector2(SCREEN_WIDTH/2, 300))
        self.button_exit = Button('exit', Vector2(SCREEN_WIDTH/2, 500))
        self.buttons_main_menu = [
            self.button_host_game,
            self.button_join_game,
            self.button_exit
        ]

        #join game menu
        self.button_back = Button('back to main menu', Vector2(SCREEN_WIDTH/2, 500))
        self.buttons_join_game_menu = [
            self.button_back
        ]
        self.buttons_found_games = []

        self.current_menu_buttons = self.buttons_main_menu
        self.finding_games = False
        self.server = None
        self.run()

    def run_client(self, server_ip: str):
        self.network.connect(server_ip)
        if not self.network.connected:
            print(f'failed to connect to {server_ip}')
            return
        Client(self.screen, self.network)

    def drawMenu(self):
        self.screen.fill(BACKGROUND_COLOR)

        if self.current_menu_buttons == self.buttons_main_menu:
            caption = 'GalPycon'
            self.screen.blit(
                FONT.render(caption, True, COLOR_WHITE),
                (SCREEN_WIDTH/2 - FONT.size(caption)[0]/2, 50)
            )
            camptionCenterY = FONT.size(caption)[1]/2+50
            pygame.draw.polygon(self.screen, COLOR_WHITE, (
                (10,camptionCenterY), (SCREEN_WIDTH/2-FONT.size(caption)[0]/2-10, camptionCenterY)
            ), 2)
            pygame.draw.polygon(self.screen, COLOR_WHITE, (
                (SCREEN_WIDTH/2+FONT.size(caption)[0]/2+10, camptionCenterY), (SCREEN_WIDTH - 10, camptionCenterY)
            ), 2)

        if self.current_menu_buttons == self.buttons_join_game_menu:
            caption = 'games on lan:'
            self.screen.blit(
                FONT.render(caption, True, COLOR_WHITE),
                (SCREEN_WIDTH/2 - FONT.size(caption)[0]/2, 50)
            )
            for button in self.buttons_found_games:
                button.draw(self.screen)
            
        for button in self.current_menu_buttons:
            button.draw(self.screen)
        pygame.display.update()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.current_menu_buttons + self.buttons_found_games:
                        if button.detect_hover():
                            #main menu
                            if button == self.button_join_game:
                                self.current_menu_buttons = self.buttons_join_game_menu
                                break
                            elif button == self.button_exit:
                                pygame.quit()
                                exit()
                            #join game menu
                            elif button == self.button_back:
                                self.current_menu_buttons = self.buttons_main_menu
                            elif button in self.buttons_found_games:
                                print('idk')
                                self.run_client(button.text)
                            elif button == self.button_host_game:
                                start_new_thread(self.start_server, ())
                                pygame.time.wait(1000)
                                self.run_client(self.server.local_ip)
                                #host disconnected - end server
                                self.server.end()
                                self.server = None
                                self.current_menu_buttons = self.buttons_main_menu
                            else:
                                print(button)

            if self.current_menu_buttons == self.buttons_join_game_menu and not self.finding_games:
                start_new_thread(self.generate_found_games_buttons, ())
            
            self.drawMenu()
    
    def generate_found_games_buttons(self):
        self.finding_games = True
        found_games = self.network.find_games()
        self.buttons_found_games = []
        y = 150
        for server in found_games:
            self.buttons_found_games.append(Button(
                server, Vector2(SCREEN_WIDTH/2, y)
            ))
            y += 50
        print(self.buttons_found_games)
        self.finding_games = False
    
    def start_server(self):
        self.server = Server()
        self.server.run()

App()