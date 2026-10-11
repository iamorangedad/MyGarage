"""Fault system for managing vehicle faults"""

from .catalog import FaultCatalog, Fault
from .injector import FaultInjector

__all__ = ["FaultCatalog", "Fault", "FaultInjector"]
