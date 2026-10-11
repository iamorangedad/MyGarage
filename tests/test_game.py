"""Test suite for Game integration."""

import pytest
from mygarage.game import Game


class TestGame:
    """Integration tests for the Game class."""
    
    @pytest.fixture
    def game(self):
        """Create a game instance."""
        return Game(headless=True)
    
    def test_game_initialization(self, game):
        """Test game initializes correctly."""
        assert game.system_model is not None
        assert game.fault_engine is not None
        assert game.diagnostic_tools is not None
        assert game.scoring_system is not None
        assert game.active_scenario is False
    
    def test_start_new_scenario(self, game):
        """Test starting a new scenario."""
        result = game.start_new_scenario()
        
        assert result['success'] is True
        assert 'complaint' in result
        assert 'difficulty' in result
        assert game.active_scenario is True
    
    def test_perform_diagnostic(self, game):
        """Test performing diagnostics."""
        game.start_new_scenario()
        
        result = game.perform_diagnostic('visual', 'battery_12v')
        
        assert 'tool' in result
        assert 'component' in result
        assert 'readings' in result
        assert result['tool'] == 'visual'
    
    def test_replace_part(self, game):
        """Test part replacement."""
        game.start_new_scenario()
        
        result = game.replace_part('battery_12v')
        
        assert result['success'] is True
        assert result['component'] == 'battery_12v'
        assert result['cost'] > 0
        assert len(game.parts_replaced) == 1
    
    def test_submit_correct_diagnosis(self, game):
        """Test submitting correct diagnosis."""
        game.start_new_scenario()
        
        # Get the actual fault (cheating for test)
        fault_info = game.fault_engine.get_active_fault_info()
        
        result = game.submit_diagnosis(
            fault_info['component_id'],
            fault_info['fault_name']
        )
        
        assert 'diagnosis' in result
        assert 'score' in result
        assert result['diagnosis']['correct'] is True
        assert game.active_scenario is False
    
    def test_submit_wrong_diagnosis(self, game):
        """Test submitting wrong diagnosis."""
        game.start_new_scenario()
        
        result = game.submit_diagnosis('wrong_component', 'wrong_fault')
        
        assert 'diagnosis' in result
        assert result['diagnosis']['correct'] is False
    
    def test_cannot_diagnose_twice(self, game):
        """Test cannot submit diagnosis twice."""
        game.start_new_scenario()
        
        fault_info = game.fault_engine.get_active_fault_info()
        game.submit_diagnosis(fault_info['component_id'], fault_info['fault_name'])
        
        # Try again
        result = game.submit_diagnosis('battery_12v', 'discharged_battery')
        
        assert 'error' in result
    
    def test_get_available_components(self, game):
        """Test getting available components."""
        components = game.get_available_components()
        
        assert isinstance(components, list)
        assert len(components) >= 2
        assert all('id' in c and 'name' in c for c in components)
    
    def test_get_available_tools(self, game):
        """Test getting available tools."""
        tools = game.get_available_tools()
        
        assert isinstance(tools, dict)
        assert len(tools) > 0
        assert 'visual' in tools
        assert 'multimeter' in tools
    
    def test_full_game_workflow(self, game):
        """Test complete game workflow."""
        # Start scenario
        result = game.start_new_scenario()
        assert result['success'] is True
        
        # Perform some diagnostics
        game.perform_diagnostic('visual', 'battery_12v')
        game.perform_diagnostic('multimeter', 'battery_12v')
        game.perform_diagnostic('crank_test', 'starter_motor')
        
        # Replace a part (possibly wrong)
        game.replace_part('starter_motor')
        
        # Get correct answer
        fault_info = game.fault_engine.get_active_fault_info()
        
        # Submit diagnosis
        result = game.submit_diagnosis(
            fault_info['component_id'],
            fault_info['fault_name']
        )
        
        # Check scoring
        assert 'score' in result
        score = result['score']
        assert score.diagnosis_correct is True
        assert score.total_score > 0
        
        # Check tool usage was tracked
        assert score.tool_usage_penalty >= 0
    
    def test_simulation_stepping(self, game):
        """Test simulation can step forward."""
        game.start_new_scenario()
        
        # Should not raise error
        game.step_simulation(10)
    
    def test_headless_mode(self):
        """Test game works in headless mode."""
        game = Game(headless=True)
        assert game.headless is True
        
        # Should be able to run without display
        game.start_new_scenario()
        game.perform_diagnostic('visual', 'battery_12v')
        game.step_simulation(5)
        game.close()
