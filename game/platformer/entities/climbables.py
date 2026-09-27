"""
Definition:
Objects the player can climb or traverse in ways other than walking/jumping.
They allow vertical or multi-directional movement without being traditional platforms.

Examples:
- Ladders (vertical climb)
- Vines (vertical climb)
- Climbable fences (multi-directional)

Trigger:
Player movement along the object when touching it, possibly with a climb key.
"""

# Standard Library Imports

# Third-Party Imports
import pygame

# Local Imports
import settings
from platformer.entities.entity  import Entity, AnimatedEntity


class Ladder(Entity):

    def __init__(self, game, location, image):
        super().__init__(game, location, image)


class Vine(Entity):
    pass


class Fence(Entity):
    pass