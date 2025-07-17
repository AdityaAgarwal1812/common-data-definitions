#!/usr/bin/env python3
"""
CLI Validation Tool
Main command-line interface for validating YAML files
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validation.main_validator import MainValidator


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Validate vehicle parameter and protocol YAML files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli/validate.py                                    # Validate with defaults
  python cli/validate.py --verbose                          # Show detailed output
  python cli/validate.py --parameters custom_params.yaml   # Custom parameters file
  python cli/validate.py --save-report                      # Save validation report
  python cli/validate.py --quick                           # Quick status check only
        """
    )
    
    parser.add_argument(
        "--parameters",
        default="data/parameters.yaml",
        help="Path to parameters YAML file (default: data/parameters.yaml)"
    )
    
    parser.add_argument(
        "--protocols", 
        default="data/protocols.yaml",
        help="Path to protocols YAML file (default: data/protocols.yaml)"
    )
    
    parser.add_argument(
        "--schemas",
        default="schemas",
        help="Directory containing JSON schema files (default: schemas)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed validation output"
    )
    
    parser.add_argument(
        "--save-report",
        action="store_true", 
        help="Save validation report to JSON file"
    )
    
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Quick status check only (no detailed output)"
    )
    
    parser.add_argument(
        "--output-report",
        default="output/validation_reports/latest_report.json",
        help="Output path for validation report"
    )
    
    args = parser.parse_args()
    
    # Initialize validator
    try:
        validator = MainValidator(schema_dir=args.schemas)
    except Exception as e:
        print(f"❌ Error initializing validator: {e}")
        return 1
    
    # Handle quick status check
    if args.quick:
        return run_quick_validation(validator, args)
    
    # Run full validation
    return run_full_validation(validator, args)


def run_quick_validation(validator, args):
    """Run quick validation status check"""
    print("🔍 Quick Validation Status Check")
    print("-" * 40)
    
    try:
        status = validator.get_validation_status(args.parameters, args.protocols)
        
        # Print status
        overall_status = "✅ VALID" if status['overall_valid'] else "❌ INVALID"
        print(f"Overall Status: {overall_status}")
        print(f"Error Count: {status['error_count']}")
        print(f"Warning Count: {status['warning_count']}")
        print(f"Duration: {status['duration_seconds']:.2f} seconds")
        print(f"Timestamp: {status['validation_timestamp']}")
        
        return 0 if status['overall_valid'] else 1
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1


def run_full_validation(validator, args):
    """Run full validation with detailed output"""
    print("🔍 Starting Validation")
    print("=" * 50)
    print(f"📄 Parameters: {args.parameters}")
    print(f"📄 Protocols: {args.protocols}")
    print(f"📂 Schemas: {args.schemas}")
    print()
    
    try:
        # Run validation
        results = validator.validate_all(
            parameters_file=args.parameters,
            protocols_file=args.protocols,
            verbose=args.verbose
        )
        
        # Save report if requested
        if args.save_report:
            save_success, save_message = validator.save_validation_report(
                results, args.output_report
            )
            print(f"\n📄 Report: {'✅' if save_success else '❌'} {save_message}")
        
        # Print summary if not verbose (verbose already prints summary)
        if not args.verbose:
            print_concise_summary(results)
        
        # Return appropriate exit code
        return 0 if results['overall_valid'] else 1
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1


def print_concise_summary(results):
    """Print concise validation summary"""
    print("\n" + "="*50)
    print("📊 VALIDATION RESULTS")
    print("="*50)
    
    # Overall status
    status_icon = "✅" if results['overall_valid'] else "❌"
    status_text = "PASSED" if results['overall_valid'] else "FAILED"
    print(f"Status: {status_icon} {status_text}")
    
    # Quick stats
    summary = results['summary']
    print(f"Steps: {summary['passed_steps']}/{summary['total_steps']} passed")
    print(f"Duration: {results['validation_duration_seconds']:.2f}s")
    
    # Show errors if any
    if results['errors']:
        print(f"\n❌ {len(results['errors'])} Error(s):")
        for i, error in enumerate(results['errors'][:5], 1):  # Show first 5 errors
            print(f"  {i}. {error}")
        if len(results['errors']) > 5:
            print(f"  ... and {len(results['errors']) - 5} more errors")
    
    # Show warnings if any
    if results['warnings']:
        print(f"\n⚠️ {len(results['warnings'])} Warning(s):")
        for i, warning in enumerate(results['warnings'][:3], 1):  # Show first 3 warnings
            print(f"  {i}. {warning}")
        if len(results['warnings']) > 3:
            print(f"  ... and {len(results['warnings']) - 3} more warnings")
    
    # Next steps
    print("\n🔧 Next Steps:")
    if results['overall_valid']:
        print("  ✅ Validation passed! You can now:")
        print("     - Generate outputs: python cli/generate_outputs.py")
        print("     - View documentation: open output/documentation/index.html")
    else:
        print("  ❌ Fix the errors above and run again:")
        print("     - Detailed output: python cli/validate.py --verbose")
        print("     - Check specific files and fix issues")
    
    print("="*50)


def check_prerequisites():
    """Check if all prerequisites are met"""
    issues = []
    
    # Check if required directories exist
    required_dirs = ["data", "schemas", "src/validation"]
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            issues.append(f"Missing directory: {dir_path}")
    
    # Check if required files exist
    required_files = [
        "schemas/parameters_schema.json",
        "schemas/protocols_schema.json"
    ]
    for file_path in required_files:
        if not Path(file_path).exists():
            issues.append(f"Missing file: {file_path}")
    
    return issues


if __name__ == "__main__":
    # Check prerequisites
    prereq_issues = check_prerequisites()
    if prereq_issues:
        print("❌ Prerequisites check failed:")
        for issue in prereq_issues:
            print(f"   - {issue}")
        print("\nPlease run the setup script first:")
        print("   python scripts/setup_environment.py")
        sys.exit(1)
    
    # Run main validation
    exit_code = main()
    sys.exit(exit_code)