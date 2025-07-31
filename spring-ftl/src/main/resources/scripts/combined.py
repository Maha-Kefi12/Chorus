#!/usr/bin/env python3
"""
XML Generation Script - Combined
Generates XML files from analyzed data
"""

import json
import os
import sys
import traceback
from pathlib import Path
from typing import Dict, Any, List

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def escape_attr(value):
    """Escape XML attribute values"""
    if value is None:
        return ""
    return str(value).replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

def find_workspace_root(start_path):
    """Find the workspace root directory"""
    current = Path(start_path)
    while current != current.parent:
        if (current / "spring-ftl").exists() or (current / "output").exists():
            return current
        current = current.parent
    return None

def get_form_id_from_environment():
    """Get form_id from environment variable or detect from data"""
    # First try environment variable
    form_id = os.environ.get('FORM_ID')
    if form_id:
        return form_id
    
    # Try to detect from data files
    output_dir = Path("output")
    if output_dir.exists():
        transformed_path = output_dir / "transformed_result.json"
        if transformed_path.exists():
            try:
                with open(transformed_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Look for forms in the data structure
                if 'originalJson' in data:
                    forms = list(data['originalJson'].keys())
                    if forms:
                        return forms[0]  # Use first form found
                elif isinstance(data, dict):
                    forms = list(data.keys())
                    if forms:
                        return forms[0]  # Use first form found
            except Exception as e:
                print(f"⚠️ Error reading transformed data: {e}")
    
    # Default fallback
    return "aini"

def build_field_mapping_from_area_map(area_map, form_fields):
    """Build field mapping from area map and form fields"""
    mapped_fields = {}
    
    for field_id, field_data in form_fields.items():
        if field_id in area_map:
            mapped_fields[field_id] = {
                **field_data,
                'area': area_map[field_id]['area'],
                'sortNumber': area_map[field_id]['sortNumber'],
                'columnNumber': area_map[field_id]['columnNumber']
            }
        else:
            # Default to area1 if not mapped
            mapped_fields[field_id] = {
                **field_data,
                'area': 'area1',
                'sortNumber': '1',
                'columnNumber': '1'
            }
    
    return mapped_fields

def group_fields_by_area(mapped_fields):
    """Group fields by their assigned areas"""
    area_fields = {
        'area1': [],
        'area2': [],
        'area3': []
    }
    
    for field_id, field_data in mapped_fields.items():
        area = field_data.get('area', 'area1')
        if area in area_fields:
            area_fields[area].append(field_data)
    
    return area_fields

def generate_field_xml(field_id: str, field_data: dict) -> str:
    """Generate XML for a single field"""
    lines = [f'<field id="{escape_attr(field_id)}"']
    
    # Add required attributes
    nature = field_data.get('nature', 'string')
    lines.append(f' nature="{escape_attr(nature)}"')
    
    # Add optional attributes
    optional_attrs = [
        ('columnNumber', 'columnNumber'),
        ('sortNumber', 'sortNumber'),
        ('readOnly', 'readOnly'),
        ('hidden', 'hidden'),
        ('label', 'label'),
        ('maxLength', 'maxLength'),
        ('defaultValue', 'defaultValue')
    ]
    
    for attr_name, xml_attr in optional_attrs:
        if attr_name in field_data:
            lines.append(f' {xml_attr}="{escape_attr(field_data[attr_name])}"')
    
    # Add LOV-specific attributes
    if nature == 'lov' and 'lov' in field_data:
        lines.append(f' lov="{escape_attr(field_data["lov"])}"')
        if 'valueField' in field_data:
            lines.append(f' valueField="{escape_attr(field_data["valueField"])}"')
        if 'displayTemplate' in field_data:
            lines.append(f' displayTemplate="{escape_attr(field_data["displayTemplate"])}"')
    
    lines.append(' />')
    
    return ''.join(lines)

def generate_fieldlinks_xml(fieldlinks_data: dict) -> str:
    """Generate XML for field links"""
    if not fieldlinks_data or 'links' not in fieldlinks_data:
        return '<fieldLinks />'
    
    lines = ['<fieldLinks>']
    
    for link in fieldlinks_data['links']:
        if not isinstance(link, dict):
            continue
            
        lines.append('<fieldLink')
        lines.append(f' childFieldId="{escape_attr(link.get("childFieldId", ""))}"')
        lines.append(f' id="{escape_attr(link.get("id", ""))}"')
        lines.append(f' methodName="{escape_attr(link.get("methodName", ""))}"')
        lines.append(f' nature="{escape_attr(link.get("nature", "CONDITIONNALHIDDEN"))}"')
        lines.append(f' disabled="{escape_attr(link.get("disabled", "false"))}"')
        
        # Get form_id for dynamic bean ID
        form_id = get_form_id_from_environment()
        bean_id = f"{form_id}FieldLinkServiceFieldLinkService"
        lines.append(f' beanId="{bean_id}">')
        
        # Add father fields
        father_field_ids = link.get('fatherFieldIds', [])
        for father_id in father_field_ids:
            lines.append(f'<fieldLinkFather fatherFieldId="{escape_attr(father_id)}" />')
        
        lines.append('</fieldLink>')
    
    lines.append('</fieldLinks>')
    return '\n'.join(lines)

def generate_properties_file(area_map, form_fields, output_path):
    """Generate properties file for the form"""
    properties = []
    
    for field_id, field_data in form_fields.items():
        if field_id in area_map:
            area = area_map[field_id]['area']
            sort_number = area_map[field_id]['sortNumber']
            column_number = area_map[field_id]['columnNumber']
            
            properties.append(f"{field_id}.area={area}")
            properties.append(f"{field_id}.sortNumber={sort_number}")
            properties.append(f"{field_id}.columnNumber={column_number}")
    
    output_path.write_text('\n'.join(properties), encoding='utf-8')
    print(f"✅ Properties file generated at: {output_path}")

def generate_xml(area_map, form_fields, fieldlinks_data, form_id):
    """Generate complete XML form in compact format"""
    # Build mapping for ALL fields
    mapped_fields = build_field_mapping_from_area_map(area_map, form_fields)
    area_fields = group_fields_by_area(mapped_fields)

    # Get form_id for dynamic IDs
    form_id = get_form_id_from_environment()
    bean_id = f"{form_id}FormService"

    # Generate XML
    lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        f'<form xmlns:jxb="http://java.sun.com/xml/ns/jaxb" xmlns:xjc="http://java.sun.com/xml/ns/jaxb/xjc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" id="{form_id}BlockForm" xsi:noNamespaceSchemaLocation="http://scheme.cf.linedata.com/function.xsd" fatherId="LotIntervallePortefeuille" beanId="{bean_id}">',
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