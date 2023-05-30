import pygame
from network import Network
from constants import *
from pygame import Vector2
from Client import Client
from Button import Button
from InputBox import InputBox
from network import Network
from _thread import *
from server import Server
import pygame.locals
import json
import random

class App:
    MENU_MAIN = 0
    MENU_SELECT_MAP = 1
    MENU_JOIN = 2

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        if FULLSCREEN:
            pygame.display.toggle_fullscreen()
        pygame.display.set_caption("GalPycon")
        
        #main menu
        self.button_host_game = Button('host game', Vector2(SCREEN_WIDTH/2, 240))
        self.button_join_game = Button('join game', Vector2(SCREEN_WIDTH/2, 300))
        self.input_nickname = InputBox('enter your nickname', Vector2(SCREEN_WIDTH/2, 400))
        self.button_fullscreen = Button('toggle fullscreen', Vector2(SCREEN_WIDTH/2, 460))
        self.button_exit = Button('exit', Vector2(SCREEN_WIDTH/2, 600))
        self.buttons_main_menu = [
            self.button_host_game,
            self.button_join_game,
            self.input_nickname,
            self.button_fullscreen,
            self.button_exit
        ]

        #join game menu
        self.button_back = Button('back to main menu', Vector2(SCREEN_WIDTH/2, 600))
        self.buttons_join_game_menu = [
            self.button_back
        ]
        self.buttons_found_lobbies = []

        #select map menu
        self.buttons_maps: list[Button] = []
        self.buttons_select_map_menu = [
            self.button_back
        ]
        maps_file = open('maps.json')
        self.maps = json.load(maps_file)
        y = 150
        for map in self.maps:
            self.buttons_maps.append(
                Button(f'{map["name"]} - {map["players"]} players', Vector2(SCREEN_WIDTH/2, y))
            )
            y += 60
        self.buttons_select_map_menu += self.buttons_maps

        self.current_menu_buttons = self.buttons_main_menu
        self.current_menu = self.MENU_MAIN
        self.finding_games = False
        self.found_lobbies = []
        self.server = None
        self.network = None
        self.default_nick = self.nick = f'player#{random.randint(0, 1000):04d}'
        self.run()

    def run_client(self, server_ip: str):
        self.network.connect(server_ip)
        if not self.network.connected:
            print(f'failed to connect to {server_ip}')
            return
        Client(self.screen, self.network)

    def drawMenu(self):
        self.screen.fill(BACKGROUND_COLOR)

        if self.current_menu == self.MENU_MAIN:
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

        if self.current_menu == self.MENU_JOIN:
            caption = 'games on lan:'
            self.screen.blit(
                FONT.render(caption, True, COLOR_WHITE),
                (SCREEN_WIDTH/2 - FONT.size(caption)[0]/2, 50)
            )
            for button in self.buttons_found_lobbies:
                button.draw(self.screen)
        
        if self.current_menu == self.MENU_SELECT_MAP:
            caption = 'select map:'
            self.screen.blit(
                FONT.render(caption, True, COLOR_WHITE),
                (SCREEN_WIDTH/2 - FONT.size(caption)[0]/2, 50)
            )
            
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
                    if self.input_nickname.text == self.input_nickname.default_text:
                        self.nick = self.default_nick
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.current_menu_buttons + self.buttons_found_lobbies:
                        if button.detect_hover():
                            if button == self.button_join_game:
                                #open join game menu
                                self.network = Network(self.nick)
                                self.current_menu = self.MENU_JOIN
                                self.current_menu_buttons = self.buttons_join_game_menu
                                break
                            elif button == self.button_exit:
                                #quit game
                                pygame.quit()
                                exit()
                            elif button == self.button_back:
                                #back to main menu
                                self.current_menu = self.MENU_MAIN
                                self.current_menu_buttons = self.buttons_main_menu
                            elif button in self.buttons_found_lobbies:
                                #join game
                                index = self.buttons_found_lobbies.index(button)
                                lobby = self.found_lobbies[index]
                                if lobby.players_connected < lobby.players_max:
                                    self.run_client(self.found_lobbies[index].ip_address)
                                    #reset network after disconnecting
                                    self.current_menu = self.MENU_MAIN
                                    self.current_menu_buttons = self.buttons_main_menu
                                    self.network = None
                                    pygame.event.wait(500)
                                    break
                            elif button == self.button_host_game:
                                #open select map menu
                                self.current_menu = self.MENU_SELECT_MAP
                                self.current_menu_buttons = self.buttons_select_map_menu
                            elif button in self.buttons_maps:
                                map_index = self.buttons_maps.index(button)
                                self.network = Network(self.nick)
                                pygame.time.wait(50)
                                self.start_server(map_index)
                                pygame.time.wait(100)
                                self.run_client(self.server.local_ip)
                                #host disconnected - end server and reset network
                                self.network.client.close()
                                self.server.end()
                                self.server = None
                                self.current_menu = self.MENU_MAIN
                                self.current_menu_buttons = self.buttons_main_menu
                                self.network = None
                                pygame.event.wait(500)
                                break
                            elif button == self.input_nickname:
                                button.active = True
                            elif button == self.button_fullscreen:
                                pygame.display.toggle_fullscreen()
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
            y += 60
        print(self.buttons_found_lobbies)
        self.finding_games = False
    
    def start_server(self, map_index: int):
        print('hosting game',self.network.player_id)
        self.server = Server(self.network.player_id, map_index)

App()