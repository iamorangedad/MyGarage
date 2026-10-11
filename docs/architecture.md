# MyGarage Architecture

## Overview

MyGarage is a layered car repair simulation system combining MuJoCo physics simulation with logical system models.

## Architecture Layers

```
┌─────────────────────────────────────────┐
│          UI Layer                        │
│  Python + MuJoCo Viewer / CLI / ImGui   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        Game Logic Layer                  │
│  Fault injection, diagnostics, scoring   │
└─────────────────┬───────────────────────┘
                  │
      ┌───────────┴───────────┐
      │                       │
┌─────▼──────────┐   ┌───────▼────────────┐
│  System Model  │   │   Component Layer  │
│  Layer         │◄──│                    │
│                │   │ - MJCF models      │
│ - Electrical   │   │ - Parameters       │
│ - Fuel         │   │ - Fault modes      │
│ - Ignition     │   │ - Diagnostics map  │
└─────┬──────────┘   └────────────────────┘
      │
┌─────▼──────────┐
│   MuJoCo       │
│   Physics      │
└────────────────┘
```

## Component System

Each component (battery, starter, brake, etc.) is a self-contained module:

### Component Interface
```python
class Component(ABC):
    @abstractmethod
    def get_mjcf(self) -> str:
        """Return MJCF XML for this component"""
        
    @abstractmethod
    def apply_fault(self, fault_id: str, params: dict):
        """Apply a fault to this component"""
        
    @abstractmethod
    def get_reading(self, tool_name: str, measurement_point: str, params: dict) -> dict:
        """Return diagnostic tool reading"""
        
    @abstractmethod
    def reset(self):
        """Reset to nominal state"""
```

## System Model Layer

Handles non-mechanical systems (electrical, fuel, ignition):

### Electrical System
- Battery state (voltage, charge, health)
- Current flow calculations
- Starter motor torque output
- Voltage drop across connections

### Key Responsibilities
- Maintain system state
- Calculate sensor readings
- Drive MuJoCo actuators based on system state
- Apply fault effects to readings

## Fault System

### Data-Driven Fault Catalog
YAML format in `data/faults/`:

```yaml
faults:
  - id: F001
    name: "Dead Battery"
    component: battery
    description: "Battery discharged, cannot provide sufficient current"
    symptoms: "Car won't start, clicking sound or no response"
    difficulty: easy
    parameters:
      voltage: 11.5
      max_current: 50
    observables:
      resting_voltage: 11.5
      loaded_voltage: 8.0
      cranking_current: 50
```

### Fault Injection Flow
1. Load fault catalog
2. Randomly select fault (or specific for testing)
3. Apply fault to affected component
4. Generate symptom description
5. Track correct diagnosis for scoring

## Diagnostic Tools

Abstract actions rather than physical manipulation:

### Tool Categories
- **Visual Inspection**: Check component condition, connections, corrosion
- **Multimeter**: Measure voltage, current, resistance
- **OBD Scanner**: Read codes, live data (future)
- **Crank Test**: Attempt to start and observe behavior
- **Voltage Drop Test**: Measure resistance in connections

### Tool Interface
```python
class DiagnosticTool(ABC):
    @abstractmethod
    def measure(self, vehicle, target: str, params: dict) -> MeasurementResult:
        """Perform measurement and return result"""
```

## Scoring System

### Metrics
- **Correct Diagnosis**: Did player identify root cause? (pass/fail)
- **Efficiency**: Number of diagnostic steps taken
- **Cost**: Total cost of parts replaced (including unnecessary ones)
- **Time**: Optional, for advanced scoring

### Scoring Formula
```
score = base_score * efficiency_multiplier * cost_multiplier
- Base: 100 points for correct diagnosis, 0 otherwise
- Efficiency: 1.0 at minimum steps, decreases with extra steps
- Cost: 1.0 for exact fix, decreases with wasteful replacements
```

## Game Loop (v0)

```
1. Initialize MuJoCo scene
2. Load components
3. Inject random fault
4. Display symptoms
5. Loop:
   a. Player selects diagnostic action
   b. System returns reading/result
   c. Player optionally replaces parts
   d. Player submits diagnosis or continues
6. Score diagnosis
7. Show results
8. Next case or exit
```

## MuJoCo Integration

### Scene Structure
- World body (ground)
- Vehicle chassis (fixed or on wheels)
- Components attached to chassis
- Joints connecting moving parts
- Actuators for starter motor torque

### Update Cycle
1. System model calculates new state (voltages, currents)
2. System model outputs actuator commands
3. MuJoCo steps physics
4. Observe MuJoCo state (positions, velocities)
5. Update system model with new observations

## Testing Strategy

### Headless Mode
All tests run without display:
- Use `mujoco.MjModel.from_xml_string()` 
- Step simulation with `mujoco.mj_step()`
- No viewer required

### Test Coverage
1. **Component Tests**: Each component's MJCF loads, fault application works
2. **Fault Tests**: Fault injection, reading calculations correct
3. **Diagnostic Tests**: Each tool returns expected readings for known faults
4. **Scoring Tests**: Scoring logic for various scenarios
5. **Integration Tests**: Full game loop with known fault

## Adding New Components

1. Create new file in `src/mygarage/components/`
2. Inherit from `Component` base class
3. Implement MJCF generation
4. Implement fault modes and effects
5. Implement diagnostic reading calculations
6. Add fault entries to YAML in `data/faults/`
7. Add tests in `tests/test_components.py`
8. No changes to core game logic required

## Future Enhancements

### Web Frontend
- Core logic already UI-independent
- Replace viewer with MuJoCo WASM
- Add web-based control panel
- Multiplayer/leaderboards

### Advanced Physics
- More detailed MJCF models
- Fluid simulation for oil/coolant
- Thermal simulation
- Sound generation

### Content Expansion
- More components (suspension, brakes, engine)
- Complex multi-fault scenarios
- Diagnostic procedure guides
- Repair tutorials
