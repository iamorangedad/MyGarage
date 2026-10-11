"""MyGarage - A game-like simulator for practicing car diagnosis and repair."""

__version__ = "0.1.0"

from mygarage.game import Game
from mygarage.fault_engine import FaultEngine
from mygarage.system_model import SystemModel

__all__ = ["Game", "FaultEngine", "SystemModel"]
