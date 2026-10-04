import pygame

from . import assets
from . import settings as S
from .npc import NPC

T = S.TILE_SIZE

TILE_ASSETS = {
    "g": "tile_grass",
    "p": "tile_path",
    "w": "tile_water",
    "r": "tile_rock",
    "s": "tile_snow",
    "f": "tile_wood_floor",
    "W": "tile_wall",
    "t": "tile_tree",
    "b": "tile_bush",
    "a": "tile_sand",
    "D": "tile_door",
    "S": "shop_stall",
}
SOLID = set("wrWtbS")


class Map:
    def __init__(self, name, data):
        self.name = name
        self.grid = data["grid"]
        self.height = len(self.grid)
        self.width = len(self.grid[0])

        for row in self.grid:
            if len(row) != self.width:
                raise ValueError(f"map '{name}': rows have different lengths")
            for ch in row:
                if ch not in TILE_ASSETS:
                    raise ValueError(f"map '{name}': unknown tile '{ch}'")

        self.links = data.get("links", {})      # edge side -> neighbour map name
        self.doors = data.get("doors", {})      # (col, row) -> (map name, spawn tile)
        self.npcs = [NPC(d) for d in data.get("npcs", [])]
        self.stalls = [
            pygame.Vector2((c + 0.5) * T, (r + 0.5) * T)
            for r, row in enumerate(self.grid)
            for c, ch in enumerate(row)
            if ch == "S"
        ]

        # Pre-render the tile grid once. Tiles never change at runtime.
        self.surface = pygame.Surface((self.width * T, self.height * T))
        for r, row in enumerate(self.grid):
            for c, ch in enumerate(row):
                self.surface.blit(assets.image(TILE_ASSETS[ch]), (c * T, r * T))

    def is_solid(self, c, r):
        # Tiles outside the map are not solid. Exits are checked in the game loop.
        if 0 <= r < self.height and 0 <= c < self.width:
            return self.grid[r][c] in SOLID
        return False

    def collides(self, rect):
        c0, c1 = rect.left // T, (rect.right - 1) // T
        r0, r1 = rect.top // T, (rect.bottom - 1) // T
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if self.is_solid(c, r):
                    return True
        return any(rect.colliderect(npc.rect) for npc in self.npcs)

    def render(self, screen, offset):
        screen.blit(self.surface, offset)
        for npc in self.npcs:
            npc.draw(screen, offset)
