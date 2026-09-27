"""Headless run: let Jev play levels without a window and report the results.

Usage:
    python eval.py                 # levels 1-2
    python eval.py 2 --runs 3      # level 2, three attempts
"""

from __future__ import annotations

import argparse
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from run import AgentGame, Game  # also puts the vendored game on sys.path

import settings

PRICE_PER_INPUT_TOKEN = 0.042 / 1_000_000
MAX_FRAMES = 5000


def play_level(brain, level: int) -> dict:
    settings.STARTING_LEVEL = level
    game = AgentGame(brain)
    game.start_level()
    hearts, hearts_lost = game.hero.hearts, 0

    result = "timeout"
    for frame in range(MAX_FRAMES):
        game.process_input()
        game.update()
        # count every hit/fall, not the net change - picked-up hearts would hide losses
        hearts_lost += max(hearts - game.hero.hearts, 0)
        hearts = game.hero.hearts
        if game.current_scene == Game.LEVEL_COMPLETE:
            result = "complete"
            break
        if game.current_scene == Game.LOSE:
            result = "lost"
            break

    return {
        "level": level,
        "result": result,
        "frames": frame + 1,
        "hearts_lost": hearts_lost,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("levels", type=int, nargs="*", default=list(range(1, len(settings.LEVELS) + 1)))
    parser.add_argument("--runs", type=int, default=1)
    args = parser.parse_args()

    from jev_brain import JevBrain

    brain = JevBrain()
    for level in args.levels:
        for _ in range(args.runs):
            calls_before, vetoes_before = brain.calls, brain.vetoes
            r = play_level(brain, level)
            print(f"level {r['level']}: {r['result']:8s} frames={r['frames']:5d} "
                  f"hearts_lost={r['hearts_lost']} calls={brain.calls - calls_before} "
                  f"vetoed={brain.vetoes - vetoes_before}")

    if brain.calls:
        print(f"\n{brain.calls} calls, avg {brain.latency_s / brain.calls * 1000:.0f} ms, "
              f"{brain.input_tokens} input tokens (~{brain.input_tokens / brain.calls:.0f}/call), "
              f"cost ${brain.input_tokens * PRICE_PER_INPUT_TOKEN:.4f}")


if __name__ == "__main__":
    main()
