"""Intake and exhaust faults change idle, fuel trim, and sensor reports."""

import pytest

from mygarage.system_model import SystemModel


@pytest.fixture
def system():
    return SystemModel()


def running(system: SystemModel):
    result = system.start_attempt()
    assert result['started'] is True
    return result


class TestHealthyMixture:
    def test_steady_idle_and_honest_sensors(self, system):
        result = running(system)
        assert result['description'] == 'Engine cranks and starts, idle is steady'
        assert result['idle_rpm'] == 750
        data = system.get_context()
        assert data['fuel_trim_pct'] == 0
        assert 28 <= data['map_reported_kpa'] <= 42
        assert data['map_reported_kpa'] == data['manifold_pressure_kpa']
        assert 2.5 <= data['maf_reported_gps'] <= 5
        assert data['maf_reported_gps'] == data['maf_actual_gps']
        assert data['o2_switching'] is True
        assert data['o2_downstream_switching'] is False
        assert data['catalyst_efficiency'] > 0.9
        assert data['power_pct'] == 100


class TestIntakeFaults:
    def test_vacuum_leak_is_unmetered(self, system):
        system.inject_fault('intake_gasket', 'vacuum_leak')
        result = running(system)
        data = system.get_context()
        assert result['idle_rpm'] >= 1000
        assert data['fuel_trim_pct'] >= 20
        assert data['manifold_pressure_kpa'] >= 50
        assert 'gasket' in result['description']
        smoke = system.get_component('intake_gasket').get_diagnostic_readings('smoke_test', {})
        assert smoke['smoke_escapes'] is True

    def test_carboned_throttle_is_metered(self, system):
        system.inject_fault('throttle_body', 'carbon_buildup')
        result = running(system)
        data = system.get_context()
        assert result['idle_rpm'] >= 950
        assert abs(data['fuel_trim_pct']) < 5
        assert 'throttle' in result['description']

    def test_stuck_throttle_drops_idle(self, system):
        system.inject_fault('throttle_body', 'stuck_closed')
        result = running(system)
        assert result['idle_rpm'] < 550
        assert result['idle_quality'] == 'low'

    def test_clogged_filter_cuts_power_without_trim(self, system):
        system.inject_fault('air_filter', 'clogged_filter')
        result = running(system)
        data = system.get_context()
        assert result['idle_rpm'] == 750
        assert data['fuel_trim_pct'] == 0
        assert data['power_pct'] < 70
        assert 'filter' in result['description']

    def test_maf_under_and_over_reading(self, system):
        system.inject_fault('maf_sensor', 'under_reading')
        running(system)
        under = system.get_context()
        assert under['maf_reported_gps'] < 2.5
        assert under['maf_actual_gps'] > under['maf_reported_gps']
        assert under['fuel_trim_pct'] > 15

        system.reset()
        system.inject_fault('maf_sensor', 'over_reading')
        running(system)
        over = system.get_context()
        assert over['maf_reported_gps'] > over['maf_actual_gps']
        assert over['fuel_trim_pct'] < -10

    def test_map_reading_disagrees_with_the_vacuum_gauge(self, system):
        system.inject_fault('map_sensor', 'reads_high')
        running(system)
        data = system.get_context()
        assert data['map_reported_kpa'] >= 90
        assert data['manifold_pressure_kpa'] < 50
        assert data['fuel_trim_pct'] < 0

    def test_pcv_stuck_open_is_a_smaller_leak_than_the_gasket(self, system):
        system.inject_fault('pcv_valve', 'stuck_open')
        pcv = running(system)
        pcv_trim = system.state['fuel_trim_pct']
        system.reset()
        system.inject_fault('intake_gasket', 'vacuum_leak')
        gasket = running(system)
        assert 800 < pcv['idle_rpm'] < gasket['idle_rpm']
        assert 0 < pcv_trim < system.state['fuel_trim_pct']

        system.reset()
        assert system.get_component('pcv_valve').get_diagnostic_readings('rattle_test', {})['rattles'] is True
        system.inject_fault('pcv_valve', 'stuck_closed')
        closed = running(system)
        assert closed['description'] == 'Engine cranks and starts, idle is steady'
        assert system.get_component('pcv_valve').get_diagnostic_readings('rattle_test', {})['rattles'] is False


class TestExhaustFaults:
    def test_lazy_o2_can_still_idle_normally(self, system):
        system.inject_fault('o2_sensor_upstream', 'lazy_sensor')
        result = running(system)
        data = system.get_context()
        assert result['idle_quality'] == 'steady'
        assert data['o2_switching'] is False
        assert 'slow' in result['description']
        codes = system.get_component('o2_sensor_upstream').get_diagnostic_readings('obd', {})
        assert 'P0133' in codes['dtcs']

    def test_stuck_lean_o2_does_not_switch(self, system):
        system.inject_fault('o2_sensor_upstream', 'stuck_lean')
        running(system)
        data = system.get_context()
        assert data['o2_switching'] is False
        assert data['o2_upstream_v'] < 0.2
        assert data['fuel_trim_pct'] > 10

    def test_bad_catalyst_switches_downstream_and_a_dead_sensor_does_not(self, system):
        system.inject_fault('catalytic_converter', 'inefficient')
        result = running(system)
        data = system.get_context()
        assert result['idle_quality'] == 'steady'
        assert data['catalyst_efficiency'] < 0.5
        assert data['o2_downstream_switching'] is True
        assert data['backpressure_kpa'] < 8

        system.reset()
        system.inject_fault('o2_sensor_downstream', 'stuck_sensor')
        running(system)
        dead = system.get_context()
        assert dead['catalyst_efficiency'] > 0.9
        assert dead['o2_downstream_switching'] is False
        assert dead['o2_switching'] is True

    def test_clogged_catalyst_raises_backpressure(self, system):
        system.inject_fault('catalytic_converter', 'clogged')
        result = running(system)
        data = system.get_context()
        assert data['backpressure_kpa'] > 20
        assert data['power_pct'] < 60
        assert result['idle_rpm'] < 750

    def test_egr_stuck_open_roughs_the_idle_and_stuck_closed_does_not(self, system):
        system.inject_fault('egr_valve', 'stuck_open')
        open_valve = running(system)
        assert open_valve['misfire'] is True
        assert open_valve['idle_rpm'] < 700
        assert system.state['egr_flow_at_idle'] is True

        system.reset()
        system.inject_fault('egr_valve', 'stuck_closed')
        closed = running(system)
        valve = system.get_component('egr_valve')
        test = valve.get_diagnostic_readings('egr_test', {})
        assert closed['idle_quality'] == 'steady'
        assert closed['idle_rpm'] == 750
        assert test['flows_at_idle'] is False
        assert test['flow_when_commanded'] is False
        assert 'P0401' in valve.get_diagnostic_readings('obd', {})['dtcs']
