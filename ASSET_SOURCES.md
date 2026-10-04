# Asset Sources

The game runs without any art or sound. Every asset has a placeholder that is drawn
in code when the real file is missing. To replace a placeholder, put a file with the
exact name listed below into the matching folder. No code changes are needed.

```
assets/images/tile_grass.png     -> replaces the grass placeholder
assets/sounds/sfx_slash.wav      -> replaces the slash sound
```

## 1. Where to find assets

| Source | Notes |
|---|---|
| [Kenney.nl](https://kenney.nl/assets) | CC0. Large top-down tilesets (Tiny Town, Tiny Dungeon, Pixel Platformer, UI packs). Best first choice. |
| [itch.io](https://itch.io/game-assets/free/tag-top-down) | Filter by *Free*, *2D*, *Top-down*, *Tileset*. Check the licence on each page. |
| [OpenGameArt.org](https://opengameart.org) | Many packs. Check the licence on each one. |
| [Freesound.org](https://freesound.org) | Sound effects. Filter by *CC0*. |
| [Pixabay](https://pixabay.com/sound-effects/) | Free sound effects and music. Pixabay licence. |

## 2. Licences

Accept:
- **CC0 / Public Domain**: no credit required (still recommended).
- **CC-BY**: credit required. Add it to `CREDITS.md`.

Avoid:
- **Non-commercial (NC)** and **GPL** licences. Not suitable for a shared project.
- Assets with no licence stated, or that come from someone else's game.

## 3. Required names and sizes

The tile size is `TILE_SIZE` in `game/settings.py` (default **32 × 32** px). Sprite
frames should use the same size. Use PNG with transparency.

### Tiles (32 × 32)
`tile_grass`, `tile_path`, `tile_water`, `tile_rock`, `tile_snow`, `tile_wood_floor`,
`tile_wall`, `tile_tree`, `tile_bush`, `tile_sand`

### Player (32 × 32, one frame per direction)
`player_up`, `player_down`, `player_left`, `player_right`

### NPCs and enemies
`npc_<id>` (one per NPC, for example `npc_elder`), `enemy_slime`

### Items and props
`item_rock`, `item_coin`, `item_fish`, `shop_stall`, `house`

### UI (any size, scaled by code)
`dialogue_box`, `icon_coin`, `icon_shield`, `icon_sword`

### Sounds (`assets/sounds/`, WAV or OGG)
`sfx_slash`, `sfx_block`, `sfx_pickup`, `music_town`

Sound and music files are optional. Missing ones are silently skipped.

## 4. Suggested packs per region

| Region | Look | Suggested search |
|---|---|---|
| Town circle and home | Warm village, market stalls | "tiny town top-down" (Kenney) |
| North: rocky mountain | Grey rock, dry grass | "rock tileset top-down" |
| East: dark green woods | Dense trees, dark grass | "forest tileset top-down" |
| South: lakeside | Water, sand, shore | "water tileset top-down" |
| West: snowy mountains | Snow, ice, pines | "snow tileset top-down" |
| Characters | One hero, a few NPCs | "16x16 / 32x32 character top-down" |

Mixing packs is fine as long as the tile size matches. If a pack uses 16 × 16 tiles,
either scale it up with a nearest-neighbour resize (for example in GIMP or Aseprite)
or change `TILE_SIZE`.

## 5. How to install

1. Download the pack and extract it.
2. Pick the image you want and rename it to the exact name from section 3.
3. Copy it into `assets/images/` (or `assets/sounds/` for audio).
4. Run the game. The placeholder is replaced automatically.

To see which assets are still placeholders, run:

```bash
DEBUG_ASSETS=1 python main.py
```

The game prints the names of any missing assets on startup.

## 6. Credits

Keep `CREDITS.md` up to date. One line per asset used:

```
| File | Author | Licence | Source URL |
|---|---|---|---|
| assets/images/tile_grass.png | Kenney | CC0 | https://kenney.nl/... |
```
