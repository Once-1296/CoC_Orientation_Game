import pygame

from . import assets
from . import settings as S

PANEL = pygame.Rect(0, 0, 520, 430)

# (state key, label) for everything the player can collect or earn
ITEMS = [
    ("coins", "Coins"),
    ("rocks", "Rocks"),
    ("snow", "Snow piles"),
    ("fish", "Fish"),
    ("slimes", "Slimes defeated"),
    ("potions", "Health potions"),
]


def _icon(key, surface_pos, screen):
    centre = (surface_pos[0] + 12, surface_pos[1] + 12)
    if key == "snow":
        pygame.draw.circle(screen, (255, 255, 255), centre, 9)
        pygame.draw.circle(screen, (40, 90, 160), centre, 9, 2)
        return
    icons = {"coins": "icon_coin", "rocks": "item_rock", "fish": "item_fish", "slimes": "enemy_slime"}
    if key in icons:
        img = assets.image(icons[key], (24, 24))
        screen.blit(img, img.get_rect(center=centre))


def draw_inventory(surface, state, quests):
    """Overlay listing items and quest progress. `quests` is a list of (npc, minigame title, item, need, done)."""
    shade = pygame.Surface((S.SCREEN_W, S.SCREEN_H), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 150))
    surface.blit(shade, (0, 0))

    panel = PANEL.copy()
    panel.center = (S.SCREEN_W // 2, S.SCREEN_H // 2)
    pygame.draw.rect(surface, (24, 26, 40), panel, border_radius=10)
    pygame.draw.rect(surface, (200, 200, 220), panel, 2, border_radius=10)

    title_font = pygame.font.Font(None, 32)
    font = pygame.font.Font(None, 26)
    small = pygame.font.Font(None, 20)

    title = title_font.render("Inventory", True, S.TEXT_COLOR)
    surface.blit(title, title.get_rect(midtop=(panel.centerx, panel.top + 12)))

    x, y = panel.left + 24, panel.top + 52
    surface.blit(font.render("Items", True, (190, 200, 220)), (x, y))
    y += 26
    for key, label in ITEMS:
        _icon(key, (x, y), surface)
        surface.blit(font.render(label, True, S.TEXT_COLOR), (x + 36, y + 4))
        count = font.render(str(state[key]), True, S.TEXT_COLOR)
        surface.blit(count, count.get_rect(topright=(panel.right - 24, y + 4)))
        y += 30

    y += 10
    surface.blit(font.render("Quests", True, (190, 200, 220)), (x, y))
    y += 26
    for npc, title_text, item, need, done in quests:
        have = min(state[item], need)
        status = "done" if done else f"{have}/{need} {item}"
        line = font.render(f"{npc}  -  {title_text}", True, S.TEXT_COLOR)
        surface.blit(line, (x, y + 4))
        status_text = font.render("done" if done else status, True, (120, 220, 130) if done else S.TEXT_COLOR)
        surface.blit(status_text, status_text.get_rect(topright=(panel.right - 24, y + 4)))
        y += 28

    hint = small.render("I or Esc to close", True, (160, 170, 190))
    surface.blit(hint, hint.get_rect(midbottom=(panel.centerx, panel.bottom - 10)))
