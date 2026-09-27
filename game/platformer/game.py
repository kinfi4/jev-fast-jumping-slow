"""
Definition:
The central game controller that manages scenes, input, updates, rendering, and
overall game flow.

Responsibilities:
- Initialize Pygame, load assets, and create necessary overlays (HUD, grid, menus)
- Track current scene (start, playing, interacting, pause, level complete, win, lose)
- Manage level loading, hero creation, and world instantiation
- Handle player input and interactions with the world
- Update the world state and camera position
- Render the world, HUD, overlays, and infoboxes
- Maintain game loop with consistent framerate

Trigger: The main game loop is executed via Game.play(), which continuously
processes input, updates game state, and renders each frame.
"""

# Standard library
import json

# Third-party
import pygame

# Local
import settings
from platformer.camera import ScrollingCamera
from platformer.world import World
from platformer.overlays import TitleScreen, WinScreen, LoseScreen, LevelCompleteScreen, PauseScreen, HUD, Grid
from platformer.entities import Hero


# Main game class 
class Game:

    # Scenes
    START = 0
    PLAYING = 1
    INTERACTING = 2
    PAUSE = 3
    LEVEL_COMPLETE = 4
    WIN = 5
    LOSE = 6

    def __init__(self):
        pygame.mixer.pre_init()
        pygame.init()

        self.screen = pygame.display.set_mode([settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT])
        pygame.display.set_caption(settings.CAPTION)
        self.clock = pygame.time.Clock()
        self.running = True

        self.load_assets()
        self.make_overlays()
        self.new_game()

    def load_assets(self):
        # Platforms
        self.grass_dirt_img = pygame.image.load(settings.GRASS_DIRT_IMG).convert_alpha()
        self.dirt_img = pygame.image.load(settings.DIRT_IMG).convert_alpha()
        self.block_img = pygame.image.load(settings.BLOCK_IMG).convert_alpha()
        
        # Hero
        self.hero_animations = {
            "idle_right": [pygame.image.load(path).convert_alpha() for path in settings.HERO_IMGS_IDLE],
            "walk_right": [pygame.image.load(path).convert_alpha() for path in settings.HERO_IMGS_WALK],
            "jump_right": [pygame.image.load(path).convert_alpha() for path in settings.HERO_IMGS_JUMP],
            "climb": [pygame.image.load(path).convert_alpha() for path in settings.HERO_IMGS_CLIMB],
        }
        self.hero_animations["idle_left"] = [pygame.transform.flip(image, True, False) for image in self.hero_animations["idle_right"]]
        self.hero_animations["walk_left"] = [pygame.transform.flip(image, True, False) for image in self.hero_animations["walk_right"]]
        self.hero_animations["jump_left"] = [pygame.transform.flip(image, True, False) for image in self.hero_animations["jump_right"]]

        # Enemies
        self.cloud_animations = {
            "default": [pygame.image.load(path).convert_alpha() for path in settings.CLOUD_IMGS]
        }

        self.spikeball_animations = {
            "default": [pygame.image.load(path).convert_alpha() for path in settings.SPIKEBALL_IMGS]
        }

        self.spikeman_animations = {
            "walk_right": [pygame.image.load(path).convert_alpha() for path in settings.SPIKEMAN_IMGS]
        }
        self.spikeman_animations["walk_left"] = [pygame.transform.flip(image, True, False) for image in self.spikeman_animations["walk_right"]]
        
        self.fish_animations = {
            "swim_left": [pygame.image.load(path).convert_alpha() for path in settings.FISH_IMGS]
        }
        self.fish_animations["swim_right"] = [pygame.transform.flip(image, True, False) for image in self.fish_animations["swim_left"]]
        
        # Items
        self.gem_img = pygame.image.load(settings.GEM_IMG).convert_alpha()
        self.heart_img = pygame.image.load(settings.HEART_IMG).convert_alpha()
        self.key_img = pygame.image.load(settings.KEY_IMG).convert_alpha()

        # Interactables
        self.door_img = pygame.image.load(settings.DOOR_IMG).convert_alpha()
        self.locked_door_img = pygame.image.load(settings.LOCKED_DOOR_IMG).convert_alpha()
        self.sign_img = pygame.image.load(settings.SIGN_IMG).convert_alpha()
        self.shopkeeper_img = pygame.image.load(settings.SHOPKEEPER_IMG).convert_alpha()
        self.wizard_img = pygame.image.load(settings.WIZARD_IMG).convert_alpha()
 
        # Climbables
        self.ladder_img = pygame.image.load(settings.LADDER_IMG).convert_alpha()
        self.ladder_top_img = pygame.image.load(settings.LADDER_TOP_IMG).convert_alpha()

        # fluids
        self.water_img = pygame.image.load(settings.WATER_IMG).convert_alpha()
        self.water_top_img = pygame.image.load(settings.WATER_TOP_IMG).convert_alpha()

        # Goal
        self.flag_animations = {
            "default": [pygame.image.load(path).convert_alpha() for path in settings.FLAG_IMGS]
        }
        self.flagpole_img = pygame.image.load(settings.FLAGPOLE_IMG).convert_alpha()

    def make_overlays(self):
        self.scene_overlays = {
            Game.START: TitleScreen(self),
            Game.WIN: WinScreen(self),
            Game.LOSE: LoseScreen(self),
            Game.LEVEL_COMPLETE: LevelCompleteScreen(self),
            Game.PAUSE: PauseScreen(self),
        }

        self.hud = HUD(self)
        self.grid = Grid(self)
        
    def new_game(self):
        self.hero = Hero(self, None, self.hero_animations, settings.CONTROLS)
        self.current_scene = Game.START
        self.level = settings.STARTING_LEVEL
        self.score = 0
        self.load_level()
    
    def load_level(self):
        # Load the level data
        current_level_file = settings.LEVELS[self.level - 1]
        with open(current_level_file) as f: 
            level_data = json.load(f)

        # World settings
        self.world = World(self, level_data)
        self.world_width = self.world.world_width
        self.world_height = self.world.world_height
        self.camera = ScrollingCamera(self.screen, [self.world_width, self.world_height], self.hero, settings.CAMERA_LAG)
        
        # Infobox
        self.infobox = None
        
    def toggle_pause(self):
        if self.current_scene == Game.PLAYING:
            self.current_scene = Game.PAUSE
        elif self.current_scene == Game.PAUSE:
            self.current_scene = Game.PLAYING

    def start_level(self):
        self.current_scene = Game.PLAYING

    def complete_level(self):
        self.current_scene = Game.LEVEL_COMPLETE

    def advance(self):
        self.level += 1
        self.load_level()
        self.start_level()

    def win(self):
        self.current_scene = Game.WIN

    def lose(self):
        self.current_scene = Game.LOSE

    def quit(self):  # good place to save high score, possibly
        self.running = False

    def check_status(self):
        if self.current_scene == Game.PLAYING:
            if not self.world.hero.is_alive:
                self.lose()
            if self.world.hero.reached_goal:
                self.complete_level()
                self.transition_time = settings.LEVEL_TRANSITION_TIME

        elif self.current_scene == Game.LEVEL_COMPLETE:
            self.transition_time -= 1

            if self.transition_time == 0:
                if self.level < len(settings.LEVELS):
                    self.advance()
                else:
                    self.win()

    def open_infobox(self, infobox):
        self.infobox = infobox
        self.current_scene = Game.INTERACTING

    def close_infobox(self):
        self.infobox = None
        self.current_scene = Game.PLAYING

    def process_input(self):
        pressed_keys = pygame.key.get_pressed()
        filtered_events = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            elif event.type == pygame.KEYDOWN:
                # for level editing
                if event.key == pygame.K_g:
                    self.grid.toggle()
                elif event.key == pygame.K_c:
                    self.camera.toggle()

                # start/restart/pause
                if self.current_scene == Game.START:
                    if event.key == pygame.K_SPACE:
                        self.start_level()
                        continue
                elif self.current_scene in [Game.WIN, Game.LOSE]:
                    if event.key == pygame.K_r:
                        self.new_game()
                        continue
                    elif event.key == pygame.K_q:
                        self.quit()
                        continue
                elif self.current_scene in [Game.PLAYING, Game.PAUSE]:
                    if event.key == pygame.K_p:
                        self.toggle_pause()
                        continue
                
            # actual gameplay
            filtered_events.append(event)

        if self.current_scene == Game.PLAYING:
            self.world.hero.act(filtered_events, pressed_keys)
        elif self.current_scene == Game.INTERACTING:
            self.infobox.act(filtered_events, pressed_keys)
     
    def update(self):
        if self.current_scene == Game.PLAYING:
            self.world.update()

        self.check_status()
        self.camera.update()

    def render(self):
        offset_x, offset_y = self.camera.get_offsets()
        self.world.draw(self.screen, offset_x, offset_y)
        self.hud.draw(self.screen)

        if self.infobox is not None:
            self.infobox.draw(self.screen)
        elif self.current_scene != Game.PLAYING:
            self.scene_overlays[self.current_scene].draw(self.screen)

        self.grid.draw(self.screen, offset_x, offset_y)
        self.camera.draw(self.screen)
        
    def play(self):
        while self.running:
            self.process_input()     
            self.update()     
            self.render()
            
            pygame.display.update()
            self.clock.tick(settings.FPS)

        pygame.quit()
