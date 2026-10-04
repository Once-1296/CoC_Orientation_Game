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
| Esc | Quit |

## Assets

Art and sound are placeholders for now. See [ASSET_SOURCES.md](ASSET_SOURCES.md) for
where to find free assets and how to swap them in.
