"""
JSON Schema Validator for Vehicle Parameters and Protocols
Uses industry-standard JSON Schema for validation
"""

import json
import yaml
from jsonschema import validate, ValidationError, Draft7Validator
from pathlib import Path


class JSONSchemaValidator:
    """JSON Schema validator for YAML data files"""
    
    def __init__(self, schema_dir="schemas"):
        """Initialize with schema directory path"""
        self.schema_dir = Path(schema_dir)
        self.parameters_schema = self._load_schema("parameters_schema.json")
        self.protocols_schema = self._load_schema("protocols_schema.json")
    
    def _load_schema(self, schema_filename):
        """Load JSON schema from file"""
        schema_path = self.schema_dir / schema_filename
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema file {schema_path}: {e}")
    
    def validate_parameters_file(self, yaml_file_path):
        """
        Validate parameters YAML file against JSON schema
        
        Args:
            yaml_file_path (str): Path to parameters.yaml file
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        try:
            # Load YAML data
            with open(yaml_file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            # Validate against schema
            return self._validate_data(yaml_data, self.parameters_schema, "parameters")
            
        except yaml.YAMLError as e:
            return False, [f"YAML parsing error: {e}"]
        except FileNotFoundError:
            return False, [f"File not found: {yaml_file_path}"]
        except Exception as e:
            return False, [f"Validation error: {e}"]
    
    def validate_protocols_file(self, yaml_file_path):
        """
        Validate protocols YAML file against JSON schema
        
        Args:
            yaml_file_path (str): Path to protocols.yaml file
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        try:
            # Load YAML data
            with open(yaml_file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            # Validate against schema
            return self._validate_data(yaml_data, self.protocols_schema, "protocols")
            
        except yaml.YAMLError as e:
            return False, [f"YAML parsing error: {e}"]
        except FileNotFoundError:
            return False, [f"File not found: {yaml_file_path}"]
        except Exception as e:
            return False, [f"Validation error: {e}"]
    
    def _validate_data(self, data, schema, data_type):
        """
        Internal method to validate data against schema
        
        Args:
            data: YAML data to validate
            schema: JSON schema to validate against
            data_type: Type description for error messages
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        try:
            # Use Draft7Validator for detailed error reporting
            validator = Draft7Validator(schema)
            errors = []
            
            # Collect all validation errors
            for error in validator.iter_errors(data):
                error_path = " -> ".join(str(p) for p in error.path) if error.path else "root"
                error_msg = f"{data_type.title()} validation error at '{error_path}': {error.message}"
                errors.append(error_msg)
            
            if errors:
                return False, errors
            else:
                return True, ["Validation successful"]
                
        except Exception as e:
            return False, [f"Schema validation failed: {e}"]
    
    def validate_new_parameter_data(self, parameter_data):
        """
        Validate new parameter data (dict format) against schema
        
        Args:
            parameter_data (dict): Parameter data to validate
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        return self._validate_data(parameter_data, self.parameters_schema, "parameter")
    
    def validate_new_protocol_data(self, protocol_data):
        """
        Validate new protocol data (dict format) against schema
        
        Args:
            protocol_data (dict): Protocol data to validate
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        return self._validate_data(protocol_data, self.protocols_schema, "protocol")
    
    def get_schema_info(self):
        """Get information about loaded schemas"""
        return {
            "parameters_schema": {
                "title": self.parameters_schema.get("title", "Unknown"),
                "description": self.parameters_schema.get("description", "No description")
            },
            "protocols_schema": {
                "title": self.protocols_schema.get("title", "Unknown"),
                "description": self.protocols_schema.get("description", "No description")
            }
        }


# Example usage and testing
if __name__ == "__main__":
    # Test the validator
    validator = JSONSchemaValidator()
    
    print("Schema Information:")
    info = validator.get_schema_info()
    for schema_name, schema_info in info.items():
        print(f"  {schema_name}: {schema_info['title']}")
    
    # Test with sample files (if they exist)
    test_files = [
        ("data/parameters.yaml", validator.validate_parameters_file),
        ("data/protocols.yaml", validator.validate_protocols_file)
    ]
    
    for file_path, validate_func in test_files:
        if Path(file_path).exists():
            is_valid, messages = validate_func(file_path)
            print(f"\n{file_path}: {'✅ VALID' if is_valid else '❌ INVALID'}")
            for msg in messages:
                print(f"  - {msg}")
        else:
            print(f"\n{file_path}: File not found (skipping)")