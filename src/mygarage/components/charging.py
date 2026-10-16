"""Charging-system parts."""

from typing import Any, Dict

from mygarage.component import CatalogPart, FaultMode


def _serviceable() -> Dict[str, Any]:
    return {
        'visual_findings': ['Appears serviceable'],
        'active_dtcs': [],
    }


class Alternator(CatalogPart):
    """Belt-driven alternator."""

    subsystem = "charging"

    def __init__(self, component_id: str = "alternator"):
        super().__init__(component_id, "发电机 Alternator", "alternator.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'output_ok': True,
            'ripple_v': 0.1,
            'replacement_cost': 320.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="failed_diodes",
                description="Rectifier diodes have failed, so the alternator does not charge",
                symptoms=["Battery light on", "Battery goes flat", "AC ripple"],
                affected_parameters={
                    'output_ok': False,
                    'ripple_v': 1.8,
                    'active_dtcs': ['P0622'],
                    'visual_findings': ['Alternator case is intact'],
                },
            ),
            FaultMode(
                name="open_output",
                description="Alternator output circuit is open",
                symptoms=["Battery light on", "No charge"],
                affected_parameters={
                    'output_ok': False,
                    'ripple_v': 0.0,
                    'active_dtcs': ['P0620'],
                    'visual_findings': ['Output stud looks clean'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'multimeter':
            running = bool(context.get('engine_running'))
            voltage = float(context.get('charging_voltage', context.get('battery_voltage', 12.6)))
            return {
                'voltage': round(voltage, 2),
                'ripple_v': self.parameters['ripple_v'] if running else 0.0,
                'unit': 'V',
                'engine_running': running,
                'note': None if running else 'Engine is not running, so this is battery voltage',
            }
        return super().get_diagnostic_readings(tool, context)


class SerpentineBelt(CatalogPart):
    """Belt that drives the alternator."""

    subsystem = "charging"

    def __init__(self, component_id: str = "serpentine_belt"):
        super().__init__(component_id, "发电机皮带 Serpentine Belt", "serpentine_belt.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'broken': False,
            'slip': 0.0,
            'replacement_cost': 40.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="broken_belt",
                description="Serpentine belt is broken, so the alternator does not turn",
                symptoms=["Battery light on", "Squeal then no charge", "Charging voltage equals battery voltage"],
                affected_parameters={
                    'broken': True,
                    'slip': 1.0,
                    'visual_findings': ['Belt is missing or snapped'],
                },
            ),
            FaultMode(
                name="glazed_belt",
                description="Belt is glazed and slips under electrical load",
                symptoms=["Chirp", "Charging voltage low at idle"],
                affected_parameters={
                    'slip': 0.55,
                    'visual_findings': ['Belt ribs are shiny and glazed'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'multimeter':
            return {
                'charging_voltage': context.get('charging_voltage'),
                'unit': 'V',
                'engine_running': bool(context.get('engine_running')),
            }
        return super().get_diagnostic_readings(tool, context)


class VoltageRegulator(CatalogPart):
    """Regulator that sets alternator output voltage."""

    subsystem = "charging"

    def __init__(self, component_id: str = "voltage_regulator"):
        super().__init__(component_id, "电压调节器 Voltage Regulator", "voltage_regulator.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'setpoint_v': 14.2,
            'replacement_cost': 110.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="failed_high",
                description="Regulator is stuck commanding a high charge voltage",
                symptoms=["Battery smells hot", "Lights bright", "Voltage above 15 V"],
                affected_parameters={
                    'setpoint_v': 15.8,
                    'active_dtcs': ['P2503'],
                    'visual_findings': ['Regulator plug looks seated'],
                },
            ),
            FaultMode(
                name="failed_low",
                description="Regulator is not commanding the field, so charge voltage is low",
                symptoms=["Battery light on", "Voltage stays near 12 V with the engine running"],
                affected_parameters={
                    'setpoint_v': 12.2,
                    'active_dtcs': ['P0622'],
                    'visual_findings': ['Regulator looks intact'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'multimeter':
            return {
                'charging_voltage': context.get('charging_voltage'),
                'unit': 'V',
                'engine_running': bool(context.get('engine_running')),
                'spec': '13.5-14.8 V with the engine running',
            }
        return super().get_diagnostic_readings(tool, context)
