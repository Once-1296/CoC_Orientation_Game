from .fishing import Fishing
from .meteor_shower import MeteorShower
from .peek_a_bush import PeekABush
from .snowball import Snowball

# Mini games by name. The NPC task in maps.py refers to these names.
MINIGAMES = {
    MeteorShower.name: MeteorShower,
    PeekABush.name: PeekABush,
    Fishing.name: Fishing,
    Snowball.name: Snowball,
}
