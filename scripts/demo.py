#!/usr/bin/env python3
"""
Demo Script
Demonstrates the complete validation and generation workflow
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validation.main_validator import MainValidator


def main():
    """Run complete demo"""
    print("🎬 Common Data Definitions - Complete Demo")
    print("=" * 60)
    print()
    
    # Step 1: Check prerequisites
    print("1️⃣ Checking prerequisites...")
    if not check_prerequisites():
        return 1
    
    # Step 2: Run validation
    print("\n2️⃣ Running complete validation...")
    validator = MainValidator()
    results = validator.validate_all(verbose=True)
    
    # Step 3: Save validation report
    print("\n3️⃣ Saving validation report...")
    save_success, save_message = validator.save_validation_report(results)
    print(f"   {'✅' if save_success else '❌'} {save_message}")
    
    # Step 4: Generate outputs if validation passed
    if results['overall_valid']:
        print("\n4️⃣ Generating outputs...")
        generate_outputs()
    else:
        print("\n❌ Validation failed - skipping output generation")
        print("Fix the validation errors and run again")
    
    # Step 5: Show summary
    print_demo_summary(results)
    
    return 0 if results['overall_valid'] else 1


def check_prerequisites():
    """Check if all required files exist"""
    required_files = [
        "data/parameters.yaml",
        "data/protocols.yaml", 
        "schemas/parameters_schema.json",
        "schemas/protocols_schema.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ Found: {file_path}")
        else:
            missing_files.append(file_path)
            print(f"   ❌ Missing: {file_path}")
    
    if missing_files:
        print(f"\n⚠️ Missing {len(missing_files)} required files")
        print("Run setup first: python scripts/setup_environment.py")
        return False
    
    print("   ✅ All prerequisites met")
    return True


def generate_outputs():
    """Generate database and other outputs"""
    try:
        # Import and run database generator
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from generators.database_generator import DatabaseGenerator
        
        db_generator = DatabaseGenerator()
        db_success, db_message = db_generator.generate_database()
        
        print(f"   Database: {'✅' if db_success else '❌'} {db_message}")
        
        # Placeholder for other generators
        print("   Documentation: 📝 Generator will be implemented next")
        print("   API: 📝 Generator will be implemented next")
        
        return db_success
        
    except Exception as e:
        print(f"   ❌ Output generation failed: {e}")
        return False


def print_demo_summary(results):
    """Print demo summary"""
    print("\n" + "="*60)
    print("🎯 DEMO SUMMARY")
    print("="*60)
    
    # Overall status
    status = "✅ SUCCESS" if results['overall_valid'] else "❌ FAILED"
    print(f"Overall Status: {status}")
    print(f"Duration: {results['validation_duration_seconds']:.2f} seconds")
    
    # Statistics
    summary = results['summary']
    print(f"\nValidation Steps: {summary['passed_steps']}/{summary['total_steps']} passed")
    print(f"Errors: {len(results['errors'])}")
    print(f"Warnings: {len(results['warnings'])}")
    
    # Generated files
    print(f"\n📁 Generated Files:")
    output_files = [
        "output/vehicle_params.db",
        "output/validation_reports/latest_report.json"
    ]
    
    for file_path in output_files:
        exists = Path(file_path).exists()
        print(f"   {'✅' if exists else '❌'} {file_path}")
    
    # Next steps
    print(f"\n🚀 What's Working:")
    print("   ✅ Directory structure created")
    print("   ✅ JSON Schema validation")
    print("   ✅ Custom business logic validation")
    print("   ✅ Cross-reference validation")
    print("   ✅ Database generation")
    print("   ✅ CLI tools")
    
    print(f"\n📝 What's Next:")
    print("   📋 Documentation generator")
    print("   🌐 API generator")
    print("   🔗 Integration with your existing app.py")
    
    # Usage examples
    print(f"\n💡 Try These Commands:")
    print("   python cli/validate.py --verbose      # Detailed validation")
    print("   python cli/validate.py --quick        # Quick status check")
    print("   python cli/generate_outputs.py        # Generate all outputs")
    print("   sqlite3 output/vehicle_params.db      # Explore database")
    
    # File locations
    print(f"\n📂 Important Files:")
    print("   📄 data/parameters.yaml               # Parameter definitions")
    print("   📄 data/protocols.yaml                # Protocol definitions")
    print("   📄 schemas/parameters_schema.json     # Parameter validation rules")
    print("   📄 schemas/protocols_schema.json      # Protocol validation rules")
    print("   🗄️ output/vehicle_params.db           # Generated SQLite database")
    print("   📊 output/validation_reports/          # Validation reports")
    
    # Integration with existing app
    print(f"\n🔗 Integration with Your Existing app.py:")
    print("   1. Your app.py can now use: output/vehicle_params.db")
    print("   2. Database has same structure as before, just validated")
    print("   3. Add validation before any data changes")
    print("   4. Use CLI tools for daily parameter management")
    
    print("="*60)


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)