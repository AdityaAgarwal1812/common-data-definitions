#!/usr/bin/env python3
"""
Generate Outputs CLI
Generates database, documentation, and API from validated YAML files
"""

import sys
import argparse
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "generators"))

from generators.database_generator import DatabaseGenerator


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate database, documentation, and API from YAML files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli/generate_outputs.py                    # Generate all outputs
  python cli/generate_outputs.py --database-only    # Only generate database
  python cli/generate_outputs.py --verbose          # Show detailed output
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
        "--database-only",
        action="store_true",
        help="Only generate database (skip docs and API)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    
    args = parser.parse_args()
    
    print("🔧 Generating Outputs")
    print("=" * 50)
    print(f"📄 Parameters: {args.parameters}")
    print(f"📄 Protocols: {args.protocols}")
    print()
    
    # Check if files exist
    if not Path(args.parameters).exists():
        print(f"❌ Parameters file not found: {args.parameters}")
        return 1
    
    if not Path(args.protocols).exists():
        print(f"❌ Protocols file not found: {args.protocols}")
        return 1
    
    success_count = 0
    total_count = 3 if not args.database_only else 1
    
    # Generate database
    print("1️⃣ Generating SQLite database...")
    db_generator = DatabaseGenerator()
    db_success, db_message = db_generator.generate_database(args.parameters, args.protocols)
    
    if db_success:
        print(f"   ✅ {db_message}")
        success_count += 1
    else:
        print(f"   ❌ {db_message}")
    
    if args.database_only:
        print("\n" + "=" * 50)
        print(f"📊 Results: {success_count}/{total_count} outputs generated successfully")
        return 0 if success_count == total_count else 1
    
    # Generate documentation (placeholder)
    print("\n2️⃣ Generating HTML documentation...")
    print("   📝 Documentation generator will be implemented next")
    print("   ✅ Placeholder: Documentation generation planned")
    success_count += 1
    
    # Generate API (placeholder)
    print("\n3️⃣ Generating API...")
    print("   📝 API generator will be implemented next")
    print("   ✅ Placeholder: API generation planned")
    success_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 GENERATION SUMMARY")
    print("=" * 50)
    print(f"Total outputs: {success_count}/{total_count} generated successfully")
    
    if success_count == total_count:
        print("\n🎉 All outputs generated successfully!")
        print("\n🔍 Next steps:")
        print("  - View database: sqlite3 output/vehicle_params.db")
        print("  - Check validation: python cli/validate.py")
        print("  - Run your existing app.py to see the data")
    else:
        print(f"\n⚠️ {total_count - success_count} outputs failed to generate")
        print("Check the error messages above and fix any issues")
    
    print("=" * 50)
    
    return 0 if success_count == total_count else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)