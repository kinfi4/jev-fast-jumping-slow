"""
Definition:
Full-screen overlays used to convey game states and instructions to the player.

Responsibilities:
- Render static or semi-static text for major game scenes such as:
    - Title screen
    - Win/Lose screens
    - Level completion
    - Pause state
- Provide minimal update logic; primarily visual.
- Drawn on top of the game surface when the game is in a corresponding scene.

Trigger / Usage:
- Activated automatically by the game when the player reaches a certain scene (start, win, lose, pause, level complete).
- Interacts with player input only to progress past the screen (e.g., 'SPACE', 'r', 'p').
"""

# Standard Library Imports


# Third-Party Imports
import pygame

# Local Imports
import settings


class TitleScreen:

    def __init__(self, game):
        self.game = game

        self.title_font = pygame.font.Font(settings.PRIMARY_FONT, 80)
        self.subtitle_font = pygame.font.Font(settings.SECONDARY_FONT, 32)
        
    def update(self):
        pass

    def draw(self, surface):
        text = self.title_font.render(settings.CAPTION, True, settings.WHITE)
        rect = text.get_rect()
        rect.centerx = settings.SCREEN_WIDTH // 2
        rect.bottom = settings.SCREEN_HEIGHT // 2 - 8
        surface.blit(text, rect)
    
        text = self.subtitle_font.render("Press 'SPACE' to start.", True, settings.WHITE)
        rect = text.get_rect()
        rect.centerx = settings.SCREEN_WIDTH // 2
        rect.top = settings.SCREEN_HEIGHT // 2 + 8
        surface.blit(text, rect)


class WinScreen:

    def __init__(self, game):
        self.game = game

        self.title_font = pygame.font.Font(settings.PRIMARY_FONT, 80)
        self.subtitle_font = pygame.font.Font(settings.SECONDARY_FONT, 32)
        
    def update(self):
        pass

    def draw(self, surface):
        text = self.title_font.render("You win!", True, settings.WHITE)
        rect = text.get_rect()
        rect.centerx = settings.SCREEN_WIDTH // 2
        rect.bottom = settings.SCREEN_HEIGHT // 2 - 8
        surface.blit(text, rect)
    
        text = self.subtitle_font.render("Press 'r' to play again or 'q' to quit.", True, settings.WHITE)
        rect = text.get_rect()
        rect.centerx = settings.SCREEN_WIDTH // 2
        rect.top = settings.SCREEN_HEIGHT // 2 + 8
        surface.blit(text, rect)


class LoseScreen:

    def __init__(self, game):
        self.game = game

        self.title_font = pygame.font.Font(settings.PRIMARY_FONT, 80)
        self.subtitle_font = pygame.font.Font(settings.SECONDARY_FONT, 32)
        
    def update(self):
        pass

    def draw(self, surface):
        text = self.title_font.render("You lose!", True, settings.WHITE)
        rect = text.get_rect()
        rect.centerx = settings.SCREEN_WIDTH // 2
        rect.bottom = settings.SCREEN_HEIGHT // 2 - 8
        surface.blit(text, rect)
    
        text = self.subtitle_font.render("Press 'r' to play again or 'q' to quit.", True, settings.WHITE)
        rect = text.get_rect()
        rect.centerx = settings.SCREEN_WIDTH // 2
        rect.top = settings.SCREEN_HEIGHT // 2 + 8
        surface.blit(text, rect)


class LevelCompleteScreen:

    def __init__(self, game):
        self.game = game

        self.title_font = pygame.font.Font(settings.SECONDARY_FONT, 32)
        
    def update(self):
        pass

    def draw(self, surface):
        text = self.title_font.render("Level Complete!", True, settings.WHITE)
        rect = text.get_rect()
        rect.centerx = settings.SCREEN_WIDTH // 2
        rect.bottom = settings.SCREEN_HEIGHT // 2 - 8
        surface.blit(text, rect)


class PauseScreen:

    def __init__(self, game):
        self.game = game

        self.title_font = pygame.font.Font(settings.PRIMARY_FONT, 80)
        self.subtitle_font = pygame.font.Font(settings.SECONDARY_FONT, 32)
        
    def update(self):
        pass

    def draw(self, surface):
        text = self.subtitle_font.render("Paused", True, settings.WHITE)
        rect = text.get_rect()
        rect.centerx = settings.SCREEN_WIDTH // 2
        rect.bottom = settings.SCREEN_HEIGHT // 2 - 8
        surface.blit(text, rect)
    
        text = self.subtitle_font.render("Press 'p' to continue", True, settings.WHITE)
        rect = text.get_rect()
        rect.centerx = settings.SCREEN_WIDTH // 2
        rect.top = settings.SCREEN_HEIGHT // 2 + 8
        surface.blit(text, rect)
