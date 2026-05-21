import sys
import ctypes
import pygame

from config import WIDTH, HEIGHT, FPS, TITLE
from views.home_page_view import home_page_view
from views.username_view import username_view
from views.play_game_view import play_game_view
from views.settings_view import settings_view


def run_game():
    def set_windows_dark_title_bar():
        if sys.platform != "win32":
            return
        hwnd = pygame.display.get_wm_info().get("window")
        if not hwnd:
            return
        value = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(value), ctypes.sizeof(value)
        )

    def init_pygame():
        pygame.init()
        pygame.font.init()

    def create_screen():
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        set_windows_dark_title_bar()
        return screen

    def create_initial_state():
        return {
            "username": "",
            "settings": {
                "music_volume": 70,
                "sfx_volume": 80,
            },
        }

    def create_views():
        return {
            "home": home_page_view,
            "username": username_view,
            "play": play_game_view,
            "settings": settings_view,
        }

    def user_wants_to_quit(events):
        for event in events:
            if event.type == pygame.QUIT:
                return True
        return False

    def handle_unknown_view(view_name, views):
        if view_name in views:
            return False
        print(f"Erreur : vue inconnue '{view_name}'")
        return True

    def run_main_loop(screen, clock, views, state):
        current_view = "home"
        running = True

        while running:
            events = pygame.event.get()

            if user_wants_to_quit(events):
                running = False

            if handle_unknown_view(current_view, views):
                running = False
                continue

            next_view = views[current_view](screen, events, state)

            if next_view is not None:
                current_view = next_view

            pygame.display.flip()
            clock.tick(FPS)

    def cleanup_and_exit():
        pygame.quit()
        sys.exit()

    init_pygame()
    screen = create_screen()
    clock = pygame.time.Clock()
    state = create_initial_state()
    views = create_views()

    run_main_loop(screen, clock, views, state)
    cleanup_and_exit()
