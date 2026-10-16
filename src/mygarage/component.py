"""Base component class for car parts."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np


@dataclass
class FaultMode:
    """Defines a fault mode for a component."""
    
    name: str
    description: str
    symptoms: List[str]
    affected_parameters: Dict[str, Any]  # Parameter name -> faulty value/modifier
    severity: str = "medium"  # low, medium, high


class Component(ABC):
    """Base class for all car components."""
    
    def __init__(self, component_id: str, name: str):
        self.component_id = component_id
        self.name = name
        self.parameters: Dict[str, Any] = {}
        self.fault_modes: List[FaultMode] = []
        self.active_fault: Optional[FaultMode] = None
        self._mjcf_path: Optional[str] = None
        
    @abstractmethod
    def get_nominal_parameters(self) -> Dict[str, Any]:
        """Return the nominal (healthy) parameters for this component."""
        pass
    
    @abstractmethod
    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return diagnostic readings for a given tool.
        
        Args:
            tool: Name of the diagnostic tool (e.g., 'multimeter', 'visual', 'obd')
            context: Context information (e.g., engine state, other component states)
            
        Returns:
            Dictionary of readings specific to the tool
        """
        pass
    
    def inject_fault(self, fault_name: str) -> bool:
        """
        Inject a specific fault into this component.
        
        Args:
            fault_name: Name of the fault mode to inject
            
        Returns:
            True if fault was successfully injected, False otherwise
        """
        for fault in self.fault_modes:
            if fault.name == fault_name:
                self.active_fault = fault
                # Apply fault parameters
                for param_name, param_value in fault.affected_parameters.items():
                    if param_name in self.parameters:
                        self.parameters[param_name] = param_value
                return True
        return False
    
    def clear_fault(self):
        """Clear any active fault and restore nominal parameters."""
        self.active_fault = None
        self.parameters = self.get_nominal_parameters()
    
    def get_mjcf_path(self) -> Optional[str]:
        """Return the path to the MJCF model file for this component."""
        return self._mjcf_path
    
    def get_replacement_cost(self) -> float:
        """Return the cost to replace this component."""
        return self.parameters.get('replacement_cost', 0.0)
    
    def unsupported_tool(self, tool: str) -> Dict[str, Any]:
        """Standard response when a tool does not apply to this part."""
        return {'error': f'Tool {tool} not supported for {self.name}'}

    def __repr__(self) -> str:
        fault_status = f"FAULTY ({self.active_fault.name})" if self.active_fault else "HEALTHY"
        return f"{self.__class__.__name__}(id={self.component_id}, status={fault_status})"


class CatalogPart(Component):
    """Component base that serves visual notes and OBD codes from parameters.

    Fault entries replace ``visual_findings`` and ``active_dtcs`` the same way
    they replace voltages or pressures. Subclasses add the tool readings that
    are specific to the part.
    """

    subsystem = "general"

    def __init__(self, component_id: str, name: str, mjcf_path: Optional[str] = None):
        super().__init__(component_id, name)
        self.subsystem = type(self).subsystem
        self._mjcf_path = mjcf_path
        self.parameters = self.get_nominal_parameters()
        self._define_fault_modes()

    @abstractmethod
    def _define_fault_modes(self) -> None:
        """Populate ``self.fault_modes``."""

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'visual':
            return {'findings': list(self.parameters.get('visual_findings', []))}
        if tool == 'obd':
            return {
                'dtcs': list(self.parameters.get('active_dtcs', [])),
                'description': self.active_fault.description if self.active_fault else 'No stored fault',
            }
        return self.unsupported_tool(tool)
