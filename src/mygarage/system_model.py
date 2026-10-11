"""System model that manages the state of all car components and simulated behavior."""

from typing import Dict, List, Any, Optional
from mygarage.component import Component
from mygarage.components import Battery, StarterMotor
import numpy as np


class SystemModel:
    """
    Manages the electrical, mechanical, and thermal state of the car.
    
    This layer sits above MuJoCo and manages the signal/state model that drives
    what the physics simulation shows.
    """
    
    def __init__(self):
        self.components: Dict[str, Component] = {}
        self.state: Dict[str, Any] = {
            'ignition_on': False,
            'engine_cranking': False,
            'engine_running': False,
            'engine_rpm': 0,
            'starter_engaged': False,
        }
        self._initialize_default_components()
    
    def _initialize_default_components(self):
        """Initialize the default set of components."""
        self.add_component(Battery())
        self.add_component(StarterMotor())
    
    def add_component(self, component: Component):
        """Add a component to the system."""
        self.components[component.component_id] = component
    
    def get_component(self, component_id: str) -> Optional[Component]:
        """Get a component by ID."""
        return self.components.get(component_id)
    
    def inject_fault(self, component_id: str, fault_name: str) -> bool:
        """
        Inject a fault into a specific component.
        
        Args:
            component_id: ID of the component
            fault_name: Name of the fault to inject
            
        Returns:
            True if successful, False otherwise
        """
        component = self.get_component(component_id)
        if component:
            return component.inject_fault(fault_name)
        return False
    
    def attempt_crank(self) -> Dict[str, Any]:
        """
        Attempt to crank the engine (simulate turning the key).
        
        Returns:
            Dictionary describing what happens
        """
        battery = self.get_component('battery_12v')
        starter = self.get_component('starter_motor')
        
        if not battery or not starter:
            return {'success': False, 'reason': 'Missing components'}
        
        # Check battery voltage
        battery_voltage = battery.parameters['voltage_resting']
        if battery_voltage < 10.0:
            return {
                'success': False,
                'sound': 'click',
                'reason': 'Battery voltage too low',
                'cranking': False
            }
        
        # Check starter solenoid
        if not starter.parameters.get('solenoid_functional', True):
            return {
                'success': False,
                'sound': 'single_click',
                'reason': 'Starter solenoid not engaging',
                'cranking': False
            }
        
        # Check starter operation
        if not starter.parameters.get('operational', True):
            return {
                'success': False,
                'sound': 'none',
                'reason': 'Starter motor not operational',
                'cranking': False
            }
        
        # Calculate cranking behavior
        self.state['engine_cranking'] = True
        self.state['starter_engaged'] = True
        
        # Get voltage under load
        context = {'engine_cranking': True}
        battery_readings = battery.get_diagnostic_readings('multimeter', context)
        voltage_under_load = battery_readings['voltage']
        
        # Get starter torque
        starter_torque = starter.parameters['torque_output']
        
        # Calculate cranking RPM
        if starter_torque > 2.0 and voltage_under_load > 9.6:
            cranking_rpm = 200
            sound = 'normal_crank'
            success = True
        elif starter_torque > 1.0 and voltage_under_load > 8.0:
            cranking_rpm = 80
            sound = 'slow_crank'
            success = False
        else:
            cranking_rpm = 0
            sound = 'grinding'
            success = False
        
        self.state['engine_rpm'] = cranking_rpm
        
        return {
            'success': success,
            'sound': sound,
            'cranking': True,
            'rpm': cranking_rpm,
            'voltage_under_load': voltage_under_load
        }
    
    def stop_crank(self):
        """Stop cranking the engine."""
        self.state['engine_cranking'] = False
        self.state['starter_engaged'] = False
        self.state['engine_rpm'] = 0
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get the current context for diagnostic readings.
        
        Returns:
            Dictionary of current system state
        """
        battery = self.get_component('battery_12v')
        battery_voltage = battery.parameters['voltage_resting'] if battery else 12.6
        
        return {
            'engine_cranking': self.state['engine_cranking'],
            'battery_voltage': battery_voltage,
            'ignition_on': self.state['ignition_on'],
            'engine_running': self.state['engine_running'],
            'engine_rpm': self.state['engine_rpm'],
        }
    
    def step(self, dt: float = 0.01):
        """
        Step the system model forward in time.
        
        Args:
            dt: Time step in seconds
        """
        # Update component states based on current conditions
        # This is where we'd update temperatures, discharge rates, etc.
        
        # For now, simple placeholder
        if self.state['engine_cranking']:
            # Battery discharges while cranking
            battery = self.get_component('battery_12v')
            if battery and battery.parameters['state_of_charge'] > 0:
                discharge_rate = 0.001  # per second
                battery.parameters['state_of_charge'] -= discharge_rate * dt
                battery.parameters['state_of_charge'] = max(0, battery.parameters['state_of_charge'])
    
    def get_all_components(self) -> List[Component]:
        """Get list of all components."""
        return list(self.components.values())
    
    def reset(self):
        """Reset all components to nominal state."""
        for component in self.components.values():
            component.clear_fault()
        self.state = {
            'ignition_on': False,
            'engine_cranking': False,
            'engine_running': False,
            'engine_rpm': 0,
            'starter_engaged': False,
        }
