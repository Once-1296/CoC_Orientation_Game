# Asset Sources

The game runs without any art or sound. Every asset has a placeholder drawn in code
when its file is missing. To replace a placeholder, put a file with the expected name
into `assets/images/` (or `assets/sounds/`). No code changes are needed.

## 1. What is already in place

| Asset | Location | Used for |
|---|---|---|
| Tiles (`tile_grass`, `tile_path`, `tile_water`, `tile_rock`, `tile_snow`, `tile_wood_floor`, `tile_wall`, `tile_tree`, `tile_bush`, `tile_sand`) | `assets/images/tile_*.png` | Map terrain and home interior |
| Player (`NobleMan2`) | `assets/images/player/{FrontWalk,BackWalk,SideWalk}/` | Player. Front = down, Back = up, Side = left, and right is the side frames flipped. 4 frames each. |
| NPC female | `assets/images/npc1/FrontWalk/` | Mom and Guide |
| NPC male | `assets/images/npc2/FrontWalk/` | Elder, Merchant, Miner, Hunter, Fisher, Hermit |
| Coin icon | `assets/images/icon_coin.png` | HUD |
| Slime, sword, shield, fish, rock, coin item images | `assets/images/` | Not used yet (combat and mini games) |

All images in `assets/images/` are 32×32. Run `python tools/resize_assets.py` after adding
any new image that is a different size (see section 4).

## 2. Still missing

These two tiles are the only ones the map uses that have no file yet. The game draws
a placeholder for each.

| File name | Used for | Notes |
|---|---|---|
| `tile_door.png` | The door of the house, in town and in the home | Brown door, 32×32 |
| `shop_stall.png` | Market stalls in the town circle (tile `S`) | 32×32. Solid, so the player walks around it |

Sound effects and music are optional. Missing sounds are skipped silently.

| File name | Used for |
|---|---|
| `sfx_slash.wav` / `.ogg` | Sword swing (combat, later) |
| `sfx_block.wav` / `.ogg` | Shield block (combat, later) |
| `sfx_pickup.wav` / `.ogg` | Picking up items (later) |
| `music_town.ogg` | Town background music (later) |

The dialogue box is drawn by the game, so it needs no image.

## 3. Where to find more

| Source | Notes |
|---|---|
| [Kenney.nl](https://kenney.nl/assets) | CC0. Top-down tilesets and UI packs. Good source for doors and stalls. |
| [itch.io](https://itch.io/game-assets/free/tag-top-down) | Filter by *Free*, *2D*, *Top-down*. Check the licence on each page. |
| [OpenGameArt.org](https://opengameart.org) | Check each licence. |
| [Freesound.org](https://freesound.org) | Sound effects. Filter by *CC0*. |

Accept CC0 or CC-BY (credit required). Avoid non-commercial (NC) and GPL licences,
and any asset with no licence stated.

## 4. Resizing images

Images from different packs come in different sizes. `tools/resize_assets.py` scales
every PNG under `assets/images/` to 32×32 with Pillow:

```bash
source .venv/bin/activate
python tools/resize_assets.py --dry-run   # list what would change
python tools/resize_assets.py             # resize in place
```

Images are scaled to fit, keeping their aspect ratio, and centred on a transparent
32×32 canvas. Pixel art uses nearest-neighbour scaling so it stays sharp. The script
overwrites the files it changes, so keep the original packs somewhere safe.

## 5. Credits

Keep `CREDITS.md` up to date with one line per asset used:

```
| File | Author | Licence | Source URL |
|---|---|---|---|
| assets/images/tile_grass.png | Kenney | CC0 | https://kenney.nl/... |
```
