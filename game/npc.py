import pygame

from . import assets
from . import settings as S

T = S.TILE_SIZE


class NPC:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.lines = data["lines"]
        self.sprite = data["sprite"]     # "npc1" (female) or "npc2" (male)
        self.task = data.get("task")     # optional quest, see maps.py
        self.shop = data.get("shop", False)   # opens the shop instead of normal dialogue
        c, r = data["tile"]
        self.rect = pygame.Rect(c * T, r * T, T, T)

    @property
    def centre(self):
        return pygame.Vector2(self.rect.center)

    def draw(self, surface, offset):
        # NPCs stand still, so they show the first front-facing frame.
        img = assets.frames(f"{self.sprite}/FrontWalk")[0]
        surface.blit(img, (self.rect.x + offset[0], self.rect.y + offset[1]))
