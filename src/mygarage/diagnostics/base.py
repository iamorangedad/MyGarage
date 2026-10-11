"""Base classes for diagnostic tools"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class MeasurementResult:
    """Result of a diagnostic measurement"""
    
    tool_name: str
    target: str
    measurement: str
    data: Dict[str, Any]
    cost: float = 0.0
    
    def __str__(self) -> str:
        """Format result as string"""
        reading = self.data.get("reading", str(self.data))
        return f"[{self.tool_name}] {self.target} - {self.measurement}: {reading}"


class DiagnosticTool(ABC):
    """Base class for diagnostic tools"""
    
    def __init__(self, name: str, cost_per_use: float = 0.0):
        self.name = name
        self.cost_per_use = cost_per_use
        
    @abstractmethod
    def measure(
        self,
        vehicle: Any,
        target: str,
        measurement: str,
        params: Dict[str, Any] = None
    ) -> MeasurementResult:
        """
        Perform a measurement.
        
        Args:
            vehicle: Vehicle object with components
            target: Target component ID
            measurement: What to measure
            params: Additional parameters
            
        Returns:
            MeasurementResult with data
        """
        pass
