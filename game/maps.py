"""Map layouts, exits, doors and NPC placement.

Tile codes:
  g grass   p path   a sand    s snow    f wood floor  t tree
  r rock    w water  b bush    W wall    D door         S market stall

Solid tiles: w r W t b S. Everything else can be walked on.

Outdoor maps are 20x15 tiles. `outdoor()` builds the border ring from the
18x13 interior. Each side listed in `exits` gets a 2-tile wide gap of path.
Gaps line up between neighbouring maps, so the player arrives on the opposite side.
"""


def outdoor(border, interior, exits):
    grid = [[border] * 20 for _ in range(15)]
    for r, row in enumerate(interior):
        for c, ch in enumerate(row):
            grid[r + 1][c + 1] = ch
    if "N" in exits:
        grid[0][9] = grid[0][10] = "p"
    if "S" in exits:
        grid[14][9] = grid[14][10] = "p"
    if "W" in exits:
        grid[6][0] = grid[7][0] = "p"
    if "E" in exits:
        grid[6][19] = grid[7][19] = "p"
    return ["".join(row) for row in grid]


TOWN = [
    "g" * 8 + "pp" + "g" * 8,
    "g" + "WWWW" + "ggg" + "pp" + "ggg" + "SSS" + "gg",
    "g" + "WWWW" + "ggg" + "pp" + "ggg" + "SSS" + "gg",
    "g" + "WWDW" + "ggg" + "pp" + "g" * 6 + "gg",
    "g" * 8 + "pp" + "g" * 8,
    "p" * 18,
    "p" * 18,
    "g" * 8 + "pp" + "g" * 8,
    "bb" + "g" * 6 + "pp" + "g" * 6 + "bb",
    "g" * 8 + "pp" + "g" * 8,
    "g" * 8 + "pp" + "g" * 8,
    "g" * 8 + "pp" + "g" * 8,
    "g" * 8 + "pp" + "g" * 8,
]

MOUNTAIN = [
    "r" * 18,
    "r" * 4 + "gg" + "r" * 4 + "gg" + "r" * 6,
    "r" * 2 + "g" * 5 + "r" * 3 + "g" * 3 + "r" * 5,
    "r" * 6 + "g" * 4 + "r" * 2 + "g" + "r" * 5,
    "r" * 3 + "g" * 6 + "r" * 9,
    "r" * 2 + "g" * 14 + "r" * 2,
    "r" * 5 + "g" * 8 + "r" * 5,
    "r" * 4 + "gg" + "r" * 3 + "g" * 4 + "r" * 5,
    "r" * 7 + "g" * 4 + "r" * 7,
    "r" * 3 + "g" * 12 + "r" * 3,
    "r" * 2 + "g" * 4 + "r" * 4 + "g" * 4 + "r" * 4,
    "r" * 6 + "g" * 6 + "r" * 6,
    "g" * 2 + "r" * 6 + "g" * 4 + "r" * 6,
]

WOODS = [
    "t" * 18,
    "t" * 2 + "g" * 3 + "t" * 5 + "b" * 2 + "t" * 6,
    "t" * 4 + "g" * 6 + "t" * 2 + "b" + "t" * 5,
    "t" + "g" * 3 + "b" * 2 + "t" * 4 + "g" * 4 + "t" * 4,
    "t" * 3 + "g" * 8 + "t" * 3 + "b" + "t" * 3,
    "g" * 6 + "t" * 3 + "g" * 4 + "t" * 5,
    "g" * 4 + "b" * 2 + "g" * 3 + "t" * 4 + "g" * 5,
    "t" * 2 + "g" * 5 + "t" * 3 + "g" * 8,
    "t" * 5 + "g" * 2 + "b" * 2 + "g" * 3 + "t" * 6,
    "t" * 3 + "g" * 4 + "t" * 2 + "g" * 6 + "t" * 3,
    "t" * 6 + "g" * 3 + "t" * 3 + "g" * 4 + "t" * 2,
    "t" * 4 + "g" * 8 + "t" * 6,
    "t" * 2 + "g" * 5 + "t" * 11,
]

LAKE = [
    "a" * 18,
    "a" * 3 + "w" * 12 + "a" * 3,
    "a" * 2 + "w" * 14 + "a" * 2,
    "a" + "w" * 16 + "a",
    "a" + "w" * 5 + "a" * 3 + "w" * 6 + "a" * 3,
    "a" * 2 + "w" * 4 + "g" * 4 + "w" * 4 + "a" * 4,
    "a" * 2 + "w" * 4 + "g" * 4 + "w" * 4 + "a" * 4,
    "a" * 3 + "w" * 12 + "a" * 3,
    "a" * 2 + "w" * 14 + "a" * 2,
    "a" * 5 + "w" * 8 + "a" * 5,
    "a" * 6 + "b" * 2 + "a" * 10,
    "a" * 18,
    "a" * 18,
]

SNOW = [
    "r" * 18,
    "r" * 3 + "s" * 6 + "r" * 2 + "s" * 4 + "r" * 3,
    "r" + "s" * 5 + "t" * 2 + "s" * 6 + "r" * 4,
    "s" * 3 + "r" * 4 + "s" * 4 + "t" * 2 + "s" * 5,
    "s" * 2 + "t" * 3 + "s" * 4 + "r" * 3 + "s" * 6,
    "s" * 5 + "r" * 2 + "s" * 11,
    "s" * 4 + "t" * 3 + "s" * 11,
    "s" * 6 + "r" * 3 + "s" * 4 + "t" * 2 + "s" * 3,
    "r" * 2 + "s" * 7 + "r" * 2 + "s" * 7,
    "s" * 3 + "t" * 4 + "s" * 6 + "r" * 2 + "s" * 3,
    "s" * 8 + "r" * 3 + "t" * 2 + "s" * 5,
    "r" * 4 + "s" * 10 + "r" * 4,
    "r" * 2 + "s" * 14 + "r" * 2,
]

MAPS = {
    "home": {
        "grid": [
            "WWWWWWWWWW",
            "WffffffffW",
            "WffffffffW",
            "WffffffffW",
            "WffffffffW",
            "WffffffffW",
            "WWWWDWWWWW",
        ],
        "spawn": (4, 5),
        "doors": {(4, 6): ("town", (4, 5))},
        "npcs": [
            {
                "id": "mom",
                "name": "Mom",
                "tile": (2, 2),
                "lines": [
                    "Good morning! The town circle is just outside.",
                    "Go talk to people. There are four ways out of town.",
                ],
            },
        ],
    },
    "town": {
        "grid": outdoor("t", TOWN, "NSEW"),
        "links": {"N": "mountain_rock", "S": "lakeside", "E": "woods", "W": "mountain_snow"},
        "doors": {(4, 4): ("home", (4, 5))},
        "npcs": [
            {
                "id": "elder",
                "name": "Elder",
                "tile": (6, 10),
                "lines": ["Welcome to town circle.", "The market is to the east. The mountains are north."],
            },
            {
                "id": "guide",
                "name": "Guide",
                "tile": (13, 10),
                "lines": ["Four paths lead out of town.", "Each region has someone who can offer a challenge."],
            },
            {
                "id": "merchant",
                "name": "Merchant",
                "tile": (14, 5),
                "lines": ["Shops are open soon. Come back later!"],
            },
        ],
    },
    "mountain_rock": {
        "grid": outdoor("r", MOUNTAIN, "S"),
        "links": {"S": "town"},
        "npcs": [
            {
                "id": "miner",
                "name": "Miner",
                "tile": (4, 3),
                "lines": ["Watch out for falling rocks up here."],
            },
        ],
    },
    "woods": {
        "grid": outdoor("t", WOODS, "W"),
        "links": {"W": "town"},
        "npcs": [
            {
                "id": "hunter",
                "name": "Hunter",
                "tile": (4, 6),
                "lines": ["Stay on the paths. Slimes live deep in the woods."],
            },
        ],
    },
    "lakeside": {
        "grid": outdoor("a", LAKE, "N"),
        "links": {"N": "town"},
        "npcs": [
            {
                "id": "fisher",
                "name": "Fisher",
                "tile": (5, 1),
                "lines": ["The fish are biting today.", "Bring bait next time."],
            },
        ],
    },
    "mountain_snow": {
        "grid": outdoor("r", SNOW, "E"),
        "links": {"E": "town"},
        "npcs": [
            {
                "id": "hermit",
                "name": "Hermit",
                "tile": (4, 6),
                "lines": ["It is cold up here. Snowballs are useful, though."],
            },
        ],
    },
}

START_MAP = "home"
