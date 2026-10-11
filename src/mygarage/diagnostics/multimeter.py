"""Multimeter tool for electrical measurements"""

from typing import Any, Dict
from .base import DiagnosticTool, MeasurementResult


class Multimeter(DiagnosticTool):
    """Digital multimeter for voltage, current, resistance measurements"""
    
    def __init__(self):
        super().__init__("Multimeter", cost_per_use=0.0)
        
    def measure(
        self,
        vehicle: Any,
        target: str,
        measurement: str,
        params: Dict[str, Any] = None
    ) -> MeasurementResult:
        """
        Measure electrical properties.
        
        Args:
            vehicle: Vehicle object
            target: Component ID (e.g., "battery", "starter")
            measurement: Type of measurement (e.g., "resting_voltage", "resistance")
            params: Additional parameters like load_current
        """
        params = params or {}
        
        if target not in vehicle.components:
            return MeasurementResult(
                tool_name=self.name,
                target=target,
                measurement=measurement,
                data={"error": f"Component {target} not found"},
                cost=self.cost_per_use
            )
            
        component = vehicle.components[target]
        data = component.get_reading("multimeter", measurement, params)
        
        return MeasurementResult(
            tool_name=self.name,
            target=target,
            measurement=measurement,
            data=data,
            cost=self.cost_per_use
        )
