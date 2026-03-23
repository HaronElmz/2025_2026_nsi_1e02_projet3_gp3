import pygame
from config import WIDTH, HEIGHT, BLACK

FONT_SIZE = 50


def username_view(screen, events, state):
    screen.fill(BLACK)

    font = pygame.font.SysFont("timesnewroman", FONT_SIZE, bold=True)

    input_box = pygame.Rect(0, 0, 400, 60)
    input_box.center = (WIDTH // 2, HEIGHT // 2 + 10)

    # état local (créé une seule fois)
    if "input_active" not in state:
        state["input_active"] = False
        state["cursor_timer"] = 0
        state["cursor_visible"] = True

    # titre
    title_surface_shadow = font.render("Entrez votre nom :", True, (20, 0, 0))
    screen.blit(title_surface_shadow, (WIDTH//2 - 197, HEIGHT//2 - 117))
    title_surface = font.render("Entrez votre nom :", True, (175, 20, 28))
    screen.blit(title_surface, (WIDTH//2 - 200, HEIGHT//2 - 120))

    # gestion événements
    for event in events:

        if event.type == pygame.MOUSEBUTTONDOWN:
            # active si on clique dedans
            state["input_active"] = input_box.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and state["input_active"]:

            if event.key == pygame.K_RETURN:
                if state["username"] != "":
                    return "play"

            elif event.key == pygame.K_BACKSPACE:
                state["username"] = state["username"][:-1]

            else:
                if len(state["username"]) < 15:
                    state["username"] += event.unicode

    # couleur selon actif
    color = (85, 12, 16) if state["input_active"] else (42, 6, 9)

    pygame.draw.rect(screen, color, input_box, border_radius=4)
    pygame.draw.rect(screen, (130, 18, 24), input_box, 2, border_radius=4)

    # texte
    available_width = input_box.width - 20
    visible_text = state["username"]
    while font.size(visible_text)[0] > available_width and visible_text:
        visible_text = visible_text[1:]

    name_surface = font.render(visible_text, True, (215, 34, 40))
    text_x = input_box.x + 10
    text_y = input_box.y + (input_box.height - name_surface.get_height()) // 2
    screen.blit(name_surface, (text_x, text_y))

    # curseur clignotant
    if state["input_active"]:
        state["cursor_timer"] += 1

        if state["cursor_timer"] >= 30:
            state["cursor_visible"] = not state["cursor_visible"]
            state["cursor_timer"] = 0

        if state["cursor_visible"]:
            cursor_x = min(input_box.right - 10, text_x + name_surface.get_width() + 5)
            cursor_y = text_y

            pygame.draw.line(
                screen,
                (215, 34, 40),
                (cursor_x, cursor_y),
                (cursor_x, cursor_y + name_surface.get_height()),
                2
            )

    return None