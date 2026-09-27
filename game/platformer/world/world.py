"""
Definition:
Encapsulates the entire game world, including all entities and level structure.

Responsibilities:
- Load level data from JSON files and instantiate the corresponding objects
- Organize sprites into logical groups (players, platforms, enemies, items, interactables, goals)
- Track world dimensions and hero starting position
- Provide centralized update and draw methods for all sprites
- Manage layering of sprite rendering for consistent visual presentation

Trigger:
- The Game class calls World.update() every frame to advance all sprites.
- The Game class calls World.draw(surface, offset_x, offset_y) every frame to render the world.
  Offsets are optional; they are used for scrolling but default to (0, 0) if not provided.
"""

# Standard Library Imports
import json

# Third-Party Imports
import pygame

# Local Imports
import settings
from platformer.entities.tiles import Tile
from platformer.entities.climbables import Fence, Ladder, Vine
from platformer.entities.enemies import Cloud, Fish, Spikeball, Spikeman
from platformer.entities.fluids import Water
from platformer.entities.items import Gem, Heart, Key
from platformer.entities.interactables import Door, NPC, Sign
from platformer.entities.platforms import BreakablePlatform, Crate, ItemBlock, MovingPlatform, Platform
from platformer.entities.triggers import Flag, Flagpole


class World:
    
    def __init__(self, game, data):
        self.game = game
        self.data = data  # could also pass in file and load in load_level (but then loading assets is in multiple places)

        # Sprite groups
        self.players = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.interactables = pygame.sprite.Group()
        self.climbables = pygame.sprite.Group()
        self.water = pygame.sprite.Group()
        self.goals = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        self.make_level()

    def make_level(self):
        self.world_width = self.data['width'] * settings.GRID_SIZE
        self.world_height = self.data['height'] * settings.GRID_SIZE

        self.hero = self.game.hero
        self.players.add(self.hero)
        self.hero.move_to(self.data['start'])
        self.hero.respawn_point = self.data['start']

        # Platforms
        if 'grass_dirt' in self.data:   
            for location in self.data['grass_dirt']:
                self.platforms.add( Platform(self.game, location, self.game.grass_dirt_img) )

        if 'dirt' in self.data:   
            for location in self.data['dirt']:
                self.platforms.add( Platform(self.game, location, self.game.dirt_img) )

        if 'blocks' in self.data:    
            for location in self.data['blocks']:
                self.platforms.add( Platform(self.game, location, self.game.block_img) )
        
        # Water
        if 'water' in self.data:    
            for location in self.data['water']:
                self.water.add( Water(self.game, location, self.game.water_img) )
        
        if 'water_tops' in self.data:    
            for location in self.data['water_tops']:
                self.water.add( Water(self.game, location, self.game.water_top_img) )
        
        # Enemies
        if 'clouds' in self.data:    
            for location in self.data['clouds']:
                self.enemies.add( Cloud(self.game, location, self.game.cloud_animations) )
        
        if 'spikeballs' in self.data:    
            for location in self.data['spikeballs']:
                self.enemies.add( Spikeball(self.game, location, self.game.spikeball_animations) )
        
        if 'spikemen' in self.data:    
            for location in self.data['spikemen']:
                self.enemies.add( Spikeman(self.game, location, self.game.spikeman_animations) )
        
        if 'fish' in self.data:    
            for location in self.data['fish']:
                self.enemies.add( Fish(self.game, location, self.game.fish_animations) )
        
        # Items
        if 'gems' in self.data:    
            for location in self.data['gems']:
                self.items.add( Gem(self.game, location, self.game.gem_img) )
        
        if 'hearts' in self.data:    
            for location in self.data['hearts']:
                self.items.add( Heart(self.game, location, self.game.heart_img) )
        
        if 'keys' in self.data:    
            for data in self.data['keys']:
                location = data['loc']
                code = data['code'] if 'code' in data else None                
                self.items.add( Key(self.game, location, self.game.key_img, code) )
        
        # Interactables
        if 'doors' in self.data:    
            for data in self.data['doors']:
                location = data['loc']
                destination = data['dest']
                code = data['code'] if 'code' in data else None
                image = self.game.locked_door_img if 'code' in data else self.game.door_img
                self.interactables.add( Door(self.game, location, image, destination, code) )
        
        if 'signs' in self.data:    
            for data in self.data['signs']:
                location = data['loc']
                message = data['message']
                self.interactables.add( Sign(self.game, location, self.game.sign_img, message) )

        if 'npcs' in self.data:    
            for data in self.data['npcs']:
                location = data['loc']
                message = data['message']
                if data['type'] == 'shopkeeper':
                    image = self.game.shopkeeper_img
                elif data['type'] == 'wizard':
                    image = self.game.wizard_img
                self.interactables.add( NPC(self.game, location, image, message) )
        
        # Climbables
        if 'ladders' in self.data:
            for location in self.data['ladders']:
                self.climbables.add( Ladder(self.game, location, self.game.ladder_img) )
        
        # Goals
        if 'goals' in self.data:    
            for i, location in enumerate(self.data['goals']):
                if i == 0:
                    self.goals.add( Flag(self.game, location, self.game.flag_animations) )
                else:
                    self.goals.add( Flagpole(self.game, location, self.game.flagpole_img) ) 

        # Make one big sprite group for easy updating
        self.all_sprites.add(self.players, self.platforms, self.enemies, self.items, 
                             self.interactables, self.climbables, self.water, self.goals)
    
    def update(self):
        self.all_sprites.update()

    def draw(self, surface, offset_x=0, offset_y=0):
        surface.fill(settings.SKY_BLUE)

        # Draw sprites with desired layering
        draw_order  = [self.water, self.platforms, self.climbables, self.interactables, 
                       self.items, self.enemies, self.goals, self.players]

        for group in draw_order:
            for sprite in group:
                x = sprite.rect.x - offset_x
                y = sprite.rect.y - offset_y
                surface.blit(sprite.image, [x, y])
