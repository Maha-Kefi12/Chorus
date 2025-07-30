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

def run_script(script_name):
    """Run a Python script with proper error handling"""
    safe_print(f"\n=== Running {script_name} ===")
    
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
    except FileNotFoundError:
        safe_print(f"❌ Python executable not found")
        return False
    except Exception as e:
        safe_print(f"❌ Error running {script_name}: {e}")
        return False
    
    safe_print(f"=== Finished {script_name} ===\n")

def print_all_xmls(output_base_dir):
    """Print all XML files in the output directory"""
    try:
        xml_files = glob.glob(os.path.join(output_base_dir, '**', '*.xml'), recursive=True)
        
        if not xml_files:
            safe_print("📄 No XML files found in output directory")
            return
        
        safe_print(f"📄 Found {len(xml_files)} XML file(s):")
        
        for xml_path in xml_files:
            safe_print(f"\n--- Content of {xml_path} ---")
            try:
                with open(xml_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        safe_print(content)
                    else:
                        safe_print("(Empty file)")
            except UnicodeDecodeError:
                safe_print(f"⚠️ Could not read {xml_path} - encoding issue")
            except Exception as e:
                safe_print(f"❌ Error reading {xml_path}: {e}")
            safe_print(f"--- End of {xml_path} ---\n")
            
    except Exception as e:
        safe_print(f"❌ Error scanning XML files: {e}")

def create_output_directories():
    """Create necessary output directories"""
    directories = [
        '.idea',
        '.idea/demo',
        '.idea/demo/aini',
        'output',
        'output/demo',
        'output/demo/aini'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            safe_print(f"📁 Created directory: {directory}")
        except Exception as e:
            safe_print(f"⚠️ Could not create directory {directory}: {e}")

def main():
    """Main function"""
    try:
        # Setup environment
        setup_environment()
        
        safe_print("🚀 Starting XML generation workflow...")
        safe_print(f"🐍 Python version: {sys.version}")
        safe_print(f"📁 Current directory: {os.getcwd()}")
        
        # Create output directories
        create_output_directories()
        
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
        
        # Run scripts
        successful_scripts = 0
        total_scripts = len(scripts)
        
        for script in scripts:
            if run_script(script):
                successful_scripts += 1
                # Print XML files after each successful script
                print_all_xmls(output_dir)
            else:
                safe_print(f"⚠️ Skipping XML output for {script} due to failure")
        
        # Final summary
        safe_print("\n" + "="*50)
        safe_print("📊 WORKFLOW SUMMARY")
        safe_print("="*50)
        safe_print(f"✅ Successful scripts: {successful_scripts}/{total_scripts}")
        safe_print(f"📁 Output directory: {output_dir}")
        
        if successful_scripts > 0:
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
