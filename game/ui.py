import pygame

from . import assets
from . import settings as S

BOX_RECT = pygame.Rect(16, S.SCREEN_H - 116, S.SCREEN_W - 32, 100)


def wrap_text(text, font, max_width):
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class DialogueBox:
    def __init__(self, speaker, lines):
        self.speaker = speaker
        self.lines = list(lines)
        self.index = 0

    def advance(self):
        """Move to the next line. Returns True when the dialogue is finished."""
        self.index += 1
        return self.index >= len(self.lines)

    def draw(self, surface):
        font = pygame.font.Font(None, 24)
        name_font = pygame.font.Font(None, 28)

        surface.blit(assets.image("dialogue_box", BOX_RECT.size), BOX_RECT)
        surface.blit(name_font.render(self.speaker, True, S.TEXT_COLOR), (BOX_RECT.x + 12, BOX_RECT.y + 8))

        y = BOX_RECT.y + 36
        for line in wrap_text(self.lines[self.index], font, BOX_RECT.width - 24):
            surface.blit(font.render(line, True, S.TEXT_COLOR), (BOX_RECT.x + 12, y))
            y += 22

        hint = font.render("[E / Space] continue", True, (160, 160, 170))
        surface.blit(hint, hint.get_rect(bottomright=(BOX_RECT.right - 12, BOX_RECT.bottom - 8)))


def draw_hud(surface, state):
    font = pygame.font.Font(None, 26)
    surface.blit(assets.image("icon_coin", (20, 20)), (10, 10))
    surface.blit(font.render(f"Coins: {state['coins']}", True, S.TEXT_COLOR), (36, 12))
