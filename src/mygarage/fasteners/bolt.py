"""A bolt or stud planted in one solid member."""

from dataclasses import dataclass
from typing import Tuple

from mygarage.fasteners.thread import Thread


@dataclass(frozen=True)
class Bolt:
    """Stud fixed in ``planted_in``. ``position`` is the thread tip in that member's frame."""

    bolt_id: str
    thread: Thread
    planted_in: str
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
