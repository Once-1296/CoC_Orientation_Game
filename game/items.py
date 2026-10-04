import pygame

from . import assets

PICKUP_SIZE = 20
PICKUP_ASSETS = {"coin": "item_coin", "rock": "item_rock", "fish": "item_fish", "snow": "tile_snow"}


class Pickup:
    """An item lying on the map. Walking over it adds it to the matching count in game state."""

    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pygame.Vector2(pos)

    def draw(self, surface, offset):
        centre = (round(self.pos.x) + offset[0], round(self.pos.y) + offset[1])
        if self.kind == "snow":
            pygame.draw.circle(surface, (255, 255, 255), centre, 9)
            pygame.draw.circle(surface, (40, 90, 160), centre, 9, 2)
            return
        img = assets.image(PICKUP_ASSETS[self.kind], (PICKUP_SIZE, PICKUP_SIZE))
        surface.blit(img, img.get_rect(center=centre))
