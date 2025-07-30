import os
import re
from pathlib import Path

SRC_DIR = Path("spring-ftl/src/main/java")
OUTPUT_DIR = Path("httpRequests")
BASE_URL = "http://localhost:8080"

http_methods = {
    "GetMapping": "GET",
    "PostMapping": "POST", 
    "PutMapping": "PUT",
    "DeleteMapping": "DELETE",
    "PatchMapping": "PATCH",
    "RequestMapping": "GET"  # default if method is not specified
}

def extract_endpoints(java_file):
    with open(java_file, "r", encoding="utf-8") as f:
        content = f.read()

    endpoints = []
    
    # Extract base path from class-level @RequestMapping
    base_path_match = re.search(r'@RequestMapping\("([^"]+)"\)', content)
    base_path = base_path_match.group(1) if base_path_match else ""
    
    # Also check for @RestController without explicit RequestMapping
    if not base_path_match and "@RestController" in content:
        base_path = ""

    # Extract endpoints with different patterns
    for annotation, method in http_methods.items():
        # Pattern 1: @GetMapping("/path")
        pattern1 = fr'@{annotation}\("([^"]+)"\)'
        for match in re.finditer(pattern1, content):
            path = match.group(1)
            full_path = f"{base_path}/{path}".replace("//", "/")
            endpoints.append((method, full_path.strip("/"), annotation))
        
        # Pattern 2: @RequestMapping(value = "/path", method = RequestMethod.GET)
        pattern2 = fr'@RequestMapping\s*\(\s*value\s*=\s*"([^"]+)"\s*,\s*method\s*=\s*RequestMethod\.{method}\s*\)'
        for match in re.finditer(pattern2, content):
            path = match.group(1)
            full_path = f"{base_path}/{path}".replace("//", "/")
            endpoints.append((method, full_path.strip("/"), "RequestMapping"))
        
        # Pattern 3: @RequestMapping(value = "/path")
        pattern3 = fr'@RequestMapping\s*\(\s*value\s*=\s*"([^"]+)"\s*\)'
        for match in re.finditer(pattern3, content):
            path = match.group(1)
            full_path = f"{base_path}/{path}".replace("//", "/")
            endpoints.append((method, full_path.strip("/"), "RequestMapping"))

    return endpoints

def generate_http_files(endpoints):
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Group endpoints by controller for better organization
    controller_endpoints = {}
    
    for method, path, annotation in endpoints:
        # Extract controller name from path for grouping
        controller_name = path.split('/')[0] if path and '/' in path else "default"
        if controller_name not in controller_endpoints:
            controller_endpoints[controller_name] = []
        controller_endpoints[controller_name].append((method, path, annotation))
    
    # Generate individual files for each endpoint
    for idx, (method, path, annotation) in enumerate(endpoints):
        # Create a safe filename
        safe_path = path.replace('/', '_').replace('-', '_').replace('{', '').replace('}', '')
        filename = f"{method.lower()}_{safe_path}.http"
        
        with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as f:
            f.write(f"### {annotation} - {method} {path}\n")
            f.write(f"{method} {BASE_URL}/{path}\n")
            
            # Add headers based on method
            if method in ["POST", "PUT", "PATCH"]:
                f.write("Content-Type: application/json\n")
                f.write("Accept: application/json\n\n")
                f.write("{\n")
                f.write('  "sampleField": "value",\n')
                f.write('  "anotherField": 123\n')
                f.write("}\n")
            else:
                f.write("Accept: application/json\n\n")
    
    # Generate a comprehensive test file with all endpoints
    with open(OUTPUT_DIR / "all_endpoints.http", "w", encoding="utf-8") as f:
        f.write("### All Generated Endpoints\n\n")
        
        for controller_name, controller_endpoints_list in controller_endpoints.items():
            f.write(f"### {controller_name.upper()} CONTROLLER\n")
            for method, path, annotation in controller_endpoints_list:
                f.write(f"\n### {annotation} - {method} {path}\n")
                f.write(f"{method} {BASE_URL}/{path}\n")
                
                if method in ["POST", "PUT", "PATCH"]:
                    f.write("Content-Type: application/json\n")
                    f.write("Accept: application/json\n\n")
                    f.write("{\n")
                    f.write('  "sampleField": "value",\n')
                    f.write('  "anotherField": 123\n')
                    f.write("}\n")
                else:
                    f.write("Accept: application/json\n\n")
            f.write("\n" + "="*50 + "\n\n")

def scan_project():
    all_endpoints = []
    controller_files = []
    
    # Find all Java files that might be controllers
    for root, _, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith(".java"):
                file_path = Path(root) / file
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Check if it's a controller (has @RestController or @Controller)
                    if "@RestController" in content or "@Controller" in content:
                        controller_files.append(file_path)
    
    print(f"Found {len(controller_files)} controller files:")
    for controller_file in controller_files:
        print(f"  - {controller_file}")
        endpoints = extract_endpoints(controller_file)
        all_endpoints.extend(endpoints)
        print(f"    Found {len(endpoints)} endpoints")
    
    return all_endpoints

if __name__ == "__main__":
    print("🔍 Scanning for Spring Boot controllers...")
    endpoints = scan_project()
    
    if endpoints:
        generate_http_files(endpoints)
        print(f"\n✅ Generated {len(endpoints)} endpoint test files in {OUTPUT_DIR}")
        print(f"📁 Individual files: {len(endpoints)}")
        print(f"📄 Summary file: all_endpoints.http")
        
        # Print summary of endpoints found
        print(f"\n📋 Endpoints found:")
        for method, path, annotation in endpoints:
            print(f"  {method} {path} ({annotation})")
    else:
        print("❌ No endpoints found. Make sure you have controllers with proper annotations.")
