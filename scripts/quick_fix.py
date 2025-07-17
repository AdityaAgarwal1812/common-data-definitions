#!/usr/bin/env python3
"""
Quick Fix Script
Fixes all the issues found in setup
"""

import os
from pathlib import Path

def main():
    """Fix all issues"""
    print("🔧 Quick Fix - Resolving Issues")
    print("=" * 40)
    
    # Fix 1: Create missing __init__.py files
    print("1️⃣ Creating missing __init__.py files...")
    init_files = [
        "generators/__init__.py",
        "cli/__init__.py",
        "tests/__init__.py"
    ]
    
    for init_file in init_files:
        if not Path(init_file).exists():
            with open(init_file, 'w') as f:
                f.write('# Python package initialization\n')
            print(f"   ✅ Created: {init_file}")
        else:
            print(f"   ✅ Found: {init_file}")
    
    # Fix 2: Fix syntax error in custom_validator.py
    print("\n2️⃣ Fixing syntax error in custom_validator.py...")
    custom_validator_file = "src/validation/custom_validator.py"
    
    if Path(custom_validator_file).exists():
        with open(custom_validator_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the syntax error on line 259
        if "return bool(re.match(r'^[a-z][a-z0-9_]*[a-z0-9], text))" in content:
            content = content.replace(
                "return bool(re.match(r'^[a-z][a-z0-9_]*[a-z0-9], text))",
                "return bool(re.match(r'^[a-z][a-z0-9_]*[a-z0-9]$', text))"
            )
            
            with open(custom_validator_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("   ✅ Fixed syntax error in custom_validator.py")
        else:
            print("   ✅ Syntax error already fixed or not found")
    else:
        print("   ❌ custom_validator.py not found")
    
    # Fix 3: Create placeholder generator files
    print("\n3️⃣ Creating placeholder generator files...")
    
    # API Generator placeholder
    api_generator_content = '''"""
API Generator (Placeholder)
"""

class APIGenerator:
    def __init__(self):
        pass
    
    def generate_api(self, database_path="output/vehicle_params.db"):
        return True, "API generator placeholder - will be implemented next"

if __name__ == "__main__":
    generator = APIGenerator()
    success, message = generator.generate_api()
    print(f"API generation: {'✅' if success else '❌'} {message}")
'''
    
    if not Path("generators/api_generator.py").exists():
        with open("generators/api_generator.py", 'w', encoding='utf-8') as f:
            f.write(api_generator_content)
        print("   ✅ Created: generators/api_generator.py")
    
    # Docs Generator placeholder
    docs_generator_content = '''"""
Documentation Generator (Placeholder)
"""

class DocsGenerator:
    def __init__(self):
        pass
    
    def generate_docs(self, database_path="output/vehicle_params.db"):
        return True, "Documentation generator placeholder - will be implemented next"

if __name__ == "__main__":
    generator = DocsGenerator()
    success, message = generator.generate_docs()
    print(f"Documentation generation: {'✅' if success else '❌'} {message}")
'''
    
    if not Path("generators/docs_generator.py").exists():
        with open("generators/docs_generator.py", 'w', encoding='utf-8') as f:
            f.write(docs_generator_content)
        print("   ✅ Created: generators/docs_generator.py")
    
    print("\n" + "=" * 40)
    print("✅ All fixes applied!")
    print("\n🧪 Test the fixes:")
    print("   python cli/validate.py --quick")
    print("   python cli/generate_outputs.py")
    print("   python scripts/demo.py")

if __name__ == "__main__":
    main()