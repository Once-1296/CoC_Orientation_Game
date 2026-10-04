import pygame

from . import settings as S


class Menu:
    """A vertical list of choices drawn over the game. Arrows move, Enter chooses, Esc cancels."""

    def __init__(self, title, options, on_choose, on_cancel):
        self.title = title
        self.options = options           # list of (label, detail, value)
        self.on_choose = on_choose
        self.on_cancel = on_cancel
        self.index = 0

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self.index = (self.index - 1) % len(self.options)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.index = (self.index + 1) % len(self.options)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
            self.on_choose(self.options[self.index][2])
        elif event.key == pygame.K_ESCAPE:
            self.on_cancel()

    def draw(self, surface):
        shade = pygame.Surface((S.SCREEN_W, S.SCREEN_H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 150))
        surface.blit(shade, (0, 0))

        panel = pygame.Rect(0, 0, 440, 60 + 46 * len(self.options) + 60)
        panel.center = (S.SCREEN_W // 2, S.SCREEN_H // 2)
        pygame.draw.rect(surface, (24, 26, 40), panel, border_radius=10)
        pygame.draw.rect(surface, (200, 200, 220), panel, 2, border_radius=10)

        title_font = pygame.font.Font(None, 32)
        font = pygame.font.Font(None, 28)
        small = pygame.font.Font(None, 22)
        surface.blit(title_font.render(self.title, True, S.TEXT_COLOR),
                     title_font.render(self.title, True, S.TEXT_COLOR).get_rect(midtop=(panel.centerx, panel.top + 16)))

        for i, (label, _, _) in enumerate(self.options):
            row = pygame.Rect(panel.left + 30, panel.top + 60 + i * 46, panel.width - 60, 36)
            if i == self.index:
                pygame.draw.rect(surface, (70, 90, 140), row, border_radius=6)
            surface.blit(font.render(label, True, S.TEXT_COLOR), (row.left + 12, row.centery - 9))

        detail = self.options[self.index][1]
        surface.blit(small.render(detail, True, (190, 200, 220)),
                     small.render(detail, True, (190, 200, 220)).get_rect(midbottom=(panel.centerx, panel.bottom - 14)))
