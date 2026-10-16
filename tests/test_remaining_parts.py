"""Every catalog row is a component, and the coupled faults change the car."""

import re
from pathlib import Path

import pytest

from mygarage.components.remaining import remaining_classes
from mygarage.fault_engine import FaultEngine
from mygarage.system_model import SystemModel

CATALOG = Path(__file__).resolve().parents[1] / 'docs' / 'parts_catalog.md'


def warm(system: SystemModel, seconds: int = 40):
    for _ in range(seconds):
        system.step(1.0)


@pytest.fixture
def system():
    return SystemModel()


def catalog_ids():
    text = CATALOG.read_text(encoding='utf-8')
    return re.findall(r'\| `([a-z0-9_]+)` \|', text)


class TestCatalogCoverage:
    def test_every_markdown_part_is_installed(self, system):
        ids = catalog_ids()
        assert len(ids) == len(set(ids))
        missing = [part_id for part_id in ids if part_id not in system.components]
        assert missing == []

    def test_every_remaining_part_has_a_fault_and_a_catalog_entry(self, system):
        engine = FaultEngine()
        catalog = {(fault.component_id, fault.fault_name) for fault in engine.fault_catalog}
        for cls in remaining_classes():
            part = system.get_component(cls().component_id)
            assert part is not None
            assert part.fault_modes
            fault = part.fault_modes[0]
            assert (part.component_id, fault.name) in catalog
            before = part.get_diagnostic_readings('visual', {})
            system.reset()
            assert system.inject_fault(part.component_id, fault.name)
            after = system.get_component(part.component_id).get_diagnostic_readings('visual', {})
            assert after != before


class TestCoupledFaults:
    def test_broken_timing_belt_cranks_without_starting(self, system):
        system.inject_fault('timing_belt', 'broken_belt')
        result = system.start_attempt()
        assert result['success'] is True
        assert result['started'] is False
        assert 'Timing belt' in result['description']

    def test_cmp_without_signal_will_not_start(self, system):
        system.inject_fault('cmp_sensor', 'no_signal')
        result = system.start_attempt()
        assert result['started'] is False
        assert 'camshaft' in result['description']

    def test_open_plug_wire_will_not_start(self, system):
        system.inject_fault('spark_plug_wire', 'open_wire')
        result = system.start_attempt()
        assert result['success'] is True
        assert result['started'] is False
        assert 'Spark plug wire' in result['description']

    def test_clogged_fuel_filter_pressure_is_too_low_to_start(self, system):
        system.inject_fault('fuel_filter', 'clogged_filter')
        result = system.start_attempt()
        assert result['started'] is False
        assert 'Fuel pressure' in result['description']
        system.set_ignition('run')
        assert system.state['fuel_pressure_psi'] < 15

    def test_low_regulator_starts_with_marginal_pressure(self, system):
        system.inject_fault('fuel_pressure_regulator', 'stuck_low')
        result = system.start_attempt()
        assert result['started'] is True
        assert system.state['fuel_pressure_psi'] == 20
        assert 'fuel pressure' in result['description']

    def test_vacuum_hose_raises_idle_and_trim(self, system):
        healthy = system.start_attempt()
        system.reset()
        system.inject_fault('vacuum_hose', 'split_hose')
        leaking = system.start_attempt()
        assert healthy['idle_rpm'] == 750
        assert leaking['idle_rpm'] > healthy['idle_rpm']
        assert system.state['fuel_trim_pct'] > 10

    def test_stuck_closed_iac_drops_idle(self, system):
        system.inject_fault('iac_valve', 'stuck_closed')
        result = system.start_attempt()
        assert result['started'] is True
        assert result['idle_rpm'] < 600
        assert 'IAC' in result['description']

    def test_clogged_muffler_raises_backpressure(self, system):
        system.inject_fault('muffler', 'clogged_muffler')
        system.start_attempt()
        assert system.state['backpressure_kpa'] >= 24
        assert system.state['engine_rpm'] < 750

    def test_breached_head_gasket_runs_hot(self, system):
        system.inject_fault('head_gasket', 'breached_gasket')
        system.start_attempt()
        warm(system)
        assert system.state['coolant_temp_c'] > 105

    def test_open_fan_relay_leaves_the_fan_off(self, system):
        system.inject_fault('fan_relay', 'failed_open')
        system.start_attempt()
        warm(system)
        assert system.state['fan_commanded'] is True
        assert system.state['fan_on'] is False
        assert system.state['coolant_temp_c'] > 100

    def test_corroded_positive_terminal_slows_the_crank(self, system):
        healthy = system.attempt_crank()
        system.reset()
        system.inject_fault('battery_pos_terminal', 'corroded_terminal')
        corroded = system.attempt_crank()
        assert healthy['sound'] == 'normal_crank'
        assert corroded['sound'] == 'slow_crank'
        assert corroded['terminal_drop'] > healthy['terminal_drop']
        assert 'ground strap' not in corroded['reason']

    def test_damaged_flywheel_grinds(self, system):
        system.inject_fault('flywheel', 'damaged_ring_gear')
        result = system.attempt_crank()
        assert result['success'] is False
        assert result['sound'] == 'grinding'
        assert 'Flywheel' in result['reason']

    def test_failed_oil_pump_has_no_pressure_and_a_low_pan_is_marginal(self, system):
        system.start_attempt()
        assert system.state['oil_pressure_psi'] == 40
        system.reset()
        system.inject_fault('oil_pump', 'failed_pump')
        system.start_attempt()
        assert system.state['oil_pressure_psi'] == 0
        system.reset()
        system.inject_fault('oil_pan', 'leaking_pan')
        system.start_attempt()
        assert system.state['oil_pressure_psi'] == 5
