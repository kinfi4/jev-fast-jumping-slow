"""
Definition:
Objects or areas that trigger a game event when the player interacts with or touches them.

Examples:
- Flag (level goal)
- Pressure plates
- Zone-based events (checkpoints)

Trigger: Activated on touch or interaction.
"""

# Standard Library Imports

# Third-Party Imports
import pygame

# Local Imports
import settings
from platformer.entities.entity  import Entity, AnimatedEntity


class Flag(AnimatedEntity):

    def __init__(self, game, location, animations):
        super().__init__(game, location, animations, default_animation_key="default")

    def update(self):
        self.animate()


class Flagpole(Entity):

    def __init__(self, game, location, image):
        super().__init__(game, location, image)

