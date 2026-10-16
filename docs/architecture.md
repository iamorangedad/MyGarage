# MyGarage Architecture

## Overview

MyGarage is a game-like simulator where players practice car diagnosis and repair in a virtual environment. The system uses MuJoCo for physics simulation and implements a modular, component-based architecture inspired by robotics simulation frameworks.

## Implemented subsystems

`components/__init__.py` lists every part the system model installs. The signal model in `system_model.py` couples them:

1. Starting circuit: ground strap, ignition switch, starter relay, fuse, and solenoid, plus the original battery and starter.
2. Charging: alternator output depends on the belt, the alternator, and the regulator setpoint, and only while the engine is running.
3. Combustion: a successful crank starts the engine only when the run circuit, crankshaft sensor, fuel pressure, and spark are good enough. A weak plug, coil, pump, or injector starts and then misfires.
4. Cooling: coolant temperature approaches a target set by the thermostat, pump, radiator, fan, and the indicated temperature from the coolant sensor.
5. Chassis: pad thickness, disc runout, wheel-speed codes, and shock bounce are diagnostic-only.

## Core Principles

1. **Modularity**: Each car part is a self-contained component with its own model, parameters, and fault modes
2. **Separation of Concerns**: Physics (MuJoCo) is separate from electrical/fuel/ignition logic
3. **Data-Driven**: Faults are defined in YAML catalogs, not hardcoded
4. **Extensibility**: Adding new components requires minimal changes to core code
5. **Testability**: Headless operation enables automated testing

## Architecture Layers

### 1. Component Layer (`component.py`, `components/`)

Each car part is a `Component` subclass with:
- **MJCF Model**: Geometry and physics properties for MuJoCo
- **Parameters**: State variables (voltage, resistance, temperature, etc.)
- **Fault Modes**: Possible failures with affected parameters
- **Diagnostic Interface**: What each tool reads from this component

**Example**: `Battery` component has:
- Parameters: `voltage_resting`, `voltage_under_load`, `state_of_charge`
- Fault modes: `discharged_battery`, `failed_cell`, `corroded_terminal`
- Tool responses: `multimeter` returns voltage, `visual` returns inspection findings

**Adding a New Component**:

```python
from mygarage.component import Component, FaultMode

class FuelPump(Component):
    def __init__(self):
        super().__init__("fuel_pump", "Fuel Pump")
        self._mjcf_path = "fuel_pump.xml"
        self.parameters = self.get_nominal_parameters()
        self._define_fault_modes()
    
    def get_nominal_parameters(self):
        return {
            'pressure_psi': 60.0,
            'flow_rate': 50.0,  # liters/hour
            'operational': True,
            'replacement_cost': 200.0
        }
    
    def _define_fault_modes(self):
        self.fault_modes = [
            FaultMode(
                name="weak_pump",
                description="Pump output pressure too low",
                symptoms=["Hard starting", "Loss of power"],
                affected_parameters={'pressure_psi': 30.0}
            )
        ]
    
    def get_diagnostic_readings(self, tool, context):
        if tool == 'pressure_gauge':
            return {'pressure': self.parameters['pressure_psi'], 'unit': 'psi'}
        return {'error': f'Tool {tool} not supported'}
```

### 2. System Model Layer (`system_model.py`)

The `SystemModel` manages:
- Component registry and lifecycle
- System-wide state (ignition, engine RPM, cranking)
- Inter-component interactions (battery voltage affects starter torque)
- Electrical/mechanical/thermal behavior separate from rigid-body physics

**Why Separate from MuJoCo?**
- MuJoCo simulates rigid bodies, joints, contacts
- Electrical circuits, fuel flow, thermal behavior are signal/state models
- System model computes these and drives MuJoCo actuators/forces

**Example**: When player cranks engine:
1. System model checks battery voltage
2. Calculates starter motor torque based on voltage and starter condition
3. Sets MuJoCo actuator to apply torque to crankshaft joint
4. MuJoCo simulates resulting rotation
5. System model updates battery discharge based on current draw

### 3. Fault Engine (`fault_engine.py`)

**Responsibilities**:
- Load fault catalog from YAML
- Select random faults (optionally filtered by difficulty)
- Generate customer complaints based on symptoms
- Check player diagnosis for correctness
- Provide scoring metadata

**Fault Catalog Format** (`data/fault_catalog.yaml`):

```yaml
faults:
  - fault_id: "F001"
    component_id: "battery_12v"
    fault_name: "discharged_battery"
    description: "Battery is deeply discharged"
    root_cause: "Insufficient charge in battery cells"
    symptoms:
      - "No crank"
      - "Clicking sound"
    difficulty: "easy"
    points: 100
```

### 4. Diagnostic Tools (`diagnostic_tools.py`)

Provides the player with tools to investigate:
- **Visual Inspection**: Look for physical damage, corrosion, leaks
- **Multimeter**: Measure voltage, current, resistance
- **Load Test**: Test components under load
- **Crank Test**: Attempt to crank engine and observe

Tools track usage for scoring and call `Component.get_diagnostic_readings()`.

### 5. Scoring System (`scoring.py`)

Evaluates player performance based on:
- **Diagnosis Correctness**: Full points for correct component + fault
- **Partial Credit**: Half points for correct component, wrong fault
- **Tool Usage Penalty**: Deduct points for unnecessary diagnostics
- **Parts Cost**: Subtract cost of replaced parts
- **Efficiency Bonus**: Bonus for solving with minimal tool use

**Grading**:
- A: 90+ points
- B: 80-89
- C: 70-79
- D: 60-69
- F: <60 or incorrect diagnosis

### 6. MuJoCo Simulation (`simulation.py`)

Wrapper around MuJoCo:
- Loads MJCF scene (car geometry, joints, actuators)
- Steps simulation forward
- Sets actuator values (starter motor torque)
- Reads sensor data (crankshaft RPM)
- Manages viewer (or runs headless)

**MJCF Structure** (`mjcf/garage_scene.xml`):
- Garage floor and lighting
- Car body (simplified box geometry)
- Engine block with crankshaft joint
- Battery (visual geometry)
- Starter motor (visual geometry)
- Actuator: `starter_motor` applies torque to `crank_joint`
- Sensor: `crank_rpm` measures crankshaft velocity

### 7. Game Loop (`game.py`)

Orchestrates everything:

```
1. Start New Scenario
   ↓
2. Select Random Fault → Inject into System Model
   ↓
3. Show Customer Complaint
   ↓
4. Player Loop:
   - Use diagnostic tools
   - Optionally replace parts
   - Submit diagnosis
   ↓
5. Score Diagnosis
   ↓
6. Show Results
```

**Game State**:
- `active_scenario`: Is a diagnostic scenario active?
- `parts_replaced`: List of component IDs replaced
- `diagnosis_submitted`: Has player submitted?

### 8. User Interface

**Current**: CLI (`cli.py`)
- Text-based menu
- Type commands to use tools, inspect components, submit diagnosis
- MuJoCo viewer shows 3D scene (if not headless)

**Future**: Web UI with MuJoCo WASM
- Core game logic is UI-independent
- Web frontend would call `Game` API methods
- MuJoCo scene rendered in browser via WebAssembly

## Data Flow Example: Player Measures Battery Voltage

```
CLI: User selects "Measure voltage"
  ↓
Game.perform_diagnostic('multimeter', 'battery_12v')
  ↓
DiagnosticTools.use_tool('multimeter', 'battery_12v')
  ↓
SystemModel.get_context() → {'engine_cranking': False, ...}
  ↓
Battery.get_diagnostic_readings('multimeter', context)
  ↓
Battery checks active_fault, returns voltage based on fault state
  ↓
DiagnosticTools tracks usage for scoring
  ↓
Result returned to player: {'voltage': 11.5, 'unit': 'V'}
```

## Extending the System

### Adding a New Component

1. Create `components/new_component.py`:
   - Subclass `Component`
   - Define `get_nominal_parameters()`
   - Define `_define_fault_modes()`
   - Implement `get_diagnostic_readings()`

2. Create MJCF model `mjcf/new_component.xml` (optional)

3. Add to `components/__init__.py`

4. Add faults to `data/fault_catalog.yaml`

5. Register in `SystemModel._initialize_default_components()`

6. Write tests in `tests/test_components.py`

### Adding a New Diagnostic Tool

1. Add tool handler in `Component.get_diagnostic_readings()`
2. Add convenience method in `DiagnosticTools` (optional)
3. Update CLI menu to expose tool
4. Add to `DiagnosticTools.get_available_tools()`

### Adding a New Fault

1. Add fault mode to component's `_define_fault_modes()`
2. Add entry to `data/fault_catalog.yaml`
3. Write test case

## Design Decisions

**Q: Why separate Component and MJCF models?**
A: Many car systems (electrical, fuel, ignition) don't map to rigid-body physics. Separating logical components from physical geometry allows flexibility.

**Q: Why YAML for fault catalog?**
A: Makes it easy for non-programmers to add/edit faults without touching code. Can be translated or versioned independently.

**Q: Why track tool usage for scoring?**
A: Mimics real-world efficiency. Expert mechanics diagnose with fewer tests. Encourages learning systematic diagnostic procedures.

**Q: Why headless mode?**
A: Enables automated testing, CI/CD, and running on servers without displays. Critical for robust development.

## Testing Strategy

- **Unit Tests**: Test individual components, fault injection, tool readings
- **Integration Tests**: Test full game workflows end-to-end
- **Headless Tests**: Verify MuJoCo simulation loads and steps without display
- **Regression Tests**: Ensure new components don't break existing ones

## Performance Considerations

- MuJoCo simulation runs at 100 Hz (0.01s timestep)
- System model can run at different rate (e.g., 10 Hz for thermal updates)
- Diagnostic tools are event-driven (no polling loop)
- Fault catalog loaded once at startup

## Future Enhancements

1. **More Components**: Engine, alternator, fuel system, cooling system
2. **Complex Faults**: Multi-component failures, intermittent issues
3. **Scenarios**: Different vehicles, weather conditions, failure modes
4. **Multiplayer**: Compare scores with other players
5. **Tutorial Mode**: Guided diagnostic procedures
6. **Advanced Physics**: Fluid dynamics for fuel/coolant, thermal simulation
7. **VR Support**: Immersive 3D garage environment
8. **Realistic Repair**: Physically remove and install parts

## References

- **MuJoCo**: https://mujoco.org/
- **Inspiration - Microduck**: https://github.com/pollen-robotics/microduck
- **Component Architecture**: Similar to ROS/Gazebo plugin systems
