"""Fault engine for managing fault injection and fault catalog."""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import random
from dataclasses import dataclass


@dataclass
class FaultDefinition:
    """Definition of a fault from the fault catalog."""
    
    fault_id: str
    component_id: str
    fault_name: str
    description: str
    symptoms: List[str]
    root_cause: str
    difficulty: str
    correct_diagnosis_points: int = 100


class FaultEngine:
    """Manages fault catalog and fault injection."""
    
    def __init__(self, catalog_path: Optional[str] = None):
        self.catalog_path = catalog_path or self._get_default_catalog_path()
        self.fault_catalog: List[FaultDefinition] = []
        self.active_fault: Optional[FaultDefinition] = None
        self._load_catalog()
    
    def _get_default_catalog_path(self) -> str:
        """Get the default fault catalog path."""
        return str(Path(__file__).parent.parent.parent / "data" / "fault_catalog.yaml")
    
    def _load_catalog(self):
        """Load fault catalog from YAML file."""
        try:
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            for fault_data in data.get('faults', []):
                fault = FaultDefinition(
                    fault_id=fault_data['fault_id'],
                    component_id=fault_data['component_id'],
                    fault_name=fault_data['fault_name'],
                    description=fault_data['description'],
                    symptoms=fault_data['symptoms'],
                    root_cause=fault_data['root_cause'],
                    difficulty=fault_data.get('difficulty', 'medium'),
                    correct_diagnosis_points=fault_data.get('points', 100)
                )
                self.fault_catalog.append(fault)
                
        except FileNotFoundError:
            print(f"Warning: Fault catalog not found at {self.catalog_path}")
            self.fault_catalog = []
    
    def select_random_fault(self, difficulty: Optional[str] = None) -> Optional[FaultDefinition]:
        """
        Select a random fault from the catalog.
        
        Args:
            difficulty: Optional difficulty filter ('easy', 'medium', 'hard')
            
        Returns:
            Selected fault definition, or None if catalog is empty
        """
        candidates = self.fault_catalog
        
        if difficulty:
            candidates = [f for f in candidates if f.difficulty == difficulty]
        
        if not candidates:
            return None
        
        self.active_fault = random.choice(candidates)
        return self.active_fault
    
    def get_customer_complaint(self) -> str:
        """
        Generate a customer complaint based on the active fault.
        
        Returns:
            Customer complaint text
        """
        if not self.active_fault:
            return "Customer: The car seems fine to me..."
        
        # Pick 1-2 symptoms to present to the player
        num_symptoms = random.randint(1, min(2, len(self.active_fault.symptoms)))
        presented_symptoms = random.sample(self.active_fault.symptoms, num_symptoms)
        
        complaint = "Customer complaint:\n"
        for symptom in presented_symptoms:
            complaint += f"- {symptom}\n"
        
        return complaint
    
    def check_diagnosis(self, diagnosed_component: str, diagnosed_fault: str) -> Dict[str, Any]:
        """
        Check if the player's diagnosis is correct.
        
        Args:
            diagnosed_component: Component ID the player diagnosed
            diagnosed_fault: Fault name the player diagnosed
            
        Returns:
            Dictionary with correctness and scoring information
        """
        if not self.active_fault:
            return {
                'correct': False,
                'message': 'No active fault to diagnose',
                'points': 0
            }
        
        component_correct = diagnosed_component == self.active_fault.component_id
        fault_correct = diagnosed_fault == self.active_fault.fault_name
        
        if component_correct and fault_correct:
            return {
                'correct': True,
                'message': f'Correct! The problem was: {self.active_fault.description}',
                'points': self.active_fault.correct_diagnosis_points,
                'root_cause': self.active_fault.root_cause
            }
        elif component_correct:
            return {
                'correct': False,
                'message': f'Component correct, but wrong fault. Try again.',
                'points': self.active_fault.correct_diagnosis_points // 2,
                'root_cause': None
            }
        else:
            return {
                'correct': False,
                'message': f'Incorrect diagnosis. The actual problem was: {self.active_fault.description}',
                'points': 0,
                'root_cause': self.active_fault.root_cause
            }
    
    def get_active_fault_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently active fault (for debugging/testing)."""
        if not self.active_fault:
            return None
        
        return {
            'fault_id': self.active_fault.fault_id,
            'component_id': self.active_fault.component_id,
            'fault_name': self.active_fault.fault_name,
            'description': self.active_fault.description,
            'root_cause': self.active_fault.root_cause
        }
