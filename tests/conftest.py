import os
import random
import sys

# Run headless: no window and no sound device.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pygame
import pytest

from game.game import Game


class NoKeys:
    """Stands in for pygame.key.get_pressed() when no key is held."""

    def __getitem__(self, key):
        return False


class HeldKeys:
    """Hold a set of keys for update()."""

    def __init__(self, *keys):
        self.keys = set(keys)

    def __getitem__(self, key):
        return key in self.keys


def key_event(key, shift=False):
    return pygame.Event(pygame.KEYDOWN, key=key, mod=pygame.KMOD_SHIFT if shift else 0)


@pytest.fixture(autouse=True)
def fixed_random():
    random.seed(12345)


@pytest.fixture
def game():
    return Game()


@pytest.fixture
def no_keys():
    return NoKeys()
