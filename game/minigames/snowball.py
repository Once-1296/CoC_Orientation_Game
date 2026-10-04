import random

import pygame

from .. import assets
from .. import settings as S
from ..effects import FloatText, tick
from .base import MiniGame


def _lerp(a, b, t):
    return a + (b - a) * t


class Thing:
    """A snow pile (grows the snowball) or a rock (shrinks it), falling down a lane."""

    RADIUS = {"snow": 10, "rock": 14}

    def __init__(self, kind, x, y, speed):
        self.kind = kind
        self.x = x
        self.y = y
        self.speed = speed

    @property
    def radius(self):
        return self.RADIUS[self.kind]


class Snowball(MiniGame):
    """Roll down three lanes. Pick up snow to grow, and dodge rocks that shrink you."""

    name = "snowball"
    title = "Snowball Fight"
    REWARD = 12
    PRESETS = {
        "easy": {"DURATION": 35.0, "TARGET": 8.0, "SPAWN_START": 0.9, "SPAWN_END": 0.5,
                 "FALL_START": 130, "FALL_END": 220, "SNOW_CHANCE": 0.7, "REWARD": 8},
        "hard": {"DURATION": 25.0, "TARGET": 13.0, "SPAWN_START": 0.5, "SPAWN_END": 0.18,
                 "FALL_START": 220, "FALL_END": 380, "SNOW_CHANCE": 0.5, "SHRINK": 1.5, "REWARD": 18},
    }

    # Tuning values. Change these to make the game easier or harder.
    LANES = 3
    DURATION = 30.0          # seconds of rolling
    TARGET = 10.0            # snowball size needed to win (the size at the end is the score)
    START_SIZE = 3.0
    GROW = 0.5               # size gained per snow pile
    SHRINK = 1.0             # size lost per rock
    LANE_SPEED = 700         # pixels per second when switching lanes
    MOVE_SPEED = 220         # pixels per second up and down
    SPAWN_START = 0.7        # seconds between falling things at the start...
    SPAWN_END = 0.3          # ...and at the end. Smaller = more things.
    FALL_START = 170         # fall speed at the start, pixels per second
    FALL_END = 300           # fall speed at the end
    SNOW_CHANCE = 0.6        # share of falling things that are snow rather than rocks

    def __init__(self, difficulty="normal"):
        super().__init__(difficulty)
        self.popups = []
        self.elapsed = 0.0
        self.size = self.START_SIZE
        self.lane = 1
        self.x = self._lane_x(self.lane)
        self.y = S.SCREEN_H - 90
        self.things = []
        self.spawn_timer = 0.5

    def _lane_x(self, lane):
        return S.SCREEN_W * (lane + 1) / (self.LANES + 1)

    @property
    def progress(self):
        return min(1.0, self.elapsed / self.DURATION)

    @property
    def radius(self):
        return 6 + self.size * 2.5

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN or self.finished:
            return
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.lane = max(0, self.lane - 1)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.lane = min(self.LANES - 1, self.lane + 1)

    def update(self, dt, keys):
        if self.finished:
            return
        self.elapsed += dt

        # Slide sideways towards the chosen lane, and move up and down with the keys.
        target_x = self._lane_x(self.lane)
        step = self.LANE_SPEED * dt
        self.x += max(-step, min(step, target_x - self.x))

        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        self.y = min(max(self.y + dy * self.MOVE_SPEED * dt, S.SCREEN_H * 0.45), S.SCREEN_H - 60)

        self.popups = tick(self.popups, dt)
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self._spawn()
            self.spawn_timer = _lerp(self.SPAWN_START, self.SPAWN_END, self.progress) * random.uniform(0.7, 1.3)

        for thing in self.things[:]:
            thing.y += thing.speed * dt
            if thing.y - thing.radius > S.SCREEN_H:
                self.things.remove(thing)
                continue
            if self._touching(thing):
                self.things.remove(thing)
                if thing.kind == "snow":
                    self.size += self.GROW
                    self.popups.append(FloatText(f"+{self.GROW:g} size", (thing.x, thing.y), (255, 255, 255)))
                else:
                    self.size = max(1.0, self.size - self.SHRINK)
                    self.popups.append(FloatText(f"-{self.SHRINK:g} size", (thing.x, thing.y), (230, 90, 90)))

        if self.elapsed >= self.DURATION:
            self.result = "won" if self.size >= self.TARGET else "lost"

    def _spawn(self):
        kind = "snow" if random.random() < self.SNOW_CHANCE else "rock"
        lane = random.randrange(self.LANES)
        speed = _lerp(self.FALL_START, self.FALL_END, self.progress) * random.uniform(0.9, 1.1)
        self.things.append(Thing(kind, self._lane_x(lane), -20, speed))

    def _touching(self, thing):
        distance = pygame.Vector2(thing.x - self.x, thing.y - self.y).length()
        return distance < self.radius + thing.radius * 0.8

    def draw(self, surface):
        surface.fill((222, 234, 246))
        for lane in range(1, self.LANES):           # dashed lane dividers
            x = round(S.SCREEN_W * lane / self.LANES)
            for y in range(0, S.SCREEN_H, 40):
                pygame.draw.line(surface, (190, 210, 230), (x, y), (x, y + 20), 2)

        rock = assets.image("item_rock", (28, 28))
        for thing in self.things:
            centre = (round(thing.x), round(thing.y))
            if thing.kind == "snow":
                pygame.draw.circle(surface, (255, 255, 255), centre, 9)
                pygame.draw.circle(surface, (40, 90, 160), centre, 9, 2)
            else:
                surface.blit(rock, rock.get_rect(center=centre))
        for popup in self.popups:
            popup.draw(surface)

        centre = (round(self.x), round(self.y))
        radius = round(self.radius)
        pygame.draw.circle(surface, (255, 255, 255), centre, radius)
        pygame.draw.circle(surface, (60, 70, 90), centre, radius, 3)

        font = pygame.font.Font(None, 26)
        time_left = max(0.0, self.DURATION - self.elapsed)
        surface.blit(font.render(f"Time: {time_left:4.1f}s", True, (30, 40, 60)), (10, 10))
        surface.blit(font.render(f"Size: {self.size:4.1f} / {self.TARGET:g}", True, (30, 40, 60)), (10, 34))
        hint = pygame.font.Font(None, 22).render(
            f"{self.title}   Left/Right lanes, Up/Down move, Esc to leave", True, (60, 80, 100))
        surface.blit(hint, hint.get_rect(midbottom=(S.SCREEN_W // 2, S.SCREEN_H - 6)))
