import pygame
from pathlib import Path

from config import WIDTH, HEIGHT
from engine.story_engine import (
    load_story_data,
    new_game_state,
    get_scene,
    get_available_choices,
    choose,
    scene_type,
    is_end_scene,
    format_narration,
    apply_scene_entry_effects,
    apply_player_pose,
    get_player_pose,
)

ASSETS = Path(__file__).resolve().parent.parent / "assets"

MARGIN = 16
PANEL_PAD = 14
CHOICE_BTN_H = 40
CHOICE_GAP = 8
TEXT_GAP = 10

PANEL_COLOR = (18, 12, 14)
PANEL_BORDER = (120, 28, 32)
TEXT_COLOR = (220, 200, 185)
DEATH_ACCENT = (140, 20, 28)
WIN_ACCENT = (80, 120, 90)

PLAYER_SPRITES = {
    "calm": "character_1_style_1.png",
    "tense": "character_1_style_2.png",
}


def wrap_text(font, text, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if font.size(trial)[0] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines if lines else [""]


def scale_keep_aspect(image, max_w, max_h):
    iw, ih = image.get_size()
    ratio = min(max_w / iw, max_h / ih)
    nw = max(1, int(iw * ratio))
    nh = max(1, int(ih * ratio))
    return pygame.transform.smoothscale(image, (nw, nh))


def play_game_view(screen, events, state):
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

    def make_cache_key(name):
        return f"{name}_{WIDTH}x{HEIGHT}"

    def load_cached_image(cache_key, filename, max_w, max_h):
        key = make_cache_key(cache_key)
        if key in state:
            return state[key]
        path = ASSETS / filename
        if not path.is_file():
            state[key] = None
            return None
        try:
            image = pygame.image.load(str(path)).convert_alpha()
        except pygame.error:
            state[key] = None
            return None
        state[key] = scale_keep_aspect(image, max_w, max_h)
        return state[key]

    def reset_story():
        state.pop("game_state", None)

    def ensure_story_loaded():
        if not state.get("story_data"):
            state["story_data"] = load_story_data()
        if not state.get("game_state"):
            state["game_state"] = new_game_state(state["story_data"])
            scene = get_scene(state["story_data"], state["game_state"]["scene_id"])
            apply_scene_entry_effects(scene, state["game_state"]["variables"])
            apply_player_pose(scene, state["game_state"])
        bg_key = make_cache_key("play_bg")
        if bg_key not in state:
            bg = pygame.image.load(str(ASSETS / "main_bg.png")).convert()
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(140)
            bg = scale_keep_aspect(bg, WIDTH, HEIGHT)
            bg_rect = bg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            canvas = pygame.Surface((WIDTH, HEIGHT))
            canvas.fill((10, 8, 12))
            canvas.blit(bg, bg_rect)
            canvas.blit(overlay, (0, 0))
            state[bg_key] = canvas

    def find_font_for_button(text, max_w, max_h, start_size=20):
        size = start_size
        while size >= 14:
            font = get_horror_font(size, bold=True)
            surf = font.render(text, True, (210, 190, 175))
            if surf.get_width() <= max_w - 16 and surf.get_height() <= max_h - 10:
                return font
            size -= 1
        return get_horror_font(14, bold=True)

    def draw_button(rect, text, font=None, accent=(90, 15, 18), hover_accent=(120, 22, 28)):
        if font is None:
            font = find_font_for_button(text, rect.width, rect.height)
        mouse_pos = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mouse_pos)
        color = hover_accent if is_hover else accent
        pygame.draw.rect(screen, color, rect, border_radius=4)
        pygame.draw.rect(screen, (150, 30, 36), rect, 2, border_radius=4)
        shadow = font.render(text, True, (15, 0, 0))
        screen.blit(shadow, shadow.get_rect(center=(rect.centerx + 1, rect.centery + 1)))
        label = font.render(text, True, (210, 190, 175))
        screen.blit(label, label.get_rect(center=rect.center))

    def compute_layout(choice_count, is_end):
        if is_end:
            choices_h = CHOICE_BTN_H + MARGIN
        elif choice_count:
            choices_h = choice_count * (CHOICE_BTN_H + CHOICE_GAP) - CHOICE_GAP + MARGIN
        else:
            choices_h = MARGIN

        choices_top = HEIGHT - choices_h
        panel_bottom = choices_top - TEXT_GAP
        panel_top_min = MARGIN + 80
        panel_max_h = panel_bottom - panel_top_min - TEXT_GAP
        panel_h = min(210, max(130, panel_max_h))
        panel_top = panel_bottom - panel_h
        scene_bottom = panel_top - 8

        return {
            "choices_top": choices_top,
            "choices_h": choices_h,
            "panel": pygame.Rect(MARGIN, panel_top, WIDTH - 2 * MARGIN, panel_h),
            "panel_bottom": panel_bottom,
            "scene_bottom": scene_bottom,
        }

    def draw_monster_panel(story_data, scene, scene_bottom, font_small):
        monster_id = scene.get("monster")
        if not monster_id:
            return
        monster = story_data["monsters"].get(monster_id, {})
        name = monster.get("name", "???")
        desc = monster.get("description", "")
        image_file = monster.get("image")

        panel_w = 230
        panel_h = min(300, scene_bottom - MARGIN - 10)
        panel = pygame.Rect(WIDTH - panel_w - MARGIN, MARGIN, panel_w, panel_h)
        pygame.draw.rect(screen, (25, 10, 12), panel, border_radius=6)
        pygame.draw.rect(screen, DEATH_ACCENT, panel, 2, border_radius=6)

        title_font = get_horror_font(22, bold=True)
        title = title_font.render(name, True, (200, 50, 55))
        screen.blit(title, title.get_rect(midtop=(panel.centerx, panel.top + 8)))

        def draw_monster_placeholder(inner_top):
            shadow_rect = pygame.Rect(panel.centerx - 40, inner_top, 80, 100)
            pygame.draw.ellipse(screen, (40, 15, 20), shadow_rect)
            pygame.draw.ellipse(screen, (90, 25, 35), shadow_rect, 2)
            return inner_top + 10

        inner_top = panel.top + 36
        if image_file:
            sprite = load_cached_image(f"monster_{monster_id}", image_file, panel_w - 24, 140)
            if sprite is not None:
                sprite_rect = sprite.get_rect(midtop=(panel.centerx, inner_top))
                screen.blit(sprite, sprite_rect)
                desc_y = min(sprite_rect.bottom + 6, panel.bottom - 50)
            else:
                desc_y = draw_monster_placeholder(inner_top)
        else:
            desc_y = draw_monster_placeholder(inner_top)

        for i, line in enumerate(wrap_text(font_small, desc, panel.width - 16)[:3]):
            y = desc_y + i * 18
            if y + 18 > panel.bottom - 6:
                break
            line_surf = font_small.render(line, True, (170, 140, 135))
            screen.blit(line_surf, (panel.x + 8, y))

    def draw_player_name(username, center_x, bottom_y):
        if not username:
            return
        font = get_horror_font(26, bold=True)
        shadow = font.render(username, True, (15, 0, 0))
        label = font.render(username, True, (235, 210, 185))
        name_rect = label.get_rect(midbottom=(center_x, bottom_y - 6))
        plate = name_rect.inflate(24, 12)
        plate.bottom = name_rect.bottom + 4
        plate.centerx = center_x
        pygame.draw.rect(screen, (28, 14, 16), plate, border_radius=6)
        pygame.draw.rect(screen, (130, 35, 40), plate, 2, border_radius=6)
        screen.blit(shadow, shadow.get_rect(midbottom=(center_x + 2, bottom_y - 4)))
        screen.blit(label, name_rect)

    def draw_player(scene, game_state, username, layout, has_monster):
        player_max_w = 200 if has_monster else 260
        player_max_h = layout["scene_bottom"] - MARGIN - 36
        if player_max_h <= 80:
            return

        pose = get_player_pose(game_state, scene)
        sprite_file = PLAYER_SPRITES.get(pose, PLAYER_SPRITES["calm"])
        player = load_cached_image(
            f"player_sprite_{pose}",
            sprite_file,
            player_max_w,
            player_max_h,
        )
        if player is None:
            return
        player_rect = player.get_rect(midleft=(MARGIN + 8, layout["scene_bottom"]))
        player_rect.bottom = min(player_rect.bottom, layout["scene_bottom"])
        screen.blit(player, player_rect)
        draw_player_name(username, player_rect.centerx, player_rect.top)

    def draw_narrative(scene, username, panel, stype):
        accent = WIN_ACCENT if stype == "win" else DEATH_ACCENT if stype == "death" else PANEL_BORDER
        pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=8)
        pygame.draw.rect(screen, accent, panel, 2, border_radius=8)

        inner_w = panel.width - 2 * PANEL_PAD
        y = panel.top + PANEL_PAD
        max_y = panel.bottom - PANEL_PAD

        if is_end_scene(scene):
            end_title = get_horror_font(36, bold=True)
            title_text = scene.get("title", "Fin")
            title_color = WIN_ACCENT if stype == "win" else DEATH_ACCENT
            title_surf = end_title.render(title_text, True, title_color)
            if y + title_surf.get_height() <= max_y:
                screen.blit(title_surf, title_surf.get_rect(midtop=(panel.centerx, y)))
                y += title_surf.get_height() + 8
        else:
            speaker = scene.get("speaker", "narrateur")
            speaker_font = get_horror_font(20, bold=True, italic=True)
            speaker_surf = speaker_font.render(speaker, True, (180, 60, 65))
            if y + speaker_surf.get_height() <= max_y:
                screen.blit(speaker_surf, (panel.x + PANEL_PAD, y))
                y += speaker_surf.get_height() + 6

        body = format_narration(scene.get("text", ""), username)
        font_size = 22
        while font_size >= 16:
            narrative_font = get_horror_font(font_size)
            line_h = narrative_font.get_height() + 3
            lines = wrap_text(narrative_font, body, inner_w)
            needed = len(lines) * line_h
            if needed <= max_y - y or font_size == 16:
                break
            font_size -= 1

        narrative_font = get_horror_font(font_size)
        line_h = narrative_font.get_height() + 3
        for line in wrap_text(narrative_font, body, inner_w):
            if y + line_h > max_y:
                break
            line_surf = narrative_font.render(line, True, TEXT_COLOR)
            screen.blit(line_surf, (panel.x + PANEL_PAD, y))
            y += line_h

    def draw_end_buttons(layout, stype):
        btn_h = CHOICE_BTN_H
        gap = 12
        btn_x = MARGIN + 40
        btn_w = WIDTH - 2 * btn_x
        total_w = min(btn_w, 220) * 2 + gap
        start_x = WIDTH // 2 - total_w // 2
        btn_y = layout["choices_top"] + (layout["choices_h"] - btn_h) // 2
        restart_rect = pygame.Rect(start_x, btn_y, min(220, (total_w - gap) // 2), btn_h)
        menu_rect = pygame.Rect(restart_rect.right + gap, btn_y, restart_rect.width, btn_h)
        end_accent = (35, 55, 40) if stype == "win" else (70, 12, 18)
        end_hover = (50, 75, 55) if stype == "win" else (95, 18, 25)
        draw_button(restart_rect, "Recommencer", accent=end_accent, hover_accent=end_hover)
        draw_button(menu_rect, "Menu", accent=end_accent, hover_accent=end_hover)
        return [("restart", restart_rect), ("menu", menu_rect)]

    def draw_story_choices(layout, available):
        choice_rects = []
        btn_x = MARGIN + 40
        btn_w = WIDTH - 2 * btn_x
        y = layout["choices_top"]
        for i, choice in enumerate(available):
            rect = pygame.Rect(btn_x, y, btn_w, CHOICE_BTN_H)
            if rect.bottom > HEIGHT - 4:
                break
            btn_font = find_font_for_button(choice["text"], rect.width, rect.height)
            draw_button(rect, choice["text"], btn_font)
            choice_rects.append((i, rect))
            y += CHOICE_BTN_H + CHOICE_GAP

        if not available:
            hint_font = get_horror_font(18, italic=True)
            hint = hint_font.render("Aucun choix disponible…", True, (150, 100, 95))
            screen.blit(
                hint,
                hint.get_rect(center=(WIDTH // 2, layout["choices_top"] + 20)),
            )
        return choice_rects

    def handle_choice_clicks(choice_rects, story_data, game_state):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "home"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for tag, rect in choice_rects:
                    if not rect.collidepoint(event.pos):
                        continue
                    if tag == "restart":
                        reset_story()
                        ensure_story_loaded()
                        break
                    if tag == "menu":
                        reset_story()
                        return "home"
                    choose(story_data, game_state, tag)
                    break
        return None

    def draw_missing_scene_error():
        font = get_horror_font(32)
        err = font.render("Scène introuvable.", True, DEATH_ACCENT)
        screen.blit(err, err.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    ensure_story_loaded()
    story_data = state["story_data"]
    game_state = state["game_state"]
    username = state.get("username", "")

    bg_key = make_cache_key("play_bg")
    screen.blit(state[bg_key], (0, 0))

    scene = get_scene(story_data, game_state["scene_id"])
    if scene is None:
        draw_missing_scene_error()
        return "home"

    small_font = get_horror_font(18)
    stype = scene_type(scene)
    ending = is_end_scene(scene)
    available = [] if ending else get_available_choices(scene, game_state["variables"])
    choice_count = 2 if ending else len(available)

    layout = compute_layout(choice_count, ending)
    has_monster = bool(scene.get("monster"))

    if scene.get("show_player", True):
        draw_player(scene, game_state, username, layout, has_monster)

    if has_monster:
        draw_monster_panel(story_data, scene, layout["scene_bottom"], small_font)

    draw_narrative(scene, username, layout["panel"], stype)

    if ending:
        choice_rects = draw_end_buttons(layout, stype)
    else:
        choice_rects = draw_story_choices(layout, available)

    return handle_choice_clicks(choice_rects, story_data, game_state)
