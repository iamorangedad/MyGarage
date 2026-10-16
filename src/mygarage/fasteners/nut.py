"""A nut that can be threaded onto a matching bolt."""

from dataclasses import dataclass

from mygarage.fasteners.thread import Thread


@dataclass(frozen=True)
class Nut:
    """Hex nut. Its thread must match the bolt it is screwed onto."""

    nut_id: str
    thread: Thread
    thickness_m: float = 0.008

    def __post_init__(self) -> None:
        if self.thickness_m <= 0:
            raise ValueError('Nut thickness must be positive')

    @property
    def spin_joint(self) -> str:
        return f'{self.nut_id}_spin'

    @property
    def travel_joint(self) -> str:
        return f'{self.nut_id}_travel'
