"""Main game loop and orchestration."""

from typing import Optional, Dict, Any, List
from mygarage.system_model import SystemModel
from mygarage.fault_engine import FaultEngine
from mygarage.diagnostic_tools import DiagnosticTools
from mygarage.scoring import ScoringSystem, GameScore
from mygarage.simulation import MuJoCoSimulation


class Game:
    """Main game controller for MyGarage."""
    
    def __init__(self, headless: bool = True, difficulty: Optional[str] = None):
        self.headless = headless
        self.difficulty = difficulty
        
        # Initialize subsystems
        self.system_model = SystemModel()
        self.fault_engine = FaultEngine()
        self.diagnostic_tools = DiagnosticTools(self.system_model)
        self.scoring_system = ScoringSystem()
        
        # Try to initialize simulation
        self.simulation: Optional[MuJoCoSimulation] = None
        try:
            self.simulation = MuJoCoSimulation(headless=headless)
        except Exception as e:
            print(f"Warning: MuJoCo simulation not available: {e}")
        
        # Game state
        self.active_scenario = False
        self.parts_replaced: List[str] = []
        self.diagnosis_submitted = False
    
    def start_new_scenario(self) -> Dict[str, Any]:
        """
        Start a new diagnostic scenario.
        
        Returns:
            Dictionary with scenario information including customer complaint
        """
        # Reset everything
        self.system_model.reset()
        self.diagnostic_tools.reset_usage_stats()
        self.parts_replaced.clear()
        self.diagnosis_submitted = False
        
        if self.simulation:
            self.simulation.reset()
        
        # Select and inject a random fault
        fault = self.fault_engine.select_random_fault(difficulty=self.difficulty)
        
        if not fault:
            return {
                'success': False,
                'error': 'No faults available in catalog'
            }
        
        # Inject the fault into the system
        self.system_model.inject_fault(fault.component_id, fault.fault_name)
        
        self.active_scenario = True
        
        return {
            'success': True,
            'scenario_id': fault.fault_id,
            'complaint': self.fault_engine.get_customer_complaint(),
            'difficulty': fault.difficulty
        }
    
    def perform_diagnostic(self, tool: str, component: str, **kwargs) -> Dict[str, Any]:
        """
        Perform a diagnostic test.
        
        Args:
            tool: Tool name to use
            component: Component ID to test
            **kwargs: Additional tool-specific parameters
            
        Returns:
            Diagnostic results
        """
        if not self.active_scenario:
            return {'error': 'No active scenario'}
        
        return self.diagnostic_tools.use_tool(tool, component, **kwargs)
    
    def replace_part(self, component_id: str) -> Dict[str, Any]:
        """
        Replace a component.
        
        Args:
            component_id: ID of component to replace
            
        Returns:
            Result of replacement operation
        """
        if not self.active_scenario:
            return {'error': 'No active scenario'}
        
        component = self.system_model.get_component(component_id)
        if not component:
            return {'error': f'Component {component_id} not found'}
        
        cost = component.get_replacement_cost()
        self.parts_replaced.append(component_id)
        
        # Clear fault if this was the faulty component
        component.clear_fault()
        
        return {
            'success': True,
            'component': component_id,
            'cost': cost,
            'total_parts_replaced': len(self.parts_replaced)
        }
    
    def submit_diagnosis(self, component_id: str, fault_name: str) -> Dict[str, Any]:
        """
        Submit a diagnosis for scoring.
        
        Args:
            component_id: Diagnosed component ID
            fault_name: Diagnosed fault name
            
        Returns:
            Diagnosis result and score
        """
        if not self.active_scenario:
            return {'error': 'No active scenario'}
        
        if self.diagnosis_submitted:
            return {'error': 'Diagnosis already submitted for this scenario'}
        
        # Check diagnosis
        diagnosis_result = self.fault_engine.check_diagnosis(component_id, fault_name)
        
        # Calculate score
        tool_usage = self.diagnostic_tools.get_usage_stats()
        parts_costs = {
            pid: self.system_model.get_component(pid).get_replacement_cost()
            for pid in self.parts_replaced
            if self.system_model.get_component(pid)
        }
        
        score = self.scoring_system.calculate_score(
            diagnosis_result,
            tool_usage,
            self.parts_replaced,
            parts_costs
        )
        
        self.diagnosis_submitted = True
        self.active_scenario = False
        
        return {
            'diagnosis': diagnosis_result,
            'score': score,
            'score_summary': self.scoring_system.get_score_summary(score)
        }
    
    def get_available_components(self) -> List[Dict[str, str]]:
        """Get list of all available components."""
        return [
            {
                'id': c.component_id,
                'name': c.name,
                'type': c.__class__.__name__
            }
            for c in self.system_model.get_all_components()
        ]
    
    def get_available_tools(self) -> Dict[str, str]:
        """Get list of available diagnostic tools."""
        return self.diagnostic_tools.get_available_tools()
    
    def step_simulation(self, nsteps: int = 1):
        """Step the MuJoCo simulation forward."""
        if self.simulation and self.simulation.is_loaded():
            self.simulation.step(nsteps)
            self.system_model.step(dt=0.01 * nsteps)
    
    def render(self):
        """Render the simulation (if not headless)."""
        if self.simulation and not self.headless:
            self.simulation.render()
    
    def close(self):
        """Clean up resources."""
        if self.simulation:
            self.simulation.close()
