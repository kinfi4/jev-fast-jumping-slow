"""Play the vendored platformer (game/), either yourself or with Jev playing.

Usage:
    python run.py manual            # you play, nothing needed
    python run.py jev               # Jev plays levels 1-2 - needs TYPESAFE_API_KEY
    python run.py jev --level 2     # start at level 2

In jev mode, human input still works for menus (space/r/q) and pausing (p);
only in-level movement is taken over. Jev's latest decision is shown at the
bottom of the screen. When the hero runs out of hearts, the "You lose!" screen
stays up for 2.5 s and then the same level restarts with full hearts.
"""

from __future__ import annotations

import argparse
import os
import sys

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DIR = os.path.join(REPO_DIR, "game")

from dotenv import load_dotenv

load_dotenv(os.path.join(REPO_DIR, ".env"))

# The vendored game loads assets ("assets/images/...") relative to its own
# directory, so it needs to be both on sys.path and the current directory.
sys.path.insert(0, GAME_DIR)
os.chdir(GAME_DIR)

import pygame
import settings
from platformer.entities.hero import Hero
from platformer.game import Game

# The demo uses its own two levels (levels/) instead of the vendored ten.
LEVELS_DIR = os.path.join(REPO_DIR, "levels")
settings.LEVELS = [os.path.join(LEVELS_DIR, name) for name in ("level-1.json", "level-2.json")]

RESTART_DELAY_FRAMES = 150  # 2.5 s on the "You lose!" screen before retrying


class AgentHero(Hero):
    """Same physics as Hero, but driven by a brain instead of the keyboard."""

    def __init__(self, game, location, animations, controls, brain):
        super().__init__(game, location, animations, controls)
        self.brain = brain

    def act(self, events, pressed_keys):
        new_decision = self.brain.maybe_decide(self.game)
        action = self.brain.action

        if action["dx"] > 0:
            self.go_right()
        elif action["dx"] < 0:
            self.go_left()
        else:
            self.stop_x()

        # One jump attempt per decision, like a key press - holding it for the
        # whole interval would re-jump the instant the hero lands.
        if new_decision and action["jump"]:
            self.jump()


class AgentGame(Game):
    def __init__(self, brain):
        self.brain = brain
        self.lose_timer = 0
        super().__init__()
        self.status_font = pygame.font.Font(settings.PRIMARY_FONT, 28)

    def new_game(self):
        self.hero = AgentHero(self, None, self.hero_animations, settings.CONTROLS, self.brain)
        self.current_scene = Game.START
        self.level = settings.STARTING_LEVEL
        self.score = 0
        self.load_level()

    def update(self):
        super().update()
        if self.current_scene != Game.LOSE:
            self.lose_timer = 0
            return

        self.lose_timer += 1
        remaining = (RESTART_DELAY_FRAMES - self.lose_timer) / settings.FPS
        self.brain.status = f"Jev lost - retrying level {self.level} in {remaining:.1f}s"
        if self.lose_timer >= RESTART_DELAY_FRAMES:
            self.retry_level()

    def retry_level(self):
        level = self.level
        self.new_game()  # fresh hero with full hearts
        self.level = level
        self.load_level()
        self.brain.action = {"dx": 0, "jump": False}
        self.start_level()
        print(f"Jev lost, retrying level {level}")

    def render(self):
        super().render()
        text = self.status_font.render(self.brain.status, True, settings.WHITE)
        self.screen.blit(text, (16, settings.SCREEN_HEIGHT - text.get_height() - 12))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=["manual", "jev"], help="'manual' to play yourself, 'jev' to watch Jev play")
    parser.add_argument("--level", type=int, default=1, choices=range(1, len(settings.LEVELS) + 1))
    args = parser.parse_args()

    settings.STARTING_LEVEL = args.level

    if args.mode == "manual":
        print("Manual mode: A/D to move, space to jump, W/S to climb, e to interact, p to pause.")
        Game().play()
    else:
        from jev_brain import JevBrain

        AgentGame(JevBrain()).play()


if __name__ == "__main__":
    main()
