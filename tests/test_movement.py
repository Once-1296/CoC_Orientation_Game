"""Player movement: corner sliding, facing and the walk animation."""
import pygame
import pytest

from game import settings as S
from game.physics import body_rect, nearest_free
from game.player import SPRITE_FOLDERS, Player

T = S.TILE_SIZE


def test_left_faces_left_and_uses_flipped_frames():
    assert SPRITE_FOLDERS["left"] == ("player/SideWalk", True)
    assert SPRITE_FOLDERS["right"] == ("player/SideWalk", False)


def test_moving_left_sets_facing_left(game):
    game._enter_tile("town", (9, 6))
    game.player.move(-1, 0, 1 / 60, game.current.collides)
    assert game.player.facing == "left"


@pytest.mark.parametrize("offset", range(-8, 9, 2))
def test_walking_into_a_gap_works_from_a_few_pixels_off_centre(game, offset):
    """Regression: the player used to stop when a few pixels off the tile centre line."""
    m = game.get_map("town")
    # Walk east along the middle row of the town, starting off-centre from a free tile.
    start_c, row = 3, 6
    pos = pygame.Vector2((start_c + 0.5) * T, (row + 0.5) * T + offset)
    player = Player(pos)
    target_x = (start_c + 3.5) * T
    for _ in range(240):
        player.move(1, 0, 1 / 60, m.collides)
        if player.pos.x >= target_x:
            break
    assert player.pos.x >= target_x - 3


def test_nearest_free_moves_out_of_a_solid_tile(game):
    m = game.get_map("woods")
    tree = pygame.Vector2(5.5 * T, 5.5 * T)     # a tree in the woods
    assert m.collides(body_rect(tree, S.PLAYER_HITBOX))
    spot = nearest_free(tree, S.PLAYER_HITBOX, m.collides)
    assert not m.collides(body_rect(spot, S.PLAYER_HITBOX))
