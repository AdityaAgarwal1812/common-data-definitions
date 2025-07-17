#!/usr/bin/env python3
"""
Script to create the complete directory structure for common-data-definitions project
Run this script from the project root directory
"""

import os

def create_directory_structure():
    """Create all necessary directories for the project"""
    
    directories = [
        # Main directories
        "data",
        "data/examples",
        "schemas", 
        "src",
        "src/validation",
        "generators",
        "cli",
        "tests",
        "tests/fixtures",
        "output",
        "output/api",
        "output/documentation", 
        "output/validation_reports",
        "scripts"
    ]
    
    print("Creating directory structure...")
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}/")
    
    # Create __init__.py files for Python packages
    init_files = [
        "src/__init__.py",
        "src/validation/__init__.py", 
        "generators/__init__.py",
        "cli/__init__.py",
        "tests/__init__.py"
    ]
    
    print("\nCreating __init__.py files...")
    for init_file in init_files:
        with open(init_file, 'w') as f:
            f.write('# Python package initialization\n')
        print(f"✅ Created: {init_file}")
    
    # Create .gitignore
    gitignore_content = """# Generated outputs
output/
*.db
*.sqlite

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("✅ Created: .gitignore")
    
    print("\n🎉 Directory structure created successfully!")
    print("\nNext steps:")
    print("1. Copy your existing YAML files to data/ directory")
    print("2. Copy your validation code to src/validation/")
    print("3. Run the setup script to verify everything works")

if __name__ == "__main__":
    create_directory_structure()