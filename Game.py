import pygame
import math
from pygame import Vector2
from constants import *
from Planet import Planet
from Ship import Ship
import json

class Game:
    def __init__(self, map_index = None) -> None:
        pygame.init()
        self.planets: list[Planet] = []
        if map_index != None:
            maps_file = open('maps.json')
            all_maps = json.load(maps_file)
            map_data = all_maps[map_index]
            for planet_data in map_data['planets']:
                color = planet_data[0]
                if color == -1:
                    color = COLOR_NEUTRAL
                else:
                    color = PLAYER_COLORS[color]
                x = planet_data[1]
                y = planet_data[2]
                radius = planet_data[3]
                ships = planet_data[4]
                self.planets.append(Planet(x, y, radius, color, ships))
        # self.planets = [
        #     Planet(300, 300, 30, COLOR_BLUE),
        #     Planet(200, 100, 50, COLOR_RED),
        #     Planet(500, 250, 40, COLOR_NEUTRAL),
        #     Planet(400, 500, 50, COLOR_YELLOW),
        #     Planet(650, 200, 50, COLOR_NEUTRAL)
        # ]
        self.ships = []
        self.winner_color: pygame.Color = None
        self.winner_nick: str = None
        

    def update(self) -> None:
        self.update_planets()
        self.update_ships()
    
    def detect_winner(self):
        winner_color = None
        for planet in self.planets:
            if winner_color == None:
                winner_color = planet.color
            elif winner_color != planet.color and planet.color != COLOR_NEUTRAL:
                return
        for ship in self.ships:
            if ship.color != winner_color:
                return
        self.winner_color = winner_color
        
    def get_drawable_objects(self) -> list:
        return self.planets + self.ships
    
    def send_ships(self, source_planet_index: int, target_planet_index: int, amount: int = None):
        source = self.planets[source_planet_index]
        target = self.planets[target_planet_index]
        if amount is not None:
            ship_count = amount
        else:
            ship_count = round(source.ships/2)
            if ship_count > source.ships:
                ship_count -= 1
            source.ships -= ship_count
        source.generate_surface()
        planet_pos = source.position
        direction:Vector2 = (target.position - planet_pos).normalize()
        distance = source.radius
        degree_step = 360/(2*3.14*(distance/(SHIP_SIZE+4)))
        direction = direction.rotate(-degree_step*ship_count/2)
        degree_counter = 0
        for i in range(0, ship_count):
            pos = planet_pos + direction * distance
            direction = direction.rotate(degree_step)
            degree_counter += degree_step
            if degree_counter >= 360:
                degree_counter = 0
                distance += SHIP_SIZE
                degree_step = 360/(2*3.14*(distance/(SHIP_SIZE+4)))
            self.ships.append(Ship(pos, source.color, target_planet_index))
    
    def get_planet_index_on_position(self, position: Vector2) -> int:
        for i in range(len(self.planets)):
            if self.planets[i].isInRadius(position):
                return i
        return -1
    
    def update_planets(self):
        for planet in self.planets:
            planet.update()
    
    def update_ships(self):
        for ship in self.ships:
            ship.update(self.planets)
            if ship.arrived:
                self.ships.remove(ship)
