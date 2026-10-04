"""Sword, shield, slimes, damage and pickups."""
import pygame
import pytest

from game import settings as S
from game import shop
from game.enemies import Slime
from game.items import Pickup

T = S.TILE_SIZE


def _slime_in_front(game):
    game._enter_tile("town", (5, 5))
    m = game.current
    m.enemies = [Slime((6, 5))]
    enemy = m.enemies[0]
    enemy.pos = pygame.Vector2(6.5 * T, 5.5 * T)
    game.player.facing = "right"
    return m, enemy


def _swing_until_dead(game, m, enemy, limit=10):
    swings = 0
    while enemy.alive and swings < limit:
        game.combat.cooldown = 0
        game.combat.start_swing()
        swings += 1
        for _ in range(20):
            game.combat.update(1 / 60, m, game.player, game.state, False)
        enemy.pos = pygame.Vector2(6.5 * T, 5.5 * T)
        enemy.knock = pygame.Vector2()
        enemy.hurt_timer = 0
    return swings


@pytest.mark.parametrize("sword_level, hits", [(0, 3), (1, 2), (2, 1)])
def test_sword_upgrades_change_hits_to_kill_a_slime(game, sword_level, hits):
    game.state["sword_level"] = sword_level
    m, enemy = _slime_in_front(game)
    assert _swing_until_dead(game, m, enemy) == hits


def test_killing_a_slime_drops_a_coin_and_counts_it(game):
    game.state["sword_level"] = 2
    m, enemy = _slime_in_front(game)
    _swing_until_dead(game, m, enemy)
    assert game.state["slimes"] == 1
    assert any(p.kind == "coin" for p in m.pickups)


def test_contact_costs_half_a_heart(game):
    m, enemy = _slime_in_front(game)
    game.player.pos = pygame.Vector2(5.5 * T, 5.5 * T)
    enemy.pos = game.player.pos + pygame.Vector2(14, 0)
    game.state["hp"] = 6
    game.combat.reset()
    game.combat.update(1 / 60, m, game.player, game.state, False)
    assert game.state["hp"] == 5


def test_shield_blocks_a_hit_from_the_front(game):
    m, enemy = _slime_in_front(game)
    game.player.pos = pygame.Vector2(5.5 * T, 5.5 * T)
    game.player.facing = "right"
    enemy.pos = game.player.pos + pygame.Vector2(14, 0)
    game.state["hp"] = 6
    game.combat.reset()
    game.combat.update(1 / 60, m, game.player, game.state, True)
    assert game.state["hp"] == 6


def test_swinging_is_blocked_while_shielding(game):
    game.combat.shielding = True
    game.combat.start_swing()
    assert not game.combat.swinging


def test_snow_pickup_is_a_pure_white_circle_and_collected(game):
    surface = pygame.Surface((64, 64))
    surface.fill((0, 0, 0))
    Pickup("snow", (32, 32)).draw(surface, (0, 0))
    assert surface.get_at((32, 32))[:3] == (255, 255, 255)

    game._enter_tile("town", (5, 5))
    m = game.current
    m.pickups = [Pickup("snow", game.player.pos)]
    game.combat.update(1 / 60, m, game.player, game.state, False)
    assert game.state["snow"] == 1
    assert m.pickups == []
    assert any("+1 snow" == p.text for p in game.combat.popups)
