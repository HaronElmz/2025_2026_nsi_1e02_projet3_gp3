import pygame
from pathlib import Path

from config import WIDTH, HEIGHT, BLACK

TITLE_FONT_SIZE = 56
INPUT_FONT_SIZE = 38


def username_view(screen, events, state):
    def get_horror_font(size, bold=False, italic=False):
        candidates = (
            "chiller",
            "oldenglishtextmt",
            "blackadderitc",
            "imprintmttshadow",
            "timesnewroman",
        )
        for name in candidates:
            if pygame.font.match_font(name):
                return pygame.font.SysFont(name, size, bold=bold, italic=italic)
        return pygame.font.SysFont(None, size, bold=bold, italic=italic)

    def load_username_background():
        if "username_bg" in state:
            return
        try:
            bg_path = (
                Path(__file__).resolve().parent.parent
                / "assets"
                / "Fond  d'écran prénom.png"
            )
            bg_image = pygame.image.load(str(bg_path)).convert()
            state["username_bg"] = pygame.transform.smoothscale(bg_image, (WIDTH, HEIGHT))
        except Exception:
            state["username_bg"] = None

    def draw_background():
        if state["username_bg"] is not None:
            screen.blit(state["username_bg"], (0, 0))
        else:
            screen.fill(BLACK)

    def init_input_state():
        if "input_active" not in state:
            state["input_active"] = False
            state["cursor_timer"] = 0
            state["cursor_visible"] = True

    def draw_title(title_font):
        title_text = "Entrez votre nom :"
        title_center = (WIDTH // 2, HEIGHT // 2 - 10)

        title_surface_shadow = title_font.render(title_text, True, (20, 0, 0))
        screen.blit(
            title_surface_shadow,
            title_surface_shadow.get_rect(center=(title_center[0] + 3, title_center[1] + 3)),
        )

        title_surface = title_font.render(title_text, True, (205, 32, 38))
        screen.blit(title_surface, title_surface.get_rect(center=title_center))

    def handle_keyboard_events(input_box):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                state["input_active"] = input_box.collidepoint(event.pos)

            if event.type == pygame.KEYDOWN and state["input_active"]:
                if event.key == pygame.K_RETURN:
                    if state["username"] != "":
                        state.pop("game_state", None)
                        return "play"

                elif event.key == pygame.K_BACKSPACE:
                    state["username"] = state["username"][:-1]

                else:
                    if event.unicode and not event.unicode.isspace() and len(state["username"]) < 15:
                        state["username"] += event.unicode
        return None

    def get_input_colors():
        border_color = (140, 85, 65) if state["input_active"] else (110, 65, 50)
        fill_color = (35, 16, 16) if state["input_active"] else (28, 12, 12)
        text_color = (215, 180, 150)
        return border_color, fill_color, text_color

    def trim_text_to_fit(text, font, max_width):
        display_text = text
        while font.size(display_text)[0] > max_width and display_text:
            display_text = display_text[1:]
        return display_text

    def draw_input_box(input_box, input_font):
        border_color, fill_color, text_color = get_input_colors()

        pygame.draw.rect(screen, fill_color, input_box, border_radius=8)
        pygame.draw.rect(screen, border_color, input_box, 4, border_radius=8)

        inner_box = input_box.inflate(-18, -18)
        pygame.draw.rect(screen, (55, 28, 26), inner_box, border_radius=6)
        pygame.draw.rect(screen, (70, 35, 33), inner_box, 2, border_radius=6)

        padding_x = 18
        available_width = input_box.width - (padding_x + 18)
        display_text = trim_text_to_fit(state["username"], input_font, available_width)

        name_surface = input_font.render(display_text, True, text_color)
        text_x = input_box.x + padding_x
        text_y = input_box.y + (input_box.height - name_surface.get_height()) // 2
        screen.blit(name_surface, (text_x, text_y))

        return text_x, text_y, name_surface, available_width, text_color

    def draw_blinking_cursor(input_box, input_font, text_x, text_y, name_surface, available_width, text_color):
        if not state["input_active"]:
            return

        state["cursor_timer"] += 1
        if state["cursor_timer"] >= 30:
            state["cursor_visible"] = not state["cursor_visible"]
            state["cursor_timer"] = 0

        if not state["cursor_visible"]:
            return

        typed_display = trim_text_to_fit(state["username"], input_font, available_width)
        cursor_x = min(input_box.right - 12, text_x + input_font.size(typed_display)[0] + 2)
        cursor_y = text_y

        pygame.draw.line(
            screen,
            text_color,
            (cursor_x, cursor_y),
            (cursor_x, cursor_y + name_surface.get_height()),
            2,
        )

    load_username_background()
    draw_background()

    title_font = get_horror_font(TITLE_FONT_SIZE, bold=True, italic=True)
    input_font = get_horror_font(INPUT_FONT_SIZE, bold=True)

    input_box = pygame.Rect(0, 0, 420, 60)
    input_box.center = (WIDTH // 2, HEIGHT // 2 + 60)

    init_input_state()
    draw_title(title_font)

    next_view = handle_keyboard_events(input_box)
    if next_view is not None:
        return next_view

    text_x, text_y, name_surface, available_width, text_color = draw_input_box(input_box, input_font)
    draw_blinking_cursor(
        input_box, input_font, text_x, text_y, name_surface, available_width, text_color
    )

    return None
