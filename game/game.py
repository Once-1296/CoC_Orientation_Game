import pygame

from . import assets
from . import settings as S
from .maps import MAPS, START_MAP
from .player import Player
from .ui import DialogueBox, draw_hud
from .world import Map

T = S.TILE_SIZE
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((S.SCREEN_W, S.SCREEN_H))
        pygame.display.set_caption(S.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Shared progress. Mini game unlocks will read and write this later.
        self.state = {"coins": 0}
        self.maps = {}
        self.dialogue = None

        start = MAPS[START_MAP]
        self._enter_tile(START_MAP, start["spawn"])

    # Map loading and transitions

    def get_map(self, name):
        if name not in self.maps:
            self.maps[name] = Map(name, MAPS[name])
        return self.maps[name]

    def _enter_tile(self, name, tile):
        """Enter a map at the centre of a tile (used for doors and the start)."""
        self.current = self.get_map(name)
        c, r = tile
        self.player = Player(((c + 0.5) * T, (r + 0.5) * T))

    def _enter_side(self, name, exit_side):
        """Enter an outdoor map through the side opposite to where the player left."""
        target = self.get_map(name)
        arrive = OPPOSITE[exit_side]
        x, y = self.player.pos.x, self.player.pos.y

        if arrive == "S":
            y = (target.height - 1.5) * T
        elif arrive == "N":
            y = 1.5 * T
        elif arrive == "E":
            x = (target.width - 1.5) * T
        else:
            x = 1.5 * T

        self.current = target
        self.player = Player((x, y))
        self.player.clamp(target.width * T, target.height * T)

    def check_transitions(self):
        m = self.current
        pos = self.player.pos
        w, h = m.width * T, m.height * T

        side = None
        if pos.x < 0:
            side = "W"
        elif pos.x > w:
            side = "E"
        elif pos.y < 0:
            side = "N"
        elif pos.y > h:
            side = "S"

        if side:
            target = m.links.get(side)
            if target:
                self._enter_side(target, side)
            else:
                self.player.clamp(w, h)
            return

        tile = (int(pos.x // T), int(pos.y // T))
        if tile in m.doors:
            target, spawn = m.doors[tile]
            self._enter_tile(target, spawn)

    # Interaction

    def interact(self):
        reach = S.INTERACT_RANGE * T
        for npc in self.current.npcs:
            if self.player.pos.distance_to(npc.centre) <= reach:
                self.dialogue = DialogueBox(npc.name, npc.lines)
                return
        for stall in self.current.stalls:
            if self.player.pos.distance_to(stall) <= reach:
                self.dialogue = DialogueBox("Market Stall", ["Shops open soon. Keep exploring!"])
                return

    # Main loop

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
                if self.dialogue:
                    if self.dialogue.advance():
                        self.dialogue = None
                else:
                    self.interact()

    def update(self, dt):
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        self.player.move(dx, dy, dt, self.current.collides)
        self.check_transitions()

    def draw(self):
        self.screen.fill(S.BG_COLOR)
        m = self.current
        offset = ((S.SCREEN_W - m.width * T) // 2, (S.SCREEN_H - m.height * T) // 2)
        m.render(self.screen, offset)
        self.player.draw(self.screen, offset)
        draw_hud(self.screen, self.state)
        if self.dialogue:
            self.dialogue.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(S.FPS) / 1000
            for event in pygame.event.get():
                self.handle_event(event)
            if self.dialogue is None:
                self.update(dt)
            self.draw()
        pygame.quit()
        assets.report_missing()
