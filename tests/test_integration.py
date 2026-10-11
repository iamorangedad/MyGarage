"""Integration tests for full game flow"""

import pytest
from pathlib import Path
from mygarage.game import MyGarageGame, Vehicle
import mujoco


def test_vehicle_mjcf_generation():
    """Test vehicle generates valid MJCF"""
    vehicle = Vehicle()
    from mygarage.components import Battery, StarterMotor
    
    vehicle.add_component(Battery())
    vehicle.add_component(StarterMotor())
    
    mjcf = vehicle.build_mjcf_scene()
    assert isinstance(mjcf, str)
    assert "<mujoco" in mjcf
    assert "battery" in mjcf
    assert "starter_motor" in mjcf


def test_vehicle_mujoco_initialization():
    """Test MuJoCo scene initializes headless"""
    vehicle = Vehicle()
    from mygarage.components import Battery, StarterMotor
    
    vehicle.add_component(Battery())
    vehicle.add_component(StarterMotor())
    
    vehicle.initialize_simulation()
    
    assert vehicle.model is not None
    assert vehicle.data is not None
    assert isinstance(vehicle.model, mujoco.MjModel)
    assert isinstance(vehicle.data, mujoco.MjData)


def test_vehicle_simulation_step():
    """Test simulation can step headless"""
    vehicle = Vehicle()
    from mygarage.components import Battery, StarterMotor
    
    vehicle.add_component(Battery())
    vehicle.add_component(StarterMotor())
    
    vehicle.initialize_simulation()
    
    initial_time = vehicle.data.time
    
    for _ in range(10):
        vehicle.step()
        
    assert vehicle.data.time > initial_time


@pytest.fixture
def game():
    """Create game instance"""
    data_dir = Path(__file__).parent.parent / "data"
    return MyGarageGame(data_dir)


def test_game_initialization(game):
    """Test game initializes correctly"""
    assert game.catalog is not None
    assert len(game.tools) > 0
    assert "multimeter" in game.tools


def test_game_start_new_case(game):
    """Test starting a new case"""
    if len(game.catalog.faults) == 0:
        pytest.skip("No faults loaded")
        
    symptoms = game.start_new_case()
    
    assert isinstance(symptoms, str)
    assert len(symptoms) > 0
    assert game.case_active is True
    assert game.injector.active_fault is not None


def test_game_use_tool(game):
    """Test using a diagnostic tool"""
    if len(game.catalog.faults) == 0:
        pytest.skip("No faults loaded")
        
    game.start_new_case()
    
    result = game.use_tool("multimeter", "battery", "resting_voltage")
    assert isinstance(result, str)
    assert len(result) > 0


def test_game_replace_part(game):
    """Test replacing a part"""
    if len(game.catalog.faults) == 0:
        pytest.skip("No faults loaded")
        
    game.start_new_case()
    
    result = game.replace_part("battery", 120.0)
    assert "Replaced" in result
    assert len(game.scoring.parts_replaced) == 1


def test_game_submit_diagnosis(game):
    """Test submitting a diagnosis"""
    if len(game.catalog.faults) == 0:
        pytest.skip("No faults loaded")
        
    game.start_new_case()
    fault_id = game.injector.active_fault.id
    
    score = game.submit_diagnosis(fault_id)
    
    assert score.correct is True
    assert game.case_active is False


def test_game_full_workflow(game):
    """Test complete game workflow"""
    if len(game.catalog.faults) == 0:
        pytest.skip("No faults loaded")
        
    symptoms = game.start_new_case()
    assert game.case_active
    
    game.use_tool("multimeter", "battery", "resting_voltage")
    game.use_tool("visual", "battery", "general")
    game.use_tool("crank_test", "starter", "attempt_start")
    
    assert len(game.scoring.measurements) == 3
    
    fault_id = game.injector.active_fault.id
    score = game.submit_diagnosis(fault_id)
    
    assert score.correct is True
    assert score.steps_taken == 3
