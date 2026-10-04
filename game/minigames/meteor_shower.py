import random

import pygame

from .. import assets
from .. import settings as S
from ..ui import draw_health
from .base import MiniGame


def _lerp(a, b, t):
    return a + (b - a) * t


class Rock:
    def __init__(self, x, size, speed):
        self.x = x
        self.y = -size           # starts just above the screen
        self.size = size
        self.speed = speed

    def rect(self):
        half = self.size / 2
        return pygame.Rect(round(self.x - half), round(self.y - half), self.size, self.size)


class MeteorShower(MiniGame):
    """Dodge falling rocks by moving left and right along the bottom of the screen."""

    name = "meteor_shower"
    title = "Meteor Shower"
    REWARD = 10
    PRESETS = {
        "easy": {"DURATION": 25.0, "LIVES": 4, "SPAWN_START": 1.2, "SPAWN_END": 0.6,
                 "FALL_START": 90, "FALL_END": 180, "ROCK_MAX_END": 34, "REWARD": 8},
        "hard": {"DURATION": 40.0, "LIVES": 2, "SPAWN_START": 0.7, "SPAWN_END": 0.25,
                 "FALL_START": 150, "FALL_END": 340, "ROCK_MAX_END": 52, "REWARD": 18},
    }

    # Tuning values. Change these to make the game easier or harder.
    DURATION = 30.0          # seconds to survive to win
    LIVES = 3
    PLAYER_SPEED = 260       # pixels per second, left and right only
    PLAYER_SIZE = 32
    PLAYER_HITBOX = 24       # the rock must overlap this smaller box, which is a little forgiving
    SPAWN_START = 0.9        # seconds between rocks at the start...
    SPAWN_END = 0.35         # ...and at the end. Smaller = more rocks.
    FALL_START = 120         # rock fall speed at the start, pixels per second
    FALL_END = 260           # rock fall speed at the end
    ROCK_MIN = 14            # smallest rock size, pixels
    ROCK_MAX_START = 20      # largest rock size at the start
    ROCK_MAX_END = 44        # largest rock size at the end
    INVULN = 1.0             # seconds of safety after being hit

    def __init__(self, difficulty="normal"):
        super().__init__(difficulty)
        self.elapsed = 0.0
        self.lives = self.LIVES
        self.dodged = 0
        self.player_x = S.SCREEN_W / 2
        self.player_y = S.SCREEN_H - 48
        self.rocks = []
        self.spawn_timer = 0.5
        self.invuln = 0.0

    @property
    def progress(self):
        return min(1.0, self.elapsed / self.DURATION)

    def update(self, dt, keys):
        if self.finished:
            return
        self.elapsed += dt
        self.invuln = max(0.0, self.invuln - dt)

        direction = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        half = self.PLAYER_SIZE / 2
        self.player_x = min(max(self.player_x + direction * self.PLAYER_SPEED * dt, half), S.SCREEN_W - half)

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self._spawn()
            self.spawn_timer = _lerp(self.SPAWN_START, self.SPAWN_END, self.progress) * random.uniform(0.7, 1.3)

        player = self._player_rect()
        for rock in self.rocks[:]:
            rock.y += rock.speed * dt
            if self.invuln <= 0 and rock.rect().colliderect(player):
                self.rocks.remove(rock)
                self.lives -= 1
                self.invuln = self.INVULN
                if self.lives <= 0:
                    self.result = "lost"
                    return
            elif rock.y - rock.size / 2 > S.SCREEN_H:
                self.rocks.remove(rock)
                self.dodged += 1

        if self.elapsed >= self.DURATION:
            self.result = "won"

    def _spawn(self):
        max_size = int(_lerp(self.ROCK_MAX_START, self.ROCK_MAX_END, self.progress))
        size = random.randint(self.ROCK_MIN, max_size)
        speed = _lerp(self.FALL_START, self.FALL_END, self.progress) * random.uniform(0.8, 1.2)
        x = random.uniform(size / 2, S.SCREEN_W - size / 2)
        self.rocks.append(Rock(x, size, speed))

    def _player_rect(self):
        half = self.PLAYER_HITBOX / 2
        return pygame.Rect(round(self.player_x - half), round(self.player_y - half),
                           self.PLAYER_HITBOX, self.PLAYER_HITBOX)

    def draw(self, surface):
        surface.fill((28, 34, 52))
        pygame.draw.rect(surface, (60, 58, 70), (0, S.SCREEN_H - 24, S.SCREEN_W, 24))

        for rock in self.rocks:
            surface.blit(assets.image("item_rock", (rock.size, rock.size)), rock.rect())

        frame = assets.frames("player/FrontWalk")[0]
        surface.blit(frame, (round(self.player_x) - self.PLAYER_SIZE // 2,
                             round(self.player_y) - self.PLAYER_SIZE // 2))

        font = pygame.font.Font(None, 26)
        time_left = max(0.0, self.DURATION - self.elapsed)
        surface.blit(font.render(f"Time: {time_left:4.1f}s", True, S.TEXT_COLOR), (10, 10))
        surface.blit(font.render(f"Dodged: {self.dodged}", True, S.TEXT_COLOR), (10, 34))
        draw_health(surface, self.lives * 2, self.LIVES * 2, S.SCREEN_W, 10)   # 2 half-hearts per life

        hint = pygame.font.Font(None, 22).render(
            f"{self.title}   Left/Right or A/D to move   Esc to leave", True, (160, 160, 170))
        surface.blit(hint, hint.get_rect(midbottom=(S.SCREEN_W // 2, S.SCREEN_H - 6)))
