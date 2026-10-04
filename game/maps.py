"""Map layouts, exits, doors, NPCs, enemies and pickups.

Tile codes:
  g grass   p path   a sand    s snow    f wood floor  t tree
  r rock    w water  b bush    W wall    D door         S market stall

Solid tiles: w r W t b S. Everything else can be walked on.

Outdoor maps are 20x15 tiles. `outdoor()` builds the border ring from the
18x13 interior. Each side listed in `exits` gets a 2-tile wide gap of path.
Gaps line up between neighbouring maps, so the player arrives on the opposite side.
Obstacles sit in clusters with open ground between them.
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
    "g" + "RRRR" + "ggg" + "pp" + "ggg" + "SSS" + "gg",
    "g" + "RRRR" + "ggg" + "pp" + "ggg" + "SSS" + "gg",
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

# North: rocky mountain. A winding path leads up from the south exit.
MOUNTAIN = [
    "r" * 8 + "gg" + "r" * 8,
    "rrr" + "g" * 12 + "rrr",
    "rr" + "g" * 14 + "rr",
    "r" + "g" * 16 + "r",
    "g" * 18,
    "gg" + "rr" + "g" * 10 + "rr" + "gg",
    "g" * 6 + "rrr" + "g" * 8 + "r",
    "g" * 4 + "rr" + "g" * 8 + "rr" + "gg",
    "gg" + "rrr" + "ggg" + "pp" + "gggg" + "rr" + "gg",
    "ggg" + "r" + "gggg" + "pp" + "ggg" + "rr" + "ggg",
    "ggggg" + "rr" + "g" + "pp" + "g" * 6 + "rr",
    "g" * 8 + "pp" + "g" * 8,
    "g" * 8 + "pp" + "g" * 8,
]

# East: dark green woods with clearings. Exit to the west.
WOODS = [
    "t" * 18,
    "tt" + "gggg" + "tt" + "g" * 8 + "tt",
    "t" + "g" * 6 + "t" + "g" * 6 + "tt" + "gg",
    "g" * 6 + "ttt" + "g" * 4 + "t" + "g" * 4,
    "ggg" + "tt" + "g" * 8 + "tt" + "ggg",
    "gggg" + "tt" + "g" * 10 + "tt",
    "g" * 6 + "t" + "g" * 5 + "tt" + "g" * 4,
    "gg" + "tt" + "gggg" + "tt" + "g" * 8,
    "g" * 6 + "t" + "g" * 4 + "ttt" + "g" * 4,
    "g" * 4 + "tt" + "g" * 6 + "t" + "g" * 5,
    "gg" + "t" + "g" * 5 + "ttt" + "g" * 7,
    "g" * 8 + "tt" + "g" * 8,
    "g" * 10 + "tt" + "g" * 6,
]

# South: lakeside. A pier crosses the lake; sand paths run around it.
LAKE = [
    "a" * 18,
    "aaa" + "w" * 12 + "aaa",
    "aa" + "w" * 14 + "aa",
    "a" + "w" * 16 + "a",
    "a" + "w" * 16 + "a",
    "p" * 18,
    "a" + "w" * 16 + "a",
    "a" + "w" * 16 + "a",
    "aa" + "w" * 14 + "aa",
    "aaa" + "w" * 12 + "aaa",
    "a" * 6 + "bb" + "a" * 10,
    "a" * 18,
    "a" * 18,
]

# West: snowy mountains with pines. Exit to the east.
SNOW = [
    "r" * 18,
    "rr" + "s" * 8 + "rr" + "s" * 6,
    "s" * 3 + "tt" + "s" * 6 + "r" + "s" * 6,
    "s" * 2 + "t" + "s" * 4 + "rrr" + "s" * 8,
    "s" * 8 + "tt" + "s" * 8,
    "s" * 6 + "t" + "s" * 11,
    "s" * 4 + "tt" + "s" * 12,
    "s" * 2 + "rrr" + "s" * 6 + "tt" + "s" * 5,
    "s" * 5 + "r" + "s" * 4 + "t" + "s" * 7,
    "s" * 9 + "rr" + "s" * 4 + "t" + "s" * 2,
    "s" * 3 + "tt" + "s" * 5 + "rrr" + "s" * 5,
    "rr" + "s" * 14 + "rr",
    "r" + "s" * 16 + "r",
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
                "sprite": "npc1",
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
                "sprite": "npc2",
                "name": "Elder",
                "tile": (6, 10),
                "lines": ["Welcome to town circle.", "The market is to the east. The mountains are north."],
            },
            {
                "id": "guide",
                "sprite": "npc1",
                "name": "Guide",
                "tile": (13, 10),
                "lines": ["Four paths lead out of town.", "Each region has someone who can offer a challenge."],
            },
            {
                "id": "merchant",
                "sprite": "npc2",
                "name": "Merchant",
                "tile": (14, 5),
                "shop": True,
                "lines": ["Welcome! Take a look at my wares.", "Potions, sharper swords, faster shoes."],
            },
        ],
    },
    "mountain_rock": {
        "grid": outdoor("r", MOUNTAIN, "S"),
        "links": {"S": "town"},
        "enemies": [(6, 6), (14, 9), (5, 12)],
        "pickups": [("rock", (3, 5)), ("rock", (12, 4)), ("rock", (6, 10)), ("rock", (13, 12))],
        "npcs": [
            {
                "id": "miner",
                "sprite": "npc2",
                "name": "Miner",
                "tile": (4, 3),
                "lines": ["Watch out for falling rocks up here."],
                "task": {
                    "item": "rocks",
                    "count": 3,
                    "minigame": "meteor_shower",
                    "todo": [
                        "Falling rocks are a problem up here.",
                        "Bring me 3 rocks from the mountain and I'll show you how to dodge them.",
                    ],
                    "ready": [
                        "You found 3 rocks! Now let's see how well you dodge.",
                        "Move left and right to avoid the falling rocks for 30 seconds.",
                    ],
                    "done": ["You've got the hang of it! Keep your eyes up."],
                },
            },
        ],
    },
    "woods": {
        "grid": outdoor("t", WOODS, "W"),
        "links": {"W": "town"},
        "enemies": [(9, 5), (12, 8), (6, 11)],
        "npcs": [
            {
                "id": "hunter",
                "sprite": "npc2",
                "name": "Hunter",
                "tile": (4, 6),
                "lines": ["Stay on the paths. Slimes live deep in the woods."],
                "task": {
                    "item": "slimes",
                    "count": 4,
                    "minigame": "peek_a_bush",
                    "todo": [
                        "Slimes have been raiding my traps.",
                        "Defeat 4 slimes and I'll teach you to spot creatures hiding in the bushes.",
                    ],
                    "ready": [
                        "Good, you're handy with that sword. Now watch the bushes.",
                        "Creatures pop out for a moment. Mark the bushes they were in before time runs out.",
                    ],
                    "done": ["You have a sharp eye. Keep practising."],
                },
            },
        ],
    },
    "lakeside": {
        "grid": outdoor("a", LAKE, "N"),
        "links": {"N": "town"},
        "enemies": [(3, 11), (16, 11), (9, 13)],
        "pickups": [("fish", (11, 1)), ("fish", (2, 11)), ("fish", (15, 12)), ("fish", (8, 12))],
        "npcs": [
            {
                "id": "fisher",
                "sprite": "npc2",
                "name": "Fisher",
                "tile": (5, 1),
                "lines": ["The fish are biting today.", "Bring bait next time."],
                "task": {
                    "item": "fish",
                    "count": 3,
                    "minigame": "fishing",
                    "todo": [
                        "The fish are hiding today.",
                        "Bring me 3 fish from the shore and I'll take you out on the lake.",
                    ],
                    "ready": [
                        "Let's go out on the lake! Steer the boat and cast with Space.",
                        "When the fish bites, reel it in quickly with Space.",
                    ],
                    "done": ["Your catch was great. The lake thanks you."],
                },
            },
        ],
    },
    "mountain_snow": {
        "grid": outdoor("r", SNOW, "E"),
        "links": {"E": "town"},
        "enemies": [(12, 4), (14, 9), (5, 12)],
        "pickups": [("snow", (3, 3)), ("snow", (14, 8)), ("snow", (8, 12)), ("snow", (16, 11))],
        "npcs": [
            {
                "id": "hermit",
                "sprite": "npc2",
                "name": "Hermit",
                "tile": (4, 6),
                "lines": ["It is cold up here. Snowballs are useful, though."],
                "task": {
                    "item": "snow",
                    "count": 4,
                    "minigame": "snowball",
                    "todo": [
                        "The snow up here is perfect for rolling.",
                        "Gather 4 snow piles for me, then I'll show you how to roll a big snowball.",
                    ],
                    "ready": [
                        "Now roll the snowball down the lanes.",
                        "Pick up snow to grow it, and steer around the rocks.",
                    ],
                    "done": ["A fine snowball! You have a knack for rolling."],
                },
            },
        ],
    },
}

START_MAP = "home"
