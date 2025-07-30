import json
import os
from typing import List

# Type mapping from JSON 'nature' to Java type
NATURE_TO_JAVA = {
    'checkbox': 'Boolean',
    'date': 'Date',
    'lov': 'String',
    'dualfield': 'List<String>',
    'string': 'String',
}

def to_camel_case(s):
    # Converts snake_case or lower_case to CamelCase for method names
    parts = s.split('_')
    return ''.join(word.capitalize() for word in parts)

def get_java_type(nature):
    return NATURE_TO_JAVA.get(nature, 'String')

def generate_java_class(function_id: str, fields: List[dict]) -> str:
    class_name = f"{function_id}IRAPImpl"
    interface_name = f"{function_id}IRAP"
    package = f"com.linedata.chorus.std.entity.{function_id}IRAP.impl"
    interface_package = f"com.linedata.chorus.std.entity.{function_id}IRAP.{interface_name}"

    # Collect imports
    imports = set([interface_package])
    if any(get_java_type(f['nature']) == 'Date' for f in fields):
        imports.add('java.util.Date')
    if any(get_java_type(f['nature']) == 'List<String>' for f in fields):
        imports.add('java.util.List')

    imports_str = '\n'.join(f'import {imp};' for imp in sorted(imports))

    # Fields
    fields_str = ''
    for f in fields:
        java_type = get_java_type(f['nature'])
        fields_str += f"    private {java_type} {f['id']};\n"

    # Getters and setters
    methods_str = ''
    for f in fields:
        java_type = get_java_type(f['nature'])
        field_id = f['id']
        camel = to_camel_case(field_id)
        methods_str += f"    @Override\n"
        methods_str += f"    public {java_type} get{camel}() {{ return {field_id}; }}\n"
        methods_str += f"    @Override\n"
        methods_str += f"    public void set{camel}({java_type} {field_id}) {{ this.{field_id} = {field_id}; }}\n\n"

    # Full class
    return f'''package {package};\n\n{imports_str}\n\npublic class {class_name} implements {interface_name}\n{{\n{fields_str}\n{methods_str}}}\n'''

def main():
    # Static paths
    input_path = r'C:/Users/USER/Downloads/spring-ftl/output/response.json'
    # Read JSON
    with open(input_path, encoding='utf-8') as f:
        data = json.load(f)
    # Extract the functionId as the first (and only) key in the JSON
    if not data:
        print("Input JSON is empty.")
        return
    function_id = next(iter(data))
    fields_dict = data[function_id]
    if not isinstance(fields_dict, dict):
        print(f"Expected a dict of fields for functionId '{function_id}', got {type(fields_dict).__name__}")
        return
    # Only use fields that are dicts and have 'nature' and 'id'
    fields = [
        { 'id': k, 'nature': v.get('nature', 'string') }
        for k, v in fields_dict.items() if isinstance(v, dict) and 'nature' in v and 'id' in v
    ]
    java_code = generate_java_class(function_id, fields)
    # Output path
    output_dir = f'C:/Users/USER/Downloads/spring-ftl/.idea/demo/{function_id}'
    os.makedirs(output_dir, exist_ok=True)
    output_path = f'{output_dir}/{function_id}IRAPImpl.java'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(java_code)
    print(f"Java class generated at {output_path}")

if __name__ == "__main__":
    main()
