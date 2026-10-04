import random

import pygame

from .. import assets
from .. import settings as S
from .base import MiniGame


class PeekABush(MiniGame):
    """Creatures pop out of bushes for a moment. Remember where they were and mark them."""

    name = "peek_a_bush"
    title = "Peek-A-Bush"
    REWARD = 12
    PRESETS = {
        "easy": {"ROUNDS": 3, "CREATURES": (1, 2), "GUESS_TIME": 8.0, "REWARD": 8},
        "hard": {"GRID": 4, "PATCH": 84, "GAP": 14, "ROUNDS": 5, "CREATURES": (4, 6),
                 "GUESS_TIME": 5.0, "REWARD": 18},
    }

    # Tuning values. Change these to make the game easier or harder.
    GRID = 3                 # 3x3 bushes
    ROUNDS = 5
    CREATURES = (2, 3)       # fewest and most creatures per round
    SHOW_TIME = 2.0          # seconds the creatures stay visible
    GUESS_TIME = 6.0         # seconds to mark the bushes
    REVEAL_TIME = 1.5        # seconds the answer is shown

    PATCH = 96               # bush size on screen
    GAP = 18                 # space between bushes

    def __init__(self, difficulty="normal"):
        super().__init__(difficulty)
        self.round = 0
        self.phase = None
        self.timer = 0.0
        self.creatures = set()
        self.marks = set()
        self.cursor = 0      # bush index, row-major
        self.reveal = None   # (correct marks, missed creatures) for the reveal phase
        self.round_failed = False
        self._start_round()

    def _origin(self):
        size = self.GRID * self.PATCH + (self.GRID - 1) * self.GAP
        return ((S.SCREEN_W - size) // 2, (S.SCREEN_H - size) // 2 + 14)

    def _bush_rect(self, index):
        ox, oy = self._origin()
        c, r = index % self.GRID, index // self.GRID
        return pygame.Rect(ox + c * (self.PATCH + self.GAP), oy + r * (self.PATCH + self.GAP),
                           self.PATCH, self.PATCH)

    def _start_round(self):
        self.round += 1
        count = random.randint(*self.CREATURES)
        self.creatures = set(random.sample(range(self.GRID * self.GRID), count))
        self.marks = set()
        self.phase = "show"
        self.timer = self.SHOW_TIME

    def _score_round(self):
        correct = self.marks & self.creatures
        missed = self.creatures - self.marks
        self.reveal = (correct, missed)
        self.round_failed = bool(missed)

    def _toggle(self, index):
        if index in self.marks:
            self.marks.remove(index)
        elif index in self.creatures:
            self.marks.add(index)
        else:
            self.result = "lost"    # marking a bush with no creature loses at once

    def _submit(self):
        self._score_round()
        self.phase = "reveal"
        self.timer = self.REVEAL_TIME

    def handle_event(self, event):
        if self.phase != "guess":
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                self._submit()     # done early: check the marks now
                return
            col, row = self.cursor % self.GRID, self.cursor // self.GRID
            if event.key in (pygame.K_LEFT, pygame.K_a):
                col = max(0, col - 1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                col = min(self.GRID - 1, col + 1)
            elif event.key in (pygame.K_UP, pygame.K_w):
                row = max(0, row - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                row = min(self.GRID - 1, row + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._toggle(self.cursor)
                return
            self.cursor = row * self.GRID + col
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index in range(self.GRID * self.GRID):
                if self._bush_rect(index).collidepoint(event.pos):
                    self.cursor = index
                    self._toggle(index)

    def update(self, dt, keys):
        if self.finished:
            return
        self.timer -= dt
        if self.timer > 0:
            return

        if self.phase == "show":
            self.phase = "guess"
            self.timer = self.GUESS_TIME
        elif self.phase == "guess":
            self._submit()
        elif self.phase == "reveal":
            if self.round_failed:
                self.result = "lost"        # a round is lost when a creature was missed
            elif self.round >= self.ROUNDS:
                self.result = "won"
            else:
                self._start_round()

    def draw(self, surface):
        surface.fill((60, 110, 60))
        font = pygame.font.Font(None, 28)
        small = pygame.font.Font(None, 22)

        bush = assets.image("tile_bush", (self.PATCH, self.PATCH))
        creature = assets.image("enemy_slime", (48, 48))
        show_creatures = self.phase in ("show", "reveal")

        for index in range(self.GRID * self.GRID):
            rect = self._bush_rect(index)
            surface.blit(bush, rect)
            if show_creatures and index in self.creatures:
                surface.blit(creature, creature.get_rect(center=(rect.centerx, rect.centery + 8)))

            if self.phase == "guess":
                if index in self.marks:
                    pygame.draw.rect(surface, (255, 220, 60), rect, 4)
                    surface.blit(font.render("?", True, (255, 220, 60)), (rect.right - 18, rect.top + 4))
            elif self.phase == "reveal" and self.reveal:
                correct, missed = self.reveal
                if index in correct:
                    pygame.draw.rect(surface, (80, 220, 100), rect, 4)
                elif index in missed:
                    pygame.draw.rect(surface, (230, 70, 70), rect, 4)

        if self.phase == "guess":
            pygame.draw.rect(surface, (255, 255, 255), self._bush_rect(self.cursor).inflate(8, 8), 2)

        if self.phase == "show":
            status = "Watch carefully!"
        elif self.phase == "guess":
            status = f"Mark only the bushes with creatures ({self.timer:0.1f}s). F submits early"
        else:
            status = "Round over"
        surface.blit(font.render(f"Round {self.round}/{self.ROUNDS}", True, S.TEXT_COLOR), (10, 10))
        status_text = font.render(status, True, S.TEXT_COLOR)
        surface.blit(status_text, status_text.get_rect(midtop=(S.SCREEN_W // 2, 40)))
        hint = small.render(f"{self.title}   Esc to leave", True, (200, 220, 200))
        surface.blit(hint, hint.get_rect(midbottom=(S.SCREEN_W // 2, S.SCREEN_H - 6)))
