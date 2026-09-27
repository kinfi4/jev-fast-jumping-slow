"""
Definition:
Solid objects that the player can stand on or collide with. May include breakable or item-containing blocks.

Examples:
- Grass, dirt, or block platforms
- Crates
- Breakable blocks that release items

Trigger:
- Collisions: player can stand on or is blocked by the platform.
"""

# Standard Library Imports

# Third-Party Imports
import pygame

# Local Imports
import settings
from platformer.entities.entity  import Entity, AnimatedEntity


class Platform(Entity):

    def __init__(self, game, location, image):
        super().__init__(game, location, image)


class BreakablePlatform(Platform):
    pass


class ItemBlock(Platform):

    def __init__(self, game, location, image, item):
        super().__init__(game, location, image)
        self.item = item
        self.used = False

    def activate(self, player):
        if not self.used:
            self.used = True
            self.game.world.items.add(self.item)


class MovingPlatform(Platform):
    pass


class Crate(Platform):

    def __init__(self, game, location, image):
        super().__init__(game, location, image)
        self.is_pushable = True

    def get_connected_crates(self, direction, connected=None):
        if connected is None:
            connected = []
        connected.append(self)

        for crate in self.game.world.crates:
            if direction > 0 and self.rect.right == crate.rect.left and abs(self.rect.y - crate.rect.y) <= settings.GRID_SIZE // 2:
                crate.get_connected_crates(direction, connected)
            elif direction < 0 and self.rect.left == crate.rect.right and abs(self.rect.y - crate.rect.y) <= settings.GRID_SIZE // 2:
                crate.get_connected_crates(direction, connected)

            if self.rect.top == crate.rect.bottom and abs(self.rect.x - crate.rect.x) <= settings.GRID_SIZE // 2:
                crate.get_connected_crates(direction, connected)

        return connected

    def push(self, hero):
        direction = 1 if hero.v_x > 0 else -1

        connected_crates = self.get_connected_crates(direction)

        for crate in connected_crates:
            crate.v_x = hero.v_x 
    
    def update(self):
        self.apply_gravity()
        self.move_x()
        hit_platform_x = self.check_platforms_x()
        self.move_y()
        self.check_platforms_y()
        self.check_world_edges()

        pushing = pygame.sprite.spritecollide(self, self.game.world.player, False)
        if not pushing:
            self.v_x = 0

        if hit_platform_x:
            self.v_x = 0
