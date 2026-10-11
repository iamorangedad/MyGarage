"""Fault catalog management"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import yaml
from pathlib import Path


@dataclass
class Fault:
    """Represents a single fault"""
    
    id: str
    name: str
    component: str
    description: str
    symptoms: str
    difficulty: str
    parameters: Dict[str, Any]
    observables: Dict[str, Any]
    repair_cost: float = 0.0
    repair_time: float = 0.0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Fault":
        """Create Fault from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            component=data["component"],
            description=data["description"],
            symptoms=data["symptoms"],
            difficulty=data["difficulty"],
            parameters=data.get("parameters", {}),
            observables=data.get("observables", {}),
            repair_cost=data.get("repair_cost", 0.0),
            repair_time=data.get("repair_time", 0.0)
        )


class FaultCatalog:
    """Manages the fault catalog"""
    
    def __init__(self):
        self.faults: Dict[str, Fault] = {}
        
    def load_from_file(self, filepath: Path):
        """Load faults from YAML file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        for fault_data in data.get("faults", []):
            fault = Fault.from_dict(fault_data)
            self.faults[fault.id] = fault
            
    def load_from_directory(self, dirpath: Path):
        """Load all fault files from directory"""
        for yaml_file in dirpath.glob("*.yaml"):
            self.load_from_file(yaml_file)
            
    def get_fault(self, fault_id: str) -> Optional[Fault]:
        """Get fault by ID"""
        return self.faults.get(fault_id)
        
    def get_faults_by_component(self, component: str) -> List[Fault]:
        """Get all faults for a component"""
        return [f for f in self.faults.values() if f.component == component]
        
    def get_faults_by_difficulty(self, difficulty: str) -> List[Fault]:
        """Get all faults of a given difficulty"""
        return [f for f in self.faults.values() if f.difficulty == difficulty]
        
    def list_all_faults(self) -> List[Fault]:
        """Get all faults"""
        return list(self.faults.values())
