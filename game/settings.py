"""
Global configuration and assets for the game.

This module centralizes constants, file paths, and default values used throughout
the game. It includes:

- Window settings (screen size, grid size, FPS, camera lag)
- Colors and fonts
- File paths for images, sounds, and music
- Level configuration and starting level
- Default character attributes and physics
- Gameplay controls mapping
- Item and enemy properties

No game logic is implemented here; this module is strictly for configuration.
"""

# Third-party imports
import pygame


# Window settings
GRID_SIZE = 64
SCREEN_WIDTH = 16 * GRID_SIZE
SCREEN_HEIGHT = 9 * GRID_SIZE
CAPTION = "My Awesome Game"
FPS = 60
CAMERA_LAG = 0.8

# Define colors
SKY_BLUE = (135, 200, 235)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fonts
PRIMARY_FONT = 'assets/fonts/Dinomouse-Regular.otf'
SECONDARY_FONT = 'assets/fonts/Dinomouse-Regular.otf'

# Images
''' hero '''
HERO_IMGS_IDLE = ['assets/images/characters/players/player_idle.png']
HERO_IMGS_WALK = ['assets/images/characters/players/player_walk1.png',
                  'assets/images/characters/players/player_walk2.png']
HERO_IMGS_JUMP = ['assets/images/characters/players/player_jump.png']
HERO_IMGS_CLIMB = ['assets/images/characters/players/player_idle.png', # Fix when I find better animated character
                   'assets/images/characters/players/player_idle.png'] 

''' platforms '''
GRASS_DIRT_IMG = 'assets/images/platforms/platformPack_tile001.png'
DIRT_IMG = 'assets/images/platforms/platformPack_tile004.png'
BLOCK_IMG = 'assets/images/platforms/platformPack_tile020.png'

''' interactables '''
DOOR_IMG = 'assets/images/interactables/door.png'
LOCKED_DOOR_IMG = 'assets/images/interactables/locked_door.png'
SIGN_IMG = 'assets/images/interactables/sign.png'

FLAG_IMGS = ['assets/images/triggers/flag.png']
FLAGPOLE_IMG = 'assets/images/triggers/flagpole.png'

''' items '''
GEM_IMG = 'assets/images/items/gem.png'
HEART_IMG = 'assets/images/items/heart.png'
KEY_IMG = 'assets/images/items/key.png'

''' enemies '''
CLOUD_IMGS = ['assets/images/characters/enemies/cloud.png']
SPIKEBALL_IMGS = ['assets/images/characters/enemies/spikeball1.png',
                  'assets/images/characters/enemies/spikeball2.png']                   
SPIKEMAN_IMGS = ['assets/images/characters/enemies/spikeman_walk1.png',
                 'assets/images/characters/enemies/spikeman_walk2.png']
FISH_IMGS = ['assets/images/characters/enemies/fishSwim1.png',
             'assets/images/characters/enemies/fishSwim1.png']

''' npcs '''
SHOPKEEPER_IMG = 'assets/images/characters/npcs/character_malePerson_talk.png'
WIZARD_IMG = 'assets/images/characters/npcs/wizard.png'

''' climbables '''
LADDER_IMG = 'assets/images/climbables/ladder_mid.png'
LADDER_TOP_IMG = 'assets/images/climbables/ladder_top.png'

''' fluids '''
WATER_IMG = 'assets/images/fluids/platformPack_tile017.png'
WATER_TOP_IMG = 'assets/images/fluids/platformPack_tile005.png'

# Sounds
JUMP_SND = 'assets/sounds/jump.wav'
GEM_SND = 'assets/sounds/collect_point.wav'

# Music
TITLE_MUSIC = 'assets/music/calm_happy.ogg'
MAIN_THEME = 'assets/music/cooking_mania.wav'

# Levels
STARTING_LEVEL = 8

LEVELS = [
    'assets/levels/world-1.json',
    'assets/levels/world-2.json',
    'assets/levels/world-3.json',
    'assets/levels/world-4.json',
    'assets/levels/world-5.json',
    'assets/levels/world-6.json',
    'assets/levels/world-7.json',
    'assets/levels/world-8.json',
    'assets/levels/world-9.json',
    'assets/levels/world-10.json'
]

LEVEL_TRANSITION_TIME = 120

# Default character attributes
DEFAULT_ANIMATION_FRAME_RATE = 0.1

HERO_HEARTS = 3
HERO_MAX_HEARTS = 5
HERO_WALK_SPEED = 5
HERO_CLIMB_SPEED = 3
HERO_JUMP_POWER = 22
HERO_CLIMB_JUMP_POWER = 8
HERO_WATER_JUMP_POWER = 8
HERO_SWIM_SPEED = 3
HERO_ESCAPE_TIME = 45

# Enemy attributes
CLOUD_SPEED = 3
FISH_SPEED = 1
SPIKEMAN_SPEED = 2
SPIKEBALL_SPEED = 2

# Item attributes
GEM_VALUE = 10

# Physics
GRAVITY = 1.0
TERMINAL_VELOCITY = 20
WATER_GRAVITY = 0.3
WATER_TERMINAL_VELOCITY = 5

# Gameplay settings
CONTROLS = {
    'left': pygame.K_a,
    'right': pygame.K_d,
    'up': pygame.K_w,
    'down': pygame.K_s,
    'jump': pygame.K_SPACE,
    'interact': pygame.K_e,
    'dismiss': pygame.K_ESCAPE,
}
