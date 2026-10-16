"""Cooling-system parts and the coolant-temperature sensor."""

from typing import Any, Dict

from mygarage.component import CatalogPart, FaultMode


def _serviceable() -> Dict[str, Any]:
    return {
        'visual_findings': ['Appears serviceable'],
        'active_dtcs': [],
    }


class Thermostat(CatalogPart):
    """Thermostat that opens the radiator circuit."""

    subsystem = "cooling"

    def __init__(self, component_id: str = "thermostat"):
        super().__init__(component_id, "节温器 Thermostat", "thermostat.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'stuck_closed': False,
            'stuck_open': False,
            'replacement_cost': 35.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="stuck_closed",
                description="Thermostat does not open, so coolant cannot reach the radiator",
                symptoms=["Overheats", "Heater works", "Upper hose stays cooler than the engine"],
                affected_parameters={
                    'stuck_closed': True,
                    'active_dtcs': ['P0128'],
                    'visual_findings': ['Thermostat valve is shut and does not move in hot water'],
                },
            ),
            FaultMode(
                name="stuck_open",
                description="Thermostat is stuck open, so the engine stays below operating temperature",
                symptoms=["Temperature stays low", "Poor heater", "High fuel use"],
                affected_parameters={
                    'stuck_open': True,
                    'active_dtcs': ['P0128'],
                    'visual_findings': ['Thermostat valve is hanging open'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'temperature':
            return {
                'coolant_temp_c': context.get('coolant_temp_c'),
                'operating_spec_c': '88-98',
            }
        return super().get_diagnostic_readings(tool, context)


class WaterPump(CatalogPart):
    """Mechanical water pump."""

    subsystem = "cooling"

    def __init__(self, component_id: str = "water_pump"):
        super().__init__(component_id, "水泵 Water Pump", "water_pump.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'pumping': True,
            'external_leak': False,
            'replacement_cost': 160.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="failed_impeller",
                description="Impeller is broken, so coolant does not circulate",
                symptoms=["Overheats quickly", "Little flow at the radiator"],
                affected_parameters={
                    'pumping': False,
                    'visual_findings': ['Weep hole is dry', 'Pulley turns but flow is absent'],
                },
            ),
            FaultMode(
                name="leaking_pump",
                description="Pump seal leaks coolant and the level falls",
                symptoms=["Coolant smell", "Low coolant", "Overheats after the level drops"],
                affected_parameters={
                    'external_leak': True,
                    'visual_findings': ['Coolant trail from the weep hole'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'temperature':
            return {
                'coolant_temp_c': context.get('coolant_temp_c'),
                'flow': 'none' if not self.parameters['pumping'] else 'normal',
            }
        return super().get_diagnostic_readings(tool, context)


class CoolingFan(CatalogPart):
    """Electric radiator fan used while the car is stationary."""

    subsystem = "cooling"

    def __init__(self, component_id: str = "cooling_fan"):
        super().__init__(component_id, "冷却风扇 Cooling Fan", "cooling_fan.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'operational': True,
            'relay_ok': True,
            'replacement_cost': 140.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="seized_motor",
                description="Fan motor is seized and cannot pull air through the radiator",
                symptoms=["Overheats at idle", "Temperature is closer to normal on the road"],
                affected_parameters={
                    'operational': False,
                    'visual_findings': ['Fan blade does not spin when commanded'],
                },
            ),
            FaultMode(
                name="failed_relay",
                description="Fan relay does not close, so the motor never receives power",
                symptoms=["Overheats at idle", "Fan does not run"],
                affected_parameters={
                    'relay_ok': False,
                    'visual_findings': ['Fan spins freely by hand', 'Relay contacts are burned'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'multimeter':
            commanded = bool(context.get('fan_commanded'))
            powered = commanded and self.parameters['operational'] and self.parameters['relay_ok']
            return {
                'fan_commanded': commanded,
                'motor_voltage': 12.0 if powered else 0.0,
                'unit': 'V',
            }
        if tool == 'temperature':
            return {
                'coolant_temp_c': context.get('coolant_temp_c'),
                'fan_on': bool(context.get('fan_on')),
            }
        return super().get_diagnostic_readings(tool, context)


class CoolantTempSensor(CatalogPart):
    """ECT sensor. A biased sensor lies to the gauge and the fan command."""

    subsystem = "cooling"

    def __init__(self, component_id: str = "ect_sensor"):
        super().__init__(component_id, "水温传感器 ECT Sensor", "ect_sensor.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'bias_c': 0.0,
            'open_circuit': False,
            'replacement_cost': 30.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="biased_cold",
                description="Sensor reads about 40 C colder than the coolant really is",
                symptoms=["Gauge reads low", "Fan never comes on", "Actual temperature is high"],
                affected_parameters={
                    'bias_c': -40.0,
                    'active_dtcs': ['P0117'],
                    'visual_findings': ['Sensor and connector look clean'],
                },
            ),
            FaultMode(
                name="open_circuit",
                description="Sensor circuit is open, so the ECU sees an implausible cold reading",
                symptoms=["Gauge pegs cold", "Fan does not run", "Hard cold-start enrichment"],
                affected_parameters={
                    'open_circuit': True,
                    'active_dtcs': ['P0118'],
                    'visual_findings': ['Broken wire at the sensor connector'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        actual = context.get('coolant_temp_c')
        if tool in ('temperature', 'obd'):
            if self.parameters['open_circuit']:
                indicated = None
            elif actual is None:
                indicated = None
            else:
                indicated = round(float(actual) + float(self.parameters['bias_c']), 1)
            payload = {
                'indicated_c': indicated,
                'actual_c': actual,
                'note': 'Compare indicated temperature with an infrared reading of the housing',
            }
            if tool == 'obd':
                payload['dtcs'] = list(self.parameters.get('active_dtcs', []))
                payload['description'] = self.active_fault.description if self.active_fault else 'No stored fault'
            return payload
        return super().get_diagnostic_readings(tool, context)


class Radiator(CatalogPart):
    """Radiator core."""

    subsystem = "cooling"

    def __init__(self, component_id: str = "radiator"):
        super().__init__(component_id, "散热器 Radiator", "radiator.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'clogged': False,
            'coolant_level': 1.0,
            'replacement_cost': 220.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="clogged_core",
                description="Radiator tubes are restricted and cannot reject heat",
                symptoms=["Overheats", "Hot spots on the core", "Coolant level is normal"],
                affected_parameters={
                    'clogged': True,
                    'visual_findings': ['Fins are packed with debris', 'Core has hot and cold patches'],
                },
            ),
            FaultMode(
                name="leaking_radiator",
                description="Radiator tank leaks and the coolant level falls",
                symptoms=["Coolant puddle", "Sweet smell", "Overheats once the level is low"],
                affected_parameters={
                    'coolant_level': 0.35,
                    'visual_findings': ['Wet seam on the end tank', 'Low coolant in the reservoir'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'temperature':
            return {
                'coolant_temp_c': context.get('coolant_temp_c'),
                'coolant_level': self.parameters['coolant_level'],
            }
        return super().get_diagnostic_readings(tool, context)
