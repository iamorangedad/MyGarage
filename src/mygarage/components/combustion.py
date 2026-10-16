"""Parts that decide whether a cranking engine catches and idles."""

from typing import Any, Dict

from mygarage.component import CatalogPart, FaultMode


def _serviceable() -> Dict[str, Any]:
    return {
        'visual_findings': ['Appears serviceable'],
        'active_dtcs': [],
    }


class SparkPlug(CatalogPart):
    """Spark plug for the sample cylinder."""

    subsystem = "combustion"

    def __init__(self, component_id: str = "spark_plug"):
        super().__init__(component_id, "火花塞 Spark Plug", "spark_plug.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'fouled': False,
            'gap_mm': 1.0,
            'replacement_cost': 12.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="fouled_plug",
                description="Plug is carbon-fouled and misfires under load and at idle",
                symptoms=["Rough idle", "Misfire", "Fuel smell"],
                affected_parameters={
                    'fouled': True,
                    'active_dtcs': ['P0301'],
                    'visual_findings': ['Insulator and electrode are covered in dry black carbon'],
                },
            ),
            FaultMode(
                name="wide_gap",
                description="Electrode is worn and the gap is too large",
                symptoms=["Misfire under load", "Hard start when hot"],
                affected_parameters={
                    'gap_mm': 2.2,
                    'active_dtcs': ['P0300'],
                    'visual_findings': ['Center electrode is rounded and the gap is wide'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'spark_test':
            return {
                'fouled': bool(self.parameters['fouled']),
                'gap_mm': self.parameters['gap_mm'],
                'spec_gap_mm': '0.9-1.1',
                'misfire': bool(context.get('misfire')),
            }
        return super().get_diagnostic_readings(tool, context)


class IgnitionCoil(CatalogPart):
    """Coil that fires the sample plug."""

    subsystem = "combustion"

    def __init__(self, component_id: str = "ignition_coil"):
        super().__init__(component_id, "点火线圈 Ignition Coil", "ignition_coil.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'spark_kv': 28.0,
            'primary_ohm': 0.6,
            'replacement_cost': 70.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="open_primary",
                description="Primary winding is open, so the coil makes no spark",
                symptoms=["Cranks but will not start", "No spark"],
                affected_parameters={
                    'spark_kv': 0.0,
                    'primary_ohm': None,
                    'active_dtcs': ['P0351'],
                    'visual_findings': ['Coil housing looks intact'],
                },
            ),
            FaultMode(
                name="weak_spark",
                description="Coil output has fallen and the spark is weak",
                symptoms=["Rough idle", "Misfire", "Worse when hot"],
                affected_parameters={
                    'spark_kv': 12.0,
                    'active_dtcs': ['P0300'],
                    'visual_findings': ['Hairline crack in the coil boot'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'multimeter':
            return {
                'primary_ohm': self.parameters['primary_ohm'],
                'spec_ohm': '0.4-0.8',
            }
        if tool == 'spark_test':
            powered = bool(context.get('run_circuit_closed', True))
            kv = self.parameters['spark_kv'] if powered else 0.0
            return {
                'spark_kv': kv,
                'spark_present': kv >= 8.0,
                'spec_kv': '>= 20',
            }
        return super().get_diagnostic_readings(tool, context)


class FuelInjector(CatalogPart):
    """One port injector on the sample engine."""

    subsystem = "combustion"

    def __init__(self, component_id: str = "fuel_injector"):
        super().__init__(component_id, "喷油器 Fuel Injector", "fuel_injector.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'clogged': False,
            'leaking': False,
            'resistance_ohm': 12.0,
            'replacement_cost': 85.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="clogged_injector",
                description="Injector is restricted and that cylinder runs lean",
                symptoms=["Rough idle", "Single-cylinder misfire", "Normal fuel pressure"],
                affected_parameters={
                    'clogged': True,
                    'active_dtcs': ['P0301', 'P0171'],
                    'visual_findings': ['Spray tip is varnished'],
                },
            ),
            FaultMode(
                name="leaking_injector",
                description="Injector drips when closed and floods one cylinder",
                symptoms=["Hard start", "Rough idle", "Fuel smell"],
                affected_parameters={
                    'leaking': True,
                    'active_dtcs': ['P0301', 'P0172'],
                    'visual_findings': ['Fuel wetness at the injector seat'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'multimeter':
            return {
                'resistance_ohm': self.parameters['resistance_ohm'],
                'spec_ohm': '11-14',
            }
        if tool == 'fuel_pressure':
            return {
                'rail_pressure_psi': context.get('fuel_pressure_psi'),
                'note': 'A bad injector does not drop rail pressure on this engine',
            }
        return super().get_diagnostic_readings(tool, context)


class FuelPump(CatalogPart):
    """In-tank electric fuel pump."""

    subsystem = "combustion"

    def __init__(self, component_id: str = "fuel_pump"):
        super().__init__(component_id, "燃油泵 Fuel Pump", "fuel_pump.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'pressure_psi': 55.0,
            'replacement_cost': 280.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="dead_pump",
                description="Fuel pump does not run, so rail pressure stays at zero",
                symptoms=["Cranks but will not start", "No pump prime"],
                affected_parameters={
                    'pressure_psi': 0.0,
                    'active_dtcs': ['P0087'],
                    'visual_findings': ['Tank and lines look dry at the rail'],
                },
            ),
            FaultMode(
                name="weak_pump",
                description="Pump runs but cannot hold specified rail pressure",
                symptoms=["Long crank", "Rough idle", "Loss of power"],
                affected_parameters={
                    'pressure_psi': 28.0,
                    'active_dtcs': ['P0087'],
                    'visual_findings': ['Pump can be heard, quieter than normal'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'fuel_pressure':
            ignition_on = bool(context.get('ignition_on'))
            run_closed = bool(context.get('run_circuit_closed', True))
            if not ignition_on:
                measured = 0.0
                note = 'Key is off. Turn the ignition to RUN to prime the pump.'
            elif not run_closed:
                measured = 0.0
                note = 'Pump is not powered because the run circuit is open.'
            else:
                measured = float(self.parameters['pressure_psi'])
                if measured < 15:
                    note = 'Pump is powered but pressure is too low to start.'
                elif measured < 45:
                    note = 'Pressure is below the 50-60 psi spec.'
                else:
                    note = 'Pressure is within spec.'
            return {
                'pressure_psi': measured,
                'spec_psi': '50-60',
                'note': note,
            }
        return super().get_diagnostic_readings(tool, context)


class CrankshaftPositionSensor(CatalogPart):
    """CKP sensor the ECU needs before it will spark or inject."""

    subsystem = "combustion"

    def __init__(self, component_id: str = "ckp_sensor"):
        super().__init__(component_id, "曲轴位置传感器 CKP Sensor", "ckp_sensor.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'signal_present': True,
            'intermittent': False,
            'resistance_ohm': 850.0,
            'replacement_cost': 75.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="no_signal",
                description="CKP sensor is open and the ECU receives no speed reference",
                symptoms=["Cranks but will not start", "No spark", "No injector pulse"],
                affected_parameters={
                    'signal_present': False,
                    'resistance_ohm': None,
                    'active_dtcs': ['P0335'],
                    'visual_findings': ['Sensor is seated, connector looks clean'],
                },
            ),
            FaultMode(
                name="intermittent_signal",
                description="CKP signal drops out, so the engine starts and then misfires",
                symptoms=["Intermittent stall", "Rough idle", "Crank but sometimes no start"],
                affected_parameters={
                    'intermittent': True,
                    'active_dtcs': ['P0336'],
                    'visual_findings': ['Connector lock is loose'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'multimeter':
            return {
                'resistance_ohm': self.parameters['resistance_ohm'],
                'spec_ohm': '500-1500',
            }
        if tool == 'spark_test':
            return {
                'ecu_enables_spark': bool(self.parameters['signal_present']),
                'note': 'Without a CKP signal the ECU does not fire the coil',
            }
        return super().get_diagnostic_readings(tool, context)
