#!/usr/bin/env python3
"""
XML Generation Main Script
Handles the execution of all XML generation scripts
"""

import subprocess
import glob
import os
import sys
import locale
import time
import json
from pathlib import Path

def setup_environment():
    """Setup the environment for proper execution"""
    # Set console encoding for Windows
    if sys.platform == 'win32':
        try:
            # Try to set console to UTF-8
            os.system('chcp 65001 >nul 2>&1')
        except:
            pass
    
    # Set environment variables
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUNBUFFERED'] = '1'

def safe_print(text):
    """Safely print text that might contain Unicode characters on Windows"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Try to encode with error handling
        try:
            encoded = text.encode(sys.stdout.encoding or 'utf-8', errors='replace')
            print(encoded.decode(sys.stdout.encoding or 'utf-8'))
        except:
            # Last resort: print as ASCII
            print(text.encode('ascii', errors='replace').decode('ascii'))

def check_script_exists(script_name):
    """Check if a script exists and is accessible"""
    if not os.path.exists(script_name):
        return False, f"Script {script_name} not found"
    
    if not os.access(script_name, os.R_OK):
        return False, f"Script {script_name} is not readable"
    
    return True, "OK"

def detect_available_forms():
    """Detect available form types from the data files"""
    forms = []
    
    # Check output directory for transformed data
    output_dir = Path("output")
    if output_dir.exists():
        transformed_path = output_dir / "transformed_result.json"
        if transformed_path.exists():
            try:
                with open(transformed_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Look for forms in the data structure
                if 'originalJson' in data:
                    forms = list(data['originalJson'].keys())
                elif isinstance(data, dict):
                    # If it's a direct form structure
                    forms = list(data.keys())
                
                safe_print(f"🔍 Detected forms: {forms}")
            except Exception as e:
                safe_print(f"⚠️ Error reading transformed data: {e}")
    
    # If no forms detected, fall back to default
    if not forms:
        forms = ['aini']  # Default fallback
        safe_print(f"⚠️ No forms detected, using default: {forms}")
    
    return forms

def create_output_directories(forms):
    """Create necessary output directories for all detected forms"""
    base_dirs = [
        '.idea',
        '.idea/demo',
        'output',
        'output/demo'
    ]
    
    # Create base directories
    for directory in base_dirs:
        try:
            os.makedirs(directory, exist_ok=True)
            safe_print(f"📁 Created directory: {directory}")
        except Exception as e:
            safe_print(f"⚠️ Could not create directory {directory}: {e}")
    
    # Create form-specific directories
    for form_id in forms:
        directories = [
            f'.idea/demo/{form_id}',
            f'output/demo/{form_id}'
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                safe_print(f"📁 Created directory: {directory}")
            except Exception as e:
                safe_print(f"⚠️ Could not create directory {directory}: {e}")

def run_script(script_name, form_id=None):
    """Run a Python script with proper error handling"""
    safe_print(f"\n=== Running {script_name} ===")
    if form_id:
        safe_print(f"📋 Processing form: {form_id}")
    
    # Check if script exists
    exists, message = check_script_exists(script_name)
    if not exists:
        safe_print(f"❌ {message}")
        return False
    
    try:
        # Set environment for better encoding support
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUNBUFFERED'] = '1'
        
        # Add form_id to environment if provided
        if form_id:
            env['FORM_ID'] = form_id
        
        # Get current working directory
        cwd = os.getcwd()
        safe_print(f"📁 Working directory: {cwd}")
        safe_print(f"📄 Script path: {os.path.abspath(script_name)}")
        
        # Run the script
        result = subprocess.run(
            [sys.executable, script_name], 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            env=env,
            errors='replace',
            cwd=cwd,
            timeout=300  # 5 minutes timeout
        )
        
        # Print output
        if result.stdout:
            safe_print("📤 STDOUT:")
            safe_print(result.stdout)
        
        if result.stderr:
            safe_print("⚠️ STDERR:")
            safe_print(result.stderr)
        
        # Check return code
        if result.returncode == 0:
            safe_print(f"✅ {script_name} completed successfully")
            return True
        else:
            safe_print(f"❌ {script_name} failed with return code: {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        safe_print(f"⏰ {script_name} timed out after 5 minutes")
        return False
    except Exception as e:
        safe_print(f"❌ Error running {script_name}: {e}")
        return False

def print_all_xmls(output_base_dir):
    """Print all generated XML files"""
    try:
        safe_print(f"\n📄 XML files in {output_base_dir}:")
        xml_files = glob.glob(f"{output_base_dir}/**/*.xml", recursive=True)
        if xml_files:
            for xml_file in sorted(xml_files):
                safe_print(f"  📄 {xml_file}")
        else:
            safe_print(f"  ⚠️ No XML files found in {output_base_dir}")
    except Exception as e:
        safe_print(f"❌ Error scanning XML files: {e}")

def main():
    """Main function"""
    try:
        # Setup environment
        setup_environment()
        
        safe_print("🚀 Starting XML generation workflow...")
        safe_print(f"🐍 Python version: {sys.version}")
        safe_print(f"📁 Current directory: {os.getcwd()}")
        
        # Detect available forms
        forms = detect_available_forms()
        safe_print(f"📋 Forms to process: {forms}")
        
        # Create output directories for all forms
        create_output_directories(forms)
        
        output_dir = os.path.join('.idea', 'demo')
        safe_print(f"📁 Output directory: {output_dir}")

        # List of scripts to run in order
        scripts = [
            'combined.py',
            'mapping.py',
            'lov_impl_.py',
            'screenfinal.py'
        ]

        # Check all scripts before running
        safe_print("\n🔍 Checking scripts...")
        all_scripts_exist = True
        for script in scripts:
            exists, message = check_script_exists(script)
            if exists:
                safe_print(f"✅ {script}")
            else:
                safe_print(f"❌ {message}")
                all_scripts_exist = False
        
        if not all_scripts_exist:
            safe_print("\n⚠️ Some scripts are missing. Continuing with available scripts...")
        
        # Run scripts for each form
        total_successful = 0
        total_attempts = len(scripts) * len(forms)
        
        for form_id in forms:
            safe_print(f"\n🎯 Processing form: {form_id}")
            
            for script in scripts:
                if run_script(script, form_id):
                    total_successful += 1
                    # Print XML files after each successful script
                    print_all_xmls(output_dir)
                else:
                    safe_print(f"⚠️ Skipping XML output for {script} (form: {form_id}) due to failure")
        
        # Final summary
        safe_print("\n" + "="*50)
        safe_print("📊 WORKFLOW SUMMARY")
        safe_print("="*50)
        safe_print(f"✅ Successful script executions: {total_successful}/{total_attempts}")
        safe_print(f"📋 Forms processed: {forms}")
        safe_print(f"📁 Output directory: {output_dir}")
        
        if total_successful > 0:
            safe_print("✅ XML generation workflow completed!")
            safe_print("📄 Check the .idea/demo directory for generated XML files")
        else:
            safe_print("❌ No scripts completed successfully")
            safe_print("🔧 Please check the error messages above")
        
        # Final XML output
        safe_print("\n📄 Final XML files:")
        print_all_xmls(output_dir)
        
    except KeyboardInterrupt:
        safe_print("\n⚠️ Workflow interrupted by user")
    except Exception as e:
        safe_print(f"\n❌ Unexpected error: {e}")
        safe_print("🔧 Please check the error messages above")
    
    safe_print("\n🎯 Workflow finished")

if __name__ == "__main__":
    main()
