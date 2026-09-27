"""
Definition:
The controllable player character. Handles input, movement, physics, health, and interactions with the world.

Examples:
- Walking, running, jumping
- Collecting items
- Interacting with doors, NPCs, and switches
- Taking damage from enemies

Trigger:
- Responds to player input each frame.
- Collision and overlap checks occur automatically in update().
"""

# Standard Library Imports

# Third-Party Imports
import pygame

# Local Imports
import settings
from platformer.entities.entity import AnimatedEntity


class Hero(AnimatedEntity):

    def __init__(self, game, location, animations, controls):
        super().__init__(game, location, animations, default_animation_key="idle_right") 

        self.controls = controls
        self.vx = 0
        self.vy = 0
        self.hearts = settings.HERO_HEARTS
        self.max_hearts = settings.HERO_MAX_HEARTS
        self.escape_time = 0
        self.facing_right = True
        self.respawn_point = location  # actually gets set in load level, location is None at instantiation (should this just be saved in game?)
        self.key_chain = []
        self.is_climbing = False
    
    def act(self, events, pressed_keys):
        if pressed_keys[self.controls['left']]:
            self.go_left()
        elif pressed_keys[self.controls['right']]:
            self.go_right()
        else:
            self.stop_x()
        
        if pressed_keys[self.controls['up']]:
            self.go_up()
        elif pressed_keys[self.controls['down']]:
            self.go_down()
        elif self.is_climbing:
            self.stop_y()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == settings.CONTROLS['jump']:
                    self.jump()
                elif event.key == settings.CONTROLS['interact']:
                    self.check_interactables()

    @property
    def can_jump(self):
        return self.on_platform or self.is_climbing or self.in_water
    
    @property
    def can_climb(self):
        # Could check that hero is somewhat centered on ladder
        on_climbable = pygame.sprite.spritecollideany(self, self.game.world.climbables)
        if not on_climbable:
            self.is_climbing = False
        return on_climbable

    @property
    def is_alive(self):
        return self.hearts > 0

    @property
    def reached_goal(self):
        return pygame.sprite.spritecollideany(self, self.game.world.goals)  # No collision resolution here, let hero overlap flag
        
    def go_left(self):
        if self.in_water:
            speed = settings.HERO_SWIM_SPEED
        else:
            speed = settings.HERO_WALK_SPEED

        self.vx = -1 * speed
        self.facing_right = False
    
    def go_right(self):
        if self.in_water:
            speed = settings.HERO_SWIM_SPEED
        else:
            speed = settings.HERO_WALK_SPEED

        self.vx = speed
        self.facing_right = True

    def stop_x(self):
        self.vx = 0

    def go_up(self):
        if self.can_climb:
            self.is_climbing = True
        
        hits = pygame.sprite.spritecollide(self, self.game.world.climbables, False)
        can_go_up_more = False
        for climbable in hits:
            if climbable.rect.top < self.rect.centery:
                can_go_up_more = True

        if self.is_climbing and can_go_up_more:
            self.vy = -1 * settings.HERO_CLIMB_SPEED
        else:
            self.vy = 0
    
    def go_down(self):
        if self.can_climb:
            self.is_climbing = True
        
        if self.is_climbing:
            self.vy = settings.HERO_CLIMB_SPEED

    def stop_y(self):
        self.vy = 0

    def jump(self):
        if self.can_jump:
            if self.is_climbing:
                jump_power = -1 * settings.HERO_CLIMB_JUMP_POWER
            elif self.in_water:
                jump_power = -1 * settings.HERO_WATER_JUMP_POWER
            else:
                jump_power = -1 * settings.HERO_JUMP_POWER

            self.vy = jump_power
            self.is_climbing = False

    def check_interactables(self):
        hits = pygame.sprite.spritecollide(self, self.game.world.interactables, False)

        for interactable in hits:
            interactable.interact(self)

    def check_enemies(self):
        hits = pygame.sprite.spritecollide(self, self.game.world.enemies, False)

        if self.escape_time == 0:
            for enemy in hits:
                self.escape_time = settings.HERO_ESCAPE_TIME
                self.hearts -= 1

                bouncex = 15  # Magic number alert!
                bouncey = -5
                if self.rect.centerx < enemy.rect.centerx:
                    bouncex *= -1
                if self.rect.centery < enemy.rect.centery:
                    bouncey *= -1

                self.vx = bouncex
                self.vy = bouncey
                # oof sound?
        else:
            self.escape_time -= 1
    
    def check_items(self):
        hits = pygame.sprite.spritecollide(self, self.game.world.items, True)
    
        for item in hits:
            item.apply(self)

    def check_world_bottom(self):
        off_bottom_edge = super().check_world_bottom()

        if off_bottom_edge:
            self.hearts -= 1

            if self.hearts > 0:
                self.move_to(self.respawn_point)

        return False

    def set_animation_key(self):
        if self.is_climbing:
            self.animation_key = "climb"
            return
        
        if self.facing_right:
            if not self.on_platform:
                self.animation_key = "jump_right"
            elif self.vx > 0:
                self.animation_key = "walk_right"
            else:
                self.animation_key = "idle_right"
        else:
            if not self.on_platform:
                self.animation_key = "jump_left"
            elif self.vx < 0:
                self.animation_key = "walk_left"
            else:
                self.animation_key = "idle_left"

    def update(self):
        self.check_water()

        if not self.can_climb:  # for sideways movement off climable object
            self.is_climbing = False

        if not self.is_climbing:
            self.apply_gravity()

        self.check_items()        # Place here in case an item affects movement
        self.check_enemies()      # Must be before move for bounce off enemies to work
        self.move_x()
        self.check_platforms_x()  # Must resolve collisions in x-direction prior to moving in y-direction
        self.move_y()
        self.check_platforms_y()
        self.check_world_edges()
        self.check_world_bottom()
        self.animate()
