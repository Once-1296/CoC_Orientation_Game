DIFFICULTIES = ("easy", "normal", "hard")
DIFFICULTY_DETAIL = {
    "easy": "More time and forgiveness, smaller reward.",
    "normal": "The standard challenge.",
    "hard": "Faster and tougher, bigger reward.",
}


class MiniGame:
    """Base class for region mini games.

    The game loop forwards events, then calls update and draw while the mini game is active.
    When `result` is set, the game ends the mini game and hands out the reward.

    Each difficulty in PRESETS overrides the class constants below for that run.
    """

    name = "base"
    title = ""
    REWARD = 0               # coins given on a win at normal difficulty
    PRESETS = {}             # difficulty -> {CONSTANT: value}

    def __init__(self, difficulty="normal"):
        self.result = None   # None while playing, then "won", "lost" or "quit"
        self.difficulty = difficulty
        for attr, value in self.PRESETS.get(difficulty, {}).items():
            setattr(self, attr, value)

    @classmethod
    def reward_for(cls, difficulty):
        return cls.PRESETS.get(difficulty, {}).get("REWARD", cls.REWARD)

    @property
    def finished(self):
        return self.result is not None

    def abort(self):
        """The player pressed Esc to leave."""
        if not self.finished:
            self.result = "quit"

    def handle_event(self, event):
        pass

    def update(self, dt, keys):
        raise NotImplementedError

    def draw(self, surface):
        raise NotImplementedError
