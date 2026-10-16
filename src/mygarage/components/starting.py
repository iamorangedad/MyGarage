"""Starting-circuit parts around the battery and starter motor."""

from typing import Any, Dict

from mygarage.component import CatalogPart, FaultMode


def _serviceable() -> Dict[str, Any]:
    return {
        'visual_findings': ['Appears serviceable'],
        'active_dtcs': [],
    }


class GroundStrap(CatalogPart):
    """Engine-to-chassis ground strap."""

    subsystem = "starting"

    def __init__(self, component_id: str = "ground_strap"):
        super().__init__(component_id, "发动机搭铁带 Ground Strap", "ground_strap.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'resistance_ohm': 0.001,
            'replacement_cost': 25.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="corroded_ground",
                description="Ground strap is corroded and drops voltage while cranking",
                symptoms=["Slow crank", "Lights dim while cranking"],
                affected_parameters={
                    'resistance_ohm': 0.02,
                    'visual_findings': ['Green corrosion where the strap bolts to the block'],
                },
            ),
            FaultMode(
                name="loose_ground",
                description="Ground strap connection is loose",
                symptoms=["Clicking", "No crank", "Lights dim or go out while cranking"],
                affected_parameters={
                    'resistance_ohm': 0.08,
                    'visual_findings': ['Strap lug is loose and rocks by hand'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool in ('voltage_drop', 'multimeter'):
            cranking = bool(context.get('engine_cranking'))
            if not cranking:
                return {
                    'voltage_drop': 0.0,
                    'unit': 'V',
                    'note': 'No cranking current. Hold the key in START and measure again.',
                }
            drop = round(self.parameters['resistance_ohm'] * 150.0, 2)
            return {
                'voltage_drop': drop,
                'unit': 'V',
                'spec_max': 0.2,
                'passed': drop <= 0.2,
                'test_condition': 'cranking',
            }
        return super().get_diagnostic_readings(tool, context)


class IgnitionSwitch(CatalogPart):
    """Key switch with separate RUN and START contacts."""

    subsystem = "starting"

    def __init__(self, component_id: str = "ignition_switch"):
        super().__init__(component_id, "点火开关 Ignition Switch", "ignition_switch.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'run_circuit_closed': True,
            'start_circuit_closed': True,
            'replacement_cost': 80.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="worn_start_contact",
                description="START contact does not close when the key is held",
                symptoms=["No crank", "Dash lights work", "No click"],
                affected_parameters={
                    'start_circuit_closed': False,
                    'visual_findings': ['Key feels worn in the START position'],
                },
            ),
            FaultMode(
                name="open_run_circuit",
                description="RUN contact is open, so the ECU and fuel pump are unpowered",
                symptoms=["Cranks but will not start", "No fuel pump prime"],
                affected_parameters={
                    'run_circuit_closed': False,
                    'visual_findings': ['Switch looks intact'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'multimeter':
            battery_v = float(context.get('battery_voltage', 12.6))
            start_requested = bool(context.get('engine_cranking') or context.get('start_requested'))
            run_powered = bool(context.get('ignition_on') or start_requested)
            run_v = battery_v if run_powered and self.parameters['run_circuit_closed'] else 0.0
            start_v = battery_v if start_requested and self.parameters['start_circuit_closed'] else 0.0
            return {
                'run_terminal_v': round(run_v, 2),
                'start_terminal_v': round(start_v, 2),
                'unit': 'V',
                'note': 'START terminal is live only while the key is held in START',
            }
        return super().get_diagnostic_readings(tool, context)


class StarterRelay(CatalogPart):
    """Relay that feeds the starter solenoid."""

    subsystem = "starting"

    def __init__(self, component_id: str = "starter_relay"):
        super().__init__(component_id, "起动继电器 Starter Relay", "starter_relay.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'coil_ok': True,
            'contacts_ok': True,
            'contact_factor': 1.0,
            'replacement_cost': 20.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="open_coil",
                description="Relay coil is open, so the contacts never close",
                symptoms=["No crank", "No click"],
                affected_parameters={
                    'coil_ok': False,
                    'active_dtcs': [],
                    'visual_findings': ['Relay case looks normal'],
                },
            ),
            FaultMode(
                name="burned_contacts",
                description="Relay clicks but the contacts are burned and resistive",
                symptoms=["Relay click", "No crank or very weak crank"],
                affected_parameters={
                    'contacts_ok': False,
                    'contact_factor': 0.15,
                    'visual_findings': ['Contacts are black and pitted'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'multimeter':
            battery_v = float(context.get('battery_voltage', 12.6))
            requested = bool(context.get('engine_cranking') or context.get('start_requested'))
            control_in = battery_v if requested else 0.0
            if not requested:
                output = 0.0
            elif not self.parameters['coil_ok']:
                output = 0.0
            elif not self.parameters['contacts_ok']:
                output = round(control_in * self.parameters['contact_factor'], 2)
            else:
                output = round(control_in, 2)
            return {
                'control_input_v': round(control_in, 2),
                'output_v': output,
                'coil_resistance_ohm': 80.0 if self.parameters['coil_ok'] else None,
                'unit': 'V',
                'note': None if requested else 'Hold the key in START to energize the relay',
            }
        return super().get_diagnostic_readings(tool, context)


class StarterFuse(CatalogPart):
    """Fuse in the starter control circuit."""

    subsystem = "starting"

    def __init__(self, component_id: str = "starter_fuse"):
        super().__init__(component_id, "起动熔断丝 Starter Fuse", "starter_fuse.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'blown': False,
            'replacement_cost': 5.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="blown_fuse",
                description="Starter fuse is open",
                symptoms=["No crank", "No click", "Accessories still work"],
                affected_parameters={
                    'blown': True,
                    'visual_findings': ['Fuse element is broken'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'multimeter':
            blown = bool(self.parameters['blown'])
            battery_v = float(context.get('battery_voltage', 12.6))
            return {
                'continuity_ohm': None if blown else 0.0,
                'voltage_in': round(battery_v, 2),
                'voltage_out': 0.0 if blown else round(battery_v, 2),
                'unit': 'V',
            }
        return super().get_diagnostic_readings(tool, context)


class StarterSolenoid(CatalogPart):
    """Solenoid that throws the pinion and closes the high-current contacts."""

    subsystem = "starting"

    def __init__(self, component_id: str = "starter_solenoid"):
        super().__init__(component_id, "起动机电磁开关 Starter Solenoid", "starter_solenoid.xml")

    def get_nominal_parameters(self) -> Dict[str, Any]:
        return {
            **_serviceable(),
            'pull_in_ok': True,
            'contacts_ok': True,
            'replacement_cost': 90.0,
        }

    def _define_fault_modes(self) -> None:
        self.fault_modes = [
            FaultMode(
                name="open_pull_in_coil",
                description="Pull-in coil is open, so the solenoid never clicks",
                symptoms=["No crank", "No click", "Battery voltage is healthy"],
                affected_parameters={
                    'pull_in_ok': False,
                    'visual_findings': ['Solenoid housing looks intact'],
                },
            ),
            FaultMode(
                name="burned_contacts",
                description="Solenoid clicks but the high-current contacts do not pass current",
                symptoms=["Single click", "No crank"],
                affected_parameters={
                    'contacts_ok': False,
                    'visual_findings': ['Solenoid clicks when powered', 'Contacts are burned'],
                },
            ),
        ]

    def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'multimeter':
            supply = float(context.get('starter_control_voltage', 0.0))
            if self.parameters['pull_in_ok'] and self.parameters['contacts_ok']:
                motor_feed = supply
            else:
                motor_feed = 0.0
            return {
                'solenoid_supply_v': round(supply, 2),
                'motor_feed_v': round(motor_feed, 2),
                'unit': 'V',
                'note': None if supply else 'No control voltage at the solenoid',
            }
        return super().get_diagnostic_readings(tool, context)
