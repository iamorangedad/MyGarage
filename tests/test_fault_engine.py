"""Test suite for fault engine."""

import pytest
from pathlib import Path
from mygarage.fault_engine import FaultEngine, FaultDefinition


class TestFaultEngine:
    """Tests for FaultEngine."""
    
    @pytest.fixture
    def engine(self, tmp_path):
        """Create a fault engine with test catalog."""
        catalog_path = tmp_path / "test_catalog.yaml"
        catalog_content = """
faults:
  - fault_id: "TEST001"
    component_id: "battery_12v"
    fault_name: "discharged_battery"
    description: "Battery is discharged"
    root_cause: "Insufficient charge"
    symptoms:
      - "No crank"
      - "Clicking sound"
    difficulty: "easy"
    points: 100
    
  - fault_id: "TEST002"
    component_id: "starter_motor"
    fault_name: "failed_solenoid"
    description: "Solenoid failed"
    root_cause: "Failed solenoid"
    symptoms:
      - "Single click"
      - "No crank"
    difficulty: "medium"
    points: 120
"""
        catalog_path.write_text(catalog_content)
        return FaultEngine(catalog_path=str(catalog_path))
    
    def test_load_catalog(self, engine):
        """Test fault catalog loads correctly."""
        assert len(engine.fault_catalog) == 2
        assert engine.fault_catalog[0].fault_id == "TEST001"
        assert engine.fault_catalog[1].fault_id == "TEST002"
    
    def test_select_random_fault(self, engine):
        """Test random fault selection."""
        fault = engine.select_random_fault()
        assert fault is not None
        assert fault in engine.fault_catalog
        assert engine.active_fault == fault
    
    def test_select_fault_by_difficulty(self, engine):
        """Test fault selection with difficulty filter."""
        fault = engine.select_random_fault(difficulty='easy')
        assert fault is not None
        assert fault.difficulty == 'easy'
        
        fault = engine.select_random_fault(difficulty='medium')
        assert fault is not None
        assert fault.difficulty == 'medium'
    
    def test_get_customer_complaint(self, engine):
        """Test customer complaint generation."""
        engine.select_random_fault()
        complaint = engine.get_customer_complaint()
        assert isinstance(complaint, str)
        assert len(complaint) > 0
        assert "Customer" in complaint or len(complaint) > 10
    
    def test_check_diagnosis_correct(self, engine):
        """Test correct diagnosis checking."""
        fault = engine.select_random_fault()
        
        result = engine.check_diagnosis(fault.component_id, fault.fault_name)
        
        assert result['correct'] is True
        assert result['points'] > 0
        assert 'Correct' in result['message']
    
    def test_check_diagnosis_wrong_component(self, engine):
        """Test diagnosis with wrong component."""
        fault = engine.select_random_fault()
        wrong_component = "wrong_component"
        
        result = engine.check_diagnosis(wrong_component, fault.fault_name)
        
        assert result['correct'] is False
        assert result['points'] == 0
    
    def test_check_diagnosis_wrong_fault(self, engine):
        """Test diagnosis with correct component but wrong fault."""
        fault = engine.select_random_fault()
        
        result = engine.check_diagnosis(fault.component_id, "wrong_fault")
        
        assert result['correct'] is False
        assert result['points'] == fault.correct_diagnosis_points // 2  # Partial credit
    
    def test_get_active_fault_info(self, engine):
        """Test getting active fault information."""
        fault = engine.select_random_fault()
        info = engine.get_active_fault_info()
        
        assert info is not None
        assert info['fault_id'] == fault.fault_id
        assert info['component_id'] == fault.component_id
        assert info['fault_name'] == fault.fault_name
    
    def test_no_active_fault(self):
        """Test behavior when no fault is active."""
        # Create engine with empty catalog
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("faults: []\n")
            f.flush()
            engine = FaultEngine(catalog_path=f.name)
        
        fault = engine.select_random_fault()
        assert fault is None
        
        info = engine.get_active_fault_info()
        assert info is None
