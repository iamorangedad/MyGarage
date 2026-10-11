"""Diagnostic tools for investigating car problems."""

from typing import Dict, Any, Optional
from mygarage.system_model import SystemModel


class DiagnosticTools:
    """Collection of diagnostic tools available to the player."""
    
    def __init__(self, system_model: SystemModel):
        self.system = system_model
        self.tool_usage_count: Dict[str, int] = {}
    
    def use_tool(self, tool_name: str, component_id: str, **kwargs) -> Dict[str, Any]:
        """
        Use a diagnostic tool on a component.
        
        Args:
            tool_name: Name of the tool to use
            component_id: ID of the component to test
            **kwargs: Additional tool-specific parameters
            
        Returns:
            Tool reading results
        """
        # Track tool usage for scoring
        key = f"{tool_name}:{component_id}"
        self.tool_usage_count[key] = self.tool_usage_count.get(key, 0) + 1
        
        component = self.system.get_component(component_id)
        if not component:
            return {'error': f'Component {component_id} not found'}
        
        context = self.system.get_context()
        context.update(kwargs)
        
        try:
            readings = component.get_diagnostic_readings(tool_name, context)
            return {
                'tool': tool_name,
                'component': component_id,
                'readings': readings,
                'timestamp': self._get_simulation_time()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def visual_inspection(self, component_id: str) -> Dict[str, Any]:
        """Perform a visual inspection of a component."""
        return self.use_tool('visual', component_id)
    
    def measure_voltage(self, component_id: str, cranking: bool = False) -> Dict[str, Any]:
        """
        Measure voltage at a component using a multimeter.
        
        Args:
            component_id: Component to measure
            cranking: Whether to measure while cranking
        """
        if cranking:
            # Simulate cranking while measuring
            crank_result = self.system.attempt_crank()
            result = self.use_tool('multimeter', component_id)
            self.system.stop_crank()
            result['crank_info'] = crank_result
            return result
        else:
            return self.use_tool('multimeter', component_id)
    
    def load_test(self, component_id: str) -> Dict[str, Any]:
        """Perform a load test on a component (e.g., battery load test)."""
        return self.use_tool('load_test', component_id)
    
    def crank_test(self, component_id: str = 'starter_motor') -> Dict[str, Any]:
        """Attempt to crank the engine and observe behavior."""
        result = self.use_tool('crank_test', component_id)
        self.system.stop_crank()
        return result
    
    def get_available_tools(self) -> Dict[str, str]:
        """
        Get list of available diagnostic tools.
        
        Returns:
            Dictionary mapping tool names to descriptions
        """
        return {
            'visual': 'Visual inspection - Look at component condition',
            'multimeter': 'Multimeter - Measure voltage, current, resistance',
            'load_test': 'Load test - Test component under load conditions',
            'crank_test': 'Crank test - Attempt to crank engine and observe',
        }
    
    def get_usage_stats(self) -> Dict[str, int]:
        """Get diagnostic tool usage statistics."""
        return self.tool_usage_count.copy()
    
    def reset_usage_stats(self):
        """Reset tool usage statistics."""
        self.tool_usage_count.clear()
    
    def _get_simulation_time(self) -> float:
        """Get current simulation time."""
        # Placeholder - would be connected to actual sim time
        import time
        return time.time()
