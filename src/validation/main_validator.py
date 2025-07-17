"""
Main Validation Orchestrator
Coordinates all validation steps and provides unified validation interface
"""

from pathlib import Path
import json
from datetime import datetime

from .json_validator import JSONSchemaValidator
from .custom_validator import CustomValidator
from .cross_reference_validator import CrossReferenceValidator


class MainValidator:
    """Main validation orchestrator that runs all validation steps"""
    
    def __init__(self, schema_dir="schemas"):
        """Initialize all validators"""
        self.json_validator = JSONSchemaValidator(schema_dir)
        self.custom_validator = CustomValidator()
        self.cross_ref_validator = CrossReferenceValidator()
        
    def validate_all(self, parameters_file="data/parameters.yaml", protocols_file="data/protocols.yaml", verbose=False):
        """
        Run complete validation workflow
        
        Args:
            parameters_file (str): Path to parameters.yaml
            protocols_file (str): Path to protocols.yaml
            verbose (bool): Show detailed output
            
        Returns:
            dict: Complete validation results
        """
        validation_start = datetime.now()
        
        results = {
            'validation_timestamp': validation_start.isoformat(),
            'files_validated': {
                'parameters_file': parameters_file,
                'protocols_file': protocols_file
            },
            'overall_valid': False,
            'validation_steps': {},
            'summary': {},
            'errors': [],
            'warnings': []
        }
        
        if verbose:
            print("🔍 Starting comprehensive validation...")
            print(f"📁 Parameters file: {parameters_file}")
            print(f"📁 Protocols file: {protocols_file}")
            print()
        
        # Step 1: Check file existence
        files_exist = self._check_file_existence(parameters_file, protocols_file, verbose)
        if not files_exist:
            results['validation_steps']['file_existence'] = {
                'status': 'failed',
                'errors': ['Required files do not exist']
            }
            results['errors'].append('Required files do not exist')
            return results
        
        # Step 2: JSON Schema Validation
        if verbose:
            print("1️⃣ Running JSON Schema validation...")
        
        schema_results = self._run_json_schema_validation(parameters_file, protocols_file, verbose)
        results['validation_steps']['json_schema'] = schema_results
        
        # Step 3: Custom Business Logic Validation
        if verbose:
            print("\n2️⃣ Running custom business logic validation...")
        
        custom_results = self._run_custom_validation(parameters_file, protocols_file, verbose)
        results['validation_steps']['custom_logic'] = custom_results
        
        # Step 4: Cross-Reference Validation
        if verbose:
            print("\n3️⃣ Running cross-reference validation...")
        
        cross_ref_results = self._run_cross_reference_validation(parameters_file, protocols_file, verbose)
        results['validation_steps']['cross_references'] = cross_ref_results
        
        # Step 5: Generate summary
        results['summary'] = self._generate_summary(results['validation_steps'])
        results['overall_valid'] = results['summary']['all_passed']
        
        # Collect all errors and warnings
        for step_name, step_results in results['validation_steps'].items():
            if step_results['status'] == 'failed':
                results['errors'].extend(step_results.get('errors', []))
            results['warnings'].extend(step_results.get('warnings', []))
        
        validation_end = datetime.now()
        results['validation_duration_seconds'] = (validation_end - validation_start).total_seconds()
        
        if verbose:
            self._print_validation_summary(results)
        
        return results
    
    def _check_file_existence(self, parameters_file, protocols_file, verbose):
        """Check if required files exist"""
        params_exist = Path(parameters_file).exists()
        protocols_exist = Path(protocols_file).exists()
        
        if verbose:
            print(f"📄 {parameters_file}: {'✅ Found' if params_exist else '❌ Not found'}")
            print(f"📄 {protocols_file}: {'✅ Found' if protocols_exist else '❌ Not found'}")
        
        return params_exist and protocols_exist
    
    def _run_json_schema_validation(self, parameters_file, protocols_file, verbose):
        """Run JSON Schema validation"""
        results = {
            'status': 'passed',
            'errors': [],
            'warnings': [],
            'details': {}
        }
        
        # Validate parameters file
        params_valid, params_messages = self.json_validator.validate_parameters_file(parameters_file)
        results['details']['parameters'] = {
            'valid': params_valid,
            'messages': params_messages
        }
        
        if verbose:
            print(f"   📋 Parameters: {'✅ Valid' if params_valid else '❌ Invalid'}")
            if not params_valid:
                for msg in params_messages:
                    print(f"      - {msg}")
        
        # Validate protocols file
        protocols_valid, protocols_messages = self.json_validator.validate_protocols_file(protocols_file)
        results['details']['protocols'] = {
            'valid': protocols_valid,
            'messages': protocols_messages
        }
        
        if verbose:
            print(f"   ⚙️ Protocols: {'✅ Valid' if protocols_valid else '❌ Invalid'}")
            if not protocols_valid:
                for msg in protocols_messages:
                    print(f"      - {msg}")
        
        # Set overall status
        if not params_valid or not protocols_valid:
            results['status'] = 'failed'
            results['errors'].extend(params_messages if not params_valid else [])
            results['errors'].extend(protocols_messages if not protocols_valid else [])
        
        return results
    
    def _run_custom_validation(self, parameters_file, protocols_file, verbose):
        """Run custom business logic validation"""
        results = {
            'status': 'passed',
            'errors': [],
            'warnings': [],
            'details': {}
        }
        
        # Validate parameters custom logic
        params_valid, params_messages = self.custom_validator.validate_parameters_business_logic(parameters_file)
        results['details']['parameters_custom'] = {
            'valid': params_valid,
            'messages': params_messages
        }
        
        if verbose:
            print(f"   📋 Parameters custom logic: {'✅ Valid' if params_valid else '❌ Invalid'}")
            if not params_valid:
                for msg in params_messages:
                    print(f"      - {msg}")
        
        # Validate protocols custom logic
        protocols_valid, protocols_messages = self.custom_validator.validate_protocols_business_logic(protocols_file)
        results['details']['protocols_custom'] = {
            'valid': protocols_valid,
            'messages': protocols_messages
        }
        
        if verbose:
            print(f"   ⚙️ Protocols custom logic: {'✅ Valid' if protocols_valid else '❌ Invalid'}")
            if not protocols_valid:
                for msg in protocols_messages:
                    print(f"      - {msg}")
        
        # Set overall status
        if not params_valid or not protocols_valid:
            results['status'] = 'failed'
            results['errors'].extend(params_messages if not params_valid else [])
            results['errors'].extend(protocols_messages if not protocols_valid else [])
        
        return results
    
    def _run_cross_reference_validation(self, parameters_file, protocols_file, verbose):
        """Run cross-reference validation"""
        results = {
            'status': 'passed',
            'errors': [],
            'warnings': [],
            'details': {}
        }
        
        # Basic cross-reference validation
        cross_valid, cross_messages = self.cross_ref_validator.validate_cross_references(
            parameters_file, protocols_file
        )
        results['details']['cross_references'] = {
            'valid': cross_valid,
            'messages': cross_messages
        }
        
        if verbose:
            print(f"   🔗 Cross-references: {'✅ Valid' if cross_valid else '❌ Invalid'}")
            if not cross_valid:
                for msg in cross_messages:
                    print(f"      - {msg}")
        
        # Bidirectional consistency validation
        bidirectional_valid, bidirectional_messages = self.cross_ref_validator.validate_bidirectional_consistency(
            parameters_file, protocols_file
        )
        results['details']['bidirectional_consistency'] = {
            'valid': bidirectional_valid,
            'messages': bidirectional_messages
        }
        
        if verbose:
            print(f"   ↔️ Bidirectional consistency: {'✅ Valid' if bidirectional_valid else '❌ Invalid'}")
            if not bidirectional_valid:
                for msg in bidirectional_messages:
                    print(f"      - {msg}")
        
        # Set overall status
        if not cross_valid or not bidirectional_valid:
            results['status'] = 'failed'
            results['errors'].extend(cross_messages if not cross_valid else [])
            results['errors'].extend(bidirectional_messages if not bidirectional_valid else [])
        
        return results
    
    def _generate_summary(self, validation_steps):
        """Generate validation summary"""
        summary = {
            'total_steps': len(validation_steps),
            'passed_steps': 0,
            'failed_steps': 0,
            'all_passed': True,
            'step_results': {}
        }
        
        for step_name, step_results in validation_steps.items():
            if step_results['status'] == 'passed':
                summary['passed_steps'] += 1
            else:
                summary['failed_steps'] += 1
                summary['all_passed'] = False
            
            summary['step_results'][step_name] = step_results['status']
        
        return summary
    
    def _print_validation_summary(self, results):
        """Print detailed validation summary"""
        print("\n" + "="*60)
        print("🎯 VALIDATION SUMMARY")
        print("="*60)
        
        # Overall result
        overall_status = "✅ PASSED" if results['overall_valid'] else "❌ FAILED"
        print(f"Overall Result: {overall_status}")
        print(f"Duration: {results['validation_duration_seconds']:.2f} seconds")
        print()
        
        # Step-by-step results
        print("📊 Step Results:")
        for step_name, step_data in results['validation_steps'].items():
            status = "✅ PASSED" if step_data['status'] == 'passed' else "❌ FAILED"
            print(f"  {step_name}: {status}")
        print()
        
        # Summary statistics
        summary = results['summary']
        print("📈 Statistics:")
        print(f"  Total validation steps: {summary['total_steps']}")
        print(f"  Passed steps: {summary['passed_steps']}")
        print(f"  Failed steps: {summary['failed_steps']}")
        print()
        
        # Errors (if any)
        if results['errors']:
            print("❌ Errors Found:")
            for error in results['errors']:
                print(f"  - {error}")
            print()
        
        # Warnings (if any)
        if results['warnings']:
            print("⚠️ Warnings:")
            for warning in results['warnings']:
                print(f"  - {warning}")
            print()
        
        # Next steps
        if results['overall_valid']:
            print("🎉 All validations passed! You can now:")
            print("  - Generate database: python cli/generate_outputs.py")
            print("  - View documentation: open output/documentation/index.html")
            print("  - Start API server: python output/api/app.py")
        else:
            print("🔧 Fix the errors above and run validation again:")
            print("  python cli/validate.py --verbose")
        
        print("="*60)
    
    def save_validation_report(self, results, output_file="output/validation_reports/latest_report.json"):
        """Save validation results to JSON file"""
        try:
            # Ensure output directory exists
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save results
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            return True, f"Validation report saved to {output_file}"
            
        except Exception as e:
            return False, f"Failed to save validation report: {e}"
    
    def validate_new_parameter_data(self, new_parameter_data):
        """
        Validate new parameter data before adding to files
        
        Args:
            new_parameter_data (dict): New parameter data to validate
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        # JSON Schema validation
        json_valid, json_messages = self.json_validator.validate_new_parameter_data(new_parameter_data)
        if not json_valid:
            errors.extend(json_messages)
        
        # Custom validation would go here
        # (This would need to be adapted for individual parameter validation)
        
        return len(errors) == 0, errors if errors else ["New parameter data validation passed"]
    
    def validate_new_protocol_data(self, new_protocol_data):
        """
        Validate new protocol data before adding to files
        
        Args:
            new_protocol_data (dict): New protocol data to validate
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        # JSON Schema validation
        json_valid, json_messages = self.json_validator.validate_new_protocol_data(new_protocol_data)
        if not json_valid:
            errors.extend(json_messages)
        
        # Custom validation would go here
        # (This would need to be adapted for individual protocol validation)
        
        return len(errors) == 0, errors if errors else ["New protocol data validation passed"]
    
    def get_validation_status(self, parameters_file="data/parameters.yaml", protocols_file="data/protocols.yaml"):
        """
        Get quick validation status without detailed output
        
        Args:
            parameters_file (str): Path to parameters.yaml
            protocols_file (str): Path to protocols.yaml
            
        Returns:
            dict: Quick validation status
        """
        results = self.validate_all(parameters_file, protocols_file, verbose=False)
        
        return {
            'overall_valid': results['overall_valid'],
            'error_count': len(results['errors']),
            'warning_count': len(results['warnings']),
            'validation_timestamp': results['validation_timestamp'],
            'duration_seconds': results['validation_duration_seconds']
        }


# Example usage and testing
if __name__ == "__main__":
    # Test the main validator
    validator = MainValidator()
    
    print("Testing Main Validator...")
    print("=" * 50)
    
    # Run complete validation
    results = validator.validate_all(verbose=True)
    
    # Save validation report
    save_success, save_message = validator.save_validation_report(results)
    print(f"\nReport saved: {'✅' if save_success else '❌'} {save_message}")
    
    # Quick status check
    print("\nQuick Status Check:")
    status = validator.get_validation_status()
    for key, value in status.items():
        print(f"  {key}: {value}")