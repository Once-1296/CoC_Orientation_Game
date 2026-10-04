import random

import pygame

from . import assets
from . import settings as S
from .physics import body_rect, move_body

T = S.TILE_SIZE
SIZE = 24                # collision box
WANDER_SPEED = 35
CHASE_SPEED = 70
SIGHT = 4 * T            # start chasing when the player is this close (px)
HURT_TIME = 0.4          # seconds of white flashing after a hit
KNOCK_DECAY = 600
KNOCK_HIT = 220          # knockback speed when the enemy takes damage


class Slime:
    MAX_HP = 3

    def __init__(self, tile):
        c, r = tile
        self.pos = pygame.Vector2((c + 0.5) * T, (r + 0.5) * T)
        self.hp = self.MAX_HP
        self.alive = True
        self.knock = pygame.Vector2()
        self.hurt_timer = 0.0
        self.wander_timer = 0.0
        self.wander_dir = pygame.Vector2()

    def rect(self):
        return body_rect(self.pos, SIZE)

    def hit(self, direction, damage=1):
        """Take `damage` points, pushed away along `direction`.

        Returns True if this hit killed the slime.
        """
        self.hp -= damage
        self.hurt_timer = HURT_TIME
        self.push(direction, KNOCK_HIT)
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def push(self, direction, strength):
        if direction.length_squared() > 0:
            self.knock = direction.normalize() * strength

    def update(self, dt, target, collides):
        self.hurt_timer = max(0.0, self.hurt_timer - dt)

        to_player = target - self.pos
        if to_player.length() < SIGHT and to_player.length() > 0:
            velocity = to_player.normalize() * CHASE_SPEED
        else:
            self.wander_timer -= dt
            if self.wander_timer <= 0:
                self.wander_timer = random.uniform(1.0, 2.5)
                self.wander_dir = random.choice([
                    pygame.Vector2(0, 0),
                    pygame.Vector2(1, 0),
                    pygame.Vector2(-1, 0),
                    pygame.Vector2(0, 1),
                    pygame.Vector2(0, -1),
                ])
            velocity = self.wander_dir * WANDER_SPEED

        self.knock = self.knock.move_towards(pygame.Vector2(), KNOCK_DECAY * dt)
        move_body(self.pos, (velocity + self.knock) * dt, SIZE, collides)

    def draw(self, surface, offset):
        # Blink while recently hit so the player can see the hit land.
        if self.hurt_timer > 0 and int(self.hurt_timer * 20) % 2 == 0:
            return
        img = assets.image("enemy_slime")
        x = round(self.pos.x) - T // 2 + offset[0]
        y = round(self.pos.y) - T // 2 + offset[1]
        surface.blit(img, (x, y))
