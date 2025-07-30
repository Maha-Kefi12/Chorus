import json
from pathlib import Path
from xml.sax.saxutils import escape

def escape_attr(value):
    """Escape XML attribute special characters"""
    return escape(str(value), {'"': "&quot;", "'": "&apos;"})

def main():
    input_json_path = Path(r"C:\Users\USER\Downloads\spring-ftl\output\fieldlink.json")
    output_xml_path = Path(r"C:\Users\USER\Downloads\spring-ftl\output\fieldlinks.xml")

    # Change this to whatever beanId prefix you want
    fonction_name = "MyFunction"

    try:
        with input_json_path.open(encoding="utf-8") as f:
            field_links = json.load(f)

        lines = ['<fieldLinks>']

        for link in field_links:
            child_id = escape_attr(link.get("childFieldId", ""))
            bean_id = f"{fonction_name}FieldLinkService"
            method_name = f"is{child_id}Visible"
            nature = link.get("nature", "CONDITIONNALHIDDEN")
            disabled = str(link.get("disabled", "false")).lower()

            lines.append(f'  <fieldLink childFieldId="{child_id}" id="link_{child_id}"')
            lines.append(f'             methodName="{method_name}" nature="{nature}" disabled="{disabled}"')
            lines.append(f'             beanId="{bean_id}">')

            for father in link.get("fatherFieldIds", []):
                father_escaped = escape_attr(father)
                lines.append(f'    <fieldLinkFather fatherFieldId="{father_escaped}" />')

            lines.append(f'  </fieldLink>')

        lines.append('</fieldLinks>')

        xml_content = "\n".join(lines)
        output_xml_path.write_text(xml_content, encoding="utf-8")

        print(f"✅ XML généré avec succès dans : {output_xml_path}")

    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    main()
