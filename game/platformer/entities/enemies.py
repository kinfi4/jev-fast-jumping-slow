"""
Definition:
Autonomous hostile entities that can harm the player. Each enemy has movement, animation, and collision behavior.

Examples:
- Cloud (moves horizontally)
- Spikeball (rolls and bounces on platforms)
- Spikeman (walks, turns at edges, damages on contact)

Trigger: Collisions with the player reduce health or trigger bounce-back effects.
"""


# Standard Library Imports

# Third-Party Imports
import pygame

# Local Imports
import settings
from platformer.entities.entity import Entity, AnimatedEntity


class Cloud(AnimatedEntity):

    def __init__(self, game, location, animations):
        super().__init__(game, location, animations)

        self.vx = -1 * settings.CLOUD_SPEED
        self.vy = 0
    
    def update(self):
        self.move_x()
        at_world_edge = self.check_world_edges()
        self.animate()

        if at_world_edge:
            self.turn_around()


class Spikeball(AnimatedEntity):

    def __init__(self, game, location, animations):
        super().__init__(game, location, animations)

        self.vx = -1 * settings.SPIKEBALL_SPEED
        self.vy = 0
    
    def update(self):
        self.check_water()
        self.apply_gravity()
        self.move_x()
        hit_platform_x = self.check_platforms_x()
        self.move_y()
        self.check_platforms_y()
        at_world_edge = self.check_world_edges()
        off_bottom_edge = self.check_world_bottom()
        self.animate()

        if at_world_edge or hit_platform_x:
            self.turn_around()

        if off_bottom_edge:
            self.kill()


class Spikeman(AnimatedEntity):

    def __init__(self, game, location, animations):
        super().__init__(game, location, animations, default_animation_key="walk_right")

        self.vx = -1 * settings.SPIKEBALL_SPEED
        self.vy = 0
    
    def set_animation_key(self):
        if self.vx > 0:
            self.animation_key = "walk_right"
        else:
            self.animation_key = "walk_left"
    
    def update(self):
        self.check_water()
        self.apply_gravity()
        self.move_x()
        hit_platform_x = self.check_platforms_x()
        self.move_y()
        self.check_platforms_y()
        at_platform_edge = self.check_platform_edges()
        at_world_edge = self.check_world_edges()
        off_bottom_edge = self.check_world_bottom()
        self.animate()

        if at_world_edge or hit_platform_x or at_platform_edge:
            self.turn_around()

        if off_bottom_edge:
            self.kill()


class Fish(AnimatedEntity):

    def __init__(self, game, location, animations):
        super().__init__(game, location, animations, default_animation_key="swim_right")

        self.vx = settings.FISH_SPEED
        self.vy = 0

    
    def set_animation_key(self):
        if self.vx > 0:
            self.animation_key = "swim_right"
        else:
            self.animation_key = "swim_left"

    def update(self):
        self.move_x()
        hit_platform_x = self.check_platforms_x()
        at_world_edge = self.check_world_edges()
        self.animate()

        if hit_platform_x or at_world_edge:
            self.turn_around()