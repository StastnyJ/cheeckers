#!/usr/bin/python3.7

from game import *
from pygame_utils import *
from menus import *
from AI_base import *
import pygame as pg


pg.init()
pg.display.set_caption("Cheekers")
screen = pg.display.set_mode((get_screen_width(), get_screen_height()))


main_menu = MainMenu(screen)
menu_result = main_menu.show_menu()

exit = False
if menu_result is None:
    exit = True
else:
    game = menu_result


while not exit:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit = True
        if event.type == pg.MOUSEBUTTONUP:
            game_over = game.click_event(get_clicked_field_coords(pg.mouse.get_pos()))
            if game_over:
                draw(screen, game)
                wait_for_click()
                if exit:
                    break
                menu_result = main_menu.show_menu()
                if menu_result is None:
                    exit = True
                else:
                    game = menu_result 
    draw(screen, game)
    pg.display.flip()
