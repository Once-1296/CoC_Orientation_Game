import pygame

from . import assets
from . import settings as S
from .combat import SHIELD_SPEED, Combat
from .effects import FloatText
from .maps import MAPS, START_MAP
from .menu import Menu
from .minigames import MINIGAMES
from .minigames.base import DIFFICULTIES, DIFFICULTY_DETAIL
from .physics import nearest_free
from .player import Player
from . import shop
from .inventory import draw_inventory
from .ui import DialogueBox, draw_hud
from .world import Map

T = S.TILE_SIZE
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
REPLAY_REWARD = 2        # coins for winning a mini game again on the same difficulty


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((S.SCREEN_W, S.SCREEN_H))
        pygame.display.set_caption(S.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Shared progress. Quests and mini game unlocks read and write this.
        self.state = {
            "coins": 0,
            "rocks": 0,
            "fish": 0,
            "snow": 0,
            "slimes": 0,
            "potions": 0,
            "sword_level": 0,
            "speed_level": 0,
            "hp": S.PLAYER_MAX_HP,          # half-hearts
            "max_hp": S.PLAYER_MAX_HP,
            "minigames_done": set(),
            "clears": {},                    # "game:difficulty" -> number of wins
        }
        self.maps = {}
        self.dialogue = None
        self.menu = None
        self.inventory_open = False
        self.minigame = None
        self.minigame_npc = None         # name of the NPC who started the current mini game
        self.combat = Combat()

        start = MAPS[START_MAP]
        self._enter_tile(START_MAP, start["spawn"])
        assets.play_music("music_town", volume=0.4)

    # Map loading and transitions

    def get_map(self, name):
        if name not in self.maps:
            self.maps[name] = Map(name, MAPS[name])
        return self.maps[name]

    def _place_player(self, m, pos):
        """Put the player at pos, or at the nearest spot where they fit (never inside a tree)."""
        pos = nearest_free(pygame.Vector2(pos), S.PLAYER_HITBOX, m.collides)
        self.player = Player(pos)
        self.player.clamp(m.width * T, m.height * T)

    def _enter_tile(self, name, tile):
        """Enter a map at the centre of a tile (used for doors and the start)."""
        self.current = self.get_map(name)
        c, r = tile
        self._place_player(self.current, ((c + 0.5) * T, (r + 0.5) * T))

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
        self._place_player(target, (x, y))

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

    def respawn(self):
        """Called when HP runs out. The player wakes up at home with full health."""
        self.state["hp"] = self.state["max_hp"]
        self.combat.reset()
        self._enter_tile(START_MAP, MAPS[START_MAP]["spawn"])
        self.dialogue = DialogueBox("Mom", [
            "Oh no, sweetheart, look at you! Come here.",
            "Rest up at home for a while. Be more careful out there, okay?",
        ])

    def quest_rows(self):
        """(NPC, mini game title, item, count needed, finished) for every quest in the maps."""
        rows = []
        for data in MAPS.values():
            for npc in data.get("npcs", []):
                task = npc.get("task")
                if task:
                    rows.append((npc["name"], MINIGAMES[task["minigame"]].title, task["item"], task["count"],
                                 task["minigame"] in self.state["minigames_done"]))
        return rows

    # Interaction

    def interact(self):
        reach = S.INTERACT_RANGE * T
        for npc in self.current.npcs:
            if self.player.pos.distance_to(npc.centre) <= reach:
                self._talk(npc)
                return
        for stall in self.current.stalls:
            if self.player.pos.distance_to(stall) <= reach:
                self._open_shop()
                return

    def _talk(self, npc):
        if npc.shop:
            self.dialogue = DialogueBox(npc.name, npc.lines, on_close=self._open_shop)
            return

        task = npc.task
        if task is None:
            self.dialogue = DialogueBox(npc.name, npc.lines)
            return

        name = task["minigame"]
        if name in self.state["minigames_done"]:
            # Finished the quest already: the NPC offers a replay.
            self.dialogue = DialogueBox(npc.name, task["done"],
                                        on_close=lambda: self._offer_difficulty(npc.name, name))
            return

        have, need = self.state[task["item"]], task["count"]
        if have < need:
            self.dialogue = DialogueBox(npc.name, task["todo"] + [f"Progress: {have}/{need} {task['item']}."])
            return

        # Task done: give the intro, then choose a difficulty.
        self.dialogue = DialogueBox(npc.name, task["ready"],
                                    on_close=lambda: self._offer_difficulty(npc.name, name))

    def _open_shop(self):
        self.menu = Menu("Merchant", shop.options(self.state), on_choose=self._shop_choose,
                         on_cancel=self._close_menu)

    def _shop_choose(self, item):
        self.menu = None
        if item == "leave":
            return
        message = shop.buy(self.state, item)
        self.dialogue = DialogueBox("Merchant", [message], on_close=self._open_shop)

    def _drink_potion(self):
        if self.state["potions"] <= 0:
            self.combat.popups.append(FloatText("No potions", self.player.pos + (0, -26)))
        elif self.state["hp"] >= self.state["max_hp"]:
            self.combat.popups.append(FloatText("Already full", self.player.pos + (0, -26)))
        else:
            self.state["potions"] -= 1
            self.state["hp"] = min(self.state["max_hp"], self.state["hp"] + shop.POTION_HEAL)
            self.combat.popups.append(FloatText("+1 heart", self.player.pos + (0, -26), (255, 120, 140)))

    def _offer_difficulty(self, npc_name, name):
        game_class = MINIGAMES[name]
        options = [
            (f"{d.capitalize()}   {game_class.reward_for(d)} coins", DIFFICULTY_DETAIL[d], d)
            for d in DIFFICULTIES
        ]
        self.menu = Menu(
            f"{game_class.title}: choose a difficulty",
            options,
            on_choose=lambda difficulty: self._choose_difficulty(name, npc_name, difficulty),
            on_cancel=self._close_menu,
        )

    def _close_menu(self):
        self.menu = None

    def _choose_difficulty(self, name, npc_name, difficulty):
        self.menu = None
        self._start_minigame(name, npc_name, difficulty)

    def _start_minigame(self, name, npc_name, difficulty="normal"):
        self.minigame = MINIGAMES[name](difficulty)
        self.minigame_npc = npc_name

    def _end_minigame(self):
        game, npc_name = self.minigame, self.minigame_npc
        self.minigame = None
        if game.result == "won":
            key = f"{game.name}:{game.difficulty}"
            first_clear = key not in self.state["clears"]
            self.state["clears"][key] = self.state["clears"].get(key, 0) + 1
            reward = game.REWARD if first_clear else REPLAY_REWARD
            self.state["coins"] += reward
            self.state["minigames_done"].add(game.name)
            if first_clear:
                text = f"Well done at {game.title}! Here are {reward} coins."
            else:
                text = f"Nice run again! Here are {reward} coins for practice."
            self.dialogue = DialogueBox(npc_name, [text])
        elif game.result == "lost":
            self.dialogue = DialogueBox(npc_name, ["Not this time. Want to try again?"],
                                        on_close=lambda: self._offer_difficulty(npc_name, game.name))

    # Main loop

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if self.minigame and event.type == pygame.MOUSEBUTTONDOWN:
            self.minigame.handle_event(event)
            return
        if event.type != pygame.KEYDOWN:
            return

        if self.minigame:
            if event.key == pygame.K_ESCAPE:
                self.minigame.abort()
            else:
                self.minigame.handle_event(event)
            return

        if self.menu:
            if event.key == pygame.K_ESCAPE:
                self.menu = None
            else:
                self.menu.handle_event(event)
            return

        if self.inventory_open:
            if event.key in (pygame.K_i, pygame.K_ESCAPE):
                self.inventory_open = False
            return

        if event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.key == pygame.K_i and self.dialogue is None:
            self.inventory_open = True
        elif event.key == pygame.K_q and self.dialogue is None:
            self._drink_potion()
        elif event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
            if self.dialogue:
                if self.dialogue.advance():
                    on_close = self.dialogue.on_close
                    self.dialogue = None
                    if on_close:
                        on_close()
            else:
                self.interact()
        elif event.key == pygame.K_j and self.dialogue is None:
            self.combat.start_swing()

    def update(self, dt):
        keys = pygame.key.get_pressed()

        if self.minigame:
            self.minigame.update(dt, keys)
            if self.minigame.finished:
                self._end_minigame()
            return

        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        shield = bool(keys[pygame.K_k] or keys[pygame.K_x])
        speed = SHIELD_SPEED if shield and not self.combat.swinging else 1.0
        speed *= 1 + shop.SPEED_BONUS * self.state["speed_level"]

        self.player.move(dx, dy, dt, self.current.collides, speed)
        self.check_transitions()

        # Enemies use the stricter collision, so they can never walk out through an exit gap.
        enemy_collides = lambda rect: self.current.collides(rect, through_exits=False)
        for enemy in self.current.enemies:
            if enemy.alive:
                enemy.update(dt, self.player.pos, enemy_collides)
        self.combat.update(dt, self.current, self.player, self.state, shield)

        if self.state["hp"] <= 0:
            self.respawn()

    def draw(self):
        if self.minigame:
            self.minigame.draw(self.screen)
            pygame.display.flip()
            return

        self.screen.fill(S.BG_COLOR)
        m = self.current
        offset = ((S.SCREEN_W - m.width * T) // 2, (S.SCREEN_H - m.height * T) // 2)
        m.render(self.screen, offset)
        self.player.draw(self.screen, offset)
        self.combat.draw(self.screen, offset, self.player)
        draw_hud(self.screen, self.state)
        if self.dialogue:
            self.dialogue.draw(self.screen)
        if self.menu:
            self.menu.draw(self.screen)
        if self.inventory_open:
            draw_inventory(self.screen, self.state, self.quest_rows())
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(S.FPS) / 1000
            for event in pygame.event.get():
                self.handle_event(event)
            if self.dialogue is None and self.menu is None and not self.inventory_open:
                self.update(dt)
            self.draw()
        pygame.quit()
        assets.report_missing()
