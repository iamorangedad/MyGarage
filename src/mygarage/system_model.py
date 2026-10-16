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
            'fuel_trim_pct': 0.0,
            'manifold_pressure_kpa': 100.0,
            'map_reported_kpa': 100.0,
            'maf_reported_gps': 0.0,
            'maf_actual_gps': 0.0,
            'o2_upstream_v': None,
            'o2_switching': False,
            'o2_downstream_v': None,
            'o2_downstream_switching': False,
            'catalyst_efficiency': None,
            'power_pct': 0.0,
            'backpressure_kpa': 0.0,
            'egr_flow_at_idle': False,
            'oil_pressure_psi': 0.0,
            'head_clamped': True,
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
        terminal_drop = self._terminal_drop()
        voltage_at_starter = voltage_under_load - ground_drop - terminal_drop
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

        flywheel = self.get_component('flywheel')
        if flywheel and not flywheel.parameters.get('teeth_ok', True):
            cranking_rpm = 0
            sound = 'grinding'
            success = False
            reason = 'Flywheel ring gear is damaged'

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
            'terminal_drop': round(terminal_drop, 2),
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
        if not result.get('success'):
            result['description'] = result.get('reason', 'Engine did not crank')
        elif not started:
            result['description'] = 'Engine cranks but does not start. ' + combustion['reason']
        else:
            mixture = self._mixture()
            if combustion['misfire']:
                result['description'] = combustion['reason']
            elif mixture['reasons']:
                self.state['engine_rpm'] = mixture['rpm']
                self.state['misfire'] = bool(mixture['misfire'])
                self.state['idle_quality'] = mixture['quality'] or combustion['idle_quality']
                result['description'] = 'Engine starts. ' + '; '.join(mixture['reasons'])
            else:
                result['description'] = combustion['reason']
        result['misfire'] = self.state['misfire']
        result['idle_quality'] = self.state['idle_quality']
        result['idle_rpm'] = self.state['engine_rpm']
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
        belt = self.get_component('timing_belt')
        if belt and belt.parameters.get('broken'):
            return self._no_start('Timing belt is broken, so the camshaft is not turning')
        cmp = self.get_component('cmp_sensor')
        if cmp and not cmp.parameters.get('signal_present', True):
            return self._no_start('No camshaft position signal, so the ECU will not fire the correct cylinder')
        fuel_pressure = self._available_fuel_pressure()
        if pump and fuel_pressure < 15:
            return self._no_start('Fuel pressure is too low to start')
        if coil and coil.parameters['spark_kv'] < 8:
            return self._no_start('Ignition coil is not producing spark')
        plug_wire = self.get_component('spark_plug_wire')
        if plug_wire and plug_wire.parameters.get('open_circuit'):
            return self._no_start('Spark plug wire is open')

        reasons = []
        if ckp and ckp.parameters.get('intermittent'):
            reasons.append('CKP signal drops out')
        if pump and fuel_pressure < 45:
            reasons.append('fuel pressure is marginal')
        if coil and coil.parameters['spark_kv'] < 20:
            reasons.append('spark is weak')
        if plug and (plug.parameters.get('fouled') or plug.parameters.get('gap_mm', 1.0) > 1.5):
            reasons.append('spark plug is fouled or the gap is excessive')
        if injector and injector.parameters.get('clogged'):
            reasons.append('a fuel injector is clogged')
        if injector and injector.parameters.get('leaking'):
            reasons.append('a fuel injector is leaking')
        distributor = self.get_component('distributor')
        if distributor and distributor.parameters.get('cracked'):
            reasons.append('distributor cap is tracking spark to ground')

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
            'fuel_trim_pct': self.state['fuel_trim_pct'],
            'manifold_pressure_kpa': self.state['manifold_pressure_kpa'],
            'map_reported_kpa': self.state['map_reported_kpa'],
            'maf_reported_gps': self.state['maf_reported_gps'],
            'maf_actual_gps': self.state['maf_actual_gps'],
            'o2_upstream_v': self.state['o2_upstream_v'],
            'o2_switching': self.state['o2_switching'],
            'o2_downstream_v': self.state['o2_downstream_v'],
            'o2_downstream_switching': self.state['o2_downstream_switching'],
            'catalyst_efficiency': self.state['catalyst_efficiency'],
            'power_pct': self.state['power_pct'],
            'backpressure_kpa': self.state['backpressure_kpa'],
            'egr_flow_at_idle': self.state['egr_flow_at_idle'],
            'oil_pressure_psi': self.state['oil_pressure_psi'],
            'head_clamped': self.state.get('head_clamped', True),
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

    def _terminal_drop(self) -> float:
        """Voltage lost in the battery posts while the starter is drawing current."""
        drop = 0.0
        for component_id in ('battery_pos_terminal', 'battery_neg_terminal'):
            terminal = self.get_component(component_id)
            if terminal:
                drop += float(terminal.parameters.get('resistance_ohm', 0.0)) * 150.0
        return drop

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

    def _available_fuel_pressure(self) -> float:
        """Rail pressure the pump can actually deliver through the filter and regulator."""
        pump = self.get_component('fuel_pump')
        pressure = float(pump.parameters['pressure_psi']) if pump else 0.0
        fuel_filter = self.get_component('fuel_filter')
        if fuel_filter and fuel_filter.parameters.get('clogged'):
            pressure = min(pressure, float(fuel_filter.parameters.get('restricted_pressure_psi', 12.0)))
        regulator = self.get_component('fuel_pressure_regulator')
        mode = regulator.parameters.get('mode', 'normal') if regulator else 'normal'
        if mode == 'low':
            pressure = min(pressure, 20.0)
        elif mode == 'high':
            pressure = max(pressure, 78.0)
        return pressure

    def _fuel_pressure(self) -> float:
        pump = self.get_component('fuel_pump')
        ignition = self.get_component('ignition_switch')
        if not pump:
            return 0.0
        powered = self.state['ignition_on'] or self.state['engine_cranking'] or self.state['engine_running']
        run_closed = True if not ignition else bool(ignition.parameters['run_circuit_closed'])
        if powered and run_closed:
            return self._available_fuel_pressure()
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
        hose = self.get_component('coolant_hose')
        if hose and hose.parameters.get('burst'):
            level = min(level, 0.2)
        heater = self.get_component('heater_core')
        if heater and heater.parameters.get('leaking'):
            level = min(level, 0.35)
        if self._head_unsealed():
            level = min(level, 0.45)
        reservoir = self.get_component('coolant_reservoir')
        if reservoir and reservoir.parameters.get('cracked'):
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
        relay = self.get_component('fan_relay')
        if relay and not relay.parameters.get('contacts_ok', True):
            return False
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
            target = 118.0
        elif stuck_open and not clogged and self._coolant_level() >= 0.5:
            target = 60.0
        elif clogged or self._coolant_level() < 0.5:
            target = 112.0
        elif not self._fan_capable(100.0):
            target = 110.0
        else:
            target = 92.0
        cap = self.get_component('radiator_cap')
        if cap and not cap.parameters.get('holds_pressure', True) and target < 100.0:
            target = 105.0
        if self._head_unsealed():
            return 116.0
        return target

    def _head_unsealed(self) -> bool:
        """A breached gasket or a head nut that is not seated lets combustion leak."""
        gasket = self.get_component('head_gasket')
        breached = bool(gasket and gasket.parameters.get('breached'))
        return breached or not bool(self.state.get('head_clamped', True))

    def _oil_pressure(self) -> float:
        """Gallery pressure while the engine is running. Zero with the key off."""
        if not self.state['engine_running']:
            return 0.0
        pump = self.get_component('oil_pump')
        if pump and not pump.parameters.get('pumping', True):
            return 0.0
        pan = self.get_component('oil_pan')
        if pan and float(pan.parameters.get('level', 1.0)) < 0.3:
            return 5.0
        return 40.0

    def _approach_temp(self, target: float, rate: float, dt: float):
        temp = float(self.state['coolant_temp_c'])
        self.state['coolant_temp_c'] = temp + (target - temp) * rate * dt

    def _mixture(self) -> Dict[str, Any]:
        """Idle air, fuel trim, and what the intake and exhaust sensors report.

        A healthy running engine sits at 750 rpm, 35 kPa, about 3.5 g/s, and
        zero fuel trim. Unmetered leaks move trim positive. A lying MAF or MAP
        moves trim without the same vacuum-gauge reading.
        """
        if not self.state['engine_running']:
            reported_map = 100.0
            map_sensor = self.get_component('map_sensor')
            if map_sensor and map_sensor.parameters.get('mode') == 'open':
                reported_map = None
            return {
                'rpm': 0,
                'quality': None,
                'misfire': False,
                'reasons': [],
                'fuel_trim_pct': 0.0,
                'manifold_pressure_kpa': 100.0,
                'map_reported_kpa': reported_map,
                'maf_reported_gps': 0.0,
                'maf_actual_gps': 0.0,
                'o2_upstream_v': None,
                'o2_switching': False,
                'o2_downstream_v': None,
                'o2_downstream_switching': False,
                'catalyst_efficiency': None,
                'power_pct': 0.0,
                'backpressure_kpa': 0.0,
                'egr_flow_at_idle': False,
            }

        actual_map = 35.0
        actual_maf = 3.5
        trim = 0.0
        rpm_add = 0
        quality = None
        misfire = False
        reasons = []
        power = 100.0

        air_filter = self.get_component('air_filter')
        if air_filter and air_filter.parameters['restriction'] > 0.5:
            actual_maf -= 0.7
            power -= 45
            reasons.append('air filter is restricting airflow')

        throttle = self.get_component('throttle_body')
        idle_air = throttle.parameters['idle_air'] if throttle else 'normal'
        if idle_air == 'high':
            rpm_add += 260
            actual_map += 8
            actual_maf += 0.8
            quality = 'high'
            reasons.append('throttle plate is open at idle, and that air is still metered')
        elif idle_air == 'low':
            rpm_add -= 280
            actual_maf -= 0.7
            quality = 'low'
            reasons.append('throttle plate is stuck and idle air is too low')

        gasket = self.get_component('intake_gasket')
        pcv = self.get_component('pcv_valve')
        if gasket and gasket.parameters['leak']:
            actual_map += 22
            rpm_add += 320
            trim += 28
            quality = 'high'
            reasons.append('intake gasket is leaking unmetered air')
        if pcv and pcv.parameters['stuck_open']:
            actual_map += 10
            rpm_add += 140
            trim += 12
            quality = quality or 'high'
            reasons.append('PCV valve is stuck open')

        vacuum = self.get_component('vacuum_hose')
        if vacuum and vacuum.parameters.get('leak'):
            actual_map += 16
            rpm_add += 220
            trim += 18
            quality = 'high'
            reasons.append('vacuum hose is leaking unmetered air')

        iac = self.get_component('iac_valve')
        iac_air = iac.parameters.get('idle_air', 'normal') if iac else 'normal'
        if iac_air == 'high':
            rpm_add += 200
            quality = quality or 'high'
            reasons.append('IAC valve is open at idle, and that air is still metered')
        elif iac_air == 'low':
            rpm_add -= 220
            quality = 'low'
            reasons.append('IAC valve is stuck closed')

        purge = self.get_component('purge_valve')
        if purge and purge.parameters.get('stuck_open'):
            rpm_add += 90
            trim += 10
            quality = quality or 'high'
            reasons.append('purge valve is stuck open')

        regulator = self.get_component('fuel_pressure_regulator')
        if regulator and regulator.parameters.get('mode') == 'high':
            trim -= 15
            quality = quality or 'rough'
            reasons.append('fuel pressure regulator is stuck high')

        egr = self.get_component('egr_valve')
        egr_flow = bool(egr and egr.parameters['stuck_open'])
        if egr_flow:
            actual_map += 12
            rpm_add -= 140
            trim += 8
            misfire = True
            quality = 'rough'
            reasons.append('EGR valve is stuck open at idle')

        maf = self.get_component('maf_sensor')
        scale = float(maf.parameters['scale']) if maf else 1.0
        if scale < 0.8:
            trim += 25
            quality = 'rough'
            reasons.append('MAF reports less air than the engine is using')
        elif scale > 1.2:
            trim -= 20
            quality = 'rough'
            reasons.append('MAF reports more air than the engine is using')

        map_sensor = self.get_component('map_sensor')
        mode = map_sensor.parameters['mode'] if map_sensor else 'normal'
        if mode == 'open':
            reported_map = None
            quality = 'rough'
            reasons.append('MAP sensor circuit is open')
        elif mode == 'high':
            reported_map = 95.0
            trim -= 22
            quality = 'rough'
            reasons.append('MAP sensor reads high at idle')
        else:
            reported_map = round(actual_map, 1)

        o2 = self.get_component('o2_sensor_upstream')
        response = o2.parameters['response'] if o2 else 'normal'
        if response == 'stuck_lean':
            o2_voltage = 0.05
            o2_switching = False
            trim += 18
            reasons.append('upstream O2 sensor is stuck lean')
        elif response == 'lazy':
            o2_voltage = 0.45
            o2_switching = False
            reasons.append('upstream O2 sensor is slow to respond')
        else:
            o2_voltage = 0.45
            o2_switching = True

        catalyst = self.get_component('catalytic_converter')
        efficiency = float(catalyst.parameters['efficiency']) if catalyst else 0.96
        clogged = bool(catalyst and catalyst.parameters['clogged'])
        backpressure = 3.0
        if clogged:
            backpressure = 32.0
            power -= 55
            rpm_add -= 80
            reasons.append('catalytic converter is restricted')
        inefficient = efficiency < 0.6
        if inefficient:
            reasons.append('catalytic converter is not storing oxygen')

        muffler = self.get_component('muffler')
        if muffler and muffler.parameters.get('clogged'):
            backpressure = max(backpressure, 24.0)
            power -= 35
            rpm_add -= 50
            reasons.append('muffler is restricted')

        downstream = self.get_component('o2_sensor_downstream')
        downstream_stuck = bool(downstream and downstream.parameters['stuck'])
        if inefficient and not downstream_stuck:
            downstream_voltage = o2_voltage
            downstream_switching = o2_switching
        elif downstream_stuck:
            downstream_voltage = 0.45
            downstream_switching = False
            reasons.append('downstream O2 sensor is not responding')
        else:
            downstream_voltage = 0.72
            downstream_switching = False

        rpm = min(1300, max(450, 750 + rpm_add))
        trim = min(40.0, max(-35.0, trim))
        return {
            'rpm': rpm,
            'quality': quality,
            'misfire': misfire,
            'reasons': reasons,
            'fuel_trim_pct': round(trim, 1),
            'manifold_pressure_kpa': round(actual_map, 1),
            'map_reported_kpa': None if reported_map is None else round(float(reported_map), 1),
            'maf_reported_gps': round(actual_maf * scale, 2),
            'maf_actual_gps': round(actual_maf, 2),
            'o2_upstream_v': o2_voltage,
            'o2_switching': o2_switching,
            'o2_downstream_v': downstream_voltage,
            'o2_downstream_switching': downstream_switching,
            'catalyst_efficiency': round(efficiency, 2),
            'power_pct': max(0.0, power),
            'backpressure_kpa': backpressure,
            'egr_flow_at_idle': egr_flow,
        }

    def _refresh_signals(self):
        self.state['starter_control_voltage'] = self._starter_control_voltage()
        self.state['fuel_pressure_psi'] = self._fuel_pressure()
        self.state['charging_voltage'] = self._charging_voltage()
        temp_c = float(self.state['coolant_temp_c'])
        self.state['fan_commanded'] = self._fan_commanded(temp_c)
        self.state['fan_on'] = self._fan_on(temp_c)
        self.state['oil_pressure_psi'] = self._oil_pressure()
        mixture = self._mixture()
        for key in (
            'fuel_trim_pct',
            'manifold_pressure_kpa',
            'map_reported_kpa',
            'maf_reported_gps',
            'maf_actual_gps',
            'o2_upstream_v',
            'o2_switching',
            'o2_downstream_v',
            'o2_downstream_switching',
            'catalyst_efficiency',
            'power_pct',
            'backpressure_kpa',
            'egr_flow_at_idle',
        ):
            self.state[key] = mixture[key]
