"""MuJoCo simulation integration."""

from typing import Optional, Any
from pathlib import Path
import numpy as np

try:
    import mujoco
    MUJOCO_AVAILABLE = True
except ImportError:
    MUJOCO_AVAILABLE = False
    mujoco = None


class MuJoCoSimulation:
    """Manages the MuJoCo physics simulation."""
    
    def __init__(self, model_path: Optional[str] = None, headless: bool = True):
        if not MUJOCO_AVAILABLE:
            raise ImportError("MuJoCo is not installed. Install with: pip install mujoco")
        
        self.headless = headless
        self.model_path = model_path or self._get_default_model_path()
        self.model: Optional[Any] = None
        self.data: Optional[Any] = None
        self.viewer: Optional[Any] = None
        
        self._load_model()
    
    def _get_default_model_path(self) -> str:
        """Get the default MJCF model path."""
        mjcf_dir = Path(__file__).parent / "mjcf"
        return str(mjcf_dir / "garage_scene.xml")
    
    def _load_model(self):
        """Load the MuJoCo model from MJCF file."""
        try:
            if self.model_path == self._get_default_model_path():
                from mygarage.fasteners.scene import load_garage_xml
                self.model = mujoco.MjModel.from_xml_string(load_garage_xml())
            else:
                self.model = mujoco.MjModel.from_xml_path(self.model_path)
            self.data = mujoco.MjData(self.model)
        except Exception as e:
            print(f"Warning: Could not load MuJoCo model from {self.model_path}: {e}")
            print("Creating a minimal default model instead.")
            self._create_minimal_model()
    
    def _create_minimal_model(self):
        """Create a minimal MuJoCo model if file loading fails."""
        xml_string = """
        <mujoco model="minimal_garage">
            <worldbody>
                <light diffuse=".5 .5 .5" pos="0 0 3" dir="0 0 -1"/>
                <geom type="plane" size="5 5 0.1" rgba=".9 .9 .9 1"/>
                <body name="car_placeholder" pos="0 0 0.5">
                    <geom type="box" size="1 0.5 0.3" rgba="0.8 0.1 0.1 1"/>
                </body>
            </worldbody>
        </mujoco>
        """
        self.model = mujoco.MjModel.from_xml_string(xml_string)
        self.data = mujoco.MjData(self.model)
    
    def step(self, nsteps: int = 1):
        """
        Step the simulation forward.
        
        Args:
            nsteps: Number of simulation steps to take
        """
        if self.model and self.data:
            for _ in range(nsteps):
                mujoco.mj_step(self.model, self.data)
    
    def set_actuator(self, name: str, value: float):
        """
        Set an actuator value.
        
        Args:
            name: Actuator name
            value: Control value
        """
        if self.model and self.data:
            try:
                actuator_id = self.model.actuator(name).id
                self.data.ctrl[actuator_id] = value
            except KeyError:
                print(f"Warning: Actuator '{name}' not found")
    
    def get_sensor_data(self, name: str) -> Optional[float]:
        """
        Get sensor data by name.
        
        Args:
            name: Sensor name
            
        Returns:
            Sensor value or None if not found
        """
        if self.model and self.data:
            try:
                sensor_id = self.model.sensor(name).id
                return self.data.sensordata[sensor_id]
            except (KeyError, IndexError):
                print(f"Warning: Sensor '{name}' not found")
        return None
    
    def set_joint_qpos(self, name: str, value: float):
        """Pose one joint and clear its velocity. The fastener model is the source of truth."""
        if not (self.model and self.data):
            return
        joint = self.model.joint(name)
        self.data.qpos[int(joint.qposadr[0])] = value
        self.data.qvel[int(joint.dofadr[0])] = 0.0

    def forward(self):
        """Update body positions from the current joint coordinates."""
        if self.model and self.data:
            mujoco.mj_forward(self.model, self.data)

    def joint_qpos(self, name: str) -> Optional[float]:
        """Current position of a named joint."""
        if not (self.model and self.data):
            return None
        joint = self.model.joint(name)
        return float(self.data.qpos[int(joint.qposadr[0])])

    def reset(self):
        """Reset the simulation to initial state."""
        if self.model and self.data:
            mujoco.mj_resetData(self.model, self.data)
    
    def render(self):
        """Render the simulation (if not headless)."""
        if not self.headless:
            if self.viewer is None:
                # Create viewer on first render
                try:
                    self.viewer = mujoco.viewer.launch_passive(self.model, self.data)
                except Exception as e:
                    print(f"Could not create viewer: {e}")
                    return
            
            if self.viewer:
                self.viewer.sync()
    
    def close(self):
        """Close the simulation and viewer."""
        if self.viewer:
            self.viewer.close()
            self.viewer = None
    
    def is_loaded(self) -> bool:
        """Check if model is loaded successfully."""
        return self.model is not None and self.data is not None
