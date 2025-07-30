# -*- coding: utf-8 -*-
"""
Windows-compatible version of main.py
Handles Unicode encoding issues on Windows systems
"""
import subprocess
import glob
import os
import sys
import codecs

# Force UTF-8 output on Windows
if sys.platform.startswith('win'):
    # Reconfigure stdout and stderr for UTF-8
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def print_all_xmls(output_base_dir):
    """Print contents of all XML files in the output directory"""
    xml_files = glob.glob(os.path.join(output_base_dir, '**', '*.xml'), recursive=True)
    for xml_path in xml_files:
        print(f"\n--- Content of {xml_path} ---")
        try:
            with open(xml_path, 'r', encoding='utf-8') as f:
                print(f.read())
        except UnicodeDecodeError:
            # Fallback to different encodings
            for encoding in ['latin1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(xml_path, 'r', encoding=encoding) as f:
                        print(f.read())
                    break
                except UnicodeDecodeError:
                    continue
        print(f"--- End of {xml_path} ---\n")

def run_script(script_name):
    """Run a Python script and capture its output"""
    print(f"\n=== Running {script_name} ===")
    try:
        # Use shell=True on Windows for better compatibility
        result = subprocess.run(
            [sys.executable, script_name], 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            shell=True if sys.platform.startswith('win') else False
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
    except Exception as e:
        print(f"Error running {script_name}: {e}")
    
    print(f"=== Finished {script_name} ===\n")

def main():
    """Main function to run all scripts in sequence"""
    # Set console code page to UTF-8 on Windows
    if sys.platform.startswith('win'):
        try:
            os.system('chcp 65001 >nul 2>&1')
        except:
            pass
    
    output_dir = os.path.join('.idea', 'demo')

    # List of scripts to run in order
    scripts = [
        'combined.py',
        'mapping.py',
        'lov_impl_.py',
        'screenfinal.py'
    ]

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print("Starting XML generation workflow...")
    print(f"Output directory: {output_dir}")
    print("-" * 50)

    for script in scripts:
        if os.path.exists(script):
            run_script(script)
            print_all_xmls(output_dir)
        else:
            print(f"WARNING: Script {script} not found, skipping...")
    
    print("-" * 50)
    print("SUCCESS: XML generation workflow completed!")

if __name__ == "__main__":
    main()