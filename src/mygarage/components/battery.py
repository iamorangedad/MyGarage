"""12V battery component"""

from typing import Any, Dict
from .base import Component


class Battery(Component):
    """12V lead-acid battery"""
    
    def __init__(self):
        super().__init__("12V Battery", "battery")
        self.nominal_voltage = 12.6
        self.nominal_capacity = 60.0
        self.nominal_internal_resistance = 0.01
        
    def get_mjcf(self) -> str:
        """Return MJCF for battery (visual representation only)"""
        return """
        <body name="battery" pos="0.5 0 0.3">
            <geom type="box" size="0.15 0.1 0.12" rgba="0.2 0.2 0.2 1" mass="15"/>
            <!-- Positive terminal -->
            <geom type="cylinder" size="0.02 0.02" pos="0.05 0 0.13" rgba="0.8 0.2 0.2 1"/>
            <!-- Negative terminal -->
            <geom type="cylinder" size="0.02 0.02" pos="-0.05 0 0.13" rgba="0.1 0.1 0.1 1"/>
        </body>
        """
        
    def apply_fault(self, fault_id: str, params: Dict[str, Any]):
        """Apply fault to battery"""
        self.state.fault_id = fault_id
        self.state.fault_params = params.copy()
        
        if fault_id == "F001":
            self.state.custom_state["voltage"] = params.get("voltage", 11.5)
            self.state.custom_state["max_current"] = params.get("max_current", 50)
        elif fault_id == "F002":
            self.state.custom_state["voltage"] = params.get("voltage", 12.6)
            self.state.custom_state["bad_cell"] = True
            self.state.custom_state["voltage_drop_rate"] = 0.3
        elif fault_id == "F003":
            self.state.custom_state["terminal_resistance"] = params.get("resistance", 0.5)
            self.state.custom_state["corrosion_visible"] = True
            
    def get_reading(
        self, 
        tool_name: str, 
        measurement_point: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Return diagnostic readings"""
        
        if tool_name == "multimeter":
            if measurement_point == "resting_voltage":
                return self._get_resting_voltage()
            elif measurement_point == "loaded_voltage":
                return self._get_loaded_voltage(params.get("load_current", 200))
            elif measurement_point == "terminal_voltage_drop":
                return self._get_terminal_voltage_drop(params.get("current", 100))
                
        elif tool_name == "visual":
            return self._get_visual_inspection()
            
        return {"error": "Unknown measurement"}
        
    def _get_resting_voltage(self) -> Dict[str, Any]:
        """Get battery voltage with no load"""
        if self.state.fault_id == "F001":
            voltage = self.state.custom_state.get("voltage", 11.5)
        elif self.state.fault_id == "F002":
            voltage = 12.6
        else:
            voltage = self.nominal_voltage
            
        return {
            "value": voltage,
            "unit": "V",
            "reading": f"{voltage:.1f}V",
            "normal_range": "12.4-12.8V"
        }
        
    def _get_loaded_voltage(self, load_current: float) -> Dict[str, Any]:
        """Get battery voltage under load"""
        base_voltage = self.state.custom_state.get("voltage", self.nominal_voltage)
        
        if self.state.fault_id == "F001":
            max_current = self.state.custom_state.get("max_current", 50)
            if load_current > max_current:
                voltage = base_voltage - (load_current - max_current) * 0.05
                voltage = max(voltage, 8.0)
            else:
                voltage = base_voltage - load_current * self.nominal_internal_resistance
        elif self.state.fault_id == "F002":
            drop = self.state.custom_state.get("voltage_drop_rate", 0.3)
            voltage = base_voltage - drop * (load_current / 100)
        elif self.state.fault_id == "F003":
            terminal_r = self.state.custom_state.get("terminal_resistance", 0.5)
            voltage = base_voltage - load_current * terminal_r / 1000
        else:
            voltage = base_voltage - load_current * self.nominal_internal_resistance
            
        return {
            "value": voltage,
            "unit": "V", 
            "reading": f"{voltage:.1f}V under {load_current}A load",
            "normal_range": ">10.5V under cranking load"
        }
        
    def _get_terminal_voltage_drop(self, current: float) -> Dict[str, Any]:
        """Get voltage drop across terminal connection"""
        if self.state.fault_id == "F003":
            resistance = self.state.custom_state.get("terminal_resistance", 0.5)
            drop = current * resistance / 1000
        else:
            drop = current * 0.001
            
        return {
            "value": drop,
            "unit": "V",
            "reading": f"{drop:.2f}V drop @ {current}A",
            "normal_range": "<0.1V"
        }
        
    def _get_visual_inspection(self) -> Dict[str, Any]:
        """Visual inspection results"""
        observations = []
        
        if self.state.fault_id == "F003" and self.state.custom_state.get("corrosion_visible"):
            observations.append("Heavy white/green corrosion on positive terminal")
            observations.append("Terminal appears loose")
        else:
            observations.append("Terminals clean")
            observations.append("Connections tight")
            
        return {
            "observations": observations,
            "image": "battery_visual.jpg"
        }
        
    def get_nominal_params(self) -> Dict[str, Any]:
        """Return nominal battery parameters"""
        return {
            "voltage": self.nominal_voltage,
            "capacity_ah": self.nominal_capacity,
            "internal_resistance": self.nominal_internal_resistance,
            "max_current": 400
        }
