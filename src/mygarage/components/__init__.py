"""Component system for car parts"""

from .base import Component, ComponentState
from .battery import Battery
from .starter import StarterMotor

__all__ = ["Component", "ComponentState", "Battery", "StarterMotor"]
