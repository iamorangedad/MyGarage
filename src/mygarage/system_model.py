"""Signal model for the electrical, combustion, and thermal systems.

MuJoCo only integrates rigid bodies. This module decides whether the starter
is powered, whether the engine catches, what the charging voltage is, and how
hot the coolant gets. Those signals are what diagnostic tools report, and the
starter torque is what the simulation applies to the crankshaft joint.
"""

from typing import Any, Dict, List, Optional

from mygarage.component import Component
from mygarage.components import default_components


class SystemModel:
    """State of every car part and the signals that couple them."""

    def __init__(self):
        self.components: Dict[str, Component] = {}
        self.state: Dict[str, Any] = self._default_state()
        self._initialize_default_components()
        self._refresh_signals()

    def _default_state(self) -> Dict[str, Any]:
        return {
            'ignition_on': False,
            'ignition_position': 'off',
            'start_requested': False,
            'engine_cranking': False,
            'engine_running': False,
            'engine_rpm': 0,
            'starter_engaged': False,
            'coolant_temp_c': 25.0,
            'ambient_temp_c': 25.0,
            'fan_on': False,
            'fan_commanded': False,
            'charging_voltage': 12.6,
            'fuel_pressure_psi': 0.0,
            'starter_control_voltage': 0.0,
            'misfire': False,
            'idle_quality': 'off',
        }

    def _initialize_default_components(self):
        """Install the built-in parts."""
        for component in default_components():
            self.add_component(component)

    def add_component(self, component: Component):
        """Add a component to the system."""
        self.components[component.component_id] = component

    def get_component(self, component_id: str) -> Optional[Component]:
        """Get a component by ID."""
        return self.components.get(component_id)

    def inject_fault(self, component_id: str, fault_name: str) -> bool:
        """Inject a fault into a specific component."""
        component = self.get_component(component_id)
        if component:
            return component.inject_fault(fault_name)
        return False

    def set_ignition(self, position: str):
        """Move the key to ``off`` or ``run`` without cranking."""
        if position not in ('off', 'run'):
            raise ValueError(f'Unsupported ignition position: {position}')
        self.state['ignition_position'] = position
        self.state['ignition_on'] = position == 'run'
        self.state['start_requested'] = False
        if position == 'off':
            self.state['engine_running'] = False
            self.state['engine_cranking'] = False
            self.state['starter_engaged'] = False
            self.state['engine_rpm'] = 0
            self.state['misfire'] = False
            self.state['idle_quality'] = 'off'
        self._refresh_signals()

    def attempt_crank(self) -> Dict[str, Any]:
        """Hold the key in START and report whether the engine turns."""
        self.state['start_requested'] = True
        battery = self.get_component('battery_12v')
        starter = self.get_component('starter_motor')
        if not battery or not starter:
            return self._crank_failure('none', 'Missing components')

        ignition = self.get_component('ignition_switch')
        if ignition and not ignition.parameters['start_circuit_closed']:
            return self._crank_failure('none', 'Ignition switch START contact is open')

        fuse = self.get_component('starter_fuse')
        if fuse and fuse.parameters['blown']:
            return self._crank_failure('none', 'Starter fuse is open')

        relay = self.get_component('starter_relay')
        if relay and not relay.parameters['coil_ok']:
            return self._crank_failure('none', 'Starter relay coil is open')
        if relay and not relay.parameters['contacts_ok']:
            return self._crank_failure('relay_click', 'Starter relay contacts are burned')

        if not starter.parameters.get('solenoid_functional', True):
            return self._crank_failure('single_click', 'Starter solenoid is not engaging')

        solenoid = self.get_component('starter_solenoid')
        if solenoid and not solenoid.parameters['pull_in_ok']:
            return self._crank_failure('none', 'Starter solenoid pull-in coil is open')
        if solenoid and not solenoid.parameters['contacts_ok']:
            return self._crank_failure('single_click', 'Starter solenoid contacts are burned')

        battery_voltage = battery.parameters['voltage_resting']
        if battery_voltage < 10.0:
            return self._crank_failure('click', 'Battery voltage too low')

        if not starter.parameters.get('operational', True):
            return self._crank_failure('none', 'Starter motor not operational')

        self.state['engine_cranking'] = True
        self.state['starter_engaged'] = True

        context = {'engine_cranking': True}
        battery_readings = battery.get_diagnostic_readings('multimeter', context)
        voltage_under_load = float(battery_readings['voltage'])
        ground_drop = self._ground_drop()
        voltage_at_starter = voltage_under_load - ground_drop
        starter_torque = starter.parameters['torque_output']

        if starter_torque > 2.0 and voltage_at_starter > 9.6:
            cranking_rpm = 200
            sound = 'normal_crank'
            success = True
            reason = 'Engine cranks normally'
        elif starter_torque > 1.0 and voltage_at_starter > 8.0:
            cranking_rpm = 80
            sound = 'slow_crank'
            success = False
            reason = 'Engine cranks slowly'
        else:
            cranking_rpm = 0
            sound = 'grinding'
            success = False
            reason = 'Starter cannot turn the engine'
            if ground_drop > 2.0:
                reason = 'Excessive voltage drop on the ground strap'

        self.state['engine_rpm'] = cranking_rpm
        self._refresh_signals()
        return {
            'success': success,
            'sound': sound,
            'reason': reason,
            'description': reason,
            'cranking': True,
            'rpm': cranking_rpm,
            'voltage_under_load': round(voltage_at_starter, 2),
            'ground_drop': round(ground_drop, 2),
        }

    def start_attempt(self) -> Dict[str, Any]:
        """Crank, release the key to RUN, and see whether the engine catches."""
        self.state['ignition_position'] = 'start'
        result = dict(self.attempt_crank())
        combustion = self.combustion_status()
        started = bool(result.get('success')) and combustion['can_idle']
        self.stop_crank()
        self.state['ignition_position'] = 'run'
        self.state['ignition_on'] = True
        self.state['engine_running'] = started
        self.state['engine_rpm'] = combustion['idle_rpm'] if started else 0
        self.state['idle_quality'] = combustion['idle_quality'] if started else 'off'
        self.state['misfire'] = bool(combustion['misfire']) if started else False
        result['started'] = started
        result['misfire'] = self.state['misfire']
        result['idle_quality'] = self.state['idle_quality']
        result['idle_rpm'] = self.state['engine_rpm']
        if not result.get('success'):
            result['description'] = result.get('reason', 'Engine did not crank')
        elif not started:
            result['description'] = 'Engine cranks but does not start. ' + combustion['reason']
        else:
            result['description'] = combustion['reason']
        self._refresh_signals()
        return result

    def combustion_status(self) -> Dict[str, Any]:
        """Whether fuel, spark, and the crank signal can sustain an idle."""
        ignition = self.get_component('ignition_switch')
        pump = self.get_component('fuel_pump')
        coil = self.get_component('ignition_coil')
        plug = self.get_component('spark_plug')
        injector = self.get_component('fuel_injector')
        ckp = self.get_component('ckp_sensor')

        if ignition and not ignition.parameters['run_circuit_closed']:
            return self._no_start('Run circuit is open, so the ECU, coil, and fuel pump have no power')
        if ckp and not ckp.parameters['signal_present']:
            return self._no_start('No crankshaft position signal, so the ECU will not fire spark or injectors')
        if pump and pump.parameters['pressure_psi'] < 15:
            return self._no_start('Fuel pressure is too low to start')
        if coil and coil.parameters['spark_kv'] < 8:
            return self._no_start('Ignition coil is not producing spark')

        reasons = []
        if ckp and ckp.parameters.get('intermittent'):
            reasons.append('CKP signal drops out')
        if pump and pump.parameters['pressure_psi'] < 45:
            reasons.append('fuel pressure is marginal')
        if coil and coil.parameters['spark_kv'] < 20:
            reasons.append('spark is weak')
        if plug and (plug.parameters.get('fouled') or plug.parameters.get('gap_mm', 1.0) > 1.5):
            reasons.append('spark plug is fouled or the gap is excessive')
        if injector and injector.parameters.get('clogged'):
            reasons.append('a fuel injector is clogged')
        if injector and injector.parameters.get('leaking'):
            reasons.append('a fuel injector is leaking')

        if reasons:
            return {
                'can_idle': True,
                'misfire': True,
                'idle_rpm': 640,
                'idle_quality': 'rough',
                'reason': 'Engine runs with a misfire: ' + '; '.join(reasons),
            }
        return {
            'can_idle': True,
            'misfire': False,
            'idle_rpm': 750,
            'idle_quality': 'steady',
            'reason': 'Engine cranks and starts, idle is steady',
        }

    def stop_crank(self):
        """Release the starter. A running engine keeps its idle speed."""
        self.state['engine_cranking'] = False
        self.state['starter_engaged'] = False
        self.state['start_requested'] = False
        if not self.state['engine_running']:
            self.state['engine_rpm'] = 0

    def starter_torque_command(self) -> float:
        """Torque to apply on the crankshaft joint while the starter is engaged."""
        if not self.state['engine_cranking']:
            return 0.0
        starter = self.get_component('starter_motor')
        if not starter:
            return 0.0
        return float(starter.parameters.get('torque_output', 0.0))

    def get_context(self) -> Dict[str, Any]:
        """Current signals passed into component diagnostic readings."""
        self._refresh_signals()
        battery = self.get_component('battery_12v')
        ignition = self.get_component('ignition_switch')
        battery_voltage = battery.parameters['voltage_resting'] if battery else 12.6
        return {
            'engine_cranking': self.state['engine_cranking'],
            'start_requested': self.state['start_requested'],
            'battery_voltage': battery_voltage,
            'ignition_on': self.state['ignition_on'],
            'ignition_position': self.state['ignition_position'],
            'engine_running': self.state['engine_running'],
            'engine_rpm': self.state['engine_rpm'],
            'charging_voltage': self.state['charging_voltage'],
            'coolant_temp_c': self.state['coolant_temp_c'],
            'fan_on': self.state['fan_on'],
            'fan_commanded': self.state['fan_commanded'],
            'fuel_pressure_psi': self.state['fuel_pressure_psi'],
            'starter_control_voltage': self.state['starter_control_voltage'],
            'run_circuit_closed': bool(ignition.parameters['run_circuit_closed']) if ignition else True,
            'idle_quality': self.state['idle_quality'],
            'misfire': self.state['misfire'],
            'ground_drop_v': round(self._ground_drop(), 2) if self.state['engine_cranking'] else 0.0,
        }

    def step(self, dt: float = 0.01):
        """Advance electrical drain and coolant temperature."""
        if self.state['engine_cranking']:
            battery = self.get_component('battery_12v')
            if battery and battery.parameters['state_of_charge'] > 0:
                discharge_rate = 0.001
                battery.parameters['state_of_charge'] -= discharge_rate * dt
                battery.parameters['state_of_charge'] = max(0, battery.parameters['state_of_charge'])

        if self.state['engine_running']:
            self._approach_temp(self._thermal_target(), rate=0.15, dt=dt)
        else:
            self._approach_temp(self.state['ambient_temp_c'], rate=0.02, dt=dt)
        self._refresh_signals()

    def get_all_components(self) -> List[Component]:
        """Get list of all components."""
        return list(self.components.values())

    def reset(self):
        """Reset all components to nominal state."""
        for component in self.components.values():
            component.clear_fault()
        self.state = self._default_state()
        self._refresh_signals()

    def _crank_failure(self, sound: str, reason: str) -> Dict[str, Any]:
        self.state['engine_cranking'] = False
        self.state['starter_engaged'] = False
        self.state['engine_rpm'] = 0
        self._refresh_signals()
        return {
            'success': False,
            'sound': sound,
            'reason': reason,
            'description': reason,
            'cranking': False,
            'rpm': 0,
        }

    def _no_start(self, reason: str) -> Dict[str, Any]:
        return {
            'can_idle': False,
            'misfire': False,
            'idle_rpm': 0,
            'idle_quality': 'no_start',
            'reason': reason,
        }

    def _ground_drop(self) -> float:
        strap = self.get_component('ground_strap')
        if not strap:
            return 0.0
        return float(strap.parameters['resistance_ohm']) * 150.0

    def _starter_control_voltage(self) -> float:
        battery = self.get_component('battery_12v')
        battery_v = float(battery.parameters['voltage_resting']) if battery else 0.0
        requested = self.state['start_requested'] or self.state['engine_cranking']
        if not requested:
            return 0.0
        ignition = self.get_component('ignition_switch')
        fuse = self.get_component('starter_fuse')
        relay = self.get_component('starter_relay')
        if ignition and not ignition.parameters['start_circuit_closed']:
            return 0.0
        if fuse and fuse.parameters['blown']:
            return 0.0
        if relay and not relay.parameters['coil_ok']:
            return 0.0
        if relay and not relay.parameters['contacts_ok']:
            return round(battery_v * float(relay.parameters.get('contact_factor', 0.2)), 2)
        return battery_v

    def _fuel_pressure(self) -> float:
        pump = self.get_component('fuel_pump')
        ignition = self.get_component('ignition_switch')
        if not pump:
            return 0.0
        powered = self.state['ignition_on'] or self.state['engine_cranking'] or self.state['engine_running']
        run_closed = True if not ignition else bool(ignition.parameters['run_circuit_closed'])
        if powered and run_closed:
            return float(pump.parameters['pressure_psi'])
        return 0.0

    def _charging_voltage(self) -> float:
        battery = self.get_component('battery_12v')
        battery_v = float(battery.parameters['voltage_resting']) if battery else 12.6
        if not self.state['engine_running']:
            return round(battery_v, 2)
        belt = self.get_component('serpentine_belt')
        alternator = self.get_component('alternator')
        regulator = self.get_component('voltage_regulator')
        if belt and belt.parameters['broken']:
            return round(battery_v, 2)
        if alternator and not alternator.parameters['output_ok']:
            return round(battery_v, 2)
        setpoint = float(regulator.parameters['setpoint_v']) if regulator else 14.2
        slip = float(belt.parameters['slip']) if belt else 0.0
        slip = min(max(slip, 0.0), 1.0)
        return round(setpoint * (1.0 - slip) + battery_v * slip, 2)

    def _coolant_level(self) -> float:
        radiator = self.get_component('radiator')
        pump = self.get_component('water_pump')
        level = float(radiator.parameters['coolant_level']) if radiator else 1.0
        if pump and pump.parameters.get('external_leak'):
            level = min(level, 0.4)
        return level

    def _fan_commanded(self, temp_c: float) -> bool:
        """ECU fan request from the indicated coolant temperature."""
        if not (self.state['ignition_on'] or self.state['engine_running']):
            return False
        ect = self.get_component('ect_sensor')
        if ect and ect.parameters['open_circuit']:
            return False
        bias = float(ect.parameters['bias_c']) if ect else 0.0
        return temp_c + bias >= 90.0

    def _fan_on(self, temp_c: float) -> bool:
        fan = self.get_component('cooling_fan')
        if not fan or not fan.parameters['operational'] or not fan.parameters['relay_ok']:
            return False
        return self._fan_commanded(temp_c)

    def _fan_capable(self, temp_c: float) -> bool:
        """Whether the fan would run if the coolant were at ``temp_c``."""
        return self._fan_on(temp_c)

    def _thermal_target(self) -> float:
        pump = self.get_component('water_pump')
        thermostat = self.get_component('thermostat')
        radiator = self.get_component('radiator')
        pumping = True if not pump else bool(pump.parameters['pumping'])
        stuck_closed = bool(thermostat and thermostat.parameters['stuck_closed'])
        stuck_open = bool(thermostat and thermostat.parameters['stuck_open'])
        clogged = bool(radiator and radiator.parameters['clogged'])
        if not pumping or stuck_closed:
            return 118.0
        if stuck_open and not clogged and self._coolant_level() >= 0.5:
            return 60.0
        if clogged or self._coolant_level() < 0.5:
            return 112.0
        if not self._fan_capable(100.0):
            return 110.0
        return 92.0

    def _approach_temp(self, target: float, rate: float, dt: float):
        temp = float(self.state['coolant_temp_c'])
        self.state['coolant_temp_c'] = temp + (target - temp) * rate * dt

    def _refresh_signals(self):
        self.state['starter_control_voltage'] = self._starter_control_voltage()
        self.state['fuel_pressure_psi'] = self._fuel_pressure()
        self.state['charging_voltage'] = self._charging_voltage()
        temp_c = float(self.state['coolant_temp_c'])
        self.state['fan_commanded'] = self._fan_commanded(temp_c)
        self.state['fan_on'] = self._fan_on(temp_c)
