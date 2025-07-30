import json
from pathlib import Path
from jinja2 import Template

# === Mapping nature → Java types ===
NATURE_TO_JAVA_TYPE = {
    "checkbox": "Boolean",
    "date": "Date",
    "lov": "String",
    "dualfield": "List<String>",
    "string": "String",
    "int": "int",
}

# === Jinja2 Template for Java Interface ===
JAVA_TEMPLATE = """\
package com.linedata.chorus.std.entity.{{ FunctionId }}IRAP;

import java.util.*;
import java.util.Date;

public interface {{ FunctionId }}IRAP
{
{% for field in fields %}
 public {{ field.FieldNature }} get{{ field.FieldId }}();
 public void set{{ field.FieldId }}({{ field.FieldNature }} {{ field.FieldId }});
{% endfor %}
}
"""

def capitalize_camel_case(s: str) -> str:
    return ''.join(part.capitalize() for part in s.split('_'))

def generate_irap_interface(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        full_data = json.load(f)

    for function_id, fields_dict in full_data.items():
        FunctionId = function_id[0].upper() + function_id[1:]
        field_entries = []

        for field_key, props in fields_dict.items():
            raw_nature = props.get("nature", "string").lower()
            java_type = NATURE_TO_JAVA_TYPE.get(raw_nature, "String")
            FieldId = capitalize_camel_case(field_key)

            field_entries.append({
                "FieldId": FieldId,
                "FieldNature": java_type,
            })

        # Create folder and file
        base_path = Path(r"C:\Users\USER\Downloads\spring-ftl\.idea\demo") / function_id
        base_path.mkdir(parents=True, exist_ok=True)

        filename = f"{function_id}IRAP.java"
        output_path = base_path / filename

        # Render Java file
        template = Template(JAVA_TEMPLATE)
        java_code = template.render(FunctionId=FunctionId, fields=field_entries)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(java_code)

        print(f"✅ Fichier généré pour '{function_id}' : {output_path}")

if __name__ == "__main__":
    json_input_path = r"C:\Users\USER\Downloads\spring-ftl\output\response.json"
    generate_irap_interface(json_input_path)
