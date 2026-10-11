"""Main game logic for MyGarage simulator"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import mujoco
import numpy as np

from .components import Component, Battery, StarterMotor
from .system_model import ElectricalSystem
from .faults import FaultCatalog, FaultInjector
from .diagnostics import DiagnosticTool, Multimeter, VisualInspection, CrankTest
from .scoring import ScoringSystem, DiagnosisScore


class Vehicle:
    """Represents the vehicle being diagnosed"""
    
    def __init__(self):
        self.components: Dict[str, Component] = {}
        self.electrical_system = ElectricalSystem()
        
        self.model: Optional[mujoco.MjModel] = None
        self.data: Optional[mujoco.MjData] = None
        
    def add_component(self, component: Component):
        """Add a component to the vehicle"""
        self.components[component.component_id] = component
        
    def build_mjcf_scene(self) -> str:
        """Build complete MJCF scene from components"""
        mjcf = """
<mujoco model="mygarage_vehicle">
    <compiler angle="radian"/>
    
    <option timestep="0.002" gravity="0 0 -9.81"/>
    
    <asset>
        <texture name="grid" type="2d" builtin="checker" width="512" height="512" 
                 rgb1=".1 .2 .3" rgb2=".2 .3 .4"/>
        <material name="grid" texture="grid" texrepeat="1 1" texuniform="true"
                  reflectance=".2"/>
    </asset>
    
    <worldbody>
        <light diffuse=".8 .8 .8" pos="0 0 3" dir="0 0 -1"/>
        <light diffuse=".5 .5 .5" pos="2 2 4" dir="-1 -1 -2"/>
        
        <geom name="floor" type="plane" size="5 5 .1" material="grid"/>
        
        <body name="chassis" pos="0 0 0.5">
            <geom type="box" size="0.8 0.4 0.2" rgba="0.6 0.6 0.6 1" mass="100"/>
"""
        
        for component in self.components.values():
            mjcf += component.get_mjcf()
            
        mjcf += """
        </body>
    </worldbody>
    
    <actuator>
        <motor name="starter_motor" joint="crank_joint" gear="1" ctrllimited="true" ctrlrange="0 10"/>
    </actuator>
</mujoco>
"""
        return mjcf
        
    def initialize_simulation(self):
        """Initialize MuJoCo simulation"""
        mjcf_xml = self.build_mjcf_scene()
        self.model = mujoco.MjModel.from_xml_string(mjcf_xml)
        self.data = mujoco.MjData(self.model)
        
        battery = self.components.get("battery")
        starter = self.components.get("starter")
        if battery and starter:
            self.electrical_system.set_components(battery, starter)
            
    def step(self, dt: float = 0.002):
        """Step the simulation"""
        if not self.model or not self.data:
            return
            
        self.electrical_system.update(dt)
        
        actuator_commands = self.electrical_system.get_actuator_commands()
        if "crank_torque" in actuator_commands:
            starter_idx = mujoco.mj_name2id(
                self.model, 
                mujoco.mjtObj.mjOBJ_ACTUATOR, 
                "starter_motor"
            )
            if starter_idx >= 0:
                self.data.ctrl[starter_idx] = actuator_commands["crank_torque"]
                
        mujoco.mj_step(self.model, self.data)


class MyGarageGame:
    """Main game controller"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        
        self.catalog = FaultCatalog()
        self.catalog.load_from_directory(data_dir / "faults")
        
        self.injector = FaultInjector(self.catalog)
        self.scoring = ScoringSystem()
        
        self.vehicle = Vehicle()
        
        self.tools: Dict[str, DiagnosticTool] = {
            "multimeter": Multimeter(),
            "visual": VisualInspection(),
            "crank_test": CrankTest(),
        }
        
        self.case_active = False
        
    def start_new_case(self, difficulty: Optional[str] = None) -> str:
        """
        Start a new diagnostic case.
        
        Args:
            difficulty: Optional difficulty filter
            
        Returns:
            Symptom description (customer complaint)
        """
        self._setup_vehicle()
        
        fault = self.injector.inject_random_fault(
            self.vehicle.components,
            difficulty=difficulty
        )
        
        self.scoring.reset()
        self.case_active = True
        
        return self.injector.get_symptom_description()
        
    def _setup_vehicle(self):
        """Set up vehicle with components"""
        self.vehicle = Vehicle()
        
        battery = Battery()
        starter = StarterMotor()
        
        self.vehicle.add_component(battery)
        self.vehicle.add_component(starter)
        
        self.vehicle.initialize_simulation()
        
    def use_tool(
        self,
        tool_name: str,
        target: str,
        measurement: str,
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Use a diagnostic tool.
        
        Args:
            tool_name: Name of tool to use
            target: Target component
            measurement: What to measure
            params: Additional parameters
            
        Returns:
            Formatted measurement result
        """
        if not self.case_active:
            return "No active case. Start a new case first."
            
        if tool_name not in self.tools:
            return f"Unknown tool: {tool_name}"
            
        tool = self.tools[tool_name]
        result = tool.measure(self.vehicle, target, measurement, params)
        
        self.scoring.record_measurement(result)
        
        return str(result)
        
    def replace_part(self, component_id: str, cost: float) -> str:
        """
        Replace a vehicle part.
        
        Args:
            component_id: ID of component to replace
            cost: Cost of the part
            
        Returns:
            Result message
        """
        if not self.case_active:
            return "No active case."
            
        if component_id not in self.vehicle.components:
            return f"Unknown component: {component_id}"
            
        self.scoring.record_part_replacement(component_id, cost)
        
        component = self.vehicle.components[component_id]
        component.reset()
        
        return f"Replaced {component.name} (${cost:.2f})"
        
    def submit_diagnosis(self, fault_id: str) -> DiagnosisScore:
        """
        Submit diagnosis and get score.
        
        Args:
            fault_id: Diagnosed fault ID
            
        Returns:
            DiagnosisScore object
        """
        if not self.case_active:
            raise ValueError("No active case")
            
        if not self.injector.active_fault:
            raise ValueError("No fault active")
            
        score = self.scoring.calculate_score(
            diagnosed_fault_id=fault_id,
            actual_fault_id=self.injector.active_fault.id,
            actual_fault_component=self.injector.active_fault.component,
            minimum_steps=3
        )
        
        self.case_active = False
        
        return score
        
    def list_available_faults(self) -> List[str]:
        """List all available faults for reference"""
        return [
            f"{f.id}: {f.name} ({f.component})"
            for f in self.catalog.list_all_faults()
        ]
        
    def get_fault_details(self, fault_id: str) -> Optional[str]:
        """Get details about a fault (for reference/study)"""
        fault = self.catalog.get_fault(fault_id)
        if not fault:
            return None
            
        details = f"{fault.id}: {fault.name}\n"
        details += f"Component: {fault.component}\n"
        details += f"Description: {fault.description}\n"
        details += f"Difficulty: {fault.difficulty}\n"
        return details
