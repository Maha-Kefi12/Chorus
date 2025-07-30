#!/usr/bin/env python3
"""
Debug script for main.py issues
"""

import os
import sys
import subprocess
import traceback

def check_python_environment():
    """Check Python environment"""
    print("🐍 Python Environment Check")
    print("=" * 40)
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {sys.platform}")
    print(f"Current directory: {os.getcwd()}")
    print()

def check_required_scripts():
    """Check if required scripts exist"""
    print("📄 Required Scripts Check")
    print("=" * 40)
    
    required_scripts = [
        'combined.py',
        'mapping.py',
        'lov_impl_.py',
        'screenfinal.py'
    ]
    
    for script in required_scripts:
        if os.path.exists(script):
            size = os.path.getsize(script)
            print(f"✅ {script} - {size} bytes")
        else:
            print(f"❌ {script} - NOT FOUND")
    print()

def check_output_directories():
    """Check output directories"""
    print("📁 Output Directories Check")
    print("=" * 40)
    
    directories = [
        '.idea',
        '.idea/demo',
        '.idea/demo/aini',
        'output',
        'output/demo',
        'output/demo/aini'
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ {directory} - EXISTS")
        else:
            print(f"❌ {directory} - NOT FOUND")
    print()

def test_script_execution(script_name):
    """Test if a script can be executed"""
    print(f"🧪 Testing {script_name}")
    print("-" * 30)
    
    if not os.path.exists(script_name):
        print(f"❌ {script_name} not found")
        return False
    
    try:
        # Test basic syntax
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', script_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ {script_name} - Syntax OK")
        else:
            print(f"❌ {script_name} - Syntax Error:")
            print(result.stderr)
            return False
        
        # Test import
        result = subprocess.run(
            [sys.executable, '-c', f'import {script_name[:-3]}'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ {script_name} - Import OK")
        else:
            print(f"⚠️ {script_name} - Import issues:")
            print(result.stderr)
        
        return True
        
    except subprocess.TimeoutExpired:
        print(f"⏰ {script_name} - Timeout")
        return False
    except Exception as e:
        print(f"❌ {script_name} - Error: {e}")
        return False

def test_main_execution():
    """Test main.py execution"""
    print("🚀 Testing main.py execution")
    print("=" * 40)
    
    try:
        result = subprocess.run(
            [sys.executable, 'main.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT length: {len(result.stdout)}")
        print(f"STDERR length: {len(result.stderr)}")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ main.py execution timed out")
        return False
    except Exception as e:
        print(f"❌ Error executing main.py: {e}")
        return False

def check_file_permissions():
    """Check file permissions"""
    print("🔐 File Permissions Check")
    print("=" * 40)
    
    files_to_check = [
        'main.py',
        'combined.py',
        'mapping.py',
        'lov_impl_.py',
        'screenfinal.py'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            # Check read permission
            if os.access(file, os.R_OK):
                print(f"✅ {file} - Readable")
            else:
                print(f"❌ {file} - Not readable")
            
            # Check execute permission
            if os.access(file, os.X_OK):
                print(f"✅ {file} - Executable")
            else:
                print(f"⚠️ {file} - Not executable")
        else:
            print(f"❌ {file} - Not found")
    print()

def main():
    """Main diagnostic function"""
    print("🔍 Main.py Diagnostic Tool")
    print("=" * 50)
    print()
    
    # Run all checks
    check_python_environment()
    check_required_scripts()
    check_output_directories()
    check_file_permissions()
    
    # Test individual scripts
    print("🧪 Individual Script Tests")
    print("=" * 40)
    
    scripts = ['combined.py', 'mapping.py', 'lov_impl_.py', 'screenfinal.py']
    for script in scripts:
        test_script_execution(script)
        print()
    
    # Test main execution
    success = test_main_execution()
    
    print("=" * 50)
    if success:
        print("✅ Main.py diagnostic completed successfully")
    else:
        print("❌ Main.py diagnostic found issues")
    
    print("\n💡 Recommendations:")
    print("- Make sure all required scripts exist")
    print("- Check file permissions")
    print("- Verify Python environment")
    print("- Check for syntax errors in scripts")

if __name__ == "__main__":
    main() 