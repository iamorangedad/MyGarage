"""Intake and exhaust parts that change idle, fuel trim, and OBD data."""

from typing import Any, Dict, Optional

from mygarage.component import CatalogPart, FaultMode


def _serviceable() -> Dict[str, Any]:
    return {
        'visual_findings': ['Appears serviceable'],
        'active_dtcs': [],
    }


def _not_running(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if context.get('engine_running'):
        return None
    return {'note': 'Engine is not running. Start it, then read live data.'}


class AirFilter(CatalogPart):
    """Air filter ahead of the mass-airflow sensor."""

    subsystem = "intake"

    def __init__(self, component_id: str = "air_filter"):
        super().__init__(component_id, "空气滤清器 Air Filter", "air_filter.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {**_serviceable(), 'restriction': 0.0, 'replacement_cost': 25.0}

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="clogged_filter",
                description="Air filter is packed with dirt and restricts airflow",
                symptoms=["Loss of power", "Normal fuel trims at idle"],
                affected_parameters={
                    'restriction': 0.85,
                    'visual_findings': ['Filter element is packed with dirt and will not pass light'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'live_data':
            stopped = _not_running(context)
            if stopped:
                return stopped
            return {
                'power_pct': context.get('power_pct'),
                'maf_reported_gps': context.get('maf_reported_gps'),
                'note': 'A clogged filter lowers power. Fuel trim stays near zero because the air is still metered.',
            }
        return super().get_diagnostic_readings(tool, context)


class ThrottleBody(CatalogPart):
    """Throttle plate. Extra air here is metered by the MAF."""

    subsystem = "intake"

    def __init__(self, component_id: str = "throttle_body"):
        super().__init__(component_id, "节气门体 Throttle Body", "throttle_body.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {**_serviceable(), 'idle_air': 'normal', 'replacement_cost': 180.0}

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="carbon_buildup",
                description="Carbon holds the throttle plate open, so idle air is high but still metered",
                symptoms=["High idle", "Fuel trims near normal"],
                affected_parameters={
                    'idle_air': 'high',
                    'visual_findings': ['Black carbon ridge around the throttle plate'],
                },
            ),
            FaultMode(
                name="stuck_closed",
                description="Throttle plate sticks shut and idle air is too low",
                symptoms=["Idle drops", "Stall when the clutch is released"],
                affected_parameters={
                    'idle_air': 'low',
                    'visual_findings': ['Plate is gummed shut and does not spring back'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'live_data':
            stopped = _not_running(context)
            if stopped:
                return stopped
            return {
                'rpm': context.get('engine_rpm'),
                'fuel_trim_pct': context.get('fuel_trim_pct'),
                'note': 'Metered idle air changes rpm without a large fuel-trim correction',
            }
        return super().get_diagnostic_readings(tool, context)


class IntakeGasket(CatalogPart):
    """Intake manifold gasket. A leak is unmetered air."""

    subsystem = "intake"

    def __init__(self, component_id: str = "intake_gasket"):
        super().__init__(component_id, "进气歧管垫 Intake Gasket", "intake_gasket.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {**_serviceable(), 'leak': False, 'replacement_cost': 60.0}

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="vacuum_leak",
                description="Intake gasket leaks unmetered air",
                symptoms=["High idle", "Positive fuel trim", "Lean misfire"],
                affected_parameters={
                    'leak': True,
                    'active_dtcs': ['P0171'],
                    'visual_findings': ['Dirt trail along the gasket seam'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'smoke_test':
            return {
                'smoke_escapes': bool(self.parameters['leak']),
                'note': 'Smoke from the gasket seam means unmetered air',
            }
        if tool == 'live_data':
            stopped = _not_running(context)
            if stopped:
                return stopped
            return {
                'fuel_trim_pct': context.get('fuel_trim_pct'),
                'vacuum_gauge_kpa': context.get('manifold_pressure_kpa'),
                'rpm': context.get('engine_rpm'),
            }
        return super().get_diagnostic_readings(tool, context)


class MassAirflowSensor(CatalogPart):
    """MAF sensor. Scale other than 1.0 is a lying meter."""

    subsystem = "intake"

    def __init__(self, component_id: str = "maf_sensor"):
        super().__init__(component_id, "空气流量传感器 MAF Sensor", "maf_sensor.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {**_serviceable(), 'scale': 1.0, 'replacement_cost': 140.0}

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="under_reading",
                description="MAF reports less air than the engine is actually using",
                symptoms=["Positive fuel trim", "Rough idle", "Lean under load"],
                affected_parameters={
                    'scale': 0.55,
                    'active_dtcs': ['P0101'],
                    'visual_findings': ['Hot-wire element is coated with oil and dust'],
                },
            ),
            FaultMode(
                name="over_reading",
                description="MAF reports more air than the engine is actually using",
                symptoms=["Negative fuel trim", "Rich exhaust", "Sooty plugs"],
                affected_parameters={
                    'scale': 1.45,
                    'active_dtcs': ['P0101'],
                    'visual_findings': ['Sensor housing looks intact'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'live_data':
            stopped = _not_running(context)
            if stopped:
                return stopped
            return {
                'maf_reported_gps': context.get('maf_reported_gps'),
                'maf_from_map_gps': context.get('maf_actual_gps'),
                'fuel_trim_pct': context.get('fuel_trim_pct'),
                'spec_idle_gps': '2.5-5.0',
                'note': 'Compare the MAF with the speed-density estimate from MAP',
            }
        return super().get_diagnostic_readings(tool, context)


class ManifoldPressureSensor(CatalogPart):
    """MAP sensor."""

    subsystem = "intake"

    def __init__(self, component_id: str = "map_sensor"):
        super().__init__(component_id, "进气压力传感器 MAP Sensor", "map_sensor.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {**_serviceable(), 'mode': 'normal', 'replacement_cost': 70.0}

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="reads_high",
                description="MAP sensor reports a high pressure while the manifold is actually at idle vacuum",
                symptoms=["Negative fuel trim", "Rich idle"],
                affected_parameters={
                    'mode': 'high',
                    'active_dtcs': ['P0108'],
                    'visual_findings': ['Vacuum hose to the sensor is soft but connected'],
                },
            ),
            FaultMode(
                name="open_circuit",
                description="MAP sensor circuit is open",
                symptoms=["Rough idle", "No manifold-pressure reading"],
                affected_parameters={
                    'mode': 'open',
                    'active_dtcs': ['P0107'],
                    'visual_findings': ['Broken signal wire at the connector'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'live_data':
            stopped = _not_running(context)
            if stopped:
                return stopped
            return {
                'reported_kpa': context.get('map_reported_kpa'),
                'vacuum_gauge_kpa': context.get('manifold_pressure_kpa'),
                'fuel_trim_pct': context.get('fuel_trim_pct'),
                'spec_idle_kpa': '28-42',
                'note': 'A vacuum gauge on the manifold should agree with the sensor',
            }
        return super().get_diagnostic_readings(tool, context)


class UpstreamO2Sensor(CatalogPart):
    """Upstream oxygen sensor used for closed-loop fuel control."""

    subsystem = "exhaust"

    def __init__(self, component_id: str = "o2_sensor_upstream"):
        super().__init__(component_id, "前氧传感器 Upstream O2", "o2_upstream.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {**_serviceable(), 'response': 'normal', 'replacement_cost': 90.0}

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="lazy_sensor",
                description="Upstream O2 sensor responds too slowly to switch rich and lean",
                symptoms=["Code for slow response", "Idle can still sound normal"],
                affected_parameters={
                    'response': 'lazy',
                    'active_dtcs': ['P0133'],
                    'visual_findings': ['Sensor tip is coated'],
                },
            ),
            FaultMode(
                name="stuck_lean",
                description="Upstream O2 sensor is stuck at a lean voltage",
                symptoms=["No switching", "ECU keeps adding fuel"],
                affected_parameters={
                    'response': 'stuck_lean',
                    'active_dtcs': ['P2195'],
                    'visual_findings': ['Sensor harness looks intact'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'live_data':
            stopped = _not_running(context)
            if stopped:
                return stopped
            return {
                'voltage': context.get('o2_upstream_v'),
                'switching': context.get('o2_switching'),
                'fuel_trim_pct': context.get('fuel_trim_pct'),
                'spec': 'Switches between about 0.1 and 0.9 V',
            }
        return super().get_diagnostic_readings(tool, context)


class DownstreamO2Sensor(CatalogPart):
    """Downstream oxygen sensor used to judge the catalyst."""

    subsystem = "exhaust"

    def __init__(self, component_id: str = "o2_sensor_downstream"):
        super().__init__(component_id, "后氧传感器 Downstream O2", "o2_downstream.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {**_serviceable(), 'stuck': False, 'replacement_cost': 95.0}

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="stuck_sensor",
                description="Downstream O2 sensor does not respond",
                symptoms=["No downstream activity", "Catalyst efficiency can still be fine"],
                affected_parameters={
                    'stuck': True,
                    'active_dtcs': ['P0140'],
                    'visual_findings': ['Sensor is installed, connector is loose'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'live_data':
            stopped = _not_running(context)
            if stopped:
                return stopped
            return {
                'voltage': context.get('o2_downstream_v'),
                'switching': context.get('o2_downstream_switching'),
                'upstream_switching': context.get('o2_switching'),
                'catalyst_efficiency': context.get('catalyst_efficiency'),
                'note': 'A dead downstream sensor stays still. A bad catalyst makes it switch with the upstream sensor.',
            }
        return super().get_diagnostic_readings(tool, context)


class CatalyticConverter(CatalogPart):
    """Three-way catalyst."""

    subsystem = "exhaust"

    def __init__(self, component_id: str = "catalytic_converter"):
        super().__init__(component_id, "三元催化器 Catalytic Converter", "catalytic_converter.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'efficiency': 0.96,
            'clogged': False,
            'replacement_cost': 650.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="inefficient",
                description="Catalyst no longer stores oxygen, so the downstream sensor switches",
                symptoms=["P0420", "Idle sounds normal", "Downstream O2 follows the upstream sensor"],
                affected_parameters={
                    'efficiency': 0.32,
                    'active_dtcs': ['P0420'],
                    'visual_findings': ['Converter shell looks intact'],
                },
            ),
            FaultMode(
                name="clogged",
                description="Catalyst substrate is broken and exhaust backpressure is high",
                symptoms=["Loss of power", "Idle a little low", "Heat at the converter inlet"],
                affected_parameters={
                    'clogged': True,
                    'visual_findings': ['Rattle from a broken substrate', 'Inlet glows before the outlet gets hot'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'live_data':
            stopped = _not_running(context)
            if stopped:
                return stopped
            return {
                'catalyst_efficiency': context.get('catalyst_efficiency'),
                'backpressure_kpa': context.get('backpressure_kpa'),
                'power_pct': context.get('power_pct'),
                'spec_backpressure_kpa': '< 8 at idle',
            }
        return super().get_diagnostic_readings(tool, context)


class EGRValve(CatalogPart):
    """EGR valve. It should be closed at idle."""

    subsystem = "intake"

    def __init__(self, component_id: str = "egr_valve"):
        super().__init__(component_id, "EGR 阀 EGR Valve", "egr_valve.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'stuck_open': False,
            'stuck_closed': False,
            'replacement_cost': 150.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="stuck_open",
                description="EGR valve is stuck open and dilutes the idle mixture",
                symptoms=["Rough idle", "Stall coming to a stop"],
                affected_parameters={
                    'stuck_open': True,
                    'active_dtcs': ['P0402'],
                    'visual_findings': ['Valve pintle is off its seat'],
                },
            ),
            FaultMode(
                name="stuck_closed",
                description="EGR valve never opens when the ECU commands it",
                symptoms=["Idle sounds normal", "No EGR flow on a command test"],
                affected_parameters={
                    'stuck_closed': True,
                    'active_dtcs': ['P0401'],
                    'visual_findings': ['Pintle is crusted shut'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'egr_test':
            if self.parameters['stuck_closed']:
                commanded_flow = False
            else:
                commanded_flow = True
            return {
                'flows_at_idle': bool(self.parameters['stuck_open']),
                'flow_when_commanded': commanded_flow,
                'note': 'EGR should be closed at idle and flow when commanded off idle',
            }
        return super().get_diagnostic_readings(tool, context)


class PCVValve(CatalogPart):
    """PCV valve. Stuck open is a small unmetered vacuum leak."""

    subsystem = "intake"

    def __init__(self, component_id: str = "pcv_valve"):
        super().__init__(component_id, "PCV 阀 PCV Valve", "pcv_valve.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'stuck_open': False,
            'stuck_closed': False,
            'replacement_cost': 15.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="stuck_open",
                description="PCV valve is stuck open and pulls unmetered air",
                symptoms=["Slightly high idle", "Moderate positive fuel trim"],
                affected_parameters={
                    'stuck_open': True,
                    'active_dtcs': ['P0171'],
                    'visual_findings': ['Valve does not rattle', 'Oil vapor in the intake hose'],
                },
            ),
            FaultMode(
                name="stuck_closed",
                description="PCV valve is stuck closed, so crankcase vapor is not drawn in",
                symptoms=["Idle sounds normal", "Oil mist at seals and the dipstick"],
                affected_parameters={
                    'stuck_closed': True,
                    'visual_findings': ['Valve is gummed shut', 'Oil film around the valve cover'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'rattle_test':
            free = not self.parameters['stuck_open'] and not self.parameters['stuck_closed']
            return {'rattles': free, 'note': 'A free PCV valve rattles when shaken'}
        if tool == 'live_data':
            stopped = _not_running(context)
            if stopped:
                return stopped
            return {
                'rpm': context.get('engine_rpm'),
                'fuel_trim_pct': context.get('fuel_trim_pct'),
            }
        return super().get_diagnostic_readings(tool, context)
