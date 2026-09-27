"""
Definition:
Objects that modify the state of the world or provide information to the player. Activated using the interact key.

Examples:
- Doors (change levels or locations, may require keys)
- Switches or Buttons (trigger world changes)
- Signs (display text)
- NPCs (display speech bubbles or messages)

Trigger: Player presses the interact key while overlapping the object.
"""

# Standard Library Imports

# Third-Party Imports
import pygame

# Local Imports
import settings
from platformer.entities.entity  import Entity, AnimatedEntity
from platformer.overlays import SignText, SpeechBubble


class Door(Entity):

    def __init__(self, game, location, image, destination, code=None):
        super().__init__(game, location, image)

        self.code = code
        self.destination = destination
        self.unlocked = True if code == None else False

    def interact(self, character):
        if not self.unlocked and self.code in character.key_chain:
            self.unlocked = True
            character.key_chain.remove(self.code)
        
        if self.unlocked:
            character.move_to(self.destination)


class Sign(Entity):

    def __init__(self, game, location, image, text):
        super().__init__(game, location, image)
        self.text = text

    def interact(self, character=None):
        self.game.open_infobox(SignText(self.game, self.text))  


class NPC(Entity):

    def __init__(self, game, location, image, text):
        super().__init__(game, location, image)

        self.text = text

    def interact(self, character=None):
        self.game.open_infobox(SpeechBubble(self.game, self.text))
 
    def update(self):
        # character might walk or be animated
        pass


class Button(AnimatedEntity):

    def __init__(self, game, location, image, action):
        super().__init__(game, location, image)

        self.action = action

    def interact(self, character):
        # This is different. A button interacts with the world, not the character.
        pass


class Switch(AnimatedEntity):

    def __init__(self, game, location, image, action):
        super().__init__(game, location, image)

        self.action = action

    def interact(self, character):
        pass



