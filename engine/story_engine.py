import copy
import json
from pathlib import Path


STORY_PATH = Path(__file__).resolve().parent.parent / "datas" / "story.json"

PLAYER_POSES = ("calm", "tense")

TENSE_CHOICE_WORDS = (
    "courir",
    "foncer",
    "fuir",
    "affronter",
    "briser",
    "forcer",
    "poursuivre",
    "trappe",
    "placard",
    "miroir",
    "graver",
    "éteindre",
    "hésiter",
    "sans clé",
    "sans lumière",
    "sans lanterne",
)

CALM_CHOICE_WORDS = (
    "calmement",
    "discrètement",
    "prudemment",
    "lire",
    "prendre",
    "allumer",
    "retourner",
    "explorer",
    "accepter",
    "parler",
    "partir avant",
    "remonter avant",
    "utiliser la clé",
)


def load_story_data():
    with open(STORY_PATH, encoding="utf-8") as f:
        return json.load(f)


def new_game_state(story_data):
    return {
        "scene_id": story_data["start"],
        "variables": copy.deepcopy(story_data["variables"]),
        "player_pose": "calm",
    }


def infer_pose_from_choice(choice):
    def pose_from_choice_field():
        pose = choice.get("player_pose")
        if pose in PLAYER_POSES:
            return pose
        return None

    def pose_from_choice_text():
        text = choice.get("text", "").lower()
        for word in TENSE_CHOICE_WORDS:
            if word in text:
                return "tense"
        for word in CALM_CHOICE_WORDS:
            if word in text:
                return "calm"
        return None

    return pose_from_choice_field() or pose_from_choice_text()


def infer_pose_from_scene(scene):
    def pose_from_scene_field():
        pose = scene.get("player_pose")
        if pose in PLAYER_POSES:
            return pose
        return None

    def pose_from_scene_context():
        if scene.get("monster"):
            return "tense"
        scene_type_value = scene.get("type", "story")
        if scene_type_value == "death":
            return "tense"
        if scene_type_value == "win":
            return "calm"
        return None

    return pose_from_scene_field() or pose_from_scene_context()


def apply_choice_pose(choice, game_state):
    pose = infer_pose_from_choice(choice)
    if pose:
        game_state["player_pose"] = pose


def apply_scene_pose(scene, game_state):
    pose = infer_pose_from_scene(scene)
    if pose:
        game_state["player_pose"] = pose
    elif game_state["variables"].get("fear", 0) >= 2:
        game_state["player_pose"] = "tense"


def apply_player_pose(scene, game_state):
    apply_scene_pose(scene, game_state)


def get_player_pose(game_state, scene):
    return game_state.get("player_pose") or infer_pose_from_scene(scene) or "calm"


def get_scene(story_data, scene_id):
    return story_data["scenes"].get(scene_id)


def get_available_choices(scene, variables):
    def conditions_are_met(conditions):
        if not conditions:
            return True
        for key, expected in conditions.items():
            if variables.get(key) != expected:
                return False
        return True

    choices = scene.get("choices", [])
    return [
        choice
        for choice in choices
        if conditions_are_met(choice.get("conditions"))
    ]


def apply_scene_entry_effects(scene, variables):
    def apply_effects(effects):
        if not effects:
            return
        for key, value in effects.items():
            if isinstance(value, bool) or not isinstance(value, int):
                variables[key] = value
            else:
                variables[key] = variables.get(key, 0) + value

    apply_effects(scene.get("effects"))


def choose(story_data, game_state, choice_index):
    def apply_effects(effects):
        if not effects:
            return
        for key, value in effects.items():
            if isinstance(value, bool) or not isinstance(value, int):
                game_state["variables"][key] = value
            else:
                game_state["variables"][key] = game_state["variables"].get(key, 0) + value

    scene = get_scene(story_data, game_state["scene_id"])
    if scene is None:
        return False

    available = get_available_choices(scene, game_state["variables"])
    if choice_index < 0 or choice_index >= len(available):
        return False

    choice = available[choice_index]
    apply_effects(choice.get("effects"))
    apply_choice_pose(choice, game_state)

    next_id = choice["next"]
    next_scene = get_scene(story_data, next_id)
    if next_scene is None:
        return False

    game_state["scene_id"] = next_id
    apply_scene_entry_effects(next_scene, game_state["variables"])
    apply_scene_pose(next_scene, game_state)
    return True


def scene_type(scene):
    return scene.get("type", "story")


def is_end_scene(scene):
    return scene_type(scene) in ("death", "win")


def format_narration(text, username):
    if not username:
        return text
    return text.replace("{player}", username)
