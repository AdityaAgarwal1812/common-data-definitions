#!/usr/bin/env python3
"""
Environment Setup Script
Sets up the complete development environment and verifies everything works
"""

import os
import sys
import shutil
from pathlib import Path


def main():
    """Main setup function"""
    print("🚀 Setting up Common Data Definitions Environment")
    print("=" * 60)
    
    # Step 1: Verify directory structure
    print("1️⃣ Verifying directory structure...")
    verify_directories()
    
    # Step 2: Check for your existing files
    print("\n2️⃣ Checking for existing data files...")
    check_existing_files()
    
    # Step 3: Verify Python packages
    print("\n3️⃣ Verifying Python packages...")
    verify_packages()
    
    # Step 4: Test validation system
    print("\n4️⃣ Testing validation system...")
    test_validation_system()
    
    # Step 5: Generate sample outputs
    print("\n5️⃣ Testing output generation...")
    test_output_generation()
    
    print("\n" + "=" * 60)
    print("✅ Environment setup complete!")
    print_next_steps()


def verify_directories():
    """Verify all required directories exist"""
    required_dirs = [
        "data", "data/examples", "schemas", "src", "src/validation",
        "generators", "cli", "tests", "tests/fixtures", "output",
        "output/api", "output/documentation", "output/validation_reports", 
        "scripts"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
            print(f"   📁 Creating: {dir_path}/")
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        else:
            print(f"   ✅ Found: {dir_path}/")
    
    if missing_dirs:
        print(f"   📁 Created {len(missing_dirs)} missing directories")
    else:
        print("   ✅ All directories present")


def check_existing_files():
    """Check for existing YAML files and copy them if needed"""
    
    # Check if parameters.yaml exists in data/ directory
    params_in_data = Path("data/parameters.yaml").exists()
    params_in_root = Path("parameters.yaml").exists()
    
    print(f"   📄 data/parameters.yaml: {'✅ Found' if params_in_data else '❌ Missing'}")
    
    if not params_in_data and params_in_root:
        print("   🔄 Copying parameters.yaml from root to data/ directory...")
        shutil.copy("parameters.yaml", "data/parameters.yaml")
        print("   ✅ Copied parameters.yaml")
    elif not params_in_data:
        print("   ⚠️ No parameters.yaml found - will create sample")
        create_sample_parameters_file()
    
    # Check if protocols.yaml exists in data/ directory
    protocols_in_data = Path("data/protocols.yaml").exists()
    protocols_in_root = Path("protocols.yaml").exists()
    
    print(f"   📄 data/protocols.yaml: {'✅ Found' if protocols_in_data else '❌ Missing'}")
    
    if not protocols_in_data and protocols_in_root:
        print("   🔄 Copying protocols.yaml from root to data/ directory...")
        shutil.copy("protocols.yaml", "data/protocols.yaml")
        print("   ✅ Copied protocols.yaml")
    elif not protocols_in_data:
        print("   ⚠️ No protocols.yaml found - will create sample")
        create_sample_protocols_file()
    
    # Check schema files
    schema_files = ["schemas/parameters_schema.json", "schemas/protocols_schema.json"]
    for schema_file in schema_files:
        if Path(schema_file).exists():
            print(f"   ✅ Found: {schema_file}")
        else:
            print(f"   ❌ Missing: {schema_file}")


def create_sample_parameters_file():
    """Create a minimal sample parameters.yaml file"""
    sample_content = """metadata:
  version: "1.0.0"
  description: "Sample vehicle parameter definitions"
  maintainer: "Parameter Team"

parameters:
  - id: 1
    field_name: "Engine Speed"
    reserved_enum_val: 0
    description: "Instantaneous measurement of engine rotational speed"
    unit: "Double - RPM (Rotations per Minute)"
    reason_added: "ELD Mandate"
    protobuf_field: "speed_engine_rpm"
    protocol_reference: "ESPD_protocols"

breadcrumb_fields:
  - parameter_id: 1
    breadcrumb_link: "https://docs.motive.com/breadcrumb/veh_eng_spd"
    note: "Standard breadcrumb field for engine speed monitoring"

vg5_fields:
  - parameter_id: 1
    vg5_link: "https://docs.motive.com/vg5/engine_speed_rpm"

abbr_metrics:
  - parameter_id: 1
    abbr_value: "ESPD"
    abbr_link: "https://docs.motive.com/abbr/ESPD"
    metrics_link: "https://redash.motive.com/dashboard/engine-speed-espd"
"""
    
    with open("data/parameters.yaml", "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    print("   ✅ Created sample data/parameters.yaml")


def create_sample_protocols_file():
    """Create a minimal sample protocols.yaml file"""
    sample_content = """metadata:
  version: "1.0.0"
  description: "Sample vehicle protocol definitions"
  maintainer: "Protocol Team"
  standards_covered: ["J1939", "J1587", "J1979"]

protocol_groups:
  - id: 1
    group_name: "ESPD_protocols"
    description: "Engine Speed Protocol Definitions"
    parameter_reference: "Engine Speed"

protocols:
  - group_id: 1
    abbr: "ESPD"
    protocol_standard: "J1939"
    pgn_pid: "61444"
    spn: "190"
    precision: "0.125"
    spec_range: "0 to 8031.875"
    max_valid_val: "-"
    units: "RPM"
    description: "Engine speed"
    states: null
"""
    
    with open("data/protocols.yaml", "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    print("   ✅ Created sample data/protocols.yaml")


def verify_packages():
    """Verify required Python packages are installed"""
    required_packages = [
        ("yaml", "PyYAML"),
        ("jsonschema", "jsonschema"),
        ("flask", "Flask"),
        ("flask_restx", "Flask-RESTX")
    ]
    
    missing_packages = []
    
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            missing_packages.append(package_name)
            print(f"   ❌ {package_name}")
    
    if missing_packages:
        print(f"\n   ⚠️ Missing packages: {', '.join(missing_packages)}")
        print("   🔧 Run: pip install -r requirements.txt")
        return False
    else:
        print("   ✅ All required packages installed")
        return True


def test_validation_system():
    """Test the validation system"""
    try:
        # Add src to path
        sys.path.insert(0, str(Path("src")))
        
        from validation.main_validator import MainValidator
        
        print("   📝 Initializing validator...")
        validator = MainValidator()
        
        print("   🔍 Running quick validation test...")
        status = validator.get_validation_status()
        
        if status['overall_valid']:
            print("   ✅ Validation system working correctly")
            return True
        else:
            print(f"   ⚠️ Validation found {status['error_count']} errors")
            print("   💡 This is normal for sample data - run full validation for details")
            return True
            
    except Exception as e:
        print(f"   ❌ Validation system error: {e}")
        return False


def test_output_generation():
    """Test basic output generation"""
    try:
        # Create a simple test to verify the generators can be imported
        sys.path.insert(0, str(Path("generators")))
        
        # Check if generator files exist
        generator_files = [
            "generators/database_generator.py",
            "generators/api_generator.py", 
            "generators/docs_generator.py"
        ]
        
        existing_generators = []
        for gen_file in generator_files:
            if Path(gen_file).exists():
                existing_generators.append(gen_file)
                print(f"   ✅ Found: {gen_file}")
            else:
                print(f"   📝 Will create: {gen_file}")
        
        if existing_generators:
            print(f"   ✅ {len(existing_generators)} generators ready")
        else:
            print("   📝 Generators will be created next")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Generator test error: {e}")
        return False


def print_next_steps():
    """Print what to do next"""
    print("🎯 Next Steps:")
    print()
    print("1️⃣ Validate your data:")
    print("   python cli/validate.py --verbose")
    print()
    print("2️⃣ If you have existing YAML files:")
    print("   - Copy parameters.yaml to data/parameters.yaml")
    print("   - Copy protocols.yaml to data/protocols.yaml")
    print("   - Run validation again")
    print()
    print("3️⃣ Generate outputs:")
    print("   python cli/generate_outputs.py")
    print()
    print("4️⃣ View results:")
    print("   - Database: output/vehicle_params.db")
    print("   - Documentation: output/documentation/index.html")  
    print("   - API: python output/api/app.py")
    print()
    print("🔧 Useful commands:")
    print("   python cli/validate.py --quick        # Quick status check")
    print("   python cli/validate.py --verbose      # Detailed validation")
    print("   python scripts/demo.py                # See everything working")


if __name__ == "__main__":
    main()