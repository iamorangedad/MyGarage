"""Test suite for component system."""

import pytest
from mygarage.components import Battery, StarterMotor


class TestBattery:
    """Tests for Battery component."""
    
    def test_battery_initialization(self):
        """Test battery is initialized with correct parameters."""
        battery = Battery()
        assert battery.component_id == "battery_12v"
        assert battery.name == "12V Battery"
        assert battery.parameters['voltage_resting'] == 12.6
        assert battery.active_fault is None
    
    def test_battery_fault_injection(self):
        """Test fault injection into battery."""
        battery = Battery()
        
        # Inject discharged battery fault
        result = battery.inject_fault("discharged_battery")
        assert result is True
        assert battery.active_fault is not None
        assert battery.active_fault.name == "discharged_battery"
        assert battery.parameters['voltage_resting'] == 11.5
    
    def test_battery_clear_fault(self):
        """Test clearing faults from battery."""
        battery = Battery()
        battery.inject_fault("discharged_battery")
        
        battery.clear_fault()
        assert battery.active_fault is None
        assert battery.parameters['voltage_resting'] == 12.6  # Back to nominal
    
    def test_battery_visual_inspection(self):
        """Test visual inspection of battery."""
        battery = Battery()
        
        # Healthy battery
        readings = battery.get_diagnostic_readings('visual', {})
        assert 'findings' in readings
        assert isinstance(readings['findings'], list)
        
        # Corroded terminal fault
        battery.inject_fault("corroded_terminal")
        readings = battery.get_diagnostic_readings('visual', {})
        findings_text = ' '.join(readings['findings'])
        assert 'corrosion' in findings_text.lower()
    
    def test_battery_voltage_measurement(self):
        """Test voltage measurements."""
        battery = Battery()
        
        # Resting voltage
        readings = battery.get_diagnostic_readings('multimeter', {'engine_cranking': False})
        assert readings['voltage'] >= 12.0
        assert readings['unit'] == 'V'
        
        # Voltage under load
        readings = battery.get_diagnostic_readings('multimeter', {'engine_cranking': True})
        assert readings['voltage'] < 12.6  # Should be lower under load
    
    def test_battery_load_test(self):
        """Test battery load test."""
        battery = Battery()
        
        # Healthy battery should pass
        readings = battery.get_diagnostic_readings('load_test', {})
        assert readings['passed'] is True
        
        # Failed cell should fail
        battery.inject_fault("failed_cell")
        readings = battery.get_diagnostic_readings('load_test', {})
        assert readings['passed'] is False


class TestStarterMotor:
    """Tests for StarterMotor component."""
    
    def test_starter_initialization(self):
        """Test starter motor is initialized correctly."""
        starter = StarterMotor()
        assert starter.component_id == "starter_motor"
        assert starter.name == "Starter Motor"
        assert starter.parameters['operational'] is True
    
    def test_starter_fault_injection(self):
        """Test fault injection into starter motor."""
        starter = StarterMotor()
        
        result = starter.inject_fault("failed_solenoid")
        assert result is True
        assert starter.active_fault.name == "failed_solenoid"
        assert starter.parameters['solenoid_functional'] is False
    
    def test_starter_crank_test_healthy(self):
        """Test crank test with healthy starter."""
        starter = StarterMotor()
        
        readings = starter.get_diagnostic_readings('crank_test', {
            'battery_voltage': 12.6
        })
        
        assert readings['cranked'] is True
        assert readings['sound'] == 'normal_cranking'
        assert readings['rpm'] == 200
    
    def test_starter_crank_test_failed_solenoid(self):
        """Test crank test with failed solenoid."""
        starter = StarterMotor()
        starter.inject_fault("failed_solenoid")
        
        readings = starter.get_diagnostic_readings('crank_test', {
            'battery_voltage': 12.6
        })
        
        assert readings['cranked'] is False
        assert readings['sound'] == 'single_click'
    
    def test_starter_crank_test_worn(self):
        """Test crank test with worn starter."""
        starter = StarterMotor()
        starter.inject_fault("worn_starter")
        
        readings = starter.get_diagnostic_readings('crank_test', {
            'battery_voltage': 12.6
        })
        
        assert readings['cranked'] is True
        assert 'slow' in readings['sound'] or 'grinding' in readings['sound']
        assert readings['rpm'] < 100
    
    def test_starter_replacement_cost(self):
        """Test replacement cost is available."""
        starter = StarterMotor()
        cost = starter.get_replacement_cost()
        assert cost > 0
