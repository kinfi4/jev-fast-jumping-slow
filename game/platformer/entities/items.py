"""
Definition:
Objects the player collects that directly modify the player's attributes or inventory.

Examples:
- Gems (score)
- Hearts (health)
- Keys (inventory unlockers)
- Powerups (jump boost, temporary buffs)

Trigger: Collect on touch.
"""


# Standard Library Imports

# Third-Party Imports
import pygame

# Local Imports
import settings
from platformer.entities.entity import Entity, AnimatedEntity


class Gem(Entity):

    def __init__(self, game, location, image):
        super().__init__(game, location, image)

    def apply(self, character):
        self.game.score += settings.GEM_VALUE


class Heart(Entity):

    def __init__(self, game, location, image):
        super().__init__(game, location, image)

    def apply(self, character):
        if character.hearts < character.max_hearts:
            character.hearts += 1
        

class Key(Entity):

    def __init__(self, game, location, image, code=None):
        super().__init__(game, location, image)
        
        self.code = code

    def apply(self, character):
        character.key_chain.append(self.code)
