"""Maps, exits, collisions and the bounds rules."""
from collections import deque

import pygame
import pytest

from game import settings as S
from game.enemies import Slime
from game.maps import MAPS
from game.player import Player

T = S.TILE_SIZE
OUTDOOR = [name for name, data in MAPS.items() if "links" in data and data["links"]]
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
# Where a player arrives when entering an outdoor map from town, on the side that leads back to town.
ARRIVE = {"N": (9, 1), "S": (9, 13), "E": (18, 6), "W": (1, 6)}


def _reachable(m, start):
    seen = {start}
    queue = deque([start])
    while queue:
        c, r = queue.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c + dc, r + dr)
            if 0 <= n[0] < m.width and 0 <= n[1] < m.height and n not in seen and not m.is_solid(*n):
                seen.add(n)
                queue.append(n)
    return seen


def _walkable(m):
    return {(c, r) for r in range(m.height) for c in range(m.width) if not m.is_solid(c, r)}


@pytest.mark.parametrize("name", OUTDOOR)
def test_every_walkable_tile_is_reachable_from_the_arrival_point(game, name):
    m = game.get_map(name)
    side = next(iter(MAPS[name]["links"]))
    seen = _reachable(m, ARRIVE[side])
    assert _walkable(m) - seen == set()


@pytest.mark.parametrize("name", OUTDOOR)
def test_exit_links_are_mutual(game, name):
    for side, target in MAPS[name]["links"].items():
        assert MAPS[target]["links"][OPPOSITE[side]] == name


@pytest.mark.parametrize("name", OUTDOOR)
def test_exit_gap_leads_to_a_free_arrival_point(game, name):
    for side, target in MAPS[name]["links"].items():
        game._enter_side(target, side)
        assert not game.current.collides(game.player.hitbox()), (name, side)


@pytest.mark.parametrize("name", list(MAPS))
def test_npcs_pickups_and_enemies_stand_on_walkable_tiles(game, name):
    m = game.get_map(name)
    walkable = _walkable(m)
    for npc in m.npcs:
        assert (npc.rect.x // T, npc.rect.y // T) in walkable
    for pickup in m.pickups:
        assert (int(pickup.pos.x // T), int(pickup.pos.y // T)) in walkable
    for enemy in m.enemies:
        assert (int(enemy.pos.x // T), int(enemy.pos.y // T)) in walkable


@pytest.mark.parametrize("name", list(MAPS))
def test_random_walk_never_enters_solid_tiles_or_leaves_the_map(game, name):
    import random
    rng = random.Random(7)
    for _ in range(2):
        m = game.get_map(name)
        walkable = sorted(_walkable(m) - {(c, r) for npc in m.npcs for c, r in [(npc.rect.x // T, npc.rect.y // T)]})
        c, r = rng.choice(walkable)
        game._enter_tile(name, (c, r))
        dx = dy = 0
        for frame in range(1500):
            if frame % 40 == 0:
                dx, dy = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0), (1, 1), (-1, -1)])
            before = game.current.name
            game.player.move(dx, dy, 1 / 60, game.current.collides)
            game.check_transitions()
            if game.current.name == before:
                assert not game.current.collides(game.player.hitbox()), (name, frame)
                assert 0 <= game.player.pos.x <= m.width * T and 0 <= game.player.pos.y <= m.height * T
            else:
                assert not game.current.collides(game.player.hitbox()), "arrival is blocked"
                game._enter_tile(name, (c, r))


@pytest.mark.parametrize("name", list(MAPS))
def test_slimes_stay_inside_their_map(game, name):
    import random
    rng = random.Random(3)
    m = game.get_map(name)
    no_exit_collides = lambda rect: m.collides(rect, through_exits=False)
    for enemy in m.enemies:
        for _ in range(1500):
            enemy.update(1 / 60, pygame.Vector2(-500, -500), no_exit_collides)
            assert not no_exit_collides(enemy.rect())
            assert 0 <= enemy.pos.x <= m.width * T and 0 <= enemy.pos.y <= m.height * T


def test_home_door_and_town_door_lead_to_each_other(game):
    game._enter_tile("home", (4, 5))
    game.player.pos = pygame.Vector2(4.5 * T, 6.4 * T)     # inside the door tile
    game.check_transitions()
    assert game.current.name == "town"
    game.player.pos = pygame.Vector2(4.5 * T, 4.4 * T)     # inside the town door tile
    game.check_transitions()
    assert game.current.name == "home"


def test_roof_and_stall_tiles_are_solid(game):
    town = game.get_map("town")
    assert town.is_solid(2, 2)      # roof
    assert town.is_solid(14, 2)     # market stall
    assert not town.is_solid(9, 5)  # path
