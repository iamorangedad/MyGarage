"""Tests for vehicle components"""

import pytest
from mygarage.components import Battery, StarterMotor


def test_battery_initialization():
    """Test battery component initializes correctly"""
    battery = Battery()
    assert battery.component_id == "battery"
    assert battery.name == "12V Battery"
    assert battery.nominal_voltage == 12.6


def test_battery_mjcf():
    """Test battery generates valid MJCF"""
    battery = Battery()
    mjcf = battery.get_mjcf()
    assert isinstance(mjcf, str)
    assert "battery" in mjcf
    assert "geom" in mjcf


def test_battery_apply_fault_F001():
    """Test applying dead battery fault"""
    battery = Battery()
    battery.apply_fault("F001", {"voltage": 11.5, "max_current": 50})
    
    assert battery.state.fault_id == "F001"
    assert battery.state.custom_state["voltage"] == 11.5
    assert battery.state.custom_state["max_current"] == 50


def test_battery_resting_voltage_normal():
    """Test resting voltage reading with no fault"""
    battery = Battery()
    result = battery.get_reading("multimeter", "resting_voltage", {})
    
    assert result["value"] == 12.6
    assert result["unit"] == "V"


def test_battery_resting_voltage_with_fault():
    """Test resting voltage with dead battery fault"""
    battery = Battery()
    battery.apply_fault("F001", {"voltage": 11.5, "max_current": 50})
    
    result = battery.get_reading("multimeter", "resting_voltage", {})
    assert result["value"] == 11.5


def test_battery_loaded_voltage():
    """Test loaded voltage calculation"""
    battery = Battery()
    result = battery.get_reading("multimeter", "loaded_voltage", {"load_current": 200})
    
    assert "value" in result
    assert result["value"] < battery.nominal_voltage


def test_battery_visual_inspection():
    """Test visual inspection"""
    battery = Battery()
    battery.apply_fault("F003", {"resistance": 0.5, "corrosion_visible": True})
    
    result = battery.get_reading("visual", "general", {})
    assert "observations" in result
    assert len(result["observations"]) > 0


def test_battery_reset():
    """Test battery reset clears fault"""
    battery = Battery()
    battery.apply_fault("F001", {"voltage": 11.5})
    battery.reset()
    
    assert battery.state.fault_id is None
    assert len(battery.state.custom_state) == 0


def test_starter_initialization():
    """Test starter motor initializes correctly"""
    starter = StarterMotor()
    assert starter.component_id == "starter"
    assert starter.name == "Starter Motor"


def test_starter_mjcf():
    """Test starter generates valid MJCF"""
    starter = StarterMotor()
    mjcf = starter.get_mjcf()
    assert isinstance(mjcf, str)
    assert "starter_motor" in mjcf
    assert "crankshaft" in mjcf


def test_starter_apply_fault_F005():
    """Test applying solenoid fault"""
    starter = StarterMotor()
    starter.apply_fault("F005", {"solenoid_failed": True, "click_sound": True})
    
    assert starter.state.fault_id == "F005"
    assert starter.state.custom_state["solenoid_failed"] is True


def test_starter_crank_test_normal():
    """Test crank test with normal starter"""
    starter = StarterMotor()
    result = starter.get_reading("crank_test", "attempt_start", {"battery_voltage": 12.6})
    
    assert result["result"] == "normal_crank"
    assert result["cranking_speed"] == 200


def test_starter_crank_test_solenoid_fault():
    """Test crank test with failed solenoid"""
    starter = StarterMotor()
    starter.apply_fault("F005", {"solenoid_failed": True})
    
    result = starter.get_reading("crank_test", "attempt_start", {"battery_voltage": 12.6})
    assert result["result"] == "click_only"
    assert result["cranking_speed"] == 0


def test_starter_torque_output_normal():
    """Test starter torque output"""
    starter = StarterMotor()
    torque = starter.get_torque_output(12.0)
    
    assert torque > 0
    assert torque == pytest.approx(starter.nominal_torque, rel=0.1)


def test_starter_torque_output_with_fault():
    """Test starter torque with worn motor fault"""
    starter = StarterMotor()
    starter.apply_fault("F006", {"torque_factor": 0.5})
    
    torque = starter.get_torque_output(12.0)
    assert torque < starter.nominal_torque
    assert torque == pytest.approx(starter.nominal_torque * 0.5, rel=0.1)
