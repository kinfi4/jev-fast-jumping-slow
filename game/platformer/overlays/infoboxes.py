"""
Definition:
Overlay text boxes that provide information or dialogue to the player.

Responsibilities:
- Display multi-page text with optional styling (font, colors, padding).
- Handle player input for navigating pages or dismissing the box.
- Specialized subclasses support specific contexts like signs or NPC speech.

Trigger / Usage:
- Activated via player interaction with an object (e.g., Sign or NPC).
- Drawn on top of the game surface while the game is in the INTERACTING scene.
"""

# Standard Library Imports


# Third-Party Imports
import pygame

# Local Imports
import settings


class InfoBox:
    BOX_COLOR = settings.WHITE
    BORDER_COLOR = settings.BLACK
    TEXT_COLOR = settings.BLACK
    BORDER_RADIUS = 12
    BORDER_THICKNESS = 4
    MAX_WIDTH = settings.SCREEN_WIDTH * 0.5
    LINE_SPACING = 6
    PADDING = 24
    FONT_SIZE = 48

    def __init__(self, game, message, **kwargs):
        self.game = game
        if isinstance(message, str):
            self.pages = [message]
        elif isinstance(message, list):
            self.pages = message

        self.current_page = 0
   
        self.background_color = kwargs.get("background_color", self.BOX_COLOR)
        self.border_color = kwargs.get("border_color", self.BORDER_COLOR)
        self.border_radius = kwargs.get("border_radius", self.BORDER_RADIUS)
        self.border_thickness = kwargs.get("border_thickness", self.BORDER_THICKNESS)
        self.max_width = kwargs.get("max_width", self.MAX_WIDTH)
        self.line_spacing = kwargs.get("line_spacing", self.LINE_SPACING)
        self.padding = kwargs.get("padding", self.PADDING)
        self.text_color = kwargs.get("text_color", self.TEXT_COLOR)
        
        font_family = kwargs.get("font_family", settings.SECONDARY_FONT)
        font_size = kwargs.get("font_size", self.FONT_SIZE)
        self.font = pygame.font.Font(font_family, font_size)

        self.render_current_page()     

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current = []

        for word in words:
            test = " ".join(current + [word])
            if font.size(test)[0] <= max_width - self.padding * 2:
                current.append(word)
            else:
                lines.append(" ".join(current))
                current = [word]

        if current:
            lines.append(" ".join(current))

        return lines
       
    def render_current_page(self):
        # Wrap text to box size
        text = self.pages[self.current_page].strip()
        self.lines = self.wrap_text(text, self.font, self.max_width)

        # Compute box size from lines
        total_text_height = len(self.lines) * self.font.get_height() + (len(self.lines)-1) * self.line_spacing
        self.box_width = self.max_width
        self.box_height = total_text_height + self.padding * 2

        # Center box
        self.rect = pygame.Rect(0, 0, self.box_width, self.box_height)
        self.rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)

    def act(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == settings.CONTROLS['dismiss']:
                    self.game.close_infobox()
                elif event.key == settings.CONTROLS['right'] and self.current_page < len(self.pages) - 1:
                    self.current_page += 1
                    self.render_current_page()
                elif event.key == settings.CONTROLS['left'] and self.current_page > 0:
                    self.current_page -= 1
                    self.render_current_page()

    def update(self):
        pass

    def draw(self, surface):
        # Draw box
        pygame.draw.rect(surface, self.background_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, self.border_color, self.rect, width=self.border_thickness, border_radius=self.border_radius)
        
        # Draw each line of text
        x = self.rect.x + self.padding
        y = self.rect.y + self.padding
        
        for line in self.lines:
            text_surf = self.font.render(line, True, self.text_color)
            surface.blit(text_surf, (x, y))
            y += text_surf.get_height() + self.line_spacing


class SignText(InfoBox):
    def __init__(self, game, text):
        super().__init__(
            game, 
            text,
            font_size=48,
            background_color=(174, 118, 64),
            border_color=(115, 97, 80),
            text_color=(255, 255, 255)
        )


class SpeechBubble(InfoBox):

    def __init__(self, game, text, npc=None):
        super().__init__(
            game, 
            text,
            font_size=32
        )
        self.npc = npc  # Use for positioning speech bubble later
