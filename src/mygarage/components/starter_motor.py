"""Starter motor component implementation."""

from typing import Dict, Any, List
from mygarage.component import Component, FaultMode


class StarterMotor(Component):
    """Automotive starter motor component."""
    
    def __init__(self, component_id: str = "starter_motor"):
        super().__init__(component_id, "Starter Motor")
        self._mjcf_path = "starter_motor.xml"
        self.parameters = self.get_nominal_parameters()
        self._define_fault_modes()
    
    def get_nominal_parameters(self) -> Dict[str, Any]:
        """Return nominal starter motor parameters."""
        return {
            'resistance': 0.05,  # Ohms (armature resistance)
            'nominal_current': 150.0,  # Amps when cranking
            'torque_output': 2.5,  # Nm
            'operational': True,
            'solenoid_functional': True,
            'replacement_cost': 250.0,
            'brush_wear': 0.0,  # 0-1 (0=new, 1=worn out)
        }
    
    def _define_fault_modes(self):
        """Define possible fault modes for the starter motor."""
        self.fault_modes = [
            FaultMode(
                name="failed_solenoid",
                description="Starter solenoid is not engaging",
                symptoms=["Single click, no crank", "No engagement"],
                affected_parameters={
                    'solenoid_functional': False,
                    'torque_output': 0.0,
                }
            ),
            FaultMode(
                name="worn_starter",
                description="Starter motor brushes are worn, causing weak cranking",
                symptoms=["Slow crank", "Grinding noise", "High current draw"],
                affected_parameters={
                    'resistance': 0.15,
                    'nominal_current': 250.0,
                    'torque_output': 1.0,
                    'brush_wear': 0.8,
                }
            ),
            FaultMode(
                name="failed_starter",
                description="Starter motor has failed completely",
                symptoms=["No crank", "No sound", "Dead short or open circuit"],
                affected_parameters={
                    'operational': False,
                    'torque_output': 0.0,
                    'resistance': 1000.0,  # Open circuit
                }
            ),
            FaultMode(
                name="bad_ground",
                description="Poor ground connection to starter motor",
                symptoms=["Intermittent crank", "Clicking", "High resistance in circuit"],
                affected_parameters={
                    'resistance': 0.8,
                    'torque_output': 0.5,
                    'nominal_current': 80.0,
                }
            ),
        ]
    
    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Return diagnostic readings for the starter motor."""
        engine_cranking = context.get('engine_cranking', False)
        battery_voltage = context.get('battery_voltage', 12.6)
        
        if tool == 'multimeter':
            # Current draw measurement (if measuring)
            if engine_cranking and self.parameters['operational']:
                current = self.parameters['nominal_current']
                import numpy as np
                current += np.random.normal(0, 10)
            else:
                current = 0.0
            
            # Voltage at starter terminal
            voltage_drop = current * self.parameters['resistance'] / 1000.0
            starter_voltage = battery_voltage - voltage_drop if engine_cranking else battery_voltage
            
            return {
                'current_draw': round(current, 1),
                'voltage_at_terminal': round(starter_voltage, 2),
                'unit_current': 'A',
                'unit_voltage': 'V'
            }
        
        elif tool == 'visual':
            findings = []
            
            if self.parameters['brush_wear'] > 0.6:
                findings.append("Starter appears worn, possible brush issues")
            else:
                findings.append("Starter casing appears intact")
            
            if not self.parameters.get('solenoid_functional', True):
                findings.append("Solenoid may not be clicking properly")
            
            return {'findings': findings}
        
        elif tool == 'crank_test':
            # Attempt to crank the engine
            if not self.parameters['operational']:
                return {
                    'cranked': False,
                    'sound': 'none',
                    'description': 'No response from starter'
                }
            
            if not self.parameters['solenoid_functional']:
                return {
                    'cranked': False,
                    'sound': 'single_click',
                    'description': 'Single click heard, starter not engaging'
                }
            
            torque = self.parameters['torque_output']
            if torque < 1.5:
                return {
                    'cranked': True,
                    'sound': 'slow_grinding',
                    'rpm': 50,
                    'description': 'Engine cranks slowly with difficulty'
                }
            else:
                return {
                    'cranked': True,
                    'sound': 'normal_cranking',
                    'rpm': 200,
                    'description': 'Engine cranks normally'
                }
        
        else:
            return {'error': f'Tool {tool} not supported for starter motor'}
