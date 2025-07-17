#!/usr/bin/env python3
"""
CLI Tool: Submit Parameter/Protocol for PR
Simple command-line tool to validate and submit files from data/examples/
"""

import sys
import os
import yaml
import argparse
from datetime import datetime

# Add src to path for validation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from validation.main_validator import MainValidator

class SubmissionCLI:
    def __init__(self):
        self.validator = MainValidator()
    
    def submit_from_examples(self, parameter_file=None, protocol_file=None):
        """Submit files from data/examples/ for PR"""
        
        print("🚀 Vehicle Parameters Submission Tool")
        print("=" * 50)
        
        # Step 1: Check what files exist in examples
        examples_dir = "data/examples"
        
        if not os.path.exists(examples_dir):
            print(f"❌ Error: {examples_dir} directory not found")
            return False
        
        # Find files to process
        param_file_path = None
        protocol_file_path = None
        
        if parameter_file:
            param_file_path = os.path.join(examples_dir, parameter_file)
            if not os.path.exists(param_file_path):
                print(f"❌ Error: Parameter file not found: {param_file_path}")
                return False
        
        if protocol_file:
            protocol_file_path = os.path.join(examples_dir, protocol_file)
            if not os.path.exists(protocol_file_path):
                print(f"❌ Error: Protocol file not found: {protocol_file_path}")
                return False
        
        # Auto-detect files if not specified
        if not parameter_file and not protocol_file:
            print("🔍 Auto-detecting files in data/examples/...")
            for file in os.listdir(examples_dir):
                if file.endswith('.yaml') or file.endswith('.yml'):
                    if 'parameter' in file.lower():
                        param_file_path = os.path.join(examples_dir, file)
                        print(f"📄 Found parameter file: {file}")
                    elif 'protocol' in file.lower():
                        protocol_file_path = os.path.join(examples_dir, file)
                        print(f"📄 Found protocol file: {file}")
        
        if not param_file_path and not protocol_file_path:
            print("❌ No parameter or protocol files found in data/examples/")
            print("💡 Expected files like: new_parameter.yaml, new_protocol.yaml")
            return False
        
        # Step 2: Load and validate files
        print("\n📋 Loading and validating files...")
        
        param_data = None
        protocol_data = None
        
        if param_file_path:
            print(f"📖 Loading parameter file: {os.path.basename(param_file_path)}")
            try:
                with open(param_file_path, 'r', encoding='utf-8') as f:
                    param_data = yaml.safe_load(f)
                print("✅ Parameter file loaded successfully")
            except Exception as e:
                print(f"❌ Error loading parameter file: {e}")
                return False
        
        if protocol_file_path:
            print(f"📖 Loading protocol file: {os.path.basename(protocol_file_path)}")
            try:
                with open(protocol_file_path, 'r', encoding='utf-8') as f:
                    protocol_data = yaml.safe_load(f)
                print("✅ Protocol file loaded successfully")
            except Exception as e:
                print(f"❌ Error loading protocol file: {e}")
                return False
        
        # Step 3: Validate the data
        print("\n🔍 Running validation...")
        
        validation_errors = []
        
        if param_data:
            print("  📋 Validating parameter data...")
            param_valid, param_errors = self._validate_parameter_data(param_data)
            if not param_valid:
                validation_errors.extend([f"Parameter: {err}" for err in param_errors])
            else:
                print("  ✅ Parameter validation passed")
        
        if protocol_data:
            print("  🔧 Validating protocol data...")
            protocol_valid, protocol_errors = self._validate_protocol_data(protocol_data)
            if not protocol_valid:
                validation_errors.extend([f"Protocol: {err}" for err in protocol_errors])
            else:
                print("  ✅ Protocol validation passed")
        
        # Step 4: Show validation results
        if validation_errors:
            print("\n❌ VALIDATION FAILED!")
            print("🚫 Errors found:")
            for error in validation_errors:
                print(f"   • {error}")
            print("\n💡 Please fix these errors and try again.")
            return False
        
        print("\n✅ ALL VALIDATION PASSED!")
        
        # Step 5: Create PR-ready files
        print("\n📤 Creating PR submission...")
        
        submission_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Move files to pending folders
        os.makedirs("data/pending_parameters", exist_ok=True)
        os.makedirs("data/pending_protocols", exist_ok=True)
        
        created_files = []
        
        if param_data:
            pending_param_file = f"data/pending_parameters/param_{submission_id}.yaml"
            with open(pending_param_file, 'w', encoding='utf-8') as f:
                yaml.dump(param_data, f, default_flow_style=False, indent=2)
            created_files.append(pending_param_file)
            print(f"📄 Created: {pending_param_file}")
        
        if protocol_data:
            pending_protocol_file = f"data/pending_protocols/protocol_{submission_id}.yaml"
            with open(pending_protocol_file, 'w', encoding='utf-8') as f:
                yaml.dump(protocol_data, f, default_flow_style=False, indent=2)
            created_files.append(pending_protocol_file)
            print(f"📄 Created: {pending_protocol_file}")
        
        # Step 6: Show next steps
        print(f"\n🎉 SUCCESS! Submission ID: {submission_id}")
        print("\n📋 Next Steps:")
        print("1. 🔍 Review your submission files:")
        for file in created_files:
            print(f"   • {file}")
        print("2. 🔄 Create a Pull Request with these files")
        print("3. ✅ Admin will review and approve")
        print("4. 🚀 After approval, data will be added to main files")
        
        print(f"\n💡 To create PR, commit these files:")
        print(f"   git add {' '.join(created_files)}")
        print(f'   git commit -m "Add parameter/protocol submission {submission_id}"')
        print(f"   git push origin feature-branch")
        
        return True
    
    def _validate_parameter_data(self, param_data):
        """Validate parameter data structure"""
        try:
            # Check required top-level keys
            if 'parameters' not in param_data:
                return False, ["Missing 'parameters' section"]
            
            if not param_data['parameters']:
                return False, ["'parameters' section is empty"]
            
            # Validate each parameter
            for i, param in enumerate(param_data['parameters']):
                # Check required fields
                required_fields = ['id', 'field_name', 'description', 'unit', 'reason_added', 'protobuf_field', 'protocol_reference']
                for field in required_fields:
                    if field not in param:
                        return False, [f"Parameter {i+1}: Missing required field '{field}'"]
                    if not param[field]:
                        return False, [f"Parameter {i+1}: Field '{field}' cannot be empty"]
                
                # Validate data types
                if not isinstance(param['id'], int):
                    return False, [f"Parameter {i+1}: 'id' must be an integer"]
                
                if not isinstance(param['reserved_enum_val'], int):
                    return False, [f"Parameter {i+1}: 'reserved_enum_val' must be an integer"]
                
                # Validate description length
                if len(param['description']) < 10:
                    return False, [f"Parameter {i+1}: 'description' must be at least 10 characters"]
            
            return True, []
            
        except Exception as e:
            return False, [f"Validation error: {e}"]
    
    def _validate_protocol_data(self, protocol_data):
        """Validate protocol data structure"""
        try:
            # Check required top-level keys
            if 'protocol_groups' not in protocol_data:
                return False, ["Missing 'protocol_groups' section"]
            
            if 'protocols' not in protocol_data:
                return False, ["Missing 'protocols' section"]
            
            # Validate protocol groups
            for i, group in enumerate(protocol_data['protocol_groups']):
                required_fields = ['id', 'group_name', 'description', 'parameter_reference']
                for field in required_fields:
                    if field not in group:
                        return False, [f"Protocol group {i+1}: Missing required field '{field}'"]
                    if not group[field]:
                        return False, [f"Protocol group {i+1}: Field '{field}' cannot be empty"]
                
                # Validate group_name pattern
                if not group['group_name'].endswith('_protocols'):
                    return False, [f"Protocol group {i+1}: 'group_name' must end with '_protocols'"]
            
            # Validate protocols
            for i, protocol in enumerate(protocol_data['protocols']):
                required_fields = ['group_id', 'abbr', 'protocol_standard', 'pgn_pid', 'precision', 'spec_range', 'units', 'description']
                for field in required_fields:
                    if field not in protocol:
                        return False, [f"Protocol {i+1}: Missing required field '{field}'"]
                
                # Validate protocol standard
                valid_standards = ['J1939', 'J1587', 'J1979']
                if protocol['protocol_standard'] not in valid_standards:
                    return False, [f"Protocol {i+1}: 'protocol_standard' must be one of {valid_standards}"]
            
            return True, []
            
        except Exception as e:
            return False, [f"Validation error: {e}"]

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='Submit parameter/protocol files for PR')
    parser.add_argument('--parameter', '-p', help='Parameter YAML file in data/examples/')
    parser.add_argument('--protocol', '-r', help='Protocol YAML file in data/examples/')
    parser.add_argument('--auto', '-a', action='store_true', help='Auto-detect files in data/examples/')
    
    args = parser.parse_args()
    
    cli = SubmissionCLI()
    
    if args.auto or (not args.parameter and not args.protocol):
        # Auto-detect mode
        success = cli.submit_from_examples()
    else:
        # Specific files mode
        success = cli.submit_from_examples(args.parameter, args.protocol)
    
    if success:
        print("\n🎉 Submission completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Submission failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()