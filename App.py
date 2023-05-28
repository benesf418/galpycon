import pygame
from network import Network
from Game import Game
from Planet import Planet
from constants import *
from pygame import Vector2
from Client import Client
from Button import Button
from InputBox import InputBox
from network import Network
from _thread import *
from server import Server
import pygame.locals
from Lobby import Lobby

class App:
    screen: pygame.display
    server: Server
    nick: str

    finding_games: bool
    found_lobbies: list[Lobby]

    #main menu
    button_host_game: Button
    button_join_game: Button
    input_nickname: InputBox
    button_exit: Button
    buttons_main_menu: list[Button]

    #join game menu
    button_back: Button
    buttons_join_game_menu: list[Button]

    #found games buttons
    buttons_found_lobbies: list[Button]

    current_menu_buttons: list[Button]

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.locals.RESIZABLE)
        if FULLSCREEN:
            pygame.display.toggle_fullscreen()
        pygame.display.set_caption("GalPycon")
        
        #main menu
        self.button_host_game = Button('host game', Vector2(SCREEN_WIDTH/2, 240))
        self.button_join_game = Button('join game', Vector2(SCREEN_WIDTH/2, 300))
        self.input_nickname = InputBox('enter your nickname', Vector2(SCREEN_WIDTH/2, 400))
        self.button_exit = Button('exit', Vector2(SCREEN_WIDTH/2, 500))
        self.buttons_main_menu = [
            self.button_host_game,
            self.button_join_game,
            self.input_nickname,
            self.button_exit
        ]

        #join game menu
        self.button_back = Button('back to main menu', Vector2(SCREEN_WIDTH/2, 500))
        self.buttons_join_game_menu = [
            self.button_back
        ]
        self.buttons_found_lobbies = []

        self.current_menu_buttons = self.buttons_main_menu
        self.finding_games = False
        self.found_lobbies = []
        self.server = None
        self.network = None
        self.nick = None
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
            caption_center_y = FONT.size(caption)[1]/2+50
            pygame.draw.polygon(self.screen, COLOR_WHITE, (
                (10,caption_center_y), (SCREEN_WIDTH/2-FONT.size(caption)[0]/2-10, caption_center_y)
            ), 2)
            pygame.draw.polygon(self.screen, COLOR_WHITE, (
                (SCREEN_WIDTH/2+FONT.size(caption)[0]/2+10, caption_center_y), (SCREEN_WIDTH - 10, caption_center_y)
            ), 2)

        if self.current_menu_buttons == self.buttons_join_game_menu:
            caption = 'games on lan:'
            self.screen.blit(
                FONT.render(caption, True, COLOR_WHITE),
                (SCREEN_WIDTH/2 - FONT.size(caption)[0]/2, 50)
            )
            for button in self.buttons_found_lobbies:
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

                #handle input (nickname)
                if self.input_nickname.active:
                    new_nick = self.input_nickname.handle_input(event)
                    if new_nick:
                        self.nick = new_nick
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.current_menu_buttons + self.buttons_found_lobbies:
                        if button.detect_hover():
                            #main menu
                            if button == self.button_join_game:
                                self.network = Network(self.nick)
                                self.current_menu_buttons = self.buttons_join_game_menu
                                break
                            elif button == self.button_exit:
                                pygame.quit()
                                exit()
                            #join game menu
                            elif button == self.button_back:
                                self.current_menu_buttons = self.buttons_main_menu
                            elif button in self.buttons_found_lobbies:
                                index = self.buttons_found_lobbies.index(button)
                                lobby = self.found_lobbies[index]
                                if lobby.players_connected < lobby.players_max:
                                    self.run_client(self.found_lobbies[index].ip_address)
                                    #reset network after disconnecting
                                    self.current_menu_buttons = self.buttons_main_menu
                                    self.network = None
                                    pygame.event.wait(500)
                                    break
                            elif button == self.button_host_game:
                                self.network = Network(self.nick)
                                pygame.time.wait(50)
                                self.start_server()
                                pygame.time.wait(100)
                                self.run_client(self.server.local_ip)
                                #host disconnected - end server and reset network
                                self.network.client.close()
                                self.server.end()
                                # self.server.socket.close()
                                self.server = None
                                self.current_menu_buttons = self.buttons_main_menu
                                self.network = None
                                pygame.event.wait(500)
                                break
                            elif button == self.input_nickname:
                                button.active = True
                            else:
                                print(button)

            if self.current_menu_buttons == self.buttons_join_game_menu and not self.finding_games:
                start_new_thread(self.find_lobbies, ())
            
            self.drawMenu()
    
    def find_lobbies(self):
        self.finding_games = True
        self.found_lobbies = self.network.find_games()
        self.buttons_found_lobbies = []
        y = 150
        for lobby in self.found_lobbies:
            lobby_leader = lobby.get_player(lobby.lobby_leader_id)['nick']
            self.buttons_found_lobbies.append(Button(
                f'{lobby_leader} ({lobby.players_connected}/{lobby.players_max})', Vector2(SCREEN_WIDTH/2, y)
            ))
            y += 50
        print(self.buttons_found_lobbies)
        self.finding_games = False
    
    def start_server(self):
        print('hosting game',self.network.player_id)
        self.server = Server(self.network.player_id)

App()