"""Components package.

Adding a part is: implement a ``Component`` subclass, export it here, and
append its faults to ``data/fault_catalog.yaml``. ``default_components`` is
what the system model instantiates.
"""

from mygarage.components.battery import Battery
from mygarage.components.chassis import (
    BrakeDisc,
    BrakePads,
    ShockAbsorber,
    WheelSpeedSensor,
)
from mygarage.components.charging import Alternator, SerpentineBelt, VoltageRegulator
from mygarage.components.combustion import (
    CrankshaftPositionSensor,
    FuelInjector,
    FuelPump,
    IgnitionCoil,
    SparkPlug,
)
from mygarage.components.cooling import (
    CoolantTempSensor,
    CoolingFan,
    Radiator,
    Thermostat,
    WaterPump,
)
from mygarage.components.intake_exhaust import (
    AirFilter,
    CatalyticConverter,
    DownstreamO2Sensor,
    EGRValve,
    IntakeGasket,
    ManifoldPressureSensor,
    MassAirflowSensor,
    PCVValve,
    ThrottleBody,
    UpstreamO2Sensor,
)
from mygarage.components.remaining import remaining_classes
from mygarage.components.starter_motor import StarterMotor
from mygarage.components.starting import (
    GroundStrap,
    IgnitionSwitch,
    StarterFuse,
    StarterRelay,
    StarterSolenoid,
)

# Hand-written parts first, then one generated class per remaining catalog row.
COMPONENT_CLASSES = [
    Battery,
    StarterMotor,
    GroundStrap,
    IgnitionSwitch,
    StarterRelay,
    StarterFuse,
    StarterSolenoid,
    Alternator,
    SerpentineBelt,
    VoltageRegulator,
    SparkPlug,
    IgnitionCoil,
    FuelInjector,
    FuelPump,
    CrankshaftPositionSensor,
    Thermostat,
    WaterPump,
    CoolingFan,
    CoolantTempSensor,
    Radiator,
    BrakePads,
    BrakeDisc,
    WheelSpeedSensor,
    ShockAbsorber,
    AirFilter,
    ThrottleBody,
    IntakeGasket,
    MassAirflowSensor,
    ManifoldPressureSensor,
    UpstreamO2Sensor,
    DownstreamO2Sensor,
    CatalyticConverter,
    EGRValve,
    PCVValve,
] + remaining_classes()


def default_components():
    """Return one healthy instance of every built-in part."""
    return [cls() for cls in COMPONENT_CLASSES]


__all__ = [cls.__name__ for cls in COMPONENT_CLASSES] + [
    "COMPONENT_CLASSES",
    "default_components",
]
