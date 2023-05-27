class Lobby:
    players_max: int
    players_connected: int

    def __init__(self) -> None:
        self.players_max = 3
        self.players_connected = 0