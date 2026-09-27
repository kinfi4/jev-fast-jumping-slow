"""
Definition:
Environmental zones that modify physics and affect entities interacting with them.

Examples:
- Water that allows swimming or buoyancy
- Lava that damages over time
- Mud or slime that slows movement
- Air currents or zero-gravity zones that change velocity

Trigger:
- Effects are applied automatically when an entity overlaps the fluid's area.
- Interaction checks occur each frame during the world's update cycle.
"""

# Standard Library Imports

# Third-Party Imports
import pygame

# Local Imports
import settings
from platformer.entities.entity  import Entity, AnimatedEntity


class Water(Entity):

    def __init__(self, game, location, image):
        super().__init__(game, location, image)

    def update(self):  # animate later
        pass