# Idea : 2D Top Down Educational Game

## Theme

Small world with following game screens:

1. Character Home
2. City Market/ Town Circle
3. Rocky mountain like terrain
4. Dark green woods
5. Lakeside
6. Snowy mountainous area

## Storyline

Player starts in their home inside town. They can go out in town circle to talk with NPCs.
There are certain stalls/shops here that player can interact with to a limited extent now.
The town circle has 4 exits:
 - North: leads to Rocky mountain
 - East: leads to dark green woods
 - South: lead to lakeside
 - West: leads to Snowy mountainous

In each of these regions, player can explore and pcik up items, talk with people and additionally there's a simple mechanic of slash and shield as in zelda games to fight off small enemies.

Additionally each region has an NPC that allows you to play the region Specfic mini game once you do some task like collecting X amount of item Y, etc.

## Ideas for Mini Game

### North Region : Meteor Shower

Player is in 2d platformer like zone with only left and right movements.
They have to dodge falling rocks coming from the top of the screen.
Difficulty varies with speed and size of rocks

### East Region: Peak-A-Bush

The Game is a puzzle like one with a 3x3 (or 5x5 or 7x7 depending on Difficulty), grid of grass patches.
The game plays for some number of rounds. At each round from certain grass patches, some creature pops up for a few seconds.
Player then has to determine which patch had what creature in a little more time limit. Player can use direction arrow keys or mouse to select patch and enter to mark it.

### South Region : Fishing mania

As its sounds its a  fishing game. Player can move boat, throw rod, use bait, etc to catch maximum amount/quality of fish.

### West Region : Snowball fight

A 3 lane vertical game, where player can move left/right/up/down.
Player should collect snow and avoid obstacles which reduce the current snowball size.
Game score is based on snowball size at end

Each mini game has some variables which can be adjusted easily in game code to make the mini game feel different.
This helps teach game loops, collisions, points, etc.

Each mini game rewards some currency/items and helps unlock more interaction in market in town circle
