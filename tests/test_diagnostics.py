"""Tests for diagnostic tools"""

import pytest
from mygarage.diagnostics import Multimeter, VisualInspection, CrankTest
from mygarage.components import Battery, StarterMotor
from mygarage.game import Vehicle


@pytest.fixture
def vehicle():
    """Create test vehicle"""
    v = Vehicle()
    v.add_component(Battery())
    v.add_component(StarterMotor())
    return v


def test_multimeter_resting_voltage(vehicle):
    """Test multimeter resting voltage measurement"""
    multimeter = Multimeter()
    result = multimeter.measure(vehicle, "battery", "resting_voltage")
    
    assert result.tool_name == "Multimeter"
    assert result.target == "battery"
    assert "value" in result.data


def test_multimeter_loaded_voltage(vehicle):
    """Test multimeter loaded voltage measurement"""
    multimeter = Multimeter()
    result = multimeter.measure(
        vehicle, 
        "battery", 
        "loaded_voltage",
        {"load_current": 200}
    )
    
    assert "value" in result.data
    assert result.data["value"] < 12.6


def test_multimeter_unknown_component(vehicle):
    """Test multimeter with unknown component"""
    multimeter = Multimeter()
    result = multimeter.measure(vehicle, "unknown", "voltage")
    
    assert "error" in result.data


def test_visual_inspection_battery(vehicle):
    """Test visual inspection of battery"""
    visual = VisualInspection()
    result = visual.measure(vehicle, "battery", "general")
    
    assert result.tool_name == "Visual Inspection"
    assert "observations" in result.data


def test_visual_inspection_with_fault(vehicle):
    """Test visual inspection with corroded terminal"""
    vehicle.components["battery"].apply_fault(
        "F003", 
        {"resistance": 0.5, "corrosion_visible": True}
    )
    
    visual = VisualInspection()
    result = visual.measure(vehicle, "battery", "general")
    
    assert "observations" in result.data
    observations_text = " ".join(result.data["observations"])
    assert "corrosion" in observations_text.lower()


def test_crank_test_normal(vehicle):
    """Test crank test with normal system"""
    crank_test = CrankTest()
    result = crank_test.measure(vehicle, "starter", "attempt_start")
    
    assert result.tool_name == "Crank Test"
    assert "result" in result.data
    assert result.data["result"] == "normal_crank"


def test_crank_test_with_solenoid_fault(vehicle):
    """Test crank test with failed solenoid"""
    vehicle.components["starter"].apply_fault("F005", {"solenoid_failed": True})
    
    crank_test = CrankTest()
    result = crank_test.measure(vehicle, "starter", "attempt_start")
    
    assert result.data["result"] == "click_only"
    assert result.data["cranking_speed"] == 0


def test_crank_test_with_dead_battery(vehicle):
    """Test crank test with dead battery"""
    vehicle.components["battery"].apply_fault("F001", {"voltage": 9.5})
    
    crank_test = CrankTest()
    result = crank_test.measure(vehicle, "starter", "attempt_start")
    
    assert result.data["cranking_speed"] < 200
