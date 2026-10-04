# CoC Orientation Game

A small 2D top-down game in Pygame. The player starts at home, walks through the
town circle, and takes one of four exits to explore the regions in `IDEA.md`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

To list the placeholder assets that are still in use when the game closes:

```bash
DEBUG_ASSETS=1 python main.py
```

## Controls

| Key | Action |
|---|---|
| Arrow keys / WASD | Move |
| E / Space / Enter | Talk, use shop, advance dialogue |
| J | Sword swing |
| K / X (hold) | Shield. Blocks hits from the front. Slows movement. |
| Shift + arrow (fishing) | Keep the line tight: match the yellow arrow |
| Esc | Quit (or leave a mini game / menu) |

## Assets

Art and sound live in `assets/images/` and `assets/sounds/`. Missing files fall back to
placeholders. See [ASSET_SOURCES.md](ASSET_SOURCES.md) for what is still needed.

To make every image 32×32 (uses Pillow, installed by `requirements.txt`):

```bash
python tools/resize_assets.py --dry-run   # preview
python tools/resize_assets.py             # resize in place
```
