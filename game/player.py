import pygame

from . import assets
from . import settings as S
from .physics import body_rect, move_body

T = S.TILE_SIZE
ANIM_FPS = 8
KNOCK_DECAY = 600   # pixels per second^2 that knockback slows down by

SPRITE_FOLDERS = {
    "down": ("player/FrontWalk", False),
    "up": ("player/BackWalk", False),
    # The SideWalk frames face right, so the left-facing frames are flipped.
    "left": ("player/SideWalk", True),
    "right": ("player/SideWalk", False),
}

FACING_VECTORS = {
    "up": pygame.Vector2(0, -1),
    "down": pygame.Vector2(0, 1),
    "left": pygame.Vector2(-1, 0),
    "right": pygame.Vector2(1, 0),
}


class Player:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)   # centre, in map pixels
        self.facing = "down"
        self.moving = False
        self.anim_time = 0.0
        self.knock = pygame.Vector2()    # extra velocity from being hit, decays over time

    def hitbox(self):
        return body_rect(self.pos, S.PLAYER_HITBOX)

    def move(self, dx, dy, dt, collides, speed_scale=1.0):
        direction = pygame.Vector2(dx, dy)
        self.moving = direction.length_squared() > 0
        if self.moving:
            if abs(dx) >= abs(dy):
                self.facing = "right" if dx > 0 else "left"
            else:
                self.facing = "down" if dy > 0 else "up"
            direction = direction.normalize()
            self.anim_time += dt

        velocity = direction * S.PLAYER_SPEED * speed_scale + self.knock
        self.knock = self.knock.move_towards(pygame.Vector2(), KNOCK_DECAY * dt)
        move_body(self.pos, velocity * dt, S.PLAYER_HITBOX, collides)

    def clamp(self, width, height):
        half = S.PLAYER_HITBOX / 2
        self.pos.x = min(max(self.pos.x, half), width - half)
        self.pos.y = min(max(self.pos.y, half), height - half)

    def draw(self, surface, offset):
        folder, flip = SPRITE_FOLDERS[self.facing]
        frames = assets.frames(folder, flip=flip)
        index = int(self.anim_time * ANIM_FPS) % len(frames) if self.moving else 0
        x = round(self.pos.x) - T // 2 + offset[0]
        y = round(self.pos.y) - T // 2 + offset[1]
        surface.blit(frames[index], (x, y))
