"""
Tests for validation system
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validation.main_validator import MainValidator
from validation.json_validator import JSONSchemaValidator
from validation.custom_validator import CustomValidator
from validation.cross_reference_validator import CrossReferenceValidator


class TestValidation(unittest.TestCase):
    """Test validation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = MainValidator()
        self.test_parameters_file = "tests/fixtures/valid_parameters.yaml"
        self.test_protocols_file = "tests/fixtures/valid_protocols.yaml"
    
    def test_json_schema_validator_init(self):
        """Test JSON schema validator initialization"""
        json_validator = JSONSchemaValidator()
        schema_info = json_validator.get_schema_info()
        
        self.assertIn('parameters_schema', schema_info)
        self.assertIn('protocols_schema', schema_info)
    
    def test_custom_validator_init(self):
        """Test custom validator initialization"""
        custom_validator = CustomValidator()
        
        self.assertIn('J1939', custom_validator.valid_protocol_standards)
        self.assertIn('ELD Mandate', custom_validator.valid_reasons)
    
    def test_cross_reference_validator_init(self):
        """Test cross-reference validator initialization"""
        cross_ref_validator = CrossReferenceValidator()
        
        # Should initialize without errors
        self.assertIsNotNone(cross_ref_validator)
    
    def test_main_validator_init(self):
        """Test main validator initialization"""
        main_validator = MainValidator()
        
        self.assertIsNotNone(main_validator.json_validator)
        self.assertIsNotNone(main_validator.custom_validator)
        self.assertIsNotNone(main_validator.cross_ref_validator)
    
    def test_validation_with_valid_files(self):
        """Test validation with valid files"""
        # Create test files if they don't exist
        self._create_test_files_if_needed()
        
        # Run validation
        results = self.validator.validate_all(
            parameters_file="data/parameters.yaml",
            protocols_file="data/protocols.yaml",
            verbose=False
        )
        
        # Check results structure
        self.assertIn('overall_valid', results)
        self.assertIn('validation_steps', results)
        self.assertIn('errors', results)
        self.assertIn('warnings', results)
    
    def _create_test_files_if_needed(self):
        """Create basic test files if they don't exist"""
        if not Path("data/parameters.yaml").exists():
            # Create minimal test file
            minimal_params = """
metadata:
  version: "1.0.0"
  maintainer: "Test"

parameters:
  - id: 1
    field_name: "Test Parameter"
    reserved_enum_val: 0
    description: "Test parameter for validation"
    unit: "Test Unit"
    reason_added: "ELD Mandate"
    protobuf_field: "test_param"
    protocol_reference: "TEST_protocols"

breadcrumb_fields: []
vg5_fields: []
abbr_metrics: []
"""
            Path("data").mkdir(exist_ok=True)
            with open("data/parameters.yaml", "w") as f:
                f.write(minimal_params)
        
        if not Path("data/protocols.yaml").exists():
            minimal_protocols = """
metadata:
  version: "1.0.0"
  maintainer: "Test"

protocol_groups:
  - id: 1
    group_name: "TEST_protocols"
    description: "Test protocol group"
    parameter_reference: "Test Parameter"

protocols:
  - group_id: 1
    abbr: "TEST"
    protocol_standard: "J1939"
    pgn_pid: "12345"
    spn: "100"
    precision: "1"
    spec_range: "0-100"
    max_valid_val: "100"
    units: "test"
    description: "Test protocol"
    states: null
"""
            with open("data/protocols.yaml", "w") as f:
                f.write(minimal_protocols)


if __name__ == "__main__":
    unittest.main()