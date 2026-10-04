import pygame

from . import assets
from . import settings as S
from .enemies import Slime
from .items import Pickup
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
    "R": "tile_roof",
}
SOLID = set("wrWtbSR")


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
        self.enemies = [Slime(tile) for tile in data.get("enemies", [])]
        # Items on the ground. Walking over them adds them to the player's state.
        self.pickups = [Pickup(kind, self.tile_centre(tile)) for kind, tile in data.get("pickups", [])]
        self.stalls = [
            pygame.Vector2((c + 0.5) * T, (r + 0.5) * T)
            for r, row in enumerate(self.grid)
            for c, ch in enumerate(row)
            if ch == "S"
        ]

        # Pre-render the tile grid once. Tiles never change at runtime.
        # Transparent tiles (bushes, trees, rocks) sit on a grass underlay so they don't show black.
        self.surface = pygame.Surface((self.width * T, self.height * T))
        underlay = assets.image("tile_grass")
        for r, row in enumerate(self.grid):
            for c, ch in enumerate(row):
                self.surface.blit(underlay, (c * T, r * T))
                self.surface.blit(assets.image(TILE_ASSETS[ch]), (c * T, r * T))

    @staticmethod
    def tile_centre(tile):
        c, r = tile
        return pygame.Vector2((c + 0.5) * T, (r + 0.5) * T)

    def _gap_outside(self, c, r):
        """True for the tile just outside an exit gap. Only the player may step onto it."""
        if r == -1:
            return "N" in self.links and c in (9, 10)
        if r == self.height:
            return "S" in self.links and c in (9, 10)
        if c == -1:
            return "W" in self.links and r in (6, 7)
        if c == self.width:
            return "E" in self.links and r in (6, 7)
        return False

    def is_solid(self, c, r, through_exits=True):
        """Whether a tile blocks movement. Anything outside the map is solid, except exit gaps.

        With through_exits=False the gaps are solid too, which is what enemies use so they stay inside.
        """
        if 0 <= r < self.height and 0 <= c < self.width:
            return self.grid[r][c] in SOLID
        return not (through_exits and self._gap_outside(c, r))

    def collides(self, rect, through_exits=True):
        c0, c1 = rect.left // T, (rect.right - 1) // T
        r0, r1 = rect.top // T, (rect.bottom - 1) // T
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if self.is_solid(c, r, through_exits):
                    return True
        return any(rect.colliderect(npc.rect) for npc in self.npcs)

    def render(self, screen, offset):
        screen.blit(self.surface, offset)
        for pickup in self.pickups:
            pickup.draw(screen, offset)
        for enemy in self.enemies:
            if enemy.alive:
                enemy.draw(screen, offset)
        for npc in self.npcs:
            npc.draw(screen, offset)
