from constants import *

class Lobby:
    ip_address: str
    players_max: int
    players_connected: int
    player_list: list
    available_colors: list
    open: bool

    def __init__(self, ip_address: str, lobby_leader_id: int) -> None:
        self.players_max = 3
        self.players_connected = 0
        self.player_list = []
        self.available_colors = [COLOR_BLUE, COLOR_RED, COLOR_YELLOW]
        self.lobby_leader_id = lobby_leader_id
        self.ip_address = ip_address
        self.open = True
    
    def add_player(self, player_id: int, nick: str) -> bool:
        if self.players_connected >= self.players_max or not self.open:
            return False
        self.players_connected += 1
        self.player_list.append({
            'player_id': player_id,
            'nick': nick,
            'color': self.available_colors.pop(0),
            'ready': False
        })
        print('current lobby', self.player_list)
        return True
    
    def remove_player(self, player_id: int) -> None:
        player = self.get_player(player_id)
        if player is not None:
            print(f'removing player {player_id} from lobby')
            self.available_colors.insert(0, player['color'])
            self.player_list.remove(player)
            self.players_connected -= 1
    
    def set_player_ready(self, player_id: int, ready: bool):
        self.get_player(player_id)['ready'] = ready
    
    def get_player(self, player_id: int) -> object:
        for i in range(len(self.player_list)):
            if self.player_list[i]['player_id'] == player_id:
                return self.player_list[i]
        return None
        