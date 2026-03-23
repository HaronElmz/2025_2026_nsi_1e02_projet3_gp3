import pygame
from config import WIDTH, HEIGHT, WHITE

FONT_SIZE = 50


def settings_view(screen, events, state):
    screen.fill((30, 20, 20))

    font = pygame.font.SysFont("timesnewroman", FONT_SIZE, bold=True)

    text_shadow = font.render("Paramètres", True, (20, 0, 0))
    screen.blit(text_shadow, text_shadow.get_rect(center=(WIDTH // 2 + 2, HEIGHT // 2 + 2)))
    text_surface = font.render("Paramètres", True, (190, 26, 34))
    screen.blit(text_surface, text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "home"

    return None