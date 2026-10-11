"""Tests for scoring system"""

import pytest
from mygarage.scoring import ScoringSystem
from mygarage.diagnostics import MeasurementResult


def test_scoring_correct_diagnosis():
    """Test scoring for correct diagnosis"""
    scoring = ScoringSystem()
    
    result1 = MeasurementResult("Multimeter", "battery", "voltage", {"value": 11.5})
    result2 = MeasurementResult("CrankTest", "starter", "crank", {"result": "no_crank"})
    result3 = MeasurementResult("Visual", "battery", "inspect", {"ok": True})
    
    scoring.record_measurement(result1)
    scoring.record_measurement(result2)
    scoring.record_measurement(result3)
    
    score = scoring.calculate_score(
        diagnosed_fault_id="F001",
        actual_fault_id="F001",
        actual_fault_component="battery",
        minimum_steps=3
    )
    
    assert score.correct is True
    assert score.base_score == 100.0
    assert score.total_score > 0


def test_scoring_incorrect_diagnosis():
    """Test scoring for incorrect diagnosis"""
    scoring = ScoringSystem()
    
    result = MeasurementResult("Multimeter", "battery", "voltage", {"value": 11.5})
    scoring.record_measurement(result)
    
    score = scoring.calculate_score(
        diagnosed_fault_id="F002",
        actual_fault_id="F001",
        actual_fault_component="battery",
        minimum_steps=3
    )
    
    assert score.correct is False
    assert score.base_score == 0.0
    assert score.total_score == 0.0


def test_scoring_efficiency_penalty():
    """Test efficiency penalty for extra steps"""
    scoring = ScoringSystem()
    
    for i in range(10):
        result = MeasurementResult("Test", "component", f"test{i}", {})
        scoring.record_measurement(result)
        
    score = scoring.calculate_score(
        diagnosed_fault_id="F001",
        actual_fault_id="F001",
        actual_fault_component="battery",
        minimum_steps=3
    )
    
    assert score.correct is True
    assert score.steps_taken == 10
    assert score.efficiency_score < 100.0


def test_scoring_cost_tracking():
    """Test cost tracking for part replacements"""
    scoring = ScoringSystem()
    
    scoring.record_part_replacement("battery", 120.0)
    scoring.record_part_replacement("starter", 200.0)
    
    score = scoring.calculate_score(
        diagnosed_fault_id="F001",
        actual_fault_id="F001",
        actual_fault_component="battery",
        minimum_steps=1
    )
    
    assert score.parts_cost == 320.0
    assert score.cost_score < 100.0


def test_scoring_reset():
    """Test scoring reset"""
    scoring = ScoringSystem()
    
    scoring.record_measurement(MeasurementResult("Test", "comp", "test", {}))
    scoring.record_part_replacement("battery", 100.0)
    
    scoring.reset()
    
    assert len(scoring.measurements) == 0
    assert len(scoring.parts_replaced) == 0


def test_scoring_optimal_performance():
    """Test optimal performance (minimal steps, correct parts)"""
    scoring = ScoringSystem()
    
    for i in range(3):
        scoring.record_measurement(MeasurementResult("Tool", "comp", f"test{i}", {}))
        
    scoring.record_part_replacement("battery", 120.0)
    
    score = scoring.calculate_score(
        diagnosed_fault_id="F001",
        actual_fault_id="F001",
        actual_fault_component="battery",
        minimum_steps=3
    )
    
    assert score.correct is True
    assert score.efficiency_score >= 95.0
    assert score.cost_score >= 95.0
