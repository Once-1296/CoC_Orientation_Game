import pygame

from . import settings as S

LIFETIME = 0.9           # seconds a floating message stays up
RISE_SPEED = 30          # pixels per second the message drifts upwards
_font = None


def _get_font():
    global _font
    if _font is None:
        _font = pygame.font.Font(None, 24)
    return _font


class FloatText:
    """A short message that rises and fades, for example "+1 fish" over a catch."""

    def __init__(self, text, pos, color=S.TEXT_COLOR):
        self.text = text
        self.pos = pygame.Vector2(pos)
        self.color = color
        self.timer = LIFETIME

    @property
    def alive(self):
        return self.timer > 0

    def update(self, dt):
        self.timer -= dt
        self.pos.y -= RISE_SPEED * dt

    def draw(self, surface, offset=(0, 0)):
        image = _get_font().render(self.text, True, self.color)
        image.set_alpha(max(0, min(255, int(255 * self.timer / LIFETIME))))
        surface.blit(image, image.get_rect(center=(round(self.pos.x) + offset[0], round(self.pos.y) + offset[1])))


def tick(popups, dt):
    """Advance every message by dt and return the ones still alive."""
    for popup in popups:
        popup.update(dt)
    return [popup for popup in popups if popup.alive]
