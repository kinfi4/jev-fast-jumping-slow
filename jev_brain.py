"""Perception in code, decisions by Jev.

perceive() reads the real game objects (not pixels) and turns them into a
compact, pre-digested description: is there a wall right ahead and how tall,
is the hero standing at the edge of a pit, what are nearby enemies doing, plus
a small ASCII map for context. Jev then answers two questions about it: how
to move, and whether to jump.

The Jev call is synchronous and made every DECISION_INTERVAL_FRAMES frames.
Game physics is frame-based, so the game simply pauses while Jev thinks: the
agent's reaction time is a fixed number of frames regardless of API latency,
which keeps jump timing reliable.
"""

from __future__ import annotations

import time

import pygame
import settings
from typesafe_sdk import Choice, Noul, TypeSafeClient

DECISION_INTERVAL_FRAMES = 6

G = settings.GRID_SIZE
# Hero runs at 5 px/frame and a jump lasts ~42 frames, so a running jump
# clears a head-on enemy only if taken within this gap.
JUMP_RANGE_PX = 80
# Following an enemy that moves away is unsafe: a jump over it lands on it.
FOLLOW_DISTANCE_PX = 192
# Ground enemies bounce off walls, so the side behind a wall is safe; jumping
# over while one is this close on the other side lands on it.
BEYOND_WALL_CAUTION_PX = 6 * 64
# Jumping a pit lands just past its far edge ~42 frames later. An enemy
# closer than this to that edge (measured at takeoff) could be under the hero.
BEYOND_PIT_CAUTION_APPROACHING_PX = 4 * 64
BEYOND_PIT_CAUTION_MOVING_AWAY_PX = 96
MAX_JUMPABLE_WALL_TILES = 3
# Pit edge probe: close enough that a running jump still clears a 3-tile pit.
PIT_PROBE_PX = 8

MAP_BEHIND, MAP_AHEAD = 2, 8
SYMBOLS = {
    "Platform": "#", "Spikeball": "S", "Spikeman": "M", "Cloud": "C", "Fish": "f",
    "Gem": "g", "Heart": "h", "Key": "k", "Ladder": "L", "Water": "~",
    "Door": "D", "Sign": "?", "NPC": "N", "Flag": "F", "Flagpole": "F",
}

# Conditions live in each option's description: with them only in the
# instructions, real Jev picked "wait" at a clear wall just for the word "wall".
QUESTIONS = {
    "move": Choice(
        instructions="How should the hero move right now? The hero must reach the goal without touching any enemy.",
        criteria={
            "forward": (
                "Walk toward the goal. Right whenever the way forward is clear, and also when the hero "
                "has to jump over a wall, a pit or an enemy coming toward it."
            ),
            "wait": (
                "Stand still. Right only when an enemy ahead is moving away but is too close to follow, "
                "when an enemy is falling onto the path just ahead, when an enemy is close on the other "
                "side of the wall directly ahead, or when the hero is at the edge of a pit and an enemy is "
                "close to where the hero would land."
            ),
            "back": "Walk away from the goal. Almost never right.",
        },
    ),
    "jump": Noul(
        instructions=(
            "The hero should jump right now. True only if: the wall directly ahead can be jumped over and its "
            "other side is clear, or the hero is standing at the edge of a pit and its far side is clear, or an "
            "enemy coming toward the hero is close enough to jump over now. False if an enemy is close on the "
            "other side of the wall ahead, or close to where the hero would land beyond the pit."
        ),
    ),
}


def _tile(rect: pygame.Rect) -> tuple[int, int]:
    return rect.centerx // G, rect.centery // G


def _ground_below(world, x: int, feet_y: int) -> bool:
    return any(p.rect.left <= x < p.rect.right and p.rect.top >= feet_y - 1 for p in world.platforms)


def _wall_height_tiles(world, hero, direction: int) -> float:
    probe = hero.rect.move(direction * 8, 0)
    probe.height -= 2  # don't count the ground under the hero's feet
    if not any(probe.colliderect(p.rect) for p in world.platforms):
        return 0

    x = probe.right - 1 if direction > 0 else probe.left
    column = sorted(
        (p.rect for p in world.platforms if p.rect.left <= x < p.rect.right and p.rect.bottom <= hero.rect.bottom + 1),
        key=lambda r: -r.bottom,
    )
    top = hero.rect.bottom
    for r in column:
        if abs(r.bottom - top) <= 1:
            top = r.top
    return max((hero.rect.bottom - top) / G, 1)


def _pit_span(world, hero, direction: int) -> tuple[int, int] | None:
    """(start, end): px from the hero's leading edge to where a pit begins and
    to where ground resumes, or None if there's no pit within 5 tiles. The
    pit is at the edge when start == PIT_PROBE_PX."""
    lead = hero.rect.right if direction > 0 else hero.rect.left
    feet = hero.rect.bottom
    start = next((s for s in range(PIT_PROBE_PX, 5 * G, 8)
                  if not _ground_below(world, lead + direction * s, feet)), None)
    if start is None:
        return None
    end = next((s for s in range(start, start + 7 * G, 8)
                if _ground_below(world, lead + direction * s, feet)), start + 7 * G)
    return start, end


def _signed_gap(hero_rect: pygame.Rect, rect: pygame.Rect) -> int:
    if rect.left >= hero_rect.right:
        return rect.left - hero_rect.right
    if rect.right <= hero_rect.left:
        return rect.right - hero_rect.left
    return 0


def _near_landing(gap: int, enemy, pit: tuple[int, int], direction: int) -> bool:
    """Whether an enemy beyond the pit is close to where a jump over it would land."""
    past_far_edge = gap - pit[1]
    approaching = enemy.vx * direction < 0
    return past_far_edge < (BEYOND_PIT_CAUTION_APPROACHING_PX if approaching else BEYOND_PIT_CAUTION_MOVING_AWAY_PX)


def _enemy_reports(world, hero, direction: int, wall_ahead: bool,
                   pit: tuple[int, int] | None) -> tuple[str, str, bool, bool, bool]:
    """Returns (ahead report, behind report, enemy falling onto the path,
    enemy close on the far side of the wall ahead, enemy close on the far
    side of the pit ahead)."""
    ahead, behind = None, None
    falling_ahead = False
    enemy_beyond_pit = False

    for e in world.enemies:
        gap = _signed_gap(hero.rect, e.rect) * direction
        same_level = e.rect.bottom > hero.rect.top and e.rect.top < hero.rect.bottom
        falling = e.vy > 1.5

        if falling and e.rect.bottom <= hero.rect.top and -G < gap < 2 * G:
            falling_ahead = True
        if same_level and pit and gap > pit[0]:
            enemy_beyond_pit |= _near_landing(gap, e, pit, direction)
        if not same_level or abs(gap) > 6 * G:
            continue
        if gap >= 0 and (ahead is None or gap < ahead[0]):
            ahead = (gap, e)
        elif gap < 0 and (behind is None or gap > behind[0]):
            behind = (gap, e)

    def describe(entry, is_ahead: bool) -> str:
        if entry is None:
            return "none"
        gap, e = entry
        name = type(e).__name__
        dist = f"{abs(gap) / G:.1f} tiles away"
        if gap == 0:
            return f"{name} is touching the hero"
        approaching = (e.vx * direction < 0) if is_ahead else (e.vx * direction > 0)
        if not is_ahead:
            return f"{name} {dist}, {'catching up' if approaching else 'moving away'}"
        motion = "coming toward the hero" if approaching else "moving away from the hero"
        if wall_ahead:
            return f"{name} {dist}, on the other side of the wall ahead, {motion}"
        if pit and gap > pit[0]:
            # "on the far side" alone next to "far side is clear" left real Jev at jump=0.47
            where = "close to" if _near_landing(gap, e, pit, direction) else "far enough from"
            return f"{name} {dist}, beyond the pit ahead, {motion}, {where} where the hero would land"
        if approaching:
            if abs(gap) <= JUMP_RANGE_PX:
                return f"{name} {dist}, coming toward the hero, close enough to jump over now"
            return f"{name} {dist}, coming toward the hero, too far to jump over yet"
        if e.vx == 0:
            return f"{name} {dist}, not moving"
        if abs(gap) < FOLLOW_DISTANCE_PX:
            return f"{name} {dist}, moving away from the hero, too close to follow"
        return f"{name} {dist}, moving away from the hero, far enough to follow"

    enemy_beyond_wall = False
    if wall_ahead and ahead is not None:
        gap, e = ahead
        approaching = e.vx * direction < 0
        enemy_beyond_wall = gap < (BEYOND_WALL_CAUTION_PX if approaching else FOLLOW_DISTANCE_PX + G)

    return describe(ahead, True), describe(behind, False), falling_ahead, enemy_beyond_wall, enemy_beyond_pit


def minimap(world) -> str:
    hx, hy = _tile(world.hero.rect)
    cells = {}
    for group in (world.water, world.platforms, world.climbables, world.interactables,
                  world.items, world.goals, world.enemies):
        for s in group:
            cells[_tile(s.rect)] = SYMBOLS.get(type(s).__name__, "?")
    cells[(hx, hy)] = "H"
    cols = range(hx - MAP_BEHIND, hx + MAP_AHEAD + 1)
    rows = world.world_height // G
    return "\n".join("".join(cells.get((x, y), ".") for x in cols) for y in range(rows))


def perceive(world) -> tuple[dict, int, dict]:
    """Returns (state for Jev, direction toward the goal: +1 right / -1 left,
    facts for the safety guard)."""
    hero = world.hero
    goal = min(world.goals, key=lambda g: abs(g.rect.centerx - hero.rect.centerx))
    direction = 1 if goal.rect.centerx >= hero.rect.centerx else -1

    wall = _wall_height_tiles(world, hero, direction)
    pit = _pit_span(world, hero, direction) if hero.on_platform else None
    enemy_ahead, enemy_behind, falling_ahead, enemy_beyond_wall, enemy_beyond_pit = _enemy_reports(
        world, hero, direction, wall_ahead=bool(wall), pit=pit
    )
    height = f"{wall:.0f} tile{'' if round(wall) == 1 else 's'} high"
    if not wall:
        wall_report = "none"
    elif wall > MAX_JUMPABLE_WALL_TILES:
        wall_report = f"{height}, too high to jump over"
    elif enemy_beyond_wall:
        wall_report = f"{height}, but an enemy is close on its other side, so it is not safe to jump over yet"
    else:
        wall_report = f"{height}, low enough to jump over, and the other side is clear"

    at_pit_edge = pit is not None and pit[0] == PIT_PROBE_PX
    if not hero.on_platform:
        pit_report = "the hero is in the air"
    elif pit is None:
        pit_report = "no pit ahead"
    elif at_pit_edge and enemy_beyond_pit:
        pit_report = ("the hero is standing at the edge of a pit, but an enemy is close to where the hero "
                      "would land, so it is not safe to jump yet")
    elif at_pit_edge:
        pit_report = ("the hero is standing at the edge of a pit, and its far side is clear - "
                      "walking on without jumping means falling in")
    else:
        pit_report = f"pit starts {pit[0] / G:.1f} tiles ahead, not at the edge yet"

    safety = {
        # a running jump covers ~3.3 tiles, so jumping before the edge of a pit lands in it
        "pit_close_but_not_at_edge": pit is not None and not at_pit_edge and pit[0] < 2 * G,
        "at_pit_edge": at_pit_edge,
        "over_pit": not hero.on_platform and not _ground_below(world, hero.rect.centerx, hero.rect.bottom),
    }

    state = {
        "goal": f"{abs(goal.rect.centerx - hero.rect.centerx) / G:.0f} tiles ahead",
        "hero_on_ground": bool(hero.on_platform),
        "hearts_left": hero.hearts,
        "wall_directly_ahead": wall_report,
        "pit": pit_report,
        "nearest_enemy_ahead": enemy_ahead,
        "nearest_enemy_behind": enemy_behind,
        "enemy_falling_onto_path_ahead": falling_ahead,
        "map": minimap(world),
        "map_legend": (
            f"H hero, # solid block, S/M/C enemies, g gem, h heart, k key, D door, F goal, . empty; "
            f"the goal is to the {'right' if direction > 0 else 'left'}"
        ),
    }
    return state, direction, safety


def guard(move: str, jump: bool, safety: dict) -> tuple[str, bool, str | None]:
    """Vetoes only actions that are certainly fatal; everything else is Jev's call."""
    if jump and safety["pit_close_but_not_at_edge"]:
        return move, False, "early jump before a pit"
    if move != "forward" and safety["over_pit"]:
        return "forward", jump, f"'{move}' in mid-air over a pit"
    if move == "forward" and not jump and safety["at_pit_edge"]:
        return "wait", jump, "walking off the edge of a pit without jumping"
    return move, jump, None


class Brain:
    """Holds the current action; refreshes it via decide() every `interval` frames.
    Subclasses implement decide() against a particular model."""

    interval = DECISION_INTERVAL_FRAMES

    def __init__(self):
        self.action = {"dx": 0, "jump": False}
        self.status = "waiting for first decision"
        self.calls = 0
        self.vetoes = 0
        self.input_tokens = 0
        self.latency_s = 0.0
        self._frame = 0

    def maybe_decide(self, game) -> bool:
        """Returns True on frames where a new decision was made."""
        self._frame += 1
        if (self._frame - 1) % self.interval:
            return False

        state, direction, safety = perceive(game.world)
        decision = self.decide(state)
        if decision is None:
            return False

        move, jump, veto = guard(*decision, safety)
        if veto:
            self.vetoes += 1
            self.status += f"  | vetoed: {veto}"
        dx = {"forward": direction, "back": -direction, "wait": 0}[move]
        self.action = {"dx": dx, "jump": jump}
        return True

    def decide(self, state: dict) -> tuple[str, bool] | None:
        """Returns (move: forward/wait/back, jump), or None to keep the last action."""
        raise NotImplementedError


class JevBrain(Brain):
    """TypeSafe's hosted Jev (needs TYPESAFE_API_KEY)."""

    def __init__(self):
        super().__init__()
        self.client = TypeSafeClient()

    def decide(self, state: dict) -> tuple[str, bool] | None:
        start = time.perf_counter()
        try:
            response = self.client.system_one(state=state, questions=QUESTIONS, timeout=5.0)
        except Exception as exc:
            self.status = f"Jev call failed, keeping last action: {exc}"
            print(f"[JevBrain] {self.status}")
            return None
        elapsed = time.perf_counter() - start

        self.calls += 1
        self.latency_s += elapsed
        self.input_tokens += response.usage.input_tokens

        move = response.answers["move"]
        jump = response.answers["jump"]
        self.status = (
            f"Jev: {move.choice} ({move.confidence:.2f})  jump={jump.noul:.2f}  {elapsed * 1000:.0f} ms"
        )
        return move.choice, jump.noul > 0.5
