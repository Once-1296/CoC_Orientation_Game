import glob
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
    "boat": (150, 100, 60),
}
NPC_COLOR = (200, 160, 60)
UNKNOWN_COLOR = (200, 0, 200)

_images = {}
_frame_cache = {}
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


def frames(folder, flip=False, size=None):
    """Return every PNG in images/<folder>, sorted by name, for animation.

    `folder` is relative to assets/images, for example "player/FrontWalk".
    """
    size = size or (S.TILE_SIZE, S.TILE_SIZE)
    key = (folder, flip, size)
    if key in _frame_cache:
        return _frame_cache[key]

    paths = sorted(glob.glob(os.path.join(IMAGE_DIR, folder, "*.png")))
    if not paths:
        _missing.add(folder)
        result = [_placeholder(folder.replace("/", "_"), size)]
    else:
        result = []
        for path in paths:
            surf = pygame.image.load(path).convert_alpha()
            if surf.get_size() != size:
                surf = pygame.transform.scale(surf, size)
            if flip:
                surf = pygame.transform.flip(surf, True, False)
            result.append(surf)

    _frame_cache[key] = result
    return result


def _placeholder(name, size):
    if name.startswith("npc"):
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


HEALTH_SHEET = os.path.join(IMAGE_DIR, "ui", "Heart_Health_Bar.png")
HEART_SCALE = 3
# Pixel positions of single hearts in the sheet: the first column of row 0 is full, row 5 is half, row 6 is empty.
HEART_CROPS = {2: (0, 0), 1: (0, 40), 0: (0, 48)}
_heart_cache = {}


def heart(value):
    """A single heart: 2 = full, 1 = half, 0 = empty (one value per half-heart)."""
    if value not in _heart_cache:
        size = (8 * HEART_SCALE, 8 * HEART_SCALE)
        if os.path.exists(HEALTH_SHEET):
            sheet = pygame.image.load(HEALTH_SHEET).convert_alpha()
            x, y = HEART_CROPS[value]
            img = sheet.subsurface(pygame.Rect(x, y, 8, 8)).copy()
            img = pygame.transform.scale(img, size)
        else:
            _missing.add("ui/Heart_Health_Bar")
            img = pygame.Surface(size)
            img.fill((220, 40, 50) if value else (70, 70, 80))
        _heart_cache[value] = img
    return _heart_cache[value]


_sound_cache = {}


def play(name, volume=1.0):
    """Play a sound effect by name. Does nothing if the file or audio device is missing."""
    if name not in _sound_cache:
        _sound_cache[name] = sound(name)
    snd = _sound_cache[name]
    if snd:
        snd.set_volume(volume)
        snd.play()


def play_music(name, volume=0.5):
    """Loop a music track by name. Streams from disk, so use it for long tracks."""
    for ext in (".ogg", ".wav", ".mp3"):
        path = os.path.join(SOUND_DIR, name + ext)
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass
            return
    _missing.add(name)


def report_missing():
    """Print the placeholders that were used. Only runs when DEBUG_ASSETS is set."""
    if S.DEBUG_ASSETS and _missing:
        print("Missing assets (placeholders in use):")
        for name in sorted(_missing):
            print(f"  - {name}")
