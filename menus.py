import pygame as pg
from pygame_utils import *
from game import *
from AI_base import *


class Menu:
    def __init__(self, screen, items, header = ""):
        self.items = items
        self.spacing = 50
        self.top = 100
        self.header = header
        self.item_height = min((get_screen_height() - self.spacing * len(items) - 2 * self.top) // len(items), 200)
        self.item_width = int(get_screen_width() * 0.8)
        self.screen = screen
    
    def show_menu(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return None
                if event.type == pg.MOUSEBUTTONUP:
                    item = self._get_clicked_item(pg.mouse.get_pos())
                    if item is not None:
                        return item
            self._draw_menu()
            pg.display.flip()

    def _get_clicked_item(self, pos):
        x, y = pos
        left = (get_screen_width() - self.item_width) // 2
        if x < left or x > left + self.item_width:
            return None
        y -= self.top
        if y % (self.item_height + self.spacing) > self.item_height:
            return None
        y = y // (self.item_height + self.spacing)
        if y >= len(self.items):
            return None
        return self.items[y]

    def _draw_menu(self):
        self.screen.fill(Colors.light_brown.value)
        draw_text(self.screen, self.header, 64, (get_screen_width() // 2, self.top // 3), Colors.black.value)
        x = (get_screen_width() - self.item_width) // 2
        y = self.top
        for item in self.items:
            self._draw_menu_item(item, (x, y))
            y += self.item_height + self.spacing

    def _draw_menu_item(self, item, pos):
        pg.draw.rect(self.screen, Colors.dark_brown.value, pg.Rect(pos[0], pos[1], self.item_width, self.item_height))
        draw_text(self.screen, item, 64, (get_screen_width() // 2, pos[1] + self.item_height // 2), Colors.white.value)

class MainMenu(Menu):
    def __init__(self, screen):
        super(MainMenu, self).__init__(screen, [
            MainMenuResults.SinglePlayer.value,
            MainMenuResults.Multiplayer.value,
            MainMenuResults.AIvsAI.value
        ])

    def show_menu(self):
        res = super(MainMenu, self).show_menu()
        if res is None:
            return None
        if res == MainMenuResults.Multiplayer.value:
            return Game(PlayerType.Player, PlayerType.Player)
        if res == MainMenuResults.SinglePlayer.value:
            sub_menu = StrategySelectMenu(self.screen)
            AI = sub_menu.show_menu()
            return Game(PlayerType.Player, PlayerType.AI, player1_AI=AI)
        sub_menu = StrategySelectMenu(self.screen, "Select AI strategy for white player")
        AI_player0 = sub_menu.show_menu()
        sub_menu = StrategySelectMenu(self.screen, "Select AI strategy for black player")
        AI_player1 = sub_menu.show_menu()
        return Game(PlayerType.AI, PlayerType.AI, AI_player0, AI_player1)

class StrategySelectMenu(Menu):
    def __init__(self, screen, header = "Select strategy for AI"):
        super(StrategySelectMenu, self).__init__(screen, list(_strategies.keys()), header)
    
    def show_menu(self):
        res = super(StrategySelectMenu, self).show_menu()
        if res is None:
            return None
        return _strategies[res]


class MainMenuResults(Enum):
    SinglePlayer = "Single player"
    Multiplayer = "Multiplayer"
    AIvsAI = "AI vs AI"

_strategies = {
    "Random": RandomStrategy(),
    "MinMax1": MinMaxStrategy(1),
    "MinMax2": MinMaxStrategy(2),
    "MinMax4": MinMaxStrategy(4),
    "MinMaxFlexible": MinMaxFlexibleDeepStrategy(0)
}