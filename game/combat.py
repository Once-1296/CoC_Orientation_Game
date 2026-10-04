import pygame

from . import assets
from . import settings as S
from .effects import FloatText, tick
from .items import Pickup
from .player import FACING_VECTORS

SWING_TIME = 0.2          # seconds the sword hit-box is active
SWING_COOLDOWN = 0.45     # seconds before the next swing can start
SWING_REACH = 24          # distance from player centre to the middle of the swing
SWING_SIZE = 28           # width and height of the swing hit-box
SWORD_SIZE = 32           # size the sword sprite is drawn at
SHIELD_SPEED = 0.5        # movement multiplier while holding the shield
PLAYER_INVULN = 1.0       # seconds of invulnerability after taking a hit
BLOCK_COOLDOWN = 0.4      # minimum seconds between block sounds
KNOCK_STRENGTH = 180      # knockback speed for the player when hit
ENEMY_BLOCK_KNOCK = 120   # knockback for an enemy that bounces off the shield
PICKUP_RANGE = 20         # pixels
SLIME_DAMAGE = 1          # half-hearts per slime touch (a slime deals half a heart)

PICKUP_STATE = {"coin": "coins", "rock": "rocks", "fish": "fish", "snow": "snow"}

# The sword sprite's blade points up-left. These are counter-clockwise rotations (degrees)
# that turn it to point in each facing direction.
SWORD_ROTATION = {"up": -45, "left": 45, "down": 135, "right": -135}


class Combat:
    """Sword swings, shield blocks, enemy contact damage and pickups."""

    def __init__(self):
        self.popups = []
        self.reset()

    def reset(self):
        self.swing_timer = 0.0
        self.cooldown = 0.0
        self.invuln = 0.0
        self.block_timer = 0.0
        self.shielding = False
        self._hit = set()

    @property
    def swinging(self):
        return self.swing_timer > 0

    def start_swing(self):
        if self.swinging or self.cooldown > 0 or self.shielding:
            return
        self.swing_timer = SWING_TIME
        self.cooldown = SWING_COOLDOWN
        self._hit = set()
        assets.play("sfx_slash")

    def swing_rect(self, player):
        centre = player.pos + FACING_VECTORS[player.facing] * SWING_REACH
        return _centred(centre, SWING_SIZE)

    def update(self, dt, world, player, state, shield_held):
        self.cooldown = max(0.0, self.cooldown - dt)
        self.swing_timer = max(0.0, self.swing_timer - dt)
        self.invuln = max(0.0, self.invuln - dt)
        self.block_timer = max(0.0, self.block_timer - dt)
        self.shielding = shield_held and not self.swinging

        self._hit_enemies(world, player, state)
        self._enemy_contact(world, player, state)
        self._collect_pickups(world, player, state)
        self.popups = tick(self.popups, dt)

    def _hit_enemies(self, world, player, state):
        if not self.swinging:
            return
        rect = self.swing_rect(player)
        for enemy in world.enemies:
            if enemy.alive and enemy not in self._hit and rect.colliderect(enemy.rect()):
                self._hit.add(enemy)
                if enemy.hit(enemy.pos - player.pos, damage=1 + state["sword_level"]):
                    world.pickups.append(Pickup("coin", enemy.pos))
                    state["slimes"] += 1

    def _in_front(self, player, enemy):
        to_enemy = enemy.pos - player.pos
        return to_enemy.length_squared() > 0 and to_enemy.dot(FACING_VECTORS[player.facing]) > 0

    def _enemy_contact(self, world, player, state):
        body = player.hitbox()
        for enemy in world.enemies:
            if not enemy.alive or not body.colliderect(enemy.rect()):
                continue

            away = enemy.pos - player.pos
            if self.shielding and self._in_front(player, enemy):
                if self.block_timer <= 0:
                    self.block_timer = BLOCK_COOLDOWN
                    assets.play("sfx_block")
                enemy.push(away, ENEMY_BLOCK_KNOCK)
            elif self.invuln <= 0:
                state["hp"] = max(0, state["hp"] - SLIME_DAMAGE)
                self.invuln = PLAYER_INVULN
                if away.length_squared() > 0:
                    player.knock = -away.normalize() * KNOCK_STRENGTH

    def _collect_pickups(self, world, player, state):
        for pickup in list(world.pickups):
            if pickup.pos.distance_to(player.pos) <= PICKUP_RANGE:
                world.pickups.remove(pickup)
                state[PICKUP_STATE[pickup.kind]] += 1
                self.popups.append(FloatText(f"+1 {pickup.kind}", pickup.pos, (255, 255, 255)))
                assets.play("sfx_pickup")

    def draw(self, surface, offset, player):
        ox, oy = offset
        for popup in self.popups:
            popup.draw(surface, offset)
        if self.swinging:
            centre = player.pos + FACING_VECTORS[player.facing] * SWING_REACH
            sword = pygame.transform.rotate(
                assets.image("icon_sword", (SWORD_SIZE, SWORD_SIZE)),
                SWORD_ROTATION[player.facing],
            )
            surface.blit(sword, sword.get_rect(center=(round(centre.x) + ox, round(centre.y) + oy)))
        if self.shielding:
            icon = assets.image("icon_shield", (16, 16))
            centre = player.pos + FACING_VECTORS[player.facing] * 12
            surface.blit(icon, (round(centre.x) - 8 + ox, round(centre.y) - 8 + oy))


def _centred(centre, size):
    rect = pygame.Rect(0, 0, size, size)
    rect.center = (round(centre.x), round(centre.y))
    return rect
