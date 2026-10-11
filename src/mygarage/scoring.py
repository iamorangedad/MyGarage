"""Scoring system for diagnosis performance"""

from dataclasses import dataclass
from typing import List, Optional
from .diagnostics.base import MeasurementResult


@dataclass
class DiagnosisScore:
    """Result of scoring a diagnosis"""
    
    correct: bool
    base_score: float
    efficiency_score: float
    cost_score: float
    total_score: float
    
    steps_taken: int
    minimum_steps: int
    parts_cost: float
    
    feedback: str
    
    def __str__(self) -> str:
        """Format score as string"""
        result = f"{'✓ CORRECT' if self.correct else '✗ INCORRECT'}\n"
        result += f"Total Score: {self.total_score:.1f} / 100\n"
        result += f"  Base: {self.base_score:.1f}\n"
        result += f"  Efficiency: {self.efficiency_score:.1f} ({self.steps_taken} steps, optimal {self.minimum_steps})\n"
        result += f"  Cost: {self.cost_score:.1f} (${self.parts_cost:.2f} spent)\n"
        result += f"\n{self.feedback}"
        return result


class ScoringSystem:
    """Scores player diagnosis performance"""
    
    def __init__(self):
        self.measurements: List[MeasurementResult] = []
        self.parts_replaced: List[tuple] = []
        
    def reset(self):
        """Reset for new case"""
        self.measurements.clear()
        self.parts_replaced.clear()
        
    def record_measurement(self, result: MeasurementResult):
        """Record a diagnostic measurement"""
        self.measurements.append(result)
        
    def record_part_replacement(self, component_id: str, cost: float):
        """Record a part replacement"""
        self.parts_replaced.append((component_id, cost))
        
    def calculate_score(
        self,
        diagnosed_fault_id: str,
        actual_fault_id: str,
        actual_fault_component: str,
        minimum_steps: int = 3
    ) -> DiagnosisScore:
        """
        Calculate score based on diagnosis.
        
        Args:
            diagnosed_fault_id: Fault ID player diagnosed
            actual_fault_id: Correct fault ID
            actual_fault_component: Component with the fault
            minimum_steps: Minimum steps needed for optimal diagnosis
            
        Returns:
            DiagnosisScore object
        """
        correct = diagnosed_fault_id == actual_fault_id
        
        base_score = 100.0 if correct else 0.0
        
        steps_taken = len(self.measurements)
        if steps_taken == 0:
            efficiency_multiplier = 0.0
        elif steps_taken <= minimum_steps:
            efficiency_multiplier = 1.0
        else:
            extra_steps = steps_taken - minimum_steps
            efficiency_multiplier = max(0.5, 1.0 - (extra_steps * 0.1))
        efficiency_score = base_score * efficiency_multiplier
        
        parts_cost = sum(cost for _, cost in self.parts_replaced)
        
        correct_replacement = any(
            comp_id == actual_fault_component 
            for comp_id, _ in self.parts_replaced
        )
        
        if not self.parts_replaced:
            cost_multiplier = 1.0
        elif correct and correct_replacement and len(self.parts_replaced) == 1:
            cost_multiplier = 1.0
        else:
            unnecessary_parts = len(self.parts_replaced)
            if correct_replacement:
                unnecessary_parts -= 1
            cost_multiplier = max(0.5, 1.0 - (unnecessary_parts * 0.2))
            
        cost_score = base_score * cost_multiplier
        
        total_score = (base_score + efficiency_score + cost_score) / 3.0
        
        if correct:
            if steps_taken <= minimum_steps and cost_multiplier >= 1.0:
                feedback = "Excellent! Perfect diagnosis with minimal steps and no wasted parts."
            elif efficiency_multiplier >= 0.8:
                feedback = "Good job! Correct diagnosis with reasonable efficiency."
            else:
                feedback = "Correct diagnosis, but consider a more systematic approach."
        else:
            feedback = f"Incorrect. The actual fault was {actual_fault_id}. Review the diagnostic data."
            
        return DiagnosisScore(
            correct=correct,
            base_score=base_score,
            efficiency_score=efficiency_score / 100.0 * 100,
            cost_score=cost_score / 100.0 * 100,
            total_score=total_score,
            steps_taken=steps_taken,
            minimum_steps=minimum_steps,
            parts_cost=parts_cost,
            feedback=feedback
        )
