import pygame

from . import assets
from . import settings as S

T = S.TILE_SIZE


class Player:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)   # centre, in map pixels
        self.facing = "down"

    def hitbox(self):
        box = pygame.Rect(0, 0, S.PLAYER_HITBOX, S.PLAYER_HITBOX)
        box.center = (round(self.pos.x), round(self.pos.y))
        return box

    def move(self, dx, dy, dt, collides):
        """Move with axis-separated collision so the player slides along walls."""
        direction = pygame.Vector2(dx, dy)
        if direction.length_squared() == 0:
            return
        if abs(dx) >= abs(dy):
            self.facing = "right" if dx > 0 else "left"
        else:
            self.facing = "down" if dy > 0 else "up"

        step = direction.normalize() * S.PLAYER_SPEED * dt

        self.pos.x += step.x
        if collides(self.hitbox()):
            self.pos.x -= step.x

        self.pos.y += step.y
        if collides(self.hitbox()):
            self.pos.y -= step.y

    def clamp(self, width, height):
        half = S.PLAYER_HITBOX / 2
        self.pos.x = min(max(self.pos.x, half), width - half)
        self.pos.y = min(max(self.pos.y, half), height - half)

    def draw(self, surface, offset):
        img = assets.image(f"player_{self.facing}")
        x = round(self.pos.x) - T // 2 + offset[0]
        y = round(self.pos.y) - T // 2 + offset[1]
        surface.blit(img, (x, y))
