"""Scoring system for evaluating player performance."""

from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class GameScore:
    """Represents the score for a game session."""
    
    diagnosis_correct: bool = False
    diagnosis_points: int = 0
    tool_usage_penalty: int = 0
    parts_replaced: List[str] = field(default_factory=list)
    parts_cost: float = 0.0
    efficiency_bonus: int = 0
    total_score: int = 0
    grade: str = "F"
    
    def calculate_total(self):
        """Calculate total score and grade."""
        self.total_score = max(0, self.diagnosis_points - self.tool_usage_penalty - int(self.parts_cost))
        self.total_score += self.efficiency_bonus
        
        # Assign grade
        if not self.diagnosis_correct:
            self.grade = "F"
        elif self.total_score >= 90:
            self.grade = "A"
        elif self.total_score >= 80:
            self.grade = "B"
        elif self.total_score >= 70:
            self.grade = "C"
        elif self.total_score >= 60:
            self.grade = "D"
        else:
            self.grade = "F"


class ScoringSystem:
    """Calculates and manages game scoring."""
    
    def __init__(self):
        self.penalty_per_unnecessary_tool = 2
        self.efficiency_thresholds = {
            'excellent': (3, 20),  # (max tools used, bonus points)
            'good': (5, 10),
            'acceptable': (8, 5),
        }
    
    def calculate_score(
        self,
        diagnosis_result: Dict[str, Any],
        tool_usage: Dict[str, int],
        parts_replaced: List[str],
        parts_costs: Dict[str, float]
    ) -> GameScore:
        """
        Calculate the final score for a game session.
        
        Args:
            diagnosis_result: Result from FaultEngine.check_diagnosis()
            tool_usage: Dictionary of tool usage counts
            parts_replaced: List of component IDs that were replaced
            parts_costs: Dictionary mapping component IDs to their replacement costs
            
        Returns:
            GameScore object with detailed scoring breakdown
        """
        score = GameScore()
        
        # Base diagnosis points
        score.diagnosis_correct = diagnosis_result.get('correct', False)
        score.diagnosis_points = diagnosis_result.get('points', 0)
        
        # Tool usage penalty
        total_tool_uses = sum(tool_usage.values())
        # Assume minimum 2 tools needed for any diagnosis
        unnecessary_uses = max(0, total_tool_uses - 2)
        score.tool_usage_penalty = unnecessary_uses * self.penalty_per_unnecessary_tool
        
        # Parts replacement cost
        score.parts_replaced = parts_replaced
        score.parts_cost = sum(parts_costs.get(part_id, 0) for part_id in parts_replaced)
        
        # Efficiency bonus
        if score.diagnosis_correct:
            for level, (max_tools, bonus) in self.efficiency_thresholds.items():
                if total_tool_uses <= max_tools:
                    score.efficiency_bonus = bonus
                    break
        
        # Calculate total
        score.calculate_total()
        
        return score
    
    def get_score_summary(self, score: GameScore) -> str:
        """
        Generate a human-readable score summary.
        
        Args:
            score: GameScore object
            
        Returns:
            Formatted score summary string
        """
        summary = "\n" + "="*50 + "\n"
        summary += "DIAGNOSIS REPORT\n"
        summary += "="*50 + "\n\n"
        
        summary += f"Diagnosis: {'CORRECT ✓' if score.diagnosis_correct else 'INCORRECT ✗'}\n"
        summary += f"Base Points: {score.diagnosis_points}\n"
        summary += f"Tool Usage Penalty: -{score.tool_usage_penalty}\n"
        summary += f"Parts Replaced: {len(score.parts_replaced)} (${score.parts_cost:.2f})\n"
        
        if score.parts_replaced:
            for part in score.parts_replaced:
                summary += f"  - {part}\n"
        
        summary += f"Efficiency Bonus: +{score.efficiency_bonus}\n"
        summary += f"\nTOTAL SCORE: {score.total_score}\n"
        summary += f"GRADE: {score.grade}\n"
        summary += "="*50 + "\n"
        
        return summary
