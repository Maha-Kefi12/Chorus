import json
from pathlib import Path
from xml.sax.saxutils import escape
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict
import traceback
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

# Static panel definitions
STATIC_PANELS = {
    'valeurPanel': {
        'area': 'area2',
        'fields': [
            {'id': 'reiv_rceval', 'nature': 'fk', 'functionId': 'FK_instrument', 'valueField': 'acecev', 'fkSearchField': 'acecev', 'displayTemplate': '{acecev}', 'sortNumber': '1', 'columnNumber': '2', 'readOnly': 'false', 'clearValueIfNotInStore': 'true', 'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}]},
            {'id': 'reiv_ridori', 'nature': 'lov', 'lov': 'IprapRidoriLovQueryServiceImpl', 'valueField': 'value', 'displayTemplate': '{value} - {longLabel}', 'sortNumber': '2', 'columnNumber': '2', 'readOnly': 'false', 'clearValueIfNotInStore': 'true', 'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}], 'filters': [{'id': 'reiv_rceval', 'fieldId': 'reiv_rceval'}, {'id': 'reiv_xidcev', 'fieldId': 'reiv_xidcev'}]},
            {'id': 'reic_rcepla', 'nature': 'lov', 'lov': 'IprapRceplaLovQueryServiceImpl', 'valueField': 'value', 'displayTemplate': '{value} - {longLabel}', 'sortNumber': '3', 'columnNumber': '2', 'readOnly': 'false', 'clearValueIfNotInStore': 'true', 'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}], 'filters': [{'id': 'reiv_rceval', 'fieldId': 'reiv_rceval'}, {'id': 'reiv_xidcev', 'fieldId': 'reiv_xidcev'}, {'id': 'reiv_ridori', 'fieldId': 'reiv_ridori'}]},
            {'id': 'iprap_adtvalid', 'nature': 'lov', 'lov': 'IprapAdtpalLovQueryServiceImpl', 'valueField': 'value', 'displayTemplate': '{value}', 'sortNumber': '4', 'columnNumber': '2', 'readOnly': 'false', 'clearValueIfNotInStore': 'true', 'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}], 'filters': [{'id': 'reiv_rceval', 'fieldId': 'reiv_rceval'}, {'id': 'reiv_xidcev', 'fieldId': 'reiv_xidcev'}, {'id': 'reiv_ridori', 'fieldId': 'reiv_ridori'}, {'id': 'xetb_xidcec', 'fieldId': 'xetb_xidcec'}, {'id': 'xetb_xidced', 'fieldId': 'xetb_xidced'}, {'id': 'reic_rcepla', 'fieldId': 'reic_rcepla'}, {'id': 'xuti_xidclg', 'fieldId': 'xuti_xidclg'}]},
            {'id': 'rgvlm_rllgvl', 'nature': 'string', 'sortNumber': '5', 'columnNumber': '2', 'readOnly': 'false', 'hidden': 'false'}
        ]
    },
    'csoPanel': {
        'area': 'area3',
        'fields': [
            {'id': 'riddev', 'nature': 'lov', 'lov': 'IprapRiddevLovQueryServiceImpl', 'valueField': 'value', 'displayTemplate': '{value} - {longLabel}', 'columnNumber': '1', 'sortNumber': '1', 'readOnly': 'false', 'clearValueIfNotInStore': 'true', 'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}]},
            {'id': 'adtchgo', 'nature': 'date', 'sortNumber': '1', 'columnNumber': '2', 'readOnly': 'false', 'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}]},
            {'id': 'rcepla', 'nature': 'lov', 'lov': 'IprapRceplaLovQueryServiceImpl', 'valueField': 'value', 'displayTemplate': '{value} - {longLabel}', 'columnNumber': '2', 'sortNumber': '2', 'readOnly': 'false', 'clearValueIfNotInStore': 'true', 'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}]},
            {'id': 'acetdev', 'nature': 'lov', 'lov': 'IprapAcetdevLovQueryServiceImpl', 'valueField': 'value', 'displayTemplate': '{value} - {longLabel}', 'columnNumber': '1', 'sortNumber': '2', 'readOnly': 'false', 'clearValueIfNotInStore': 'true', 'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}]}
        ]
    }
}

def escape_attr(value):
    """Escape XML attribute values"""
    if value is None:
        return ""
    from xml.sax.saxutils import escape
    return escape(str(value), {'"': "&quot;", "'": "&apos;"})

def find_workspace_root(start_path):
    """Find the workspace root by looking for the output directory"""
    current = Path(start_path).resolve()
    while current != current.parent:  # Stop at root directory
        if (current / "output").exists():
            return current
        if (current.parent / "output").exists():
            return current.parent
        current = current.parent
    return None

def build_field_mapping_from_area_map(area_map, form_fields):
    """Build field mapping from area_map.json for ALL fields in transformed_result.json"""
    mapped = {}

    # Create area_map lookup by fieldId
    area_map_lookup = {}
    area_name_map = {
        "Critères de lancement": "area1",
        "Critères avancés": "area2",
        "Critères de consolidation": "area3"
    }

    for entry in area_map:
        if 'fieldId' in entry:
            area_name = entry.get('area', 'Critères de lancement')
            mapped_area = area_name_map.get(area_name, 'area1')
            area_map_lookup[entry['fieldId']] = {
                'area': mapped_area,
                'sortNumber': entry.get('sortNumber', 10),
                'columnNumber': entry.get('columnNumber', 1)
            }

    # Process ALL fields from transformed_result.json
    for field_id, field_data in form_fields.items():
        if not isinstance(field_data, dict):
            continue

        # Start with field data from transformed_result.json
        field = dict(field_data)
        field['id'] = field_id

        # If field exists in area_map.json, use its mapping
        if field_id in area_map_lookup:
            mapping = area_map_lookup[field_id]
            field['area'] = mapping['area']
            field['sortNumber'] = mapping['sortNumber']
            field['columnNumber'] = mapping['columnNumber']
        else:
            # Default to area1 with incremental sort numbers
            field['area'] = 'area1'
            field['sortNumber'] = len([f for f in mapped.values() if f.get('area') == 'area1']) * 10 + 10
            field['columnNumber'] = 1

        mapped[field_id] = field

    # Add static panel fields if panel exists in form_fields
    for panel_id, panel_config in STATIC_PANELS.items():
        if panel_id in form_fields:
            print(f"✅ Found {panel_id} in form_fields, adding {len(panel_config['fields'])} static fields to {panel_config['area']}")
            for static_field in panel_config['fields']:
                static = dict(static_field)
                static['area'] = panel_config['area']
                static['is_static_panel'] = True
                mapped[static['id']] = static

    return mapped

def group_fields_by_area(mapped_fields):
    """Group fields by area"""
    area_fields = {'area1': [], 'area2': [], 'area3': []}
    for field in mapped_fields.values():
        area = field.get('area', 'area1')
        if area not in area_fields:
            area_fields[area] = []
        area_fields[area].append(field)

    # Sort by sortNumber within each area
    for area in area_fields:
        area_fields[area].sort(key=lambda x: int(x.get('sortNumber', 0)))

    return area_fields

def generate_field_xml(field_id: str, field_data: dict) -> str:
    """Generate XML for a field in compact format"""
    attrs = [
        f'id="{field_id}"',
        f'nature="{field_data.get("nature", "string")}"',
        f'columnNumber="{field_data.get("columnNumber", "1")}"',
        f'sortNumber="{field_data.get("sortNumber", "10")}"',
        f'readOnly="{str(field_data.get("readOnly", "false")).lower()}"',
        f'hidden="{str(field_data.get("hidden", "false")).lower()}"'
    ]
    # Add optional attributes
    optional_attrs = [
        'functionId', 'valueField', 'fkSearchField', 'displayTemplate',
        'clearValueIfNotInStore', 'lov', 'maxDualFieldValues'
    ]
    for attr in optional_attrs:
        if attr in field_data:
            attrs.append(f'{attr}="{field_data[attr]}"')
    # Check if field has controls or filters
    has_controls = 'controls' in field_data
    has_filters = 'filters' in field_data and field_data.get('nature') == 'lov'
    if has_controls or has_filters:
        # Multi-line field with controls/filters
        xml = f'<field {" ".join(attrs)}>'
        if has_controls:
            xml += '<controls>'
            for control in field_data['controls']:
                xml += f'<control id="{control["id"]}" nature="{control["nature"]}"/>'
            xml += '</controls>'
        if has_filters:
            xml += '<filters>'
            for filter_data in field_data['filters']:
                filter_id = filter_data.get('fieldId')
                if filter_id and not filter_id.isdigit() and not (filter_id.startswith("'") and filter_id.endswith("'")):
                    xml += f'<filter id="{filter_id}" fieldId="{filter_id}"/>'
            xml += '</filters>'
        xml += '</field>'
        return xml
    else:
        # Single-line field
        return f'<field {" ".join(attrs)}/>'

def generate_fieldlinks_xml(fieldlinks_data: dict) -> str:
    """Generate XML for fieldlinks in compact format"""
    lines = ['<fieldLinks>']
    for link in fieldlinks_data.get("links", []):
        if not link.get("childFieldId"):
            continue
        attrs = [
            f'childFieldId="{link["childFieldId"]}"',
            f'id="{link.get("id", f"link_{link["childFieldId"]}")}"',
            f'methodName="{link.get("methodName", f"is{link["childFieldId"][:1].upper() + link["childFieldId"][1:]}Visible")}"',
            f'nature="{link.get("nature", "CONDITIONNALHIDDEN")}"',
            f'disabled="{str(link.get("disabled", False)).lower()}"',
            f'beanId="ainiFieldLinkServiceFieldLinkService"'
        ]
        xml = f'<fieldLink {" ".join(attrs)}>'
        for father_id in link.get("fatherFieldIds", []):
            xml += f'<fieldLinkFather fatherFieldId="{father_id}"/>'
        xml += '</fieldLink>'
        lines.append(xml)
    lines.append('</fieldLinks>')
    return '\n'.join(lines)

def generate_properties_file(area_map, form_fields, output_path):
    """Generate properties file with id.label=label from area_map.json"""
    lines = []

    # Create lookup for labels from area_map.json
    label_lookup = {}
    for entry in area_map:
        if 'fieldId' in entry and 'label' in entry:
            label_lookup[entry['fieldId']] = entry['label']

    # Add properties for all fields from form_fields
    for field_id, field_data in form_fields.items():
        if not isinstance(field_data, dict):
            continue

        # Get label from area_map.json if available, otherwise from field data
        label = label_lookup.get(field_id, '')
        if not label:
            label = field_data.get('label2') or field_data.get('label1') or field_data.get('label') or ''

        if label:  # Only add if there's a label
            lines.append(f"{field_id}.label={label}")

    # Add properties for static panel fields
    static_labels = {
        'riddev': 'Risque de défaut',
        'adtchgo': 'Date de changement',
        'rcepla': 'Risque de crédit',
        'acetdev': 'Acceptation de défaut',
        'reiv_rceval': 'Revenu évalué',
        'reiv_ridori': 'Revenu origine',
        'reic_rcepla': 'Revenu crédit place',
        'iprap_adtvalid': 'Date de validation',
        'rgvlm_rllgvl': 'Réglement valeur'
    }

    for field_id, label in static_labels.items():
        lines.append(f"{field_id}.label={label}")

    # Write properties file
    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"✅ Properties file generated at: {output_path}")

def generate_xml(area_map, form_fields, fieldlinks_data, form_id):
    """Generate complete XML form in compact format"""
    # Build mapping for ALL fields
    mapped_fields = build_field_mapping_from_area_map(area_map, form_fields)
    area_fields = group_fields_by_area(mapped_fields)

    # Generate XML
    lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        f'<form xmlns:jxb="http://java.sun.com/xml/ns/jaxb" xmlns:xjc="http://java.sun.com/xml/ns/jaxb/xjc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" id="{form_id}BlockForm" xsi:noNamespaceSchemaLocation="http://scheme.cf.linedata.com/function.xsd" fatherId="LotIntervallePortefeuille" beanId="ainiFormService">',
        '<graphic>',
        '<headerVisible>false</headerVisible>',
        '<collapsible>false</collapsible>',
        '<collapsed>false</collapsed>',
        '</graphic>'
    ]

    # Add fieldLinks
    fieldlinks_xml = generate_fieldlinks_xml(fieldlinks_data)
    lines.append(fieldlinks_xml)

    # Areas
    lines.append('<areas>')

    # Process areas in order
    for area_id in ['area1', 'area2', 'area3']:
        if area_id not in area_fields or not area_fields[area_id]:
            continue

        sort_number = '1' if area_id == 'area1' else '3' if area_id == 'area2' else '2'
        lines.append(f'<area id="{area_id}" sortNumber="{sort_number}">')

        # Add graphic only for area1
        if area_id == 'area1':
            lines.append('<graphic>')
            lines.append('<headerVisible>false</headerVisible>')
            lines.append('</graphic>')

        lines.append('<fields>')

        # Add fields
        for field in area_fields[area_id]:
            field_xml = generate_field_xml(field['id'], field)
            lines.append(field_xml)

        lines.append('</fields>')
        lines.append('</area>')

    lines.append('</areas>')
    lines.append('</form>')

    return '\n'.join(lines)

def main():
    """Main entry point"""
    # Find workspace root
    script_dir = Path(__file__).parent.resolve()
    workspace_root = find_workspace_root(script_dir)
    if not workspace_root:
        print("❌ Could not find workspace root")
        return

    # Set up paths
    base_path = workspace_root / "output"
    area_map_path = base_path / "area_map.json"
    transformed_path = base_path / "transformed_result.json"
    fieldlinks_path = base_path / "fieldlink.json"

    try:
        # Load data
        area_map = json.load(open(resource_path(str(area_map_path)), encoding="utf-8"))
        transformed_data = json.load(open(resource_path(str(transformed_path)), encoding="utf-8"))

        # Get form data
        if 'originalJson' in transformed_data:
            form_id = next(iter(transformed_data['originalJson']))
            form_fields = transformed_data['originalJson'][form_id]
        else:
            form_id = next(iter(transformed_data))
            form_fields = transformed_data[form_id]

        # Load field links
        fieldlinks_data = {"links": []}
        if fieldlinks_path.exists():
            fieldlinks_data = json.load(open(resource_path(str(fieldlinks_path)), encoding="utf-8"))

        # Generate XML
        xml_content = generate_xml(area_map, form_fields, fieldlinks_data, form_id)

        # Create output directory
        output_dir = base_path / "demo" / form_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save XML
        xml_path = output_dir / f"{form_id}.block.xml"
        xml_path.write_text(xml_content, encoding="utf-8")
        print(f"✅ XML generated at: {xml_path}")

        # Generate properties file
        properties_path = output_dir / f"{form_id}.block.properties"
        generate_properties_file(area_map, form_fields, properties_path)

        # Print summary
        mapped_fields = build_field_mapping_from_area_map(area_map, form_fields)
        area_fields = group_fields_by_area(mapped_fields)
        print(f"\n📊 Summary:")
        for area_id, fields in area_fields.items():
            print(f"{area_id}: {len(fields)} fields")
        print(f"Total fields: {len(mapped_fields)}")

    except Exception as e:
        print(f"❌ Error generating files: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()