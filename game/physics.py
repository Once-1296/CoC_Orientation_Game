"""Tile-collision movement shared by the player and enemies."""
import pygame

# How far (px) a blocked body may slide sideways to get past a corner.
# This lets you walk into a gap even when you are a few pixels off its centre line.
CORNER_NUDGE = 6


def body_rect(pos, size):
    """Square collision box of `size` pixels centred on `pos`."""
    rect = pygame.Rect(0, 0, size, size)
    rect.center = (round(pos.x), round(pos.y))
    return rect


def _free(pos, size, collides):
    return not collides(body_rect(pos, size))


def move_body(pos, delta, size, collides):
    """Move `pos` (a centre point) by `delta`, one axis at a time.

    If an axis is blocked, the body slides up to CORNER_NUDGE pixels sideways
    to find a free path around the corner.
    """
    for axis in (0, 1):
        step = delta[axis]
        if step == 0:
            continue

        move = pygame.Vector2(0, 0)
        move[axis] = step
        if _free(pos + move, size, collides):
            pos += move
            continue

        side = 1 - axis
        moved = False
        for offset in range(1, CORNER_NUDGE + 1):
            for sign in (1, -1):
                nudge = pygame.Vector2(0, 0)
                nudge[side] = sign * offset
                if _free(pos + nudge + move, size, collides):
                    pos += nudge + move
                    moved = True
                    break
            if moved:
                break


def nearest_free(pos, size, collides, max_radius=96):
    """Return `pos` if the box fits there, otherwise the closest free spot within max_radius px."""
    if not collides(body_rect(pos, size)):
        return pygame.Vector2(pos)
    for radius in range(4, max_radius + 1, 4):
        for dx in range(-radius, radius + 1, 4):
            for dy in (-radius, radius):
                for candidate in (pygame.Vector2(pos.x + dx, pos.y + dy), pygame.Vector2(pos.x + dy, pos.y + dx)):
                    if not collides(body_rect(candidate, size)):
                        return candidate
    return pygame.Vector2(pos)
