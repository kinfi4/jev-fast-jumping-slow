"""
Definition:
Heads-up display (HUD) overlay showing vital player and game information.

Responsibilities:
- Render player stats such as level, score, and hearts.
- Optionally update or animate HUD elements if needed (currently a placeholder update method).
- Draws directly to the game surface each frame.

Trigger / Usage:
- Called each frame from Game.render() after the world has been drawn.
- No input handling; purely visual feedback.
"""

# Standard Library Imports


# Third-Party Imports
import pygame

# Local Imports
import settings


class HUD:

    def __init__(self, game):
        self.game = game

        self.primary_font = pygame.font.Font(settings.PRIMARY_FONT, 32)
        self.secondary_font = pygame.font.Font(settings.SECONDARY_FONT, 16)
        
    def update(self):
        pass

    def draw(self, surface):
        text = self.primary_font.render(f"Level: {self.game.level}", True, settings.WHITE)
        rect = text.get_rect()
        rect.topleft = 16, 16
        surface.blit(text, rect)

        text = self.primary_font.render(f"Score: {self.game.score}", True, settings.WHITE)
        rect = text.get_rect()
        rect.topleft = 16, 56
        surface.blit(text, rect)

        text = self.primary_font.render(f"Hearts: {self.game.world.hero.hearts}", True, settings.WHITE)
        rect = text.get_rect()
        rect.topleft = 16, 96
        surface.blit(text, rect)
