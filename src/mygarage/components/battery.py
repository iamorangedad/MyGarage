"""Battery component implementation."""

from typing import Dict, Any, List
from mygarage.component import Component, FaultMode


class Battery(Component):
    """12V automotive battery component."""
    
    def __init__(self, component_id: str = "battery_12v"):
        super().__init__(component_id, "12V Battery")
        self._mjcf_path = "battery.xml"
        self.parameters = self.get_nominal_parameters()
        self._define_fault_modes()
    
    def get_nominal_parameters(self) -> Dict[str, Any]:
        """Return nominal battery parameters."""
        return {
            'voltage_resting': 12.6,  # Volts
            'voltage_under_load': 12.0,  # Volts (cranking)
            'internal_resistance': 0.01,  # Ohms
            'capacity_ah': 60.0,  # Amp-hours
            'state_of_charge': 1.0,  # 0-1
            'replacement_cost': 150.0,  # USD
            'cold_cranking_amps': 600,  # CCA
        }
    
    def _define_fault_modes(self):
        """Define possible fault modes for the battery."""
        self.fault_modes = [
            FaultMode(
                name="discharged_battery",
                description="Battery is deeply discharged",
                symptoms=["No crank", "Dim lights", "Clicking sound"],
                affected_parameters={
                    'voltage_resting': 11.5,
                    'voltage_under_load': 8.0,
                    'state_of_charge': 0.2,
                }
            ),
            FaultMode(
                name="failed_cell",
                description="One or more battery cells have failed",
                symptoms=["Slow crank", "Voltage drops quickly under load"],
                affected_parameters={
                    'voltage_resting': 10.5,
                    'voltage_under_load': 7.0,
                    'internal_resistance': 0.15,
                }
            ),
            FaultMode(
                name="corroded_terminal",
                description="Battery terminal is corroded, increasing resistance",
                symptoms=["Intermittent start", "Voltage drop at terminal", "Clicking"],
                affected_parameters={
                    'internal_resistance': 0.5,  # High resistance at connection
                    'voltage_under_load': 10.5,
                }
            ),
        ]
    
    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return diagnostic readings for the battery.
        
        Args:
            tool: Diagnostic tool name
            context: Context including engine state, load conditions
        """
        engine_cranking = context.get('engine_cranking', False)
        
        if tool == 'multimeter':
            # Voltage measurement
            if engine_cranking:
                voltage = self.parameters['voltage_under_load']
                # Add some realistic noise
                import numpy as np
                voltage += np.random.normal(0, 0.1)
            else:
                voltage = self.parameters['voltage_resting']
            
            return {
                'voltage': round(voltage, 2),
                'unit': 'V',
                'test_condition': 'cranking' if engine_cranking else 'resting'
            }
        
        elif tool == 'visual':
            # Visual inspection results
            findings = []
            if self.active_fault and self.active_fault.name == 'corroded_terminal':
                findings.append("White/green corrosion visible on terminals")
                findings.append("Poor cable connection")
            else:
                findings.append("Terminals appear clean")
            
            # Check state of charge indicator
            soc = self.parameters['state_of_charge']
            if soc < 0.3:
                findings.append("Charge indicator shows low (if equipped)")
            
            return {'findings': findings}
        
        elif tool == 'load_test':
            # Battery load test
            voltage_drop = self.parameters['voltage_resting'] - self.parameters['voltage_under_load']
            internal_r = self.parameters['internal_resistance']
            
            return {
                'voltage_before': round(self.parameters['voltage_resting'], 2),
                'voltage_during_load': round(self.parameters['voltage_under_load'], 2),
                'voltage_drop': round(voltage_drop, 2),
                'estimated_cca': int(self.parameters['cold_cranking_amps'] * self.parameters['state_of_charge']),
                'passed': voltage_drop < 1.5 and self.parameters['voltage_under_load'] > 9.6
            }
        
        else:
            return {'error': f'Tool {tool} not supported for battery'}
