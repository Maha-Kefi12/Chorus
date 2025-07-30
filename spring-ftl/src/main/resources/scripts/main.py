import subprocess
import glob
import os
import sys

def print_all_xmls(output_base_dir):
    xml_files = glob.glob(os.path.join(output_base_dir, '**', '*.xml'), recursive=True)
    for xml_path in xml_files:
        print(f"\n--- Content of {xml_path} ---")
        try:
            with open(xml_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Safe print for Windows console
                try:
                    print(content)
                except UnicodeEncodeError:
                    # Fallback: print as bytes or skip problematic characters
                    print(content.encode('utf-8', errors='replace').decode('utf-8'))
        except Exception as e:
            print(f"Error reading {xml_path}: {e}")
        print(f"--- End of {xml_path} ---\n")

def run_script(script_name):
    print(f"\n=== Running {script_name} ===")
    try:
        result = subprocess.run([sys.executable, script_name], capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except UnicodeEncodeError:
        # Fallback for Windows console
        result = subprocess.run([sys.executable, script_name], capture_output=True, text=True, encoding='utf-8', errors='replace')
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    print(f"=== Finished {script_name} ===\n")

def main():
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

    for script in scripts:
        if os.path.exists(script):
            run_script(script)
            print_all_xmls(output_dir)
        else:
            print(f"⚠️ Warning: Script {script} not found, skipping...")
    
    print("✅ XML generation workflow completed!")

if __name__ == "__main__":
    main()
