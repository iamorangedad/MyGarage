"""Starter motor component"""

from typing import Any, Dict
from .base import Component


class StarterMotor(Component):
    """Electric starter motor with solenoid"""
    
    def __init__(self):
        super().__init__("Starter Motor", "starter")
        self.nominal_resistance = 0.05
        self.nominal_current_draw = 150.0
        self.nominal_torque = 2.5
        
    def get_mjcf(self) -> str:
        """Return MJCF for starter motor and crankshaft"""
        return """
        <body name="starter_motor" pos="0.3 -0.2 0.2">
            <!-- Starter motor body -->
            <geom type="cylinder" size="0.06 0.12" rgba="0.4 0.4 0.4 1" mass="4"/>
            <!-- Drive gear -->
            <geom type="cylinder" size="0.03 0.02" pos="0 0 0.14" rgba="0.3 0.3 0.3 1"/>
        </body>
        
        <body name="crankshaft" pos="0.3 0 0.2">
            <joint name="crank_joint" type="hinge" axis="0 0 1" damping="0.5"/>
            <!-- Crankshaft representation -->
            <geom type="cylinder" size="0.04 0.15" rgba="0.5 0.5 0.5 1" mass="10"/>
            <!-- Flywheel -->
            <geom type="cylinder" size="0.12 0.03" pos="0 0 0.18" rgba="0.6 0.6 0.6 1" mass="8"/>
        </body>
        """
        
    def apply_fault(self, fault_id: str, params: Dict[str, Any]):
        """Apply fault to starter motor"""
        self.state.fault_id = fault_id
        self.state.fault_params = params.copy()
        
        if fault_id == "F005":
            self.state.custom_state["solenoid_failed"] = True
            self.state.custom_state["click_sound"] = True
        elif fault_id == "F006":
            self.state.custom_state["worn_brushes"] = True
            self.state.custom_state["high_resistance"] = True
            self.state.custom_state["current_draw"] = params.get("current", 250)
            self.state.custom_state["torque_reduction"] = params.get("torque_factor", 0.5)
        elif fault_id == "F007":
            self.state.custom_state["fuse_blown"] = True
        elif fault_id == "F008":
            self.state.custom_state["relay_failed"] = True
            
    def get_reading(
        self, 
        tool_name: str, 
        measurement_point: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Return diagnostic readings"""
        
        if tool_name == "multimeter":
            if measurement_point == "resistance":
                return self._get_resistance()
            elif measurement_point == "current_draw":
                return self._get_current_draw(params.get("voltage", 12.0))
                
        elif tool_name == "crank_test":
            return self._perform_crank_test(params)
            
        elif tool_name == "visual":
            return self._get_visual_inspection()
            
        return {"error": "Unknown measurement"}
        
    def _get_resistance(self) -> Dict[str, Any]:
        """Measure starter motor resistance"""
        if self.state.fault_id == "F006":
            resistance = self.nominal_resistance * 2
        else:
            resistance = self.nominal_resistance
            
        return {
            "value": resistance,
            "unit": "Ω",
            "reading": f"{resistance:.3f}Ω",
            "normal_range": "0.03-0.1Ω"
        }
        
    def _get_current_draw(self, voltage: float) -> Dict[str, Any]:
        """Measure current draw during cranking"""
        if self.state.fault_id == "F005":
            current = 10.0
        elif self.state.fault_id == "F006":
            current = self.state.custom_state.get("current_draw", 250)
        elif self.state.fault_id in ["F007", "F008"]:
            current = 0.0
        else:
            current = self.nominal_current_draw
            
        return {
            "value": current,
            "unit": "A",
            "reading": f"{current:.0f}A",
            "normal_range": "100-200A during cranking"
        }
        
    def _perform_crank_test(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate attempting to crank the engine"""
        voltage = params.get("battery_voltage", 12.0)
        
        if self.state.fault_id == "F005":
            return {
                "result": "click_only",
                "sound": "Single CLICK, no rotation",
                "cranking_speed": 0,
                "observation": "Solenoid engages but motor doesn't spin"
            }
        elif self.state.fault_id == "F006":
            speed = 50
            return {
                "result": "slow_crank",
                "sound": "Slow grinding/whirring",
                "cranking_speed": speed,
                "observation": "Motor spins slowly, may hear grinding"
            }
        elif self.state.fault_id in ["F007", "F008"]:
            return {
                "result": "no_response",
                "sound": "Nothing/silence",
                "cranking_speed": 0,
                "observation": "No sound, no movement"
            }
        elif voltage < 10.0:
            return {
                "result": "weak_crank",
                "sound": "Slow cranking",
                "cranking_speed": 80,
                "observation": "Cranks slowly due to low battery voltage"
            }
        else:
            return {
                "result": "normal_crank",
                "sound": "Normal cranking sound (rr-rr-rr)",
                "cranking_speed": 200,
                "observation": "Engine cranks normally"
            }
            
    def _get_visual_inspection(self) -> Dict[str, Any]:
        """Visual inspection results"""
        observations = []
        
        if self.state.fault_id == "F006":
            observations.append("Starter motor appears dirty/worn")
            observations.append("Possible brush dust visible")
        else:
            observations.append("Starter motor appears normal")
            
        return {
            "observations": observations,
            "accessible": "partially_visible"
        }
        
    def get_torque_output(self, voltage: float) -> float:
        """Calculate starter motor torque output"""
        if voltage < 9.0:
            return 0.0
            
        if self.state.fault_id == "F005":
            return 0.0
        elif self.state.fault_id == "F006":
            factor = self.state.custom_state.get("torque_factor", 0.5)
            return self.nominal_torque * factor * (voltage / 12.0)
        elif self.state.fault_id in ["F007", "F008"]:
            return 0.0
        else:
            return self.nominal_torque * (voltage / 12.0)
            
    def get_nominal_params(self) -> Dict[str, Any]:
        """Return nominal starter parameters"""
        return {
            "resistance": self.nominal_resistance,
            "current_draw": self.nominal_current_draw,
            "torque_nm": self.nominal_torque,
            "cranking_rpm": 200
        }
