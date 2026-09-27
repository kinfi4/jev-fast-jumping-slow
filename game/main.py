"""
Entry point for running the game.

Responsibilities:
- Instantiate the Game class.
- Start the main game loop via Game.play().

Usage:
- Run this file directly to launch the game.
"""

# Standard library
import json

# Third-party

# Local
from platformer.game import Game


def main():
    g = Game()
    g.play()


if __name__ == "__main__":
    main()
