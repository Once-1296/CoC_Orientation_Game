import os

import pygame

from . import settings as S

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
IMAGE_DIR = os.path.join(ROOT, "images")
SOUND_DIR = os.path.join(ROOT, "sounds")

# Colours used when a real image is missing. Unknown names fall back to magenta.
PLACEHOLDER_COLORS = {
    "tile_grass": (86, 140, 70),
    "tile_path": (170, 140, 95),
    "tile_water": (50, 100, 170),
    "tile_rock": (120, 115, 110),
    "tile_snow": (235, 240, 245),
    "tile_wood_floor": (150, 105, 65),
    "tile_wall": (90, 70, 60),
    "tile_tree": (30, 80, 40),
    "tile_bush": (50, 110, 50),
    "tile_sand": (220, 200, 140),
    "tile_door": (110, 70, 30),
    "shop_stall": (200, 90, 60),
    "house": (140, 90, 70),
    "player_up": (60, 120, 220),
    "player_down": (60, 120, 220),
    "player_left": (60, 120, 220),
    "player_right": (60, 120, 220),
    "dialogue_box": (20, 20, 30),
    "icon_coin": (230, 190, 40),
}
NPC_COLOR = (200, 160, 60)
UNKNOWN_COLOR = (200, 0, 200)

_images = {}
_missing = set()
_fonts = {}


def _font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(None, size)
    return _fonts[size]


def image(name, size=None):
    """Return the image for `name`, scaled to `size`. Falls back to a placeholder."""
    size = size or (S.TILE_SIZE, S.TILE_SIZE)
    key = (name, size)
    if key in _images:
        return _images[key]

    path = os.path.join(IMAGE_DIR, name + ".png")
    if os.path.exists(path):
        surf = pygame.image.load(path).convert_alpha()
        if surf.get_size() != size:
            surf = pygame.transform.scale(surf, size)
    else:
        _missing.add(name)
        surf = _placeholder(name, size)

    _images[key] = surf
    return surf


def _placeholder(name, size):
    if name.startswith("npc_"):
        color = NPC_COLOR
    else:
        color = PLACEHOLDER_COLORS.get(name, UNKNOWN_COLOR)

    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(color)
    pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 1)
    if size[0] >= 40:
        label = _font(16).render(name, True, (0, 0, 0))
        surf.blit(label, label.get_rect(center=(size[0] // 2, size[1] // 2)))
    return surf


def sound(name):
    """Return a Sound for `name`, or None when the file or mixer is unavailable."""
    path = None
    for ext in (".wav", ".ogg"):
        candidate = os.path.join(SOUND_DIR, name + ext)
        if os.path.exists(candidate):
            path = candidate
            break
    if path is None:
        _missing.add(name)
        return None
    try:
        return pygame.mixer.Sound(path)
    except pygame.error:
        return None


def report_missing():
    """Print the placeholders that were used. Only runs when DEBUG_ASSETS is set."""
    if S.DEBUG_ASSETS and _missing:
        print("Missing assets (placeholders in use):")
        for name in sorted(_missing):
            print(f"  - {name}")
