"""Test suite for scoring system."""

import pytest
from mygarage.scoring import ScoringSystem, GameScore


class TestScoringSystem:
    """Tests for ScoringSystem."""
    
    @pytest.fixture
    def scoring(self):
        """Create a scoring system."""
        return ScoringSystem()
    
    def test_perfect_score(self, scoring):
        """Test perfect diagnosis with minimal tool usage."""
        diagnosis_result = {
            'correct': True,
            'points': 100
        }
        tool_usage = {
            'visual:battery_12v': 1,
            'multimeter:battery_12v': 1
        }
        parts_replaced = []
        parts_costs = {}
        
        score = scoring.calculate_score(
            diagnosis_result,
            tool_usage,
            parts_replaced,
            parts_costs
        )
        
        assert score.diagnosis_correct is True
        assert score.diagnosis_points == 100
        assert score.tool_usage_penalty == 0  # 2 tools is minimum
        assert score.parts_cost == 0.0
        assert score.efficiency_bonus == 20  # Excellent efficiency
        assert score.total_score == 120
        assert score.grade == 'A'
    
    def test_correct_diagnosis_with_penalties(self, scoring):
        """Test correct diagnosis but with tool usage penalties."""
        diagnosis_result = {
            'correct': True,
            'points': 100
        }
        tool_usage = {
            'visual:battery_12v': 2,
            'multimeter:battery_12v': 3,
            'load_test:battery_12v': 2,
            'crank_test:starter_motor': 1
        }  # Total: 8 uses
        parts_replaced = []
        parts_costs = {}
        
        score = scoring.calculate_score(
            diagnosis_result,
            tool_usage,
            parts_replaced,
            parts_costs
        )
        
        assert score.diagnosis_correct is True
        # 8 uses - 2 minimum = 6 unnecessary
        assert score.tool_usage_penalty == 6 * 2  # 12 points penalty
        assert score.efficiency_bonus == 5  # Acceptable efficiency (<=8 tools)
    
    def test_wrong_diagnosis(self, scoring):
        """Test wrong diagnosis results in F grade."""
        diagnosis_result = {
            'correct': False,
            'points': 0
        }
        tool_usage = {
            'visual:battery_12v': 1
        }
        parts_replaced = []
        parts_costs = {}
        
        score = scoring.calculate_score(
            diagnosis_result,
            tool_usage,
            parts_replaced,
            parts_costs
        )
        
        assert score.diagnosis_correct is False
        assert score.diagnosis_points == 0
        assert score.efficiency_bonus == 0  # No bonus for wrong diagnosis
        assert score.grade == 'F'
    
    def test_with_parts_replacement(self, scoring):
        """Test score with parts replaced."""
        diagnosis_result = {
            'correct': True,
            'points': 100
        }
        tool_usage = {
            'visual:battery_12v': 1,
            'multimeter:battery_12v': 1
        }
        parts_replaced = ['battery_12v', 'starter_motor']
        parts_costs = {
            'battery_12v': 150.0,
            'starter_motor': 250.0
        }
        
        score = scoring.calculate_score(
            diagnosis_result,
            tool_usage,
            parts_replaced,
            parts_costs
        )
        
        assert score.parts_cost == 400.0
        assert len(score.parts_replaced) == 2
        # Score will be negative due to high parts cost
        assert score.total_score < 100
    
    def test_partial_credit(self, scoring):
        """Test partial credit for correct component."""
        diagnosis_result = {
            'correct': False,
            'points': 50  # Half points
        }
        tool_usage = {
            'visual:battery_12v': 1,
            'multimeter:battery_12v': 1,
            'load_test:battery_12v': 1
        }
        parts_replaced = []
        parts_costs = {}
        
        score = scoring.calculate_score(
            diagnosis_result,
            tool_usage,
            parts_replaced,
            parts_costs
        )
        
        assert score.diagnosis_points == 50
        assert score.diagnosis_correct is False
        assert score.grade == 'F'  # Still F because diagnosis not fully correct
    
    def test_score_summary_format(self, scoring):
        """Test score summary is properly formatted."""
        diagnosis_result = {'correct': True, 'points': 100}
        tool_usage = {'visual:battery_12v': 1, 'multimeter:battery_12v': 1}
        parts_replaced = []
        parts_costs = {}
        
        score = scoring.calculate_score(
            diagnosis_result, tool_usage, parts_replaced, parts_costs
        )
        
        summary = scoring.get_score_summary(score)
        
        assert isinstance(summary, str)
        assert 'CORRECT' in summary
        assert 'TOTAL SCORE' in summary
        assert 'GRADE' in summary
        assert str(score.total_score) in summary
