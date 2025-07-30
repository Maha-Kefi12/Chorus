import subprocess
import glob
import os
import sys

def print_all_xmls(output_base_dir):
    xml_files = glob.glob(os.path.join(output_base_dir, '**', '*.xml'), recursive=True)
    for xml_path in xml_files:
        print(f"\n--- Content of {xml_path} ---")
        with open(xml_path, 'r', encoding='utf-8') as f:
            print(f.read())
        print(f"--- End of {xml_path} ---\n")

def run_script(script_name):
    print(f"\n=== Running {script_name} ===")
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
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

    for script in scripts:
        run_script(script)
        print_all_xmls(output_dir)

if __name__ == "__main__":
    main()
