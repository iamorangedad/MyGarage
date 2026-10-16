"""Brake and suspension parts used for the chassis diagnostic cases."""

from typing import Any, Dict

from mygarage.component import CatalogPart, FaultMode


def _serviceable() -> Dict[str, Any]:
    return {
        'visual_findings': ['Appears serviceable'],
        'active_dtcs': [],
    }


class BrakePads(CatalogPart):
    """Front brake pads."""

    subsystem = "chassis"

    def __init__(self, component_id: str = "brake_pads"):
        super().__init__(component_id, "制动片 Brake Pads", "brake_pads.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'thickness_mm': 10.0,
            'replacement_cost': 80.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="worn_pads",
                description="Friction material is worn down to the wear indicator",
                symptoms=["Squeal", "Longer pedal travel", "Metal-on-metal if ignored"],
                affected_parameters={
                    'thickness_mm': 1.5,
                    'visual_findings': ['Pad friction material is about 1.5 mm', 'Wear indicator is touching the disc'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'visual':
            thickness = self.parameters['thickness_mm']
            findings = list(self.parameters['visual_findings'])
            return {
                'findings': findings,
                'thickness_mm': thickness,
                'spec_min_mm': 3.0,
                'passed': thickness >= 3.0,
            }
        return super().get_diagnostic_readings(tool, context)


class BrakeDisc(CatalogPart):
    """Front brake disc."""

    subsystem = "chassis"

    def __init__(self, component_id: str = "brake_disc"):
        super().__init__(component_id, "制动盘 Brake Disc", "brake_disc.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'thickness_mm': 26.0,
            'runout_mm': 0.03,
            'min_thickness_mm': 24.0,
            'replacement_cost': 120.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="warped_disc",
                description="Disc runout is high, so the pedal pulses while braking",
                symptoms=["Steering shake while braking", "Pulsing pedal"],
                affected_parameters={
                    'runout_mm': 0.18,
                    'visual_findings': ['Blue heat spots on the friction surface'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'visual':
            runout = self.parameters['runout_mm']
            return {
                'findings': list(self.parameters['visual_findings']),
                'thickness_mm': self.parameters['thickness_mm'],
                'runout_mm': runout,
                'spec_max_runout_mm': 0.08,
                'passed': runout <= 0.08,
            }
        return super().get_diagnostic_readings(tool, context)


class WheelSpeedSensor(CatalogPart):
    """Front wheel-speed sensor for ABS."""

    subsystem = "chassis"

    def __init__(self, component_id: str = "wheel_speed_sensor"):
        super().__init__(component_id, "轮速传感器 Wheel Speed Sensor", "wheel_speed_sensor.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'signal_ok': True,
            'resistance_ohm': 1200.0,
            'replacement_cost': 65.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="open_sensor",
                description="Wheel-speed sensor circuit is open",
                symptoms=["ABS light", "No signal from one wheel"],
                affected_parameters={
                    'signal_ok': False,
                    'resistance_ohm': None,
                    'active_dtcs': ['C0035'],
                    'visual_findings': ['Sensor tip is clean', 'Wiring at the knuckle is broken'],
                },
            ),
            FaultMode(
                name="debris_on_tone_ring",
                description="Metallic debris on the tone ring interrupts the signal",
                symptoms=["ABS light comes on over bumps", "Erratic wheel-speed reading"],
                affected_parameters={
                    'signal_ok': False,
                    'active_dtcs': ['C0035'],
                    'visual_findings': ['Steel fuzz is stuck to the magnetic sensor tip'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'multimeter':
            return {
                'resistance_ohm': self.parameters['resistance_ohm'],
                'spec_ohm': '1000-1500',
                'signal_ok': bool(self.parameters['signal_ok']),
            }
        return super().get_diagnostic_readings(tool, context)


class ShockAbsorber(CatalogPart):
    """Front shock absorber."""

    subsystem = "chassis"

    def __init__(self, component_id: str = "shock_absorber"):
        super().__init__(component_id, "减振器 Shock Absorber", "shock_absorber.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'leaking': False,
            'damping': 1.0,
            'replacement_cost': 180.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="leaking_shock",
                description="Shock seal leaks oil and damping is reduced",
                symptoms=["Bounce after a dip", "Oil wet on the shock body"],
                affected_parameters={
                    'leaking': True,
                    'damping': 0.3,
                    'visual_findings': ['Oil film on the shock tube'],
                },
            ),
            FaultMode(
                name="worn_shock",
                description="Damping has faded even though the seal is still dry",
                symptoms=["Several bounces after a bump", "Nose dive under braking"],
                affected_parameters={
                    'damping': 0.35,
                    'visual_findings': ['Shock body is dry', 'Bump stop is contacted often'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'bounce_test':
            damping = float(self.parameters['damping'])
            # A healthy damper settles in one or two bounces.
            oscillations = 1 if damping >= 0.8 else 5
            return {
                'oscillations': oscillations,
                'spec_max': 2,
                'passed': oscillations <= 2,
                'leaking': bool(self.parameters['leaking']),
            }
        return super().get_diagnostic_readings(tool, context)
