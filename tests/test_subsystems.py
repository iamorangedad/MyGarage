"""Behavior of the starting, charging, combustion, cooling, and chassis parts."""

import pytest

from mygarage.fault_engine import FaultEngine
from mygarage.simulation import MuJoCoSimulation
from mygarage.system_model import SystemModel


def warm(system: SystemModel, seconds: int = 40):
    """Run the thermal model long enough to approach its equilibrium."""
    for _ in range(seconds):
        system.step(1.0)


@pytest.fixture
def system():
    return SystemModel()


class TestCatalogWiring:
    def test_every_catalog_fault_injects(self, system):
        engine = FaultEngine()
        seen = set()
        assert len(engine.fault_catalog) >= 48
        for fault in engine.fault_catalog:
            assert fault.fault_id not in seen
            seen.add(fault.fault_id)
            system.reset()
            assert system.inject_fault(fault.component_id, fault.fault_name), fault.fault_id

    def test_builtin_parts_cover_the_five_batches(self, system):
        expected = {
            'ground_strap', 'ignition_switch', 'starter_relay', 'starter_fuse', 'starter_solenoid',
            'alternator', 'serpentine_belt', 'voltage_regulator',
            'spark_plug', 'ignition_coil', 'fuel_injector', 'fuel_pump', 'ckp_sensor',
            'thermostat', 'water_pump', 'cooling_fan', 'ect_sensor', 'radiator',
            'brake_pads', 'brake_disc', 'wheel_speed_sensor', 'shock_absorber',
        }
        assert expected <= set(system.components)


class TestStartingCircuit:
    def test_healthy_start(self, system):
        result = system.start_attempt()
        assert result['success'] is True
        assert result['started'] is True
        assert result['idle_quality'] == 'steady'
        assert system.state['engine_running'] is True
        assert system.state['engine_cranking'] is False

    def test_blown_fuse_has_no_click(self, system):
        system.inject_fault('starter_fuse', 'blown_fuse')
        result = system.attempt_crank()
        assert result['success'] is False
        assert result['sound'] == 'none'
        fuse = system.get_component('starter_fuse').get_diagnostic_readings('multimeter', system.get_context())
        assert fuse['continuity_ohm'] is None
        assert fuse['voltage_out'] == 0.0

    def test_worn_start_contact_leaves_run_circuit(self, system):
        system.inject_fault('ignition_switch', 'worn_start_contact')
        result = system.attempt_crank()
        assert result['sound'] == 'none'
        switch = system.get_component('ignition_switch')
        reading = switch.get_diagnostic_readings('multimeter', system.get_context())
        assert reading['start_terminal_v'] == 0.0

    def test_open_run_circuit_cranks_without_starting(self, system):
        system.inject_fault('ignition_switch', 'open_run_circuit')
        result = system.start_attempt()
        assert result['success'] is True
        assert result['started'] is False
        assert 'Run circuit' in result['description']

    def test_open_relay_has_input_and_no_output(self, system):
        system.inject_fault('starter_relay', 'open_coil')
        system.attempt_crank()
        reading = system.get_component('starter_relay').get_diagnostic_readings(
            'multimeter', system.get_context()
        )
        assert reading['control_input_v'] > 10
        assert reading['output_v'] == 0.0

    def test_burned_relay_clicks(self, system):
        system.inject_fault('starter_relay', 'burned_contacts')
        result = system.attempt_crank()
        assert result['sound'] == 'relay_click'
        assert result['success'] is False

    def test_solenoid_distinguishes_open_coil_from_burned_contacts(self, system):
        system.inject_fault('starter_solenoid', 'open_pull_in_coil')
        open_coil = system.attempt_crank()
        system.reset()
        system.inject_fault('starter_solenoid', 'burned_contacts')
        burned = system.attempt_crank()
        assert open_coil['sound'] == 'none'
        assert burned['sound'] == 'single_click'

    def test_loose_ground_drops_more_voltage_than_corrosion(self, system):
        system.inject_fault('ground_strap', 'corroded_ground')
        system.attempt_crank()
        corroded = system.get_component('ground_strap').get_diagnostic_readings(
            'voltage_drop', system.get_context()
        )
        assert corroded['passed'] is False
        assert corroded['voltage_drop'] > 0.2

        system.reset()
        system.inject_fault('ground_strap', 'loose_ground')
        loose = system.attempt_crank()
        assert loose['success'] is False
        assert 'ground' in loose['description'].lower()


class TestCharging:
    def test_healthy_charge_voltage(self, system):
        system.start_attempt()
        assert 13.8 <= system.state['charging_voltage'] <= 14.8

    def test_broken_belt_does_not_charge(self, system):
        system.inject_fault('serpentine_belt', 'broken_belt')
        result = system.start_attempt()
        assert result['started'] is True
        assert system.state['charging_voltage'] < 13.0

    def test_glazed_belt_is_marginal(self, system):
        system.inject_fault('serpentine_belt', 'glazed_belt')
        system.start_attempt()
        assert 13.0 <= system.state['charging_voltage'] <= 13.8

    def test_regulator_failed_high_and_low(self, system):
        system.inject_fault('voltage_regulator', 'failed_high')
        system.start_attempt()
        assert system.state['charging_voltage'] > 15.0

        system.reset()
        system.inject_fault('voltage_regulator', 'failed_low')
        system.start_attempt()
        assert system.state['charging_voltage'] < 13.0

    def test_failed_diodes_show_ripple(self, system):
        system.inject_fault('alternator', 'failed_diodes')
        system.start_attempt()
        reading = system.get_component('alternator').get_diagnostic_readings(
            'multimeter', system.get_context()
        )
        assert reading['voltage'] < 13.0
        assert reading['ripple_v'] > 1.0


class TestCombustion:
    def test_dead_pump_cranks_without_starting(self, system):
        system.inject_fault('fuel_pump', 'dead_pump')
        result = system.start_attempt()
        assert result['success'] is True
        assert result['started'] is False
        assert 'fuel' in result['description'].lower()

    def test_weak_pump_starts_rough_with_low_pressure(self, system):
        system.inject_fault('fuel_pump', 'weak_pump')
        result = system.start_attempt()
        assert result['started'] is True
        assert result['misfire'] is True
        pressure = system.get_component('fuel_pump').get_diagnostic_readings(
            'fuel_pressure', system.get_context()
        )
        assert pressure['pressure_psi'] < 45

    def test_open_coil_and_missing_ckp_are_no_spark_no_start(self, system):
        system.inject_fault('ignition_coil', 'open_primary')
        coil = system.start_attempt()
        assert coil['started'] is False
        assert 'spark' in coil['description'].lower()

        system.reset()
        system.inject_fault('ckp_sensor', 'no_signal')
        ckp = system.start_attempt()
        assert ckp['success'] is True
        assert ckp['started'] is False
        assert 'crankshaft' in ckp['description'].lower()

    def test_fouled_plug_and_clogged_injector_misfire_with_fuel_pressure(self, system):
        system.inject_fault('spark_plug', 'fouled_plug')
        plug = system.start_attempt()
        assert plug['started'] is True and plug['misfire'] is True

        system.reset()
        system.inject_fault('fuel_injector', 'clogged_injector')
        injector = system.start_attempt()
        assert injector['misfire'] is True
        assert system.state['fuel_pressure_psi'] >= 50


class TestCooling:
    def test_healthy_engine_reaches_operating_temperature(self, system):
        system.start_attempt()
        warm(system)
        assert 85 <= system.state['coolant_temp_c'] <= 98
        assert system.state['fan_commanded'] is True

    def test_thermostat_stuck_closed_overheats_and_stuck_open_stays_cold(self, system):
        system.inject_fault('thermostat', 'stuck_closed')
        system.start_attempt()
        warm(system)
        assert system.state['coolant_temp_c'] > 105

        system.reset()
        system.inject_fault('thermostat', 'stuck_open')
        system.start_attempt()
        warm(system)
        assert system.state['coolant_temp_c'] < 75

    def test_seized_fan_is_commanded_but_not_powered(self, system):
        system.inject_fault('cooling_fan', 'seized_motor')
        system.start_attempt()
        warm(system)
        assert system.state['coolant_temp_c'] > 100
        assert system.state['fan_commanded'] is True
        assert system.state['fan_on'] is False
        reading = system.get_component('cooling_fan').get_diagnostic_readings(
            'multimeter', system.get_context()
        )
        assert reading['fan_commanded'] is True
        assert reading['motor_voltage'] == 0.0

    def test_ect_biased_cold_disagrees_with_actual_temperature(self, system):
        system.inject_fault('ect_sensor', 'biased_cold')
        system.start_attempt()
        warm(system)
        reading = system.get_component('ect_sensor').get_diagnostic_readings(
            'temperature', system.get_context()
        )
        assert reading['actual_c'] > 100
        assert reading['indicated_c'] < 80

    def test_leaking_radiator_lowers_coolant_level(self, system):
        system.inject_fault('radiator', 'leaking_radiator')
        system.start_attempt()
        warm(system)
        reading = system.get_component('radiator').get_diagnostic_readings(
            'temperature', system.get_context()
        )
        assert reading['coolant_level'] < 0.5
        assert reading['coolant_temp_c'] > 100


class TestChassis:
    def test_worn_pads_and_warped_disc(self, system):
        system.inject_fault('brake_pads', 'worn_pads')
        pads = system.get_component('brake_pads').get_diagnostic_readings('visual', {})
        assert pads['thickness_mm'] < 3
        assert pads['passed'] is False

        system.inject_fault('brake_disc', 'warped_disc')
        disc = system.get_component('brake_disc').get_diagnostic_readings('visual', {})
        assert disc['runout_mm'] > 0.08
        assert disc['passed'] is False

    def test_open_wheel_speed_sensor_sets_a_code(self, system):
        system.inject_fault('wheel_speed_sensor', 'open_sensor')
        sensor = system.get_component('wheel_speed_sensor')
        ohms = sensor.get_diagnostic_readings('multimeter', {})
        codes = sensor.get_diagnostic_readings('obd', {})
        assert ohms['resistance_ohm'] is None
        assert 'C0035' in codes['dtcs']

    def test_leaking_shock_fails_the_bounce_test(self, system):
        system.inject_fault('shock_absorber', 'leaking_shock')
        shock = system.get_component('shock_absorber')
        bounce = shock.get_diagnostic_readings('bounce_test', {})
        visual = shock.get_diagnostic_readings('visual', {})
        assert bounce['passed'] is False
        assert bounce['oscillations'] > 2
        assert any('oil' in line.lower() for line in visual['findings'])


class TestScene:
    def test_scene_loads_new_parts_headless(self):
        sim = MuJoCoSimulation(headless=True)
        assert sim.is_loaded()
        for body_name in ('ground_strap_body', 'alternator_body', 'radiator_body', 'wheel_corner'):
            assert sim.model.body(body_name).id >= 0
        sim.step(10)
        sim.close()
