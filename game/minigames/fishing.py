import random

import pygame

from .. import assets
from .. import settings as S
from ..effects import FloatText, tick
from .base import MiniGame

DIRECTIONS = {
    "up": pygame.Vector2(0, -1),
    "down": pygame.Vector2(0, 1),
    "left": pygame.Vector2(-1, 0),
    "right": pygame.Vector2(1, 0),
}
DIRECTION_KEYS = {
    pygame.K_UP: "up", pygame.K_w: "up",
    pygame.K_DOWN: "down", pygame.K_s: "down",
    pygame.K_LEFT: "left", pygame.K_a: "left",
    pygame.K_RIGHT: "right", pygame.K_d: "right",
}
# points, spawn weight, sprite size, how fast it runs (progress lost per second),
# and how often it changes the way it pulls (seconds)
FISH_SIZES = {
    "small": {"points": 1, "weight": 3, "sprite": 16, "drag": 4.0, "pull": 1.4},
    "medium": {"points": 2, "weight": 4, "sprite": 22, "drag": 6.0, "pull": 1.1},
    "big": {"points": 3, "weight": 3, "sprite": 28, "drag": 9.0, "pull": 0.9},
}
SWIM_SPEED = 35


class Swimmer:
    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pygame.Vector2(pos)
        self.heading = pygame.Vector2(1, 0)
        self.turn_timer = 0.0
        self.hooked = False

    def wander(self, dt, bounds):
        self.turn_timer -= dt
        if self.turn_timer <= 0:
            self.turn_timer = random.uniform(1.0, 3.0)
            self.heading = pygame.Vector2(1, 0).rotate(random.uniform(0, 360))
        self.pos += self.heading * SWIM_SPEED * dt
        if not bounds.collidepoint(self.pos):
            self.heading = -self.heading
            self.pos.x = min(max(self.pos.x, bounds.left), bounds.right)
            self.pos.y = min(max(self.pos.y, bounds.top), bounds.bottom)


class Fishing(MiniGame):
    """Cast, wait for a fish to swim up to the bobber, set the hook, then reel it in.

    While hooked, the fish pulls in a direction shown by the yellow arrow. Hold Shift and press
    that arrow to keep the line tight. Press Space again and again to reel in. Slack line snaps.
    """

    name = "fishing"
    title = "Fishing Mania"
    REWARD = 12
    PRESETS = {
        "easy": {"DURATION": 75.0, "TARGET": 10, "TENSION_MISS": 8, "DRAG_MULT": 0.7, "REWARD": 8},
        "hard": {"DURATION": 50.0, "TARGET": 16, "TENSION_MISS": 18, "DRAG_MULT": 1.4, "REWARD": 18},
    }

    # Tuning values. Change these to make the game easier or harder.
    DURATION = 60.0          # seconds to fish
    TARGET = 12              # points needed to win
    BOAT_SPEED = 150         # pixels per second
    CAST_DISTANCE = 130      # how far the line is thrown in front of the boat
    FISH_COUNT = 6           # fish in the lake at once
    ATTRACT_RADIUS = 130     # fish this close to the bobber drift towards it and can bite
    IDLE_LIMIT = 8.0         # seconds with no fish nearby before the line is reeled in
    BITE_DELAY = (1.0, 2.5)  # seconds a nearby fish takes to bite
    HOOK_WINDOW = 0.9        # seconds to set the hook after a bite
    TENSION_START = 60
    TENSION_MAX = 100
    TENSION_GOOD = 10        # gained for Shift + the right arrow
    TENSION_BAD = 12         # lost for Shift + the wrong arrow
    TENSION_MISS = 12        # lost when the pull changes and no correct arrow was pressed
    REEL_STEP = 7            # progress gained per Space press
    DRAG_MULT = 1.0          # multiplies how fast fish run
    WATER = pygame.Rect(40, 70, 560, 360)

    def __init__(self, difficulty="normal"):
        super().__init__(difficulty)
        self.elapsed = 0.0
        self.score = 0
        self.catches = 0
        self.boat = pygame.Vector2(self.WATER.centerx, self.WATER.bottom - 60)
        self.facing = pygame.Vector2(0, -1)
        self.swimmers = [self._new_swimmer() for _ in range(self.FISH_COUNT)]
        self.line = None         # {"pos", "state": "waiting" | "bite" | "fight", "timer", "fish"}
        self.fight = None        # {"progress", "tension", "pull", "pull_timer", "good", ...} while hooked
        self.popups = []
        self.message = ""
        self.message_timer = 0.0

    # Helpers

    def _new_swimmer(self):
        names, weights = zip(*[(name, info["weight"]) for name, info in FISH_SIZES.items()])
        kind = random.choices(names, weights=weights)[0]
        inner = self.WATER.inflate(-60, -60)
        pos = (random.uniform(inner.left, inner.right), random.uniform(inner.top, inner.bottom))
        return Swimmer(kind, pos)

    def _clamp_to_water(self, pos):
        inner = self.WATER.inflate(-30, -30)
        return pygame.Vector2(min(max(pos.x, inner.left), inner.right),
                              min(max(pos.y, inner.top), inner.bottom))

    def _say(self, text):
        self.message = text
        self.message_timer = 2.5

    # Input

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN or self.finished:
            return

        if event.key == pygame.K_f and self.score >= self.TARGET:
            self.result = "won"     # enough fish already: skip the rest of the timer
            return

        if self.fight:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.fight["progress"] = min(100.0, self.fight["progress"] + self.REEL_STEP)
                if self.fight["progress"] >= 100:
                    self._catch()
            elif event.key in DIRECTION_KEYS and event.mod & pygame.KMOD_SHIFT:
                self._steer(DIRECTION_KEYS[event.key])
            return

        if event.key not in (pygame.K_SPACE, pygame.K_RETURN):
            return
        if self.line is None:
            self.line = {
                "pos": self._clamp_to_water(self.boat + self.facing * self.CAST_DISTANCE),
                "state": "waiting",
                "timer": None,
                "fish": None,
            }
        elif self.line["state"] == "bite":
            self._hook()
        else:
            self.line = None     # reel in early, nothing caught

    def _steer(self, direction):
        fight = self.fight
        if direction == fight["pull"]:
            fight["tension"] = min(self.TENSION_MAX, fight["tension"] + self.TENSION_GOOD)
            fight["good"] = True
        else:
            fight["tension"] -= self.TENSION_BAD

    # Fishing steps

    def _hook(self):
        fish = self.line["fish"]
        fish.hooked = True
        info = FISH_SIZES[fish.kind]
        self.fight = {
            "progress": 35.0,
            "tension": float(self.TENSION_START),
            "pull": random.choice(list(DIRECTIONS)),
            "pull_timer": info["pull"],
            "pull_interval": info["pull"],
            "drag": info["drag"] * self.DRAG_MULT,
            "good": False,
        }
        self.line["state"] = "fight"
        self.line["fish"] = fish
        self._say("Hooked! Shift + arrow to keep the line tight, Space to reel!")

    def _update_line(self, dt):
        line = self.line
        if line["state"] == "waiting":
            near = [s for s in self.swimmers if s.pos.distance_to(line["pos"]) <= self.ATTRACT_RADIUS]
            for fish in near:
                fish.pos = fish.pos.move_towards(line["pos"], 40 * dt)
            line["idle"] = 0.0 if near else line.get("idle", 0.0) + dt
            if line["idle"] > self.IDLE_LIMIT:
                self.line = None
                self._say("No fish around here. Try another spot.")
                return
            if near:
                if line["timer"] is None:
                    line["timer"] = random.uniform(*self.BITE_DELAY)
                line["timer"] -= dt
                if line["timer"] <= 0:
                    line["state"] = "bite"
                    line["fish"] = min(near, key=lambda s: s.pos.distance_to(line["pos"]))
                    line["timer"] = self.HOOK_WINDOW
            else:
                line["timer"] = None
        elif line["state"] == "bite":
            line["timer"] -= dt
            if line["timer"] <= 0:
                self.line = None
                self._say("Nothing took the bait this time.")

    def _update_fight(self, dt):
        fight = self.fight
        fight["pull_timer"] -= dt
        if fight["pull_timer"] <= 0:
            if not fight["good"]:
                fight["tension"] -= self.TENSION_MISS
            fight["pull"] = random.choice([d for d in DIRECTIONS if d != fight["pull"]])
            fight["pull_timer"] = fight["pull_interval"]
            fight["good"] = False

        fight["progress"] = max(0.0, fight["progress"] - fight["drag"] * dt)
        fish = self.line["fish"]
        fish.pos = self.line["pos"].lerp(self.boat, fight["progress"] / 100)

        if fight["tension"] <= 0:
            self._lose_fish("The line snapped!")

    def _lose_fish(self, text):
        self.line["fish"].hooked = False
        self.line = None
        self.fight = None
        self._say(text)

    def _catch(self):
        fish = self.line["fish"]
        points = FISH_SIZES[fish.kind]["points"]
        self.swimmers.remove(fish)
        self.swimmers.append(self._new_swimmer())
        self.score += points
        self.catches += 1
        self.popups.append(FloatText(f"+{points} {fish.kind} fish", self.boat + (0, -30), (255, 230, 120)))
        assets.play("sfx_pickup")
        self.line = None
        self.fight = None
        self._say(f"Caught a {fish.kind} fish!")

    # Main update

    def update(self, dt, keys):
        if self.finished:
            return
        self.elapsed += dt
        self.message_timer = max(0.0, self.message_timer - dt)
        self.popups = tick(self.popups, dt)

        bounds = self.WATER.inflate(-40, -40)
        for fish in self.swimmers:
            if not fish.hooked:
                fish.wander(dt, bounds)

        if self.fight:
            self._update_fight(dt)
        else:
            dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
            dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
            move = pygame.Vector2(dx, dy)
            if move.length_squared() > 0:
                self.facing = move.normalize()
                self.boat = self._clamp_to_water(self.boat + move.normalize() * self.BOAT_SPEED * dt)
            if self.line:
                self._update_line(dt)

        if self.elapsed >= self.DURATION:
            self.result = "won" if self.score >= self.TARGET else "lost"

    # Drawing

    def _draw_arrow(self, surface, direction, origin):
        tip = origin + direction * 34
        side = pygame.Vector2(-direction.y, direction.x) * 10
        base = origin + direction * 10
        pygame.draw.polygon(surface, (255, 220, 60), [tip, base + side, base - side])

    def draw(self, surface):
        surface.fill((30, 60, 40))
        pygame.draw.rect(surface, (210, 190, 130), self.WATER.inflate(10, 10), border_radius=12)
        pygame.draw.rect(surface, (40, 100, 170), self.WATER, border_radius=8)
        for y in range(self.WATER.top + 40, self.WATER.bottom, 60):
            for x in range(self.WATER.left + 30, self.WATER.right, 110):
                pygame.draw.line(surface, (70, 130, 200), (x, y), (x + 24, y), 2)

        for fish in self.swimmers:
            if fish.hooked:
                continue
            self._draw_fish(surface, fish)

        boat = assets.image("boat", (40, 22))
        surface.blit(boat, boat.get_rect(center=(round(self.boat.x), round(self.boat.y))))

        if self.line:
            if self.line["state"] == "fight":
                fish = self.line["fish"]
                pygame.draw.line(surface, (230, 230, 230), self.boat, fish.pos, 1)
                self._draw_fish(surface, fish)
                self._draw_arrow(surface, DIRECTIONS[self.fight["pull"]], self.boat)
            else:
                bobber = self.line["pos"]
                pygame.draw.line(surface, (230, 230, 230), self.boat, bobber, 1)
                bite = self.line["state"] == "bite"
                bob = 4 if bite and int(self.line["timer"] * 10) % 2 else 0
                pygame.draw.circle(surface, (230, 60, 60), (round(bobber.x), round(bobber.y) + bob), 5)
                pygame.draw.circle(surface, (255, 255, 255), (round(bobber.x), round(bobber.y) + bob), 5, 1)
                if bite:
                    alert = pygame.font.Font(None, 36).render("!", True, (255, 220, 60))
                    surface.blit(alert, alert.get_rect(center=(round(bobber.x), round(bobber.y) - 18)))

        if self.fight:
            self._draw_fight_bars(surface)

        font = pygame.font.Font(None, 26)
        time_left = max(0.0, self.DURATION - self.elapsed)
        surface.blit(font.render(f"Time: {time_left:4.1f}s", True, S.TEXT_COLOR), (10, 10))
        surface.blit(font.render(f"Score: {self.score} / {self.TARGET}", True, S.TEXT_COLOR), (10, 34))
        if self.message_timer > 0:
            text = font.render(self.message, True, S.TEXT_COLOR)
            surface.blit(text, text.get_rect(midbottom=(S.SCREEN_W // 2, S.SCREEN_H - 32)))
        for popup in self.popups:
            popup.draw(surface)

        if self.score >= self.TARGET:
            done = font.render("Enough fish! Press F to finish now", True, (255, 220, 60))
            surface.blit(done, done.get_rect(topright=(S.SCREEN_W - 12, 10)))

        if self.fight:
            hint = "Shift + arrow matches the yellow arrow.   Space (spam) reels in.   Esc leaves"
        else:
            hint = "Arrows/WASD move, Space casts or sets the hook, Esc to leave"
        surface.blit(pygame.font.Font(None, 22).render(hint, True, (200, 220, 200)),
                     pygame.font.Font(None, 22).render(hint, True, (200, 220, 200)).get_rect(
                         midbottom=(S.SCREEN_W // 2, S.SCREEN_H - 6)))

    def _draw_fish(self, surface, fish):
        size = FISH_SIZES[fish.kind]["sprite"]
        img = assets.image("item_fish", (size, size))
        if fish.heading.x < 0 and not fish.hooked:
            img = pygame.transform.flip(img, True, False)
        surface.blit(img, img.get_rect(center=(round(fish.pos.x), round(fish.pos.y))))

    def _draw_fight_bars(self, surface):
        font = pygame.font.Font(None, 22)
        x, y = S.SCREEN_W - 230, 34
        surface.blit(font.render("Line", True, S.TEXT_COLOR), (x, y))
        pygame.draw.rect(surface, (50, 50, 60), (x + 50, y, 170, 12))
        pygame.draw.rect(surface, (90, 200, 110), (x + 50, y, 170 * max(0, self.fight["tension"]) / self.TENSION_MAX, 12))
        surface.blit(font.render("Reel", True, S.TEXT_COLOR), (x, y + 22))
        pygame.draw.rect(surface, (50, 50, 60), (x + 50, y + 22, 170, 12))
        pygame.draw.rect(surface, (90, 150, 230), (x + 50, y + 22, 170 * self.fight["progress"] / 100, 12))
