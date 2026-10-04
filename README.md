# CoC Orientation Game

A small 2D top-down game made with Pygame. The player starts at home, walks out into the
town circle, and takes one of four exits into the regions described in `IDEA.md`. Each region
has enemies, things to collect, and a quest from a local NPC. Finishing a quest unlocks a
mini game, and you can replay those mini games on three difficulty levels.

This README describes the game as it is now. For the original design, see `IDEA.md`.

## Contents

- [Setup and running](#setup-and-running)
- [Controls](#controls)
- [The world](#the-world)
- [Combat and health](#combat-and-health)
- [Quests and mini games](#quests-and-mini-games)
- [Shop, potions and upgrades](#shop-potions-and-upgrades)
- [Inventory](#inventory)
- [Project structure](#project-structure)
- [Assets](#assets)
- [Tools](#tools)
- [Current limitations](#current-limitations)

## Setup and running

Tested with Python 3.12 and pygame-ce 2.5.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # pygame-ce, and pillow for the asset tool
python main.py
```

To print the placeholder assets that are still in use when the game closes:

```bash
DEBUG_ASSETS=1 python main.py
```

## Controls

| Key | Where | Action |
|---|---|---|
| Arrow keys or WASD | World | Move |
| E, Space or Enter | World | Talk to an NPC, open a stall, advance dialogue |
| J | World | Sword swing |
| K or X (hold) | World | Shield. Blocks hits from the front, and slows movement |
| Q | World | Drink a health potion (restores one heart) |
| I | World | Open or close the inventory |
| Esc | World | Quit the game |
| Arrow keys or W/S, then Enter | Menus and shop | Choose an option. Esc cancels |
| Left / Right (or A / D) | Meteor Shower | Move left and right |
| Left / Right (or A / D) | Snowball Fight | Switch lane |
| Up / Down (or W / S) | Snowball Fight | Move up and down |
| Arrows or WASD, Space | Fishing Mania | Move the boat. Space casts, sets the hook, or reels in |
| Shift + arrow | Fishing Mania | While hooked: match the yellow arrow to keep the line tight |
| Space (spam) | Fishing Mania | While hooked: reel the fish in |
| F | Fishing Mania | Finish early, once you have reached the target |
| Arrow keys or W/A/S/D, then Enter or Space | Peek-A-Bush | Move the cursor and mark or unmark a bush. Mouse click also works |
| F | Peek-A-Bush | Submit your marks now, without waiting for the timer |
| Esc | Mini games | Leave the mini game. No reward is paid |

## The world

The town circle is the hub. Its four exits lead to the regions, and each region has an exit
back to town on the opposite side. Walking off the map is blocked everywhere except those exit
gaps. When you enter a region, you arrive on the side that leads back to town.

| Area | Terrain | Enemies | Pickups | NPC and quest |
|---|---|---|---|---|
| Home | Wooden floor, walls | none | none | Mom. Your starting point and where you wake up after a blackout |
| Town circle | Grass, paths, a house with a door, market stalls | none | none | Elder, Guide, and the Merchant (shop) |
| North: rocky mountain | Rock and grass with a winding path | 3 slimes | 4 rocks | Miner: Meteor Shower |
| East: dark green woods | Trees, bushes, clearings | 3 slimes | none | Hunter: Peek-A-Bush |
| South: lakeside | Sand, a lake, a pier across it | 3 slimes | 4 fish on the shore | Fisher: Fishing Mania |
| West: snowy mountains | Snow, rock, pine trees | 3 slimes | 4 snow piles | Hermit: Snowball Fight |

Trees, rocks, water, walls, and stalls block movement. Everything outside the map is solid.
Slimes stay inside their region.

## Combat and health

- **Sword (J):** swings in the direction you face. The swing has a short cooldown.
- **Shield (K or X):** hold to block hits from the front. Blocked hits cost nothing and push the
  enemy back. Shielding slows you down, and you can't swing while shielding.
- **Slimes:** each has 3 HP at the start. The base sword deals 1 damage, so a slime takes 3 hits.
  Each sword upgrade adds 1 damage, so two upgrades kill a slime in one hit. A defeated slime
  drops a coin.
- **Health:** you start with 3 hearts, and the maximum is 5. Health is tracked in half-hearts, so
  a slime touch costs half a heart. After touching a slime you are briefly invulnerable.
- **Dying:** at zero health you wake up at home with full health. Mom says something about it.
- **Hearts on screen:** the top-right corner shows your hearts as full, half, or empty.

## Quests and mini games

Each region's NPC gives a quest. Bring what they ask for, then choose a difficulty and play the
mini game. Each game pays its reward on the first win at each difficulty. Repeat wins pay only
2 coins, so you can practise without farming coins.

| Quest | NPC | Needs | Mini game |
|---|---|---|---|
| Rocks for the falling-rocks lesson | Miner (north) | 3 rocks | Meteor Shower |
| Defeat slimes | Hunter (east) | 4 slimes defeated (any region) | Peek-A-Bush |
| Fish from the shore | Fisher (south) | 3 fish | Fishing Mania |
| Snow for rolling | Hermit (west) | 4 snow piles | Snowball Fight |

Losing a game offers an immediate retry. Once a quest is finished, its NPC offers to play again.

The difficulty menu appears after the NPC's briefing. Each game has its own Easy, Normal, and Hard
settings. Rewards at each level:

| Mini game | Easy | Normal | Hard |
|---|---|---|---|
| Meteor Shower | 8 coins. 25 s, 4 lives | 10 coins. 30 s, 3 lives | 18 coins. 40 s, 2 lives |
| Peek-A-Bush | 8 coins. 3 rounds, 1-2 creatures | 12 coins. 5 rounds, 2-3 creatures | 18 coins. 4×4 bushes, 4-6 creatures |
| Fishing Mania | 8 coins. 75 s, target 10 | 12 coins. 60 s, target 12 | 18 coins. 50 s, target 16 |
| Snowball Fight | 8 coins. 35 s, target size 8 | 12 coins. 30 s, target size 10 | 18 coins. 25 s, target size 13 |

### Meteor Shower (north)
Dodge rocks as they fall. Rocks get faster and bigger over time. You lose a life when a rock hits
you, and you win by surviving until the timer runs out.

### Peek-A-Bush (east)
Creatures pop out of bushes for a couple of seconds. Then you mark the bushes that had creatures
before the timer runs out. Marking a bush with no creature loses the game at once. Missing a
creature loses the round, and that also loses the game. Win by clearing every round. Press **F** to
submit early.

### Fishing Mania (south)
Cast the line with Space and wait. Fish swim around the lake and bite when they drift close to the
bobber. Press Space in the short bite window to set the hook. A hooked fish pulls in a direction
shown by a yellow arrow. Hold Shift and press that arrow to keep the line tight. Each Space press
reels the fish in. Bigger fish pull harder and run faster. If the tension drops to zero, the line
snaps. A fish that doesn't bite for a while is reeled in automatically. Fish are worth 1, 2, or 3
points. Medium and big fish are the most common. Once you reach the target, press **F** to finish
early.

### Snowball Fight (west)
Roll your snowball down three lanes. Pick up snow piles to grow it, and avoid rocks, which shrink
it. The snowball size at the end is your score, and the target is size 10 at Normal.

## Shop, potions and upgrades

Talk to the Merchant in town, or open a market stall, to browse the shop. Everything costs coins.

| Item | Price | Effect |
|---|---|---|
| Health potion | 5 coins | Restores one heart. Press Q to drink it. You can carry up to 5 |
| Sharper sword | 10, then 20 coins | +1 sword damage per level, up to 2 levels |
| Running shoes | 8, then 16 coins | +20% running speed per level, up to 2 levels |
| Extra heart | 12, then 20 coins | +1 heart of maximum health, and it fills immediately. Up to 5 hearts |

The shop reopens after each purchase. Sold-out upgrades are marked.

## Inventory

Press **I** to open the inventory. It lists your coins, rocks, snow piles, fish, slimes defeated,
and health potions. Under that, each quest shows its progress, and finished quests are marked
"done". The rock counter is only in the inventory, not on the main screen.

## Project structure

```
main.py                    entry point
game/
  settings.py              screen size, tile size, speeds, starting health
  game.py                  main loop, map transitions, quests, shop, menus, mini game routing
  maps.py                  every map: layout, exits, doors, NPCs, enemies, pickups, quests
  world.py                 Map class: tile grid, collision, pre-rendered background
  player.py                player movement, facing, walk animation
  physics.py               shared tile collision with corner sliding, and free-spot search
  combat.py                sword swings, shield blocks, contact damage, pickup collection
  enemies.py               slimes: wander, chase, knockback
  npc.py                   NPCs, with optional quests and shop flag
  items.py                 pickups on the ground (coins, rocks, fish, snow)
  shop.py                  shop items, prices and purchase rules
  inventory.py             the I inventory overlay
  menu.py                  simple list menu, used for difficulty and the shop
  ui.py                    dialogue box, HUD, hearts
  effects.py               floating "+1 fish" style messages
  assets.py                image, sound and animation loading, with placeholders
  minigames/
    base.py                MiniGame base class, difficulty presets
    meteor_shower.py       Meteor Shower
    peek_a_bush.py         Peek-A-Bush
    fishing.py             Fishing Mania
    snowball.py            Snowball Fight
tools/
  resize_assets.py         Pillow script: scales images to 32×32
```

Each mini game keeps its tuning values as class constants. The difficulty presets override them
for each run.

## Assets

Art and sound live in `assets/images/` and `assets/sounds/`. Only those two folders are tracked by
git. Everything else under `assets/` (the art packs and archives) is ignored. See `.gitignore`.

If a file is missing, the game draws a placeholder in its place, so it still runs. See
[ASSET_SOURCES.md](ASSET_SOURCES.md) for what is still missing and where to find more.

- **Sprites:** 32×32 tiles and characters. The player and NPCs use the 4-frame walk animation.
- **Heart sheet:** `assets/images/ui/Heart_Health_Bar.png` is a 24×56 sprite sheet. It is kept at
  its native size, and the game cuts out the full, half, and empty hearts from it.
- **Sounds:** `.wav` for sound effects (`sfx_slash`, `sfx_block`, `sfx_pickup`) and `.ogg` for the
  town music (`music_town`).

To make every image 32×32 (the `ui/` folder is skipped, so the heart sheet keeps its size):

```bash
python tools/resize_assets.py --dry-run   # preview
python tools/resize_assets.py             # resize in place
```

## Tools

- `tools/resize_assets.py`: resizes every PNG under `assets/images/` to 32×32 with Pillow. Images
  are fitted and centred on a transparent canvas, and pixel art stays sharp. The files are
  overwritten, so run it with `--dry-run` first.

## Current limitations

- **No saving.** Progress lasts only while the game is running.
- **No selling.** The Merchant only sells. Fish, rocks, and snow can't be sold yet.
- **Placeholder art** for the house door and the market stall. The snow pickup is a plain white circle.
- **Balance is untested by players.** The mini game numbers are first guesses.
- **No automated tests in the repository.** Testing has been done by scripts, and they are not
  committed yet.
