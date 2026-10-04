"""Each mini game: its rules, win and loss, and its difficulty presets."""
import random

import pygame
import pytest

from game.minigames.fishing import FISH_SIZES, Fishing
from game.minigames.meteor_shower import MeteorShower, Rock
from game.minigames.peek_a_bush import PeekABush
from game.minigames.snowball import Snowball, Thing

from conftest import HeldKeys, key_event

DT = 1 / 60


def _run(game_obj, keys, limit_seconds, step=None):
    frames = 0
    while not game_obj.finished and frames < int(limit_seconds / DT):
        if step:
            step(game_obj)
        game_obj.update(DT, keys)
        frames += 1
    return game_obj.result


# Meteor Shower

def test_meteor_shower_is_lost_when_out_of_lives(no_keys):
    g = MeteorShower("normal")
    g.lives = 1
    for _ in range(int(40 / DT)):
        if g.invuln <= 0:
            rock = Rock(g.player_x, 20, 0)
            rock.y = g.player_y
            g.rocks.append(rock)
        g.update(DT, no_keys)
        if g.finished:
            break
    assert g.result == "lost"


def test_meteor_shower_is_won_by_surviving_the_timer(no_keys):
    g = MeteorShower("easy")
    assert _run(g, no_keys, 30) == "won"


@pytest.mark.parametrize("difficulty, reward", [("easy", 8), ("normal", 10), ("hard", 18)])
def test_meteor_shower_rewards_per_difficulty(difficulty, reward):
    assert MeteorShower.reward_for(difficulty) == reward


# Peek-A-Bush

def test_marking_an_empty_bush_loses_at_once():
    g = PeekABush()
    g.phase, g.timer, g.creatures = "guess", 9, {0}
    g.cursor = 4
    g.handle_event(key_event(pygame.K_RETURN))
    assert g.result == "lost"


def test_marking_exactly_the_creatures_wins_the_game(no_keys):
    g = PeekABush("easy")

    def mark_perfectly(game_obj):
        if game_obj.phase == "guess" and not game_obj.marks:
            game_obj.marks = set(game_obj.creatures)

    assert _run(g, no_keys, 100, mark_perfectly) == "won"


def test_missing_a_creature_loses_the_round(no_keys):
    g = PeekABush("easy")

    def miss_one(game_obj):
        if game_obj.phase == "guess" and not game_obj.marks and game_obj.creatures:
            game_obj.marks = set(list(game_obj.creatures)[:-1])

    assert _run(g, no_keys, 100, miss_one) == "lost"


def test_f_submits_the_round_early():
    g = PeekABush("easy")
    g.round = g.ROUNDS
    g.phase, g.timer, g.creatures, g.marks = "guess", 9, {0}, {0}
    g.handle_event(key_event(pygame.K_f))
    assert g.phase == "reveal"


# Fishing

KEY_FOR = {"up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT}


def _fishing_bot(g):
    """Cast, set the hook, steer each pull and spam reel."""
    if g.line is None:
        g.handle_event(key_event(pygame.K_SPACE))
    elif g.line["state"] == "bite":
        g.handle_event(key_event(pygame.K_SPACE))
    elif g.fight:
        if not g.fight["good"]:
            g.handle_event(key_event(KEY_FOR[g.fight["pull"]], shift=True))
        g._bot_spam = getattr(g, "_bot_spam", 0) - DT
        if g._bot_spam <= 0:
            g.handle_event(key_event(pygame.K_SPACE))
            g._bot_spam = 0.14


@pytest.mark.parametrize("difficulty", ["easy", "normal"])
def test_fishing_bot_can_win(no_keys, difficulty):
    g = Fishing(difficulty)
    assert _run(g, no_keys, 200, _fishing_bot) == "won"


def test_fishing_without_steering_catches_nothing(no_keys):
    g = Fishing()
    cast_if_idle = lambda gm: gm.handle_event(key_event(pygame.K_SPACE)) if gm.line is None else None
    assert _run(g, no_keys, 70, cast_if_idle) == "lost"
    assert g.catches == 0


def test_shift_with_the_right_arrow_keeps_tension_and_wrong_arrow_lowers_it():
    g = Fishing()
    g.handle_event(key_event(pygame.K_SPACE))
    fish = g.swimmers[0]
    fish.pos = g.line["pos"].copy()
    g.line["state"], g.line["fish"], g.line["timer"] = "bite", fish, 0.5
    g.handle_event(key_event(pygame.K_SPACE))
    assert g.fight is not None and fish.hooked

    before = g.fight["tension"]
    g.handle_event(key_event(KEY_FOR[g.fight["pull"]], shift=True))
    assert g.fight["tension"] > before

    wrong = next(k for d, k in KEY_FOR.items() if d != g.fight["pull"])
    before = g.fight["tension"]
    g.handle_event(key_event(wrong, shift=True))
    assert g.fight["tension"] < before


def test_arrow_without_shift_does_nothing_in_a_fight():
    g = Fishing()
    g.handle_event(key_event(pygame.K_SPACE))
    g.line["state"], g.line["fish"], g.line["timer"] = "bite", g.swimmers[0], 0.5
    g.handle_event(key_event(pygame.K_SPACE))
    before = g.fight["tension"]
    g.handle_event(key_event(KEY_FOR[g.fight["pull"]]))
    assert g.fight["tension"] == before


def test_f_finishes_fishing_only_once_the_target_is_reached():
    g = Fishing()
    g.score = g.TARGET - 1
    g.handle_event(key_event(pygame.K_f))
    assert not g.finished
    g.score = g.TARGET
    g.handle_event(key_event(pygame.K_f))
    assert g.result == "won"


def test_medium_and_big_fish_are_most_of_the_catches():
    rng = random.Random(1)
    names = list(FISH_SIZES)
    weights = [FISH_SIZES[n]["weight"] for n in names]
    rolls = [rng.choices(names, weights=weights)[0] for _ in range(5000)]
    assert (rolls.count("medium") + rolls.count("big")) / len(rolls) > 0.6


# Snowball

def test_snowball_is_lost_when_idle(no_keys):
    g = Snowball("normal")
    assert _run(g, no_keys, 40) == "lost"


def test_snowball_grows_from_snow_and_shrinks_from_rocks():
    g = Snowball()
    start = g.size
    g.things = []
    g.things.append(Thing("snow", g.x, g.y - 2, 0))
    g.update(DT, _Keys())
    assert g.size > start
    g.things.append(Thing("rock", g.x, g.y - 2, 0))
    before = g.size
    g.update(DT, _Keys())
    assert g.size < before


class _Keys:
    def __getitem__(self, key):
        return False
