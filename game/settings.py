import os

TITLE = "CoC Orientation Game"
TILE_SIZE = 32
SCREEN_W = 640
SCREEN_H = 480
FPS = 60

PLAYER_SPEED = 150       # pixels per second
PLAYER_HITBOX = 24       # collision box inside a tile
INTERACT_RANGE = 1.5     # tiles from player centre

BG_COLOR = (20, 20, 28)
TEXT_COLOR = (240, 240, 240)

DEBUG_ASSETS = bool(os.environ.get("DEBUG_ASSETS"))
