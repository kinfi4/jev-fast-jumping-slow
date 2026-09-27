"""
Definition:
A visual debugging aid for level design that overlays a grid on the screen.

Responsibilities:
- Draw vertical and horizontal grid lines based on the game's GRID_SIZE.
- Optionally display coordinates of each grid cell.
- Adjust lines dynamically based on camera offsets for accurate positioning.

Trigger / Usage:
- Can be toggled on/off.
- Updated and drawn each frame during level editing or debugging.
- Primarily intended for developers; does not affect gameplay mechanics.
"""

# Standard Library Imports


# Third-Party Imports
import pygame

# Local Imports
import settings


# Used for level editing
class Grid:

    def __init__(self, game, color=(125, 125, 125)):
        self.game = game
        self.on = False

        self.color = color
        self.font = pygame.font.Font(None, 16)

    def toggle(self):
        self.on = not self.on

    def draw(self, surface, offset_x=0, offset_y=0):
        if self.on:
            width = surface.get_width()
            height = surface.get_height()
            
            for x in range(0, width + settings.GRID_SIZE, settings.GRID_SIZE):
                adj_x = x - offset_x % settings.GRID_SIZE
                pygame.draw.line(surface, self.color, [adj_x, 0], [adj_x, height], 1)

            for y in range(0, height + settings.GRID_SIZE, settings.GRID_SIZE):
                adj_y = y - offset_y % settings.GRID_SIZE
                pygame.draw.line(surface, self.color, [0, adj_y], [width, adj_y], 1)

            for x in range(0, width + settings.GRID_SIZE, settings.GRID_SIZE):
                for y in range(0, height + settings.GRID_SIZE, settings.GRID_SIZE):
                    adj_x = x - offset_x % settings.GRID_SIZE + 4
                    adj_y = y - offset_y % settings.GRID_SIZE + 4
                    disp_x = x // settings.GRID_SIZE + offset_x // settings.GRID_SIZE
                    disp_y = y // settings.GRID_SIZE + offset_y // settings.GRID_SIZE
                    
                    point = f'({disp_x}, {disp_y})'
                    text = self.font.render(point, True, self.color)
                    surface.blit(text, [adj_x, adj_y])
