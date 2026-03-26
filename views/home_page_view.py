import pygame
from pathlib import Path
from config import WIDTH, HEIGHT

TITLE_FONT_SIZE = 72
BUTTON_FONT_SIZE = 42


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


def draw_button(screen, rect, text, font):
    mouse_pos = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(mouse_pos)
    color = (90, 15, 18) if is_hover else (45, 8, 10)

    pygame.draw.rect(screen, color, rect, border_radius=4)
    pygame.draw.rect(screen, (130, 18, 24), rect, 2, border_radius=4)

    shadow_surface = font.render(text, True, (15, 0, 0))
    shadow_rect = shadow_surface.get_rect(center=(rect.centerx + 2, rect.centery + 2))
    screen.blit(shadow_surface, shadow_rect)

    text_surface = font.render(text, True, (205, 32, 38))
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


def home_page_view(screen, events, state):
    if "home_bg" not in state:
        bg_path = Path(__file__).resolve().parent.parent / "assets" / "main_bg.png"
        bg_image = pygame.image.load(str(bg_path)).convert()
        state["home_bg"] = pygame.transform.smoothscale(bg_image, (WIDTH, HEIGHT))

    screen.blit(state["home_bg"], (0, 0))

    title_font = get_horror_font(TITLE_FONT_SIZE, bold=True, italic=True)
    button_font = get_horror_font(BUTTON_FONT_SIZE, bold=True)

    title_shadow = title_font.render("L'ombre du passé", True, (20, 0, 0))
    screen.blit(title_shadow, title_shadow.get_rect(center=(WIDTH // 2 + 3, 120 + 3)))
    title_surface = title_font.render("L'ombre du passé", True, (175, 20, 28))
    screen.blit(title_surface, title_surface.get_rect(center=(WIDTH // 2, 120)))

    play_button = pygame.Rect(WIDTH // 2 - 150, 240, 300, 70)
    settings_button = pygame.Rect(WIDTH // 2 - 150, 340, 300, 70)

    draw_button(screen, play_button, "Jouer", button_font)
    draw_button(screen, settings_button, "Paramètres", button_font)

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if play_button.collidepoint(event.pos):
                return "username"
            if settings_button.collidepoint(event.pos):
                return "settings"

    return None