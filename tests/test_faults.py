"""Tests for fault system"""

import pytest
from pathlib import Path
from mygarage.faults import FaultCatalog, FaultInjector, Fault
from mygarage.components import Battery, StarterMotor


@pytest.fixture
def fault_catalog():
    """Create fault catalog with test data"""
    catalog = FaultCatalog()
    data_dir = Path(__file__).parent.parent / "data" / "faults"
    if data_dir.exists():
        catalog.load_from_directory(data_dir)
    return catalog


def test_fault_catalog_load(fault_catalog):
    """Test fault catalog loads"""
    assert len(fault_catalog.faults) > 0


def test_fault_catalog_get_fault(fault_catalog):
    """Test getting specific fault"""
    fault = fault_catalog.get_fault("F001")
    if fault:
        assert fault.id == "F001"
        assert fault.component == "battery"


def test_fault_catalog_get_faults_by_component(fault_catalog):
    """Test filtering faults by component"""
    battery_faults = fault_catalog.get_faults_by_component("battery")
    assert all(f.component == "battery" for f in battery_faults)


def test_fault_catalog_get_faults_by_difficulty(fault_catalog):
    """Test filtering faults by difficulty"""
    easy_faults = fault_catalog.get_faults_by_difficulty("easy")
    assert all(f.difficulty == "easy" for f in easy_faults)


def test_fault_injector_inject_specific_fault(fault_catalog):
    """Test injecting a specific fault"""
    battery = Battery()
    components = {"battery": battery}
    
    injector = FaultInjector(fault_catalog)
    fault = fault_catalog.get_fault("F001")
    
    if fault:
        injector.inject_fault(fault, components)
        
        assert injector.active_fault == fault
        assert battery.state.fault_id == "F001"


def test_fault_injector_random_fault(fault_catalog):
    """Test injecting random fault"""
    battery = Battery()
    starter = StarterMotor()
    components = {"battery": battery, "starter": starter}
    
    if len(fault_catalog.faults) > 0:
        injector = FaultInjector(fault_catalog)
        fault = injector.inject_random_fault(components)
        
        assert injector.active_fault is not None
        assert fault.component in components


def test_fault_injector_symptom_description(fault_catalog):
    """Test getting symptom description"""
    battery = Battery()
    components = {"battery": battery}
    
    injector = FaultInjector(fault_catalog)
    fault = fault_catalog.get_fault("F001")
    
    if fault:
        injector.inject_fault(fault, components)
        symptoms = injector.get_symptom_description()
        
        assert isinstance(symptoms, str)
        assert len(symptoms) > 0


def test_fault_injector_check_diagnosis_correct(fault_catalog):
    """Test checking correct diagnosis"""
    battery = Battery()
    components = {"battery": battery}
    
    injector = FaultInjector(fault_catalog)
    fault = fault_catalog.get_fault("F001")
    
    if fault:
        injector.inject_fault(fault, components)
        
        assert injector.check_diagnosis("F001") is True
        assert injector.check_diagnosis("F002") is False


def test_fault_injector_clear_fault(fault_catalog):
    """Test clearing fault"""
    battery = Battery()
    components = {"battery": battery}
    
    injector = FaultInjector(fault_catalog)
    fault = fault_catalog.get_fault("F001")
    
    if fault:
        injector.inject_fault(fault, components)
        injector.clear_fault(components)
        
        assert injector.active_fault is None
        assert battery.state.fault_id is None
