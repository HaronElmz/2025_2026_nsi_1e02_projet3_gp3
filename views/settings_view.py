import pygame

from config import WIDTH, HEIGHT
from views.home_page_view import draw_button, get_horror_font

TITLE_FONT_SIZE = 56
LABEL_FONT_SIZE = 34
CONTROL_FONT_SIZE = 30
SMALL_BTN_W, SMALL_BTN_H = 52, 44
ROW_GAP = 120


def _ensure_settings(state):
    defaults = {
        "music_volume": 70,
        "sfx_volume": 80,
    }
    if "settings" not in state:
        state["settings"] = defaults.copy()
        return
    for key, value in defaults.items():
        state["settings"].setdefault(key, value)
    state["settings"].pop("difficulty", None)


def _draw_small_button(screen, rect, text, font):
    mouse_pos = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(mouse_pos)
    color = (90, 15, 18) if is_hover else (45, 8, 10)
    pygame.draw.rect(screen, color, rect, border_radius=4)
    pygame.draw.rect(screen, (130, 18, 24), rect, 2, border_radius=4)
    shadow = font.render(text, True, (15, 0, 0))
    screen.blit(shadow, shadow.get_rect(center=(rect.centerx + 1, rect.centery + 1)))
    surf = font.render(text, True, (205, 32, 38))
    screen.blit(surf, surf.get_rect(center=rect.center))


def settings_view(screen, events, state):
    _ensure_settings(state)
    s = state["settings"]

    screen.fill((22, 14, 14))

    title_font = get_horror_font(TITLE_FONT_SIZE, bold=True, italic=True)
    label_font = get_horror_font(LABEL_FONT_SIZE, bold=True)
    control_font = get_horror_font(CONTROL_FONT_SIZE, bold=True)

    title_shadow = title_font.render("Paramètres", True, (20, 0, 0))
    screen.blit(title_shadow, title_shadow.get_rect(center=(WIDTH // 2 + 2, 72 + 2)))
    title_surface = title_font.render("Paramètres", True, (190, 26, 34))
    screen.blit(title_surface, title_surface.get_rect(center=(WIDTH // 2, 72)))

    center_x = WIDTH // 2
    block_top = 150

    def volume_block(label, key, y_title):
        lab = label_font.render(label, True, (200, 185, 175))
        screen.blit(lab, lab.get_rect(center=(center_x, y_title)))

        val = s[key]
        val_surface = control_font.render(f"{val} %", True, (215, 200, 185))
        gap = 22
        total_w = SMALL_BTN_W + gap + val_surface.get_width() + gap + SMALL_BTN_W
        left = center_x - total_w // 2
        y_ctrl = y_title + 44

        minus_r = pygame.Rect(left, y_ctrl, SMALL_BTN_W, SMALL_BTN_H)
        val_x = left + SMALL_BTN_W + gap
        plus_r = pygame.Rect(val_x + val_surface.get_width() + gap, y_ctrl, SMALL_BTN_W, SMALL_BTN_H)

        _draw_small_button(screen, minus_r, "−", control_font)
        _draw_small_button(screen, plus_r, "+", control_font)
        val_y = y_ctrl + (SMALL_BTN_H - val_surface.get_height()) // 2
        screen.blit(val_surface, (val_x, val_y))

        return minus_r, plus_r

    m_minus, m_plus = volume_block("Volume musique", "music_volume", block_top)
    fx_minus, fx_plus = volume_block("Volume effets sonores", "sfx_volume", block_top + ROW_GAP)

    back_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 120, 300, 58)
    draw_button(screen, back_rect, "Retour au menu", get_horror_font(32, bold=True))

    hint = get_horror_font(22, bold=False).render("Échap : retour au menu", True, (120, 100, 95))
    screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 38)))

    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "home"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            def clamp_vol(v):
                return max(0, min(100, v))

            if m_minus.collidepoint(pos):
                s["music_volume"] = clamp_vol(s["music_volume"] - 10)
            elif m_plus.collidepoint(pos):
                s["music_volume"] = clamp_vol(s["music_volume"] + 10)
            elif fx_minus.collidepoint(pos):
                s["sfx_volume"] = clamp_vol(s["sfx_volume"] - 10)
            elif fx_plus.collidepoint(pos):
                s["sfx_volume"] = clamp_vol(s["sfx_volume"] + 10)
            elif back_rect.collidepoint(pos):
                return "home"

    return None
