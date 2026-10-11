"""Visual inspection tool"""

from typing import Any, Dict
from .base import DiagnosticTool, MeasurementResult


class VisualInspection(DiagnosticTool):
    """Visual inspection of components"""
    
    def __init__(self):
        super().__init__("Visual Inspection", cost_per_use=0.0)
        
    def measure(
        self,
        vehicle: Any,
        target: str,
        measurement: str = "general",
        params: Dict[str, Any] = None
    ) -> MeasurementResult:
        """
        Visually inspect a component.
        
        Args:
            vehicle: Vehicle object
            target: Component ID
            measurement: Aspect to inspect (usually "general")
            params: Additional parameters
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
        data = component.get_reading("visual", measurement, params)
        
        return MeasurementResult(
            tool_name=self.name,
            target=target,
            measurement=measurement,
            data=data,
            cost=self.cost_per_use
        )
