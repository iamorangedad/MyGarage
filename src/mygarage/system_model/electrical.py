"""Electrical system model"""

from typing import Dict, Any, Optional
import numpy as np


class ElectricalSystem:
    """Models the vehicle electrical system behavior"""
    
    def __init__(self):
        self.battery_voltage = 12.6
        self.battery_charge = 100.0
        self.starter_engaged = False
        self.ignition_on = False
        
        self.battery_component = None
        self.starter_component = None
        
        self._ground_resistance = 0.001
        
    def set_components(self, battery, starter):
        """Set component references"""
        self.battery_component = battery
        self.starter_component = starter
        
    def update(self, dt: float):
        """Update electrical system state"""
        if not self.battery_component or not self.starter_component:
            return
            
        if self.starter_engaged and self.ignition_on:
            self._simulate_cranking(dt)
        else:
            battery_params = self.battery_component.get_current_params()
            self.battery_voltage = battery_params.get("voltage", 12.6)
            
    def _simulate_cranking(self, dt: float):
        """Simulate electrical behavior during cranking"""
        battery_params = self.battery_component.get_current_params()
        starter_params = self.starter_component.get_current_params()
        
        base_voltage = battery_params.get("voltage", 12.6)
        max_current = battery_params.get("max_current", 400)
        internal_r = battery_params.get("internal_resistance", 0.01)
        
        starter_r = starter_params.get("resistance", 0.05)
        
        total_r = internal_r + starter_r + self._ground_resistance
        
        fault_id = self.starter_component.state.fault_id
        if fault_id in ["F007", "F008"]:
            desired_current = 0
        elif fault_id == "F005":
            desired_current = 10
        else:
            desired_current = starter_params.get("current_draw", 150)
            
        actual_current = min(desired_current, max_current)
        
        self.battery_voltage = base_voltage - actual_current * total_r
        
        self.battery_charge = max(0, self.battery_charge - actual_current * dt / 36)
        
    def engage_starter(self):
        """Engage the starter motor"""
        self.starter_engaged = True
        
    def disengage_starter(self):
        """Disengage the starter motor"""
        self.starter_engaged = False
        
    def set_ignition(self, on: bool):
        """Set ignition switch state"""
        self.ignition_on = on
        
    def get_actuator_commands(self) -> Dict[str, float]:
        """Get commands for MuJoCo actuators"""
        if not self.starter_component:
            return {"crank_torque": 0.0}
            
        if self.starter_engaged and self.ignition_on:
            torque = self.starter_component.get_torque_output(self.battery_voltage)
        else:
            torque = 0.0
            
        return {
            "crank_torque": torque
        }
        
    def get_state(self) -> Dict[str, Any]:
        """Get current electrical system state"""
        return {
            "battery_voltage": self.battery_voltage,
            "battery_charge": self.battery_charge,
            "starter_engaged": self.starter_engaged,
            "ignition_on": self.ignition_on
        }
