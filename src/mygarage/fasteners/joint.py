"""One nut engaged on one bolt.

Turns are counted from the first thread engagement toward the seat.
Zero turns is still on the first thread but not clamping. ``seated_turns``
is fully tight. Positive ``turn`` tightens; negative backs the nut off.
"""

import math
from dataclasses import dataclass
from typing import Tuple

from mygarage.fasteners.bolt import Bolt
from mygarage.fasteners.nut import Nut


@dataclass
class ThreadedJoint:
    """Clamps ``clamps[1]`` against ``clamps[0]`` when the nut is seated."""

    joint_id: str
    bolt: Bolt
    nut: Nut
    clamps: Tuple[str, str]
    turns: float = 0.0

    def __post_init__(self) -> None:
        if not self.bolt.thread.matches(self.nut.thread):
            raise ValueError(
                f'{self.nut.nut_id} does not match {self.bolt.bolt_id}: '
                'diameter and pitch must be the same'
            )
        self.turns = min(self.seated_turns, max(0.0, self.turns))

    @property
    def seated_turns(self) -> float:
        """Turns from first engagement until the nut is against the seat."""
        return min(self.bolt.thread.turns_available, self.nut.thread.turns_available)

    @property
    def advance_m(self) -> float:
        """How far the nut has traveled from the thread tip toward the seat."""
        return self.bolt.thread.advance_m(self.turns)

    @property
    def spin_rad(self) -> float:
        return self.turns * 2.0 * math.pi

    @property
    def seated(self) -> bool:
        return self.turns >= self.seated_turns - 1e-6

    @property
    def engaged(self) -> bool:
        return self.turns > 0.0

    def turn(self, delta_turns: float) -> float:
        """Turn the nut. Returns the turns actually applied after the limits."""
        before = self.turns
        self.turns = min(self.seated_turns, max(0.0, self.turns + delta_turns))
        return self.turns - before

    def seat(self) -> None:
        """Run the nut down to the seat."""
        self.turns = self.seated_turns
