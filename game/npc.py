import pygame

from . import assets
from . import settings as S

T = S.TILE_SIZE


class NPC:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.lines = data["lines"]
        c, r = data["tile"]
        self.rect = pygame.Rect(c * T, r * T, T, T)

    @property
    def centre(self):
        return pygame.Vector2(self.rect.center)

    def draw(self, surface, offset):
        img = assets.image(f"npc_{self.id}")
        surface.blit(img, (self.rect.x + offset[0], self.rect.y + offset[1]))
