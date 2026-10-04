"""Quests, difficulty menus, replays, the shop, potions, hearts and the inventory."""
import pygame
import pytest

from game import settings as S
from game import shop
from game.maps import MAPS
from game.minigames import MINIGAMES
from game.ui import draw_health

from conftest import key_event

T = S.TILE_SIZE
DT = 1 / 60


def _npc(game, map_name, npc_id):
    game._enter_tile(map_name, (9, 9))
    npc = next(n for n in game.current.npcs if n.id == npc_id)
    game.player.pos = pygame.Vector2(npc.centre.x + 20, npc.centre.y)
    return npc


@pytest.mark.parametrize("map_name, npc_id, item, need, game_name", [
    ("mountain_rock", "miner", "rocks", 3, "meteor_shower"),
    ("woods", "hunter", "slimes", 4, "peek_a_bush"),
    ("lakeside", "fisher", "fish", 3, "fishing"),
    ("mountain_snow", "hermit", "snow", 4, "snowball"),
])
def test_quest_asks_for_items_then_offers_the_difficulty_menu(game, map_name, npc_id, item, need, game_name):
    npc = _npc(game, map_name, npc_id)
    game.state[item] = need - 1
    game.interact()
    assert f"{need - 1}/{need}" in game.dialogue.lines[-1]

    game.dialogue = None
    game.state[item] = need
    game.interact()
    on_close = game.dialogue.on_close
    game.dialogue = None
    on_close()
    assert game.menu is not None and game.menu.title.startswith(MINIGAMES[game_name].title)


def test_difficulty_choice_starts_the_mini_game_with_that_difficulty(game):
    game._choose_difficulty("peek_a_bush", "Hunter", "hard")
    assert game.minigame.name == "peek_a_bush"
    assert game.minigame.difficulty == "hard"
    assert game.minigame.GRID == 4


def test_first_clear_pays_full_reward_and_repeats_pay_two(game):
    game.state["clears"] = {}
    game._start_minigame("peek_a_bush", "Hunter", "easy")
    game.minigame.result = "won"
    game._end_minigame()
    assert game.state["coins"] == 8

    game._start_minigame("peek_a_bush", "Hunter", "easy")
    game.minigame.result = "won"
    game._end_minigame()
    assert game.state["coins"] == 10


def test_a_loss_offers_an_immediate_retry(game):
    game._start_minigame("meteor_shower", "Miner", "normal")
    game.minigame.result = "lost"
    game._end_minigame()
    on_close = game.dialogue.on_close
    game.dialogue = None
    on_close()
    assert game.menu is not None


def test_finished_quest_offers_a_replay(game):
    game.state["minigames_done"].add("fishing")
    npc = _npc(game, "lakeside", "fisher")
    game.interact()
    on_close = game.dialogue.on_close
    game.dialogue = None
    on_close()
    assert game.menu is not None


def test_respawn_comes_from_mom_at_home_with_full_health(game):
    game._enter_tile("woods", (4, 6))
    game.state["hp"] = 0
    game.update(DT)
    assert game.current.name == "home"
    assert game.state["hp"] == game.state["max_hp"]
    assert game.dialogue.speaker == "Mom"


# Shop

def test_potions_need_coins_and_cap_at_five():
    state = {"coins": 0, "potions": 0, "max_hp": 6, "hp": 6, "sword_level": 0, "speed_level": 0}
    shop.buy(state, "potion")
    assert state["potions"] == 0
    state["coins"] = 100
    for _ in range(10):
        shop.buy(state, "potion")
    assert state["potions"] == shop.MAX_POTIONS


def test_extra_hearts_stop_at_five():
    state = {"coins": 1000, "potions": 0, "max_hp": 6, "hp": 6, "sword_level": 0, "speed_level": 0}
    for _ in range(4):
        shop.buy(state, "heart")
    assert state["max_hp"] == 10
    assert state["hp"] == 10


def test_sword_and_shoes_stop_at_their_maximum():
    state = {"coins": 1000, "potions": 0, "max_hp": 6, "hp": 6, "sword_level": 2, "speed_level": 2}
    assert "sold out" in shop.buy(state, "sword")
    assert "sold out" in shop.buy(state, "shoes")
    assert state["coins"] == 1000


def test_potion_heals_one_heart_and_is_used_with_q(game):
    game.state.update(hp=4, max_hp=10, potions=1)
    game._enter_tile("town", (5, 5))
    game.handle_event(key_event(pygame.K_q))
    assert game.state["hp"] == 6
    assert game.state["potions"] == 0


def test_potion_is_not_used_at_full_health(game):
    game.state.update(hp=10, max_hp=10, potions=1)
    game._enter_tile("town", (5, 5))
    game.handle_event(key_event(pygame.K_q))
    assert game.state["potions"] == 1


def test_running_shoes_are_forty_percent_faster_at_level_two():
    def distance(level):
        state = {"speed_level": level}
        from game.player import Player
        from game.world import Map
        from game.maps import MAPS as M
        m = Map("town", M["town"])
        p = Player((300, 180))
        start = p.pos.x
        p.move(1, 0, 0.5, m.collides, 1 + shop.SPEED_BONUS * state["speed_level"])
        return p.pos.x - start
    assert abs(distance(2) / distance(0) - 1.4) < 0.02


def test_merchant_opens_the_shop_after_his_greeting(game):
    game._enter_tile("town", (13, 5))
    merchant = next(n for n in game.current.npcs if n.id == "merchant")
    game.player.pos = pygame.Vector2(merchant.centre.x - 20, merchant.centre.y)
    game.interact()
    on_close = game.dialogue.on_close
    game.dialogue = None
    on_close()
    assert game.menu.title == "Merchant"


def test_buying_a_sword_upgrade_reopens_the_shop(game):
    game.state.update(coins=100, sword_level=0)
    game._open_shop()
    game._shop_choose("sword")
    assert game.state["sword_level"] == 1
    on_close = game.dialogue.on_close
    game.dialogue = None
    on_close()
    assert game.menu is not None


# Hearts and the inventory

@pytest.mark.parametrize("units", range(0, 11))
def test_hearts_draw_for_every_value_up_to_five_hearts(game, units):
    draw_health(game.screen, units, 10, S.SCREEN_W, 10)


def test_inventory_toggles_with_i_and_lists_four_quests(game):
    game.handle_event(key_event(pygame.K_i))
    assert game.inventory_open
    game.handle_event(key_event(pygame.K_i))
    assert not game.inventory_open
    assert len(game.quest_rows()) == 4


def test_quests_come_from_the_map_data():
    quest_count = sum(1 for data in MAPS.values() for npc in data.get("npcs", []) if npc.get("task"))
    assert quest_count == 4
