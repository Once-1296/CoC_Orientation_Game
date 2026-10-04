"""What the merchant sells, and what each purchase does. Health is in half-hearts."""

MAX_HEARTS = 5
MAX_POTIONS = 5
MAX_SWORD_LEVEL = 2
MAX_SPEED_LEVEL = 2
SPEED_BONUS = 0.2        # +20% running speed per shoe upgrade
POTION_HEAL = 2          # one heart
HEART_UPGRADE = 2        # adds one heart to the maximum and fills it

PRICES = {
    "potion": 5,
    "sword": [10, 20],   # price of level 1, then level 2
    "shoes": [8, 16],
    "heart": [12, 20],   # price of 4 hearts, then 5 hearts
}


def options(state):
    """Menu entries for the shop: (label, detail, item id)."""
    sword = state["sword_level"]
    shoes = state["speed_level"]
    hearts = state["max_hp"] // 2
    items = [
        (f"Health potion   {PRICES['potion']} coins   ({state['potions']}/{MAX_POTIONS})",
         "Restores one heart. Press Q to drink one.", "potion"),
    ]
    if sword < MAX_SWORD_LEVEL:
        items.append((f"Sharper sword   {PRICES['sword'][sword]} coins   (level {sword}/{MAX_SWORD_LEVEL})",
                      "Each level adds 1 damage. Slimes take fewer hits.", "sword"))
    else:
        items.append((f"Sharper sword   sold out   (level {sword}/{MAX_SWORD_LEVEL})",
                      "Slimes now die in one hit.", "sold"))
    if shoes < MAX_SPEED_LEVEL:
        items.append((f"Running shoes   {PRICES['shoes'][shoes]} coins   (level {shoes}/{MAX_SPEED_LEVEL})",
                      "Run 20% faster per level.", "shoes"))
    else:
        items.append((f"Running shoes   sold out   (level {shoes}/{MAX_SPEED_LEVEL})",
                      "You're as fast as the shoes allow.", "sold"))
    if hearts < MAX_HEARTS:
        items.append((f"Extra heart   {PRICES['heart'][hearts - 3]} coins   ({hearts}/{MAX_HEARTS} hearts)",
                      "Raises your maximum health and fills the new heart.", "heart"))
    else:
        items.append((f"Extra heart   sold out   ({hearts}/{MAX_HEARTS} hearts)",
                      "You already have the most hearts.", "sold"))
    items.append(("Leave", "Close the shop.", "leave"))
    return items


def buy(state, item):
    """Try to buy `item`. Returns the message the merchant says."""
    if item in ("leave", "sold"):
        return "Anything else?" if item == "leave" else "Sorry, that's sold out."

    if item == "potion":
        if state["potions"] >= MAX_POTIONS:
            return "You can't carry any more potions."
        price = PRICES["potion"]
    elif item == "sword":
        if state["sword_level"] >= MAX_SWORD_LEVEL:
            return "Sorry, that's sold out."
        price = PRICES["sword"][state["sword_level"]]
    elif item == "shoes":
        if state["speed_level"] >= MAX_SPEED_LEVEL:
            return "Sorry, that's sold out."
        price = PRICES["shoes"][state["speed_level"]]
    else:
        hearts = state["max_hp"] // 2
        if hearts >= MAX_HEARTS:
            return "Sorry, that's sold out."
        price = PRICES["heart"][hearts - 3]

    if state["coins"] < price:
        return f"That costs {price} coins. Come back when you have enough."

    state["coins"] -= price
    if item == "potion":
        state["potions"] += 1
        return "Here's a potion. Drink it with Q when you need it."
    if item == "sword":
        state["sword_level"] += 1
        return "Your sword is sharper now."
    if item == "shoes":
        state["speed_level"] += 1
        return "Your new shoes feel light."
    state["max_hp"] += HEART_UPGRADE
    state["hp"] += HEART_UPGRADE
    return "You feel tougher. One more heart!"
