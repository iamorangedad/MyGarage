"""Test suite for system model."""

import pytest
from mygarage.system_model import SystemModel
from mygarage.components import Battery, StarterMotor


class TestSystemModel:
    """Tests for SystemModel."""
    
    @pytest.fixture
    def system(self):
        """Create a system model."""
        return SystemModel()
    
    def test_initialization(self, system):
        """Test system initializes with default components."""
        assert len(system.components) >= 2  # At least battery and starter
        assert 'battery_12v' in system.components
        assert 'starter_motor' in system.components
    
    def test_add_component(self, system):
        """Test adding a component."""
        initial_count = len(system.components)
        
        new_battery = Battery("battery_aux")
        system.add_component(new_battery)
        
        assert len(system.components) == initial_count + 1
        assert 'battery_aux' in system.components
    
    def test_get_component(self, system):
        """Test retrieving a component."""
        battery = system.get_component('battery_12v')
        assert battery is not None
        assert isinstance(battery, Battery)
        
        nonexistent = system.get_component('nonexistent')
        assert nonexistent is None
    
    def test_inject_fault(self, system):
        """Test fault injection through system model."""
        result = system.inject_fault('battery_12v', 'discharged_battery')
        assert result is True
        
        battery = system.get_component('battery_12v')
        assert battery.active_fault is not None
        assert battery.active_fault.name == 'discharged_battery'
    
    def test_attempt_crank_healthy(self, system):
        """Test cranking with healthy components."""
        result = system.attempt_crank()
        
        assert result['success'] is True
        assert result['cranking'] is True
        assert result['rpm'] > 150
        assert result['sound'] == 'normal_crank'
    
    def test_attempt_crank_dead_battery(self, system):
        """Test cranking with dead battery."""
        system.inject_fault('battery_12v', 'discharged_battery')
        
        result = system.attempt_crank()
        
        # May or may not crank depending on how discharged
        assert 'success' in result
        assert 'sound' in result
    
    def test_attempt_crank_failed_solenoid(self, system):
        """Test cranking with failed starter solenoid."""
        system.inject_fault('starter_motor', 'failed_solenoid')
        
        result = system.attempt_crank()
        
        assert result['success'] is False
        assert result['sound'] == 'single_click'
        assert result['cranking'] is False
    
    def test_stop_crank(self, system):
        """Test stopping crank resets state."""
        system.attempt_crank()
        assert system.state['engine_cranking'] is True
        
        system.stop_crank()
        assert system.state['engine_cranking'] is False
        assert system.state['engine_rpm'] == 0
    
    def test_get_context(self, system):
        """Test context retrieval."""
        context = system.get_context()
        
        assert 'engine_cranking' in context
        assert 'battery_voltage' in context
        assert 'engine_rpm' in context
        assert isinstance(context['battery_voltage'], (int, float))
    
    def test_step_simulation(self, system):
        """Test system model stepping."""
        battery = system.get_component('battery_12v')
        initial_soc = battery.parameters['state_of_charge']
        
        # Start cranking
        system.attempt_crank()
        
        # Step forward
        system.step(dt=1.0)
        
        # Battery should have discharged
        assert battery.parameters['state_of_charge'] < initial_soc
    
    def test_reset(self, system):
        """Test system reset."""
        # Inject fault and modify state
        system.inject_fault('battery_12v', 'discharged_battery')
        system.attempt_crank()
        
        # Reset
        system.reset()
        
        # Check components are healthy
        battery = system.get_component('battery_12v')
        assert battery.active_fault is None
        
        # Check state is reset
        assert system.state['engine_cranking'] is False
        assert system.state['engine_rpm'] == 0
    
    def test_get_all_components(self, system):
        """Test getting all components."""
        components = system.get_all_components()
        
        assert isinstance(components, list)
        assert len(components) >= 2
        assert all(hasattr(c, 'component_id') for c in components)
