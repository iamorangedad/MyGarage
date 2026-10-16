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
        
        context = self.system.get_context()
        context.update(kwargs)

        if tool_name == 'crank_test':
            started = self.system.start_attempt()
            readings = {
                'cranked': bool(started.get('success')),
                'started': bool(started.get('started')),
                'sound': started.get('sound'),
                'description': started.get('description'),
                'rpm': started.get('idle_rpm', 0) if started.get('started') else started.get('rpm', 0),
                'cranking_rpm': started.get('rpm', 0),
                'idle_quality': started.get('idle_quality'),
                'misfire': started.get('misfire', False),
            }
            return {
                'tool': tool_name,
                'component': component_id,
                'readings': readings,
                'timestamp': self._get_simulation_time(),
            }

        if tool_name == 'live_data' and component_id in ('all', 'vehicle', 'engine'):
            return {
                'tool': tool_name,
                'component': component_id,
                'readings': {
                    'engine_running': context.get('engine_running'),
                    'rpm': context.get('engine_rpm'),
                    'idle_quality': context.get('idle_quality'),
                    'fuel_trim_pct': context.get('fuel_trim_pct'),
                    'maf_reported_gps': context.get('maf_reported_gps'),
                    'maf_from_map_gps': context.get('maf_actual_gps'),
                    'map_reported_kpa': context.get('map_reported_kpa'),
                    'vacuum_gauge_kpa': context.get('manifold_pressure_kpa'),
                    'o2_upstream_v': context.get('o2_upstream_v'),
                    'o2_switching': context.get('o2_switching'),
                    'o2_downstream_v': context.get('o2_downstream_v'),
                    'o2_downstream_switching': context.get('o2_downstream_switching'),
                    'catalyst_efficiency': context.get('catalyst_efficiency'),
                    'power_pct': context.get('power_pct'),
                    'backpressure_kpa': context.get('backpressure_kpa'),
                    'oil_pressure_psi': context.get('oil_pressure_psi'),
                    'note': None if context.get('engine_running') else 'Engine is not running',
                },
                'timestamp': self._get_simulation_time(),
            }

        if tool_name == 'obd' and component_id in ('all', 'vehicle', 'obd'):
            codes = []
            for part in self.system.get_all_components():
                part_reading = part.get_diagnostic_readings('obd', context)
                for code in part_reading.get('dtcs', []) or []:
                    codes.append({
                        'code': code,
                        'component': part.component_id,
                        'description': part_reading.get('description'),
                    })
            return {
                'tool': tool_name,
                'component': component_id,
                'readings': {
                    'dtcs': codes,
                    'note': 'No codes stored' if not codes else f'{len(codes)} code(s)',
                },
                'timestamp': self._get_simulation_time(),
            }

        component = self.system.get_component(component_id)
        if not component:
            return {'error': f'Component {component_id} not found'}

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
            'crank_test': 'Crank and start - Hold the key in START, then release to RUN',
            'obd': 'OBD scanner - Read stored diagnostic codes',
            'fuel_pressure': 'Fuel pressure gauge - Rail pressure with the key in RUN',
            'temperature': 'Temperature - Gauge, scanner, or infrared reading',
            'voltage_drop': 'Voltage drop - Measure a connection while cranking',
            'spark_test': 'Spark test - Coil output and plug condition',
            'bounce_test': 'Bounce test - How many times the corner oscillates',
            'live_data': 'Live data - RPM, fuel trim, MAF, MAP, and O2 while running',
            'smoke_test': 'Smoke test - Look for an intake leak',
            'egr_test': 'EGR test - Flow at idle, and flow when the valve is commanded',
            'rattle_test': 'Rattle test - Shake a PCV valve',
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
