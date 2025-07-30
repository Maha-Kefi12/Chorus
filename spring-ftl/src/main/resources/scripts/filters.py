import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

def main():
    # Using the exact old paths you gave me
    base_path = Path(r"C:\Users\USER\Downloads\spring-ftl\output")
    response_path = base_path / "response.json"
    parsed_result_path = base_path / "parsed_result.json"
    fieldlinks_path = Path(r"C:\Users\USER\Downloads\spring-ftl\output\fieldlink.json")
    template_dir = Path(r"C:\Users\USER\Downloads\spring-ftl\spring-ftl\src\main\resources\templates")
    output_path = base_path / "final_output.xml"

    # Load JSON files from old paths
    with open(response_path, encoding="utf-8") as f:
        response_json = json.load(f)
    with open(parsed_result_path, encoding="utf-8") as f:
        parsed_result = json.load(f)
    with open(fieldlinks_path, encoding="utf-8") as f:
        fieldlinks_json = json.load(f)

    # Extract fields and LOV fields
    fields = response_json.get("fields", [])
    lov_fields = [field for field in fields if field.get("nature") == "lov"]

    # Map filters by champ from parsed_result
    filters_map = {entry["champ"]: entry for entry in parsed_result}

    # Extract fieldLinks from fieldlinks.json
    fieldLinks = fieldlinks_json.get("links", [])

    # Attach filters to LOV fields
    for field in lov_fields:
        champ_id = field.get("id")
        if champ_id in filters_map:
            param_list = filters_map[champ_id].get("parametres", [])
            field["filters"] = [
                {"id": p.strip("'\""), "fieldId": p.strip("'\"")} for p in param_list if p.strip("'\"")
            ]
        else:
            field["filters"] = []

    # Initialize Jinja2
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = env.get_template("filters_tmp.ftl.j2")

    # Render XML
    xml_output = template.render(fields=fields, fieldLinks=fieldLinks)

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_output)

    print(f"[✅] Fichier XML généré : {output_path}")

if __name__ == "__main__":
    main()
