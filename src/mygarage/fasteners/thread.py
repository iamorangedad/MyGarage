"""Metric thread geometry.

One turn of a matching nut advances it by exactly one pitch along the bolt.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Thread:
    """A single-start thread. Length is the usable threaded distance."""

    diameter_m: float
    pitch_m: float
    length_m: float

    def __post_init__(self) -> None:
        if self.diameter_m <= 0 or self.pitch_m <= 0 or self.length_m <= 0:
            raise ValueError('Thread diameter, pitch, and length must be positive')

    @property
    def turns_available(self) -> float:
        """How many turns fit on this thread."""
        return self.length_m / self.pitch_m

    def advance_m(self, turns: float) -> float:
        """Axial travel after ``turns``. One turn moves one pitch."""
        return turns * self.pitch_m

    def matches(self, other: 'Thread') -> bool:
        """A nut can start on a bolt only when diameter and pitch agree."""
        return (
            abs(self.diameter_m - other.diameter_m) <= 1e-9
            and abs(self.pitch_m - other.pitch_m) <= 1e-9
        )
