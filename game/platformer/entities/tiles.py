"""
Definition:
Decorative or background objects that do not affect player movement or game logic.

Examples:
- Background tiles (grass, stone, dirt patterns)
- Animated scenery (water, clouds, etc.)

Trigger: None. Tiles are purely visual and do not interact with the player.
"""

# Standard Library Imports

# Third-Party Imports
import pygame

# Local Imports
import settings
from platformer.entities.entity  import Entity, AnimatedEntity


class Tile(Entity):

    def __init__(self, game, location, image):
        super().__init__(game, location, image)


class AnimatedTile(AnimatedEntity):

    def __init__(self, game, location, animations):
        super().__init__(game, location, animations, default_animation_key="default")

    def update(self):
        self.animate()
