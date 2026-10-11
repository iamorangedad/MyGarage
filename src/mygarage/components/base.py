"""Base classes for vehicle components"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ComponentState:
    """State of a component including any active faults"""
    
    fault_id: Optional[str] = None
    fault_params: Dict[str, Any] = field(default_factory=dict)
    custom_state: Dict[str, Any] = field(default_factory=dict)


class Component(ABC):
    """Base class for all vehicle components"""
    
    def __init__(self, name: str, component_id: str):
        self.name = name
        self.component_id = component_id
        self.state = ComponentState()
        
    @abstractmethod
    def get_mjcf(self) -> str:
        """
        Return MJCF XML string for this component.
        Should be a complete <body> or set of bodies.
        """
        pass
        
    @abstractmethod
    def apply_fault(self, fault_id: str, params: Dict[str, Any]):
        """
        Apply a fault to this component.
        
        Args:
            fault_id: Unique identifier for the fault
            params: Parameters affecting the fault behavior
        """
        pass
        
    @abstractmethod
    def get_reading(
        self, 
        tool_name: str, 
        measurement_point: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Return diagnostic tool reading for this component.
        
        Args:
            tool_name: Name of the diagnostic tool being used
            measurement_point: Specific point being measured
            params: Additional parameters for the measurement
            
        Returns:
            Dictionary with measurement results
        """
        pass
        
    def reset(self):
        """Reset component to nominal state"""
        self.state = ComponentState()
        
    def get_nominal_params(self) -> Dict[str, Any]:
        """Return nominal parameters for this component"""
        return {}
        
    def get_current_params(self) -> Dict[str, Any]:
        """Return current parameters including fault effects"""
        nominal = self.get_nominal_params()
        if self.state.fault_params:
            nominal.update(self.state.fault_params)
        return nominal
