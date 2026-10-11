"""Fault injection system"""

import random
from typing import Dict, Optional, List
from .catalog import Fault, FaultCatalog


class FaultInjector:
    """Handles fault injection into vehicle"""
    
    def __init__(self, catalog: FaultCatalog):
        self.catalog = catalog
        self.active_fault: Optional[Fault] = None
        
    def inject_random_fault(
        self, 
        components: Dict[str, any],
        difficulty: Optional[str] = None
    ) -> Fault:
        """
        Inject a random fault into the vehicle.
        
        Args:
            components: Dictionary of component_id -> Component
            difficulty: Optional difficulty filter
            
        Returns:
            The injected Fault
        """
        available_faults = []
        
        for comp_id in components.keys():
            comp_faults = self.catalog.get_faults_by_component(comp_id)
            if difficulty:
                comp_faults = [f for f in comp_faults if f.difficulty == difficulty]
            available_faults.extend(comp_faults)
            
        if not available_faults:
            raise ValueError(f"No faults available for components: {list(components.keys())}")
            
        fault = random.choice(available_faults)
        self.inject_fault(fault, components)
        return fault
        
    def inject_fault(self, fault: Fault, components: Dict[str, any]):
        """
        Inject a specific fault into the vehicle.
        
        Args:
            fault: The fault to inject
            components: Dictionary of component_id -> Component
        """
        self.active_fault = fault
        
        if fault.component in components:
            component = components[fault.component]
            component.apply_fault(fault.id, fault.parameters)
        else:
            raise ValueError(f"Component {fault.component} not found")
            
    def clear_fault(self, components: Dict[str, any]):
        """Clear the active fault and reset components"""
        if self.active_fault:
            if self.active_fault.component in components:
                components[self.active_fault.component].reset()
        self.active_fault = None
        
    def get_symptom_description(self) -> str:
        """Get customer complaint/symptom description"""
        if not self.active_fault:
            return "No symptoms reported."
        return self.active_fault.symptoms
        
    def check_diagnosis(self, diagnosed_fault_id: str) -> bool:
        """Check if diagnosis is correct"""
        if not self.active_fault:
            return False
        return self.active_fault.id == diagnosed_fault_id
