"""
Definition:
Abstract base classes providing core position, movement, collision, and optional
animation support for all game objects. These classes are never instantiated
directly; only their subclasses are used in the game.

Examples of subclasses:
- Hero and enemies
- NPCs
- Items and interactables (for positioning and collision)
- Platforms, decorative tiles, and triggers

Responsibilities:
- Track position and velocity
- Handle collisions with platforms and world bounds
- Apply gravity and movement logic
- Provide a framework for animations (AnimatedEntity subclass)

Trigger: None. These classes provide foundational behavior for derived objects.
"""

# Standard Library Imports

# Third-Party Imports
import pygame

# Local Imports
import settings


# Base Entity Class
class Entity(pygame.sprite.Sprite):

    def __init__(self, game, location, image):
        super().__init__()

        self.game = game
        self.image = image
        self.rect = self.image.get_rect()

        self.vx = 0
        self.vy = 0

        self.in_water = False

        if location is not None:
            self.move_to(location)

    def move_to(self, location):
        self.rect.centerx = location[0] * settings.GRID_SIZE + settings.GRID_SIZE // 2
        self.rect.centery = location[1] * settings.GRID_SIZE + settings.GRID_SIZE // 2

    @property
    def on_platform(self):
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, self.game.world.platforms, False)
        self.rect.y -= 1

        return len(hits) > 0

    def apply_gravity(self):
        if self.in_water:
            gravity = settings.WATER_GRAVITY
            terminal_velocity = settings.WATER_TERMINAL_VELOCITY
        else:
            gravity = settings.GRAVITY
            terminal_velocity = settings.TERMINAL_VELOCITY

        self.vy += gravity
        self.vy = min(self.vy, terminal_velocity)

    def move_x(self):
        self.rect.x += self.vx

    def move_y(self):
        self.rect.y += self.vy

    def turn_around(self):
        self.vx *= -1

    def check_water(self):
        self.in_water = pygame.sprite.spritecollideany(self, self.game.world.water)
    
    def check_platforms_x(self):
        hits = pygame.sprite.spritecollide(self, self.game.world.platforms, False)

        for platform in hits:
            if self.vx > 0:
                self.rect.right = platform.rect.left
            elif self.vx < 0:
                self.rect.left = platform.rect.right

        return len(hits) > 0

    def check_platforms_y(self):
        hits = pygame.sprite.spritecollide(self, self.game.world.platforms, False)

        for platform in hits:
            if self.vy > 0:
                self.rect.bottom = platform.rect.top
            elif self.vy < 0:
                self.rect.top = platform.rect.bottom

        if len(hits) > 0:
            self.vy = 0

    def check_platform_edges(self):
        at_edge = True

        self.rect.y +=  1
        hits = pygame.sprite.spritecollide(self, self.game.world.platforms, False)
        self.rect.y -= 1

        for platform in hits:
            if self.vx < 0:
                if platform.rect.left <= self.rect.left:
                    at_edge = False
            elif self.vx > 0:
                if platform.rect.right >= self.rect.right:
                    at_edge = False

        return at_edge

    def check_world_edges(self):
        hit_edge = False

        if self.rect.left < 0:
            self.rect.left = 0
            hit_edge = True
        elif self.rect.right > self.game.world.world_width:
            self.rect.right = self.game.world.world_width
            hit_edge = True

        return hit_edge
    
    def check_world_bottom(self):
        return self.rect.top > self.game.world.world_height


class AnimatedEntity(Entity):
    
    def __init__(self, game, location, animations, default_animation_key="default"):
        super().__init__(game, location, image=animations[default_animation_key][0])
        
        self.animations = animations
        self.animation_key = default_animation_key
        self.image_index = 0
        self.frame_rate = settings.DEFAULT_ANIMATION_FRAME_RATE

    def set_animation_key(self):
        pass  # Override in subclasses

    def animate(self):
        previous_animation_key = self.animation_key

        self.set_animation_key()
        self.image_index += self.frame_rate

        if self.image_index >= len(self.animations[self.animation_key]) or self.animation_key != previous_animation_key:
            self.image_index = 0
                
        self.image = self.animations[self.animation_key][int(self.image_index)]

        
    def update(self):
        self.animate()
