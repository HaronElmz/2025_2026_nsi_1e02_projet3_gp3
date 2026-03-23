import sys
import ctypes
import pygame

from config import WIDTH, HEIGHT, FPS, TITLE
from views.home_page_view import home_page_view
from views.username_view import username_view
from views.play_game_view import play_game_view
from views.settings_view import settings_view


def _set_windows_dark_title_bar():
    if sys.platform != "win32":
        return
    hwnd = pygame.display.get_wm_info().get("window")
    if not hwnd:
        return
    value = ctypes.c_int(1)
    ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))


def run_game():
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    _set_windows_dark_title_bar()
    clock = pygame.time.Clock()

    state = {
        "username": ""
    }

    views = {
        "home": home_page_view,
        "username": username_view,
        "play": play_game_view,
        "settings": settings_view,
    }

    current_view = "home"
    running = True

    while running:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        if current_view not in views:
            print(f"Erreur : vue inconnue '{current_view}'")
            running = False
            continue

        next_view = views[current_view](screen, events, state)

        if next_view is not None:
            current_view = next_view

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()