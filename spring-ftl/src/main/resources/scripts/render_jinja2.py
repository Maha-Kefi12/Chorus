# template_renderer.py
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template
import xml.etree.ElementTree as ET
from xml.dom import minidom

def prepare_template_data(field_links_data: Dict[str, Any], 
                         area_fields: Dict[str, List], 
                         filters_map: Dict[str, List[str]]) -> Dict[str, Any]:
    """Prepare data for template rendering"""
    
    # Process field links
    field_links = []
    for link_id, link_data in field_links_data.items():
        field_link = {
            'id': link_id,
            'childFieldId': link_data.get('childFieldId', ''),
            'methodName': link_data.get('methodName', ''),
            'nature': link_data.get('nature', 'CONDITIONNALHIDDEN'),
            'disabled': link_data.get('disabled', 'false'),
            'beanId': link_data.get('beanId', 'ainiFieldLinkServiceFieldLinkServiceFieldLinkService'),
            'fathers': link_data.get('fathers', [])
        }
        field_links.append(field_link)
    
    # Process areas and fields
    areas = []
    for area_id in ['area1', 'area2', 'area3']:
        if area_id in area_fields and area_fields[area_id]:
            fields = []
            for field_id, field_data in area_fields[area_id]:
                field_nature = field_data.get('nature', 'text')
                field = {
                    'id': field_id,
                    'nature': field_nature,
                    'columnNumber': field_data.get('columnNumber', '1'),
                    'sortNumber': field_data.get('sortNumber', '1'),
                    'readOnly': field_data.get('readOnly', 'false'),
                    'hidden': field_data.get('hidden', 'false'),
                    'label': field_data.get('label2', ''),  # Use label2 as requested
                    'lov': field_data.get('lov', ''),
                    # Only include valueField if nature is "lov"
                    'valueField': field_data.get('valueField', '') if field_nature == 'lov' else '',
                    'displayTemplate': field_data.get('displayTemplate', ''),
                    'functionId': field_data.get('functionId', ''),
                    'fkSearchField': field_data.get('fkSearchField', ''),
                    'clearValueIfNotInStore': field_data.get('clearValueIfNotInStore', ''),
                    'controls': field_data.get('controls', []),
                    'filters': []
                }
                
                # Add filters if they exist
                if field_id in filters_map:
                    for filter_field in filters_map[field_id]:
                        field['filters'].append({
                            'id': filter_field,
                            'fieldId': filter_field
                        })
                
                fields.append(field)
            
            # Sort fields by sortNumber
            fields.sort(key=lambda x: int(x['sortNumber']))
            
            # Correct sortNumber for areas: area1=1, area3=2, area2=3
            area_sort_mapping = {
                'area1': '1',
                'area3': '2', 
                'area2': '3'
            }
            
            area = {
                'id': area_id,
                'sortNumber': area_sort_mapping[area_id],
                'fields': fields
            }
            areas.append(area)
    
    return {
        'form_id': 'ainiBlockForm',
        'bean_id': 'ainiFormService',
        'field_links': field_links,
        'areas': areas
    }

def render_template(template_dir: Path, 
                   template_name: str, 
                   data: Dict[str, Any], 
                   output_path: Path) -> None:
    """Render Jinja2 template to XML file"""
    
    # If template exists, use Jinja2
    template_file = template_dir / template_name
    if template_file.exists():
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_name)
        rendered_xml = template.render(**data)
    else:
        # Generate XML directly if template doesn't exist
        rendered_xml = generate_xml_directly(data)
    
    # Pretty print the XML
    try:
        # Parse and format the XML
        root = ET.fromstring(rendered_xml)
        rough_string = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent='    ', encoding=None)
        
        # Remove empty lines and fix encoding declaration
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        if lines and lines[0].startswith('<?xml'):
            lines[0] = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        
        formatted_xml = '\n'.join(lines)
        
    except ET.ParseError:
        # If parsing fails, use the original rendered XML
        formatted_xml = rendered_xml
    
    # Write to output file
    with output_path.open('w', encoding='utf-8') as f:
        f.write(formatted_xml)

def generate_xml_directly(data: Dict[str, Any]) -> str:
    """Generate XML directly without template"""
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        f'<form xmlns:jxb="http://java.sun.com/xml/ns/jaxb" '
        f'xmlns:xjc="http://java.sun.com/xml/ns/jaxb/xjc" '
        f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        f'id="{data["form_id"]}" '
        f'xsi:noNamespaceSchemaLocation="http://scheme.cf.linedata.com/function.xsd" '
        f'fatherId="" beanId="{data["bean_id"]}">',
        '    <graphic>',
        '        <headerVisible>false</headerVisible>',
        '        <collapsible>false</collapsible>',
        '        <collapsed>false</collapsed>',
        '    </graphic>',
        '',
        '    <fieldLinks>'
    ]
    
    # Add field links
    for link in data['field_links']:
        xml_lines.extend([
            f'        <fieldLink childFieldId="{link["childFieldId"]}" '
            f'id="{link["id"]}" methodName="{link["methodName"]}" '
            f'nature="{link["nature"]}" disabled="{link["disabled"]}" '
            f'beanId="{link["beanId"]}">',
        ])
        
        for father in link['fathers']:
            xml_lines.append(f'            <fieldLinkFather fatherFieldId="{father}" />')
        
        xml_lines.append('        </fieldLink>')
    
    xml_lines.extend([
        '    </fieldLinks>',
        '',
        '    <areas>'
    ])
    
    # Add areas
    for area in data['areas']:
        xml_lines.extend([
            '',
            f'        <area id="{area["id"]}" sortNumber="{area["sortNumber"]}">',
            '            <graphic><headerVisible>false</headerVisible></graphic>',
            '            <fields>'
        ])
        
        # Add fields
        for field in area['fields']:
            field_attrs = [
                f'id="{field["id"]}"',
                f'nature="{field["nature"]}"',
                f'columnNumber="{field["columnNumber"]}"',
                f'sortNumber="{field["sortNumber"]}"',
                f'readOnly="{field["readOnly"]}"',
                f'hidden="{field["hidden"]}"'
            ]
            
            # Add optional attributes
            if field.get('lov'):
                field_attrs.append(f'lov="{field["lov"]}"')
            # Only add valueField if nature is "lov"
            if field.get('valueField') and field['nature'] == 'lov':
                field_attrs.append(f'valueField="{field["valueField"]}"')
            if field.get('functionId'):
                field_attrs.append(f'functionId="{field["functionId"]}"')
            if field.get('fkSearchField'):
                field_attrs.append(f'fkSearchField="{field["fkSearchField"]}"')
            if field.get('displayTemplate'):
                field_attrs.append(f'displayTemplate="{field["displayTemplate"]}"')
            if field.get('clearValueIfNotInStore'):
                field_attrs.append(f'clearValueIfNotInStore="{field["clearValueIfNotInStore"]}"')
            
            field_line = f'                <field {" ".join(field_attrs)}>'
            xml_lines.append(field_line)
            
            # Add label
            if field.get('label'):
                xml_lines.append(f'<label>{field["label"]}</label>')
            
            # Add controls
            if field.get('controls'):
                xml_lines.append('                    <controls>')
                for control in field['controls']:
                    xml_lines.append(f'                        <control id="{control["id"]}" nature="{control["nature"]}" />')
                xml_lines.append('                    </controls>')
            
            # Add filters
            if field.get('filters'):
                xml_lines.append('                    <filters>')
                for filter_item in field['filters']:
                    xml_lines.append(f'                        <filter id="{filter_item["id"]}" fieldId="{filter_item["fieldId"]}" />')
                xml_lines.append('                    </filters>')
            
            xml_lines.append('                </field>')
        
        xml_lines.extend([
            '            </fields>',
            '        </area>'
        ])
    
    xml_lines.extend([
        '',
        '    </areas>',
        '</form>'
    ])
    
    return '\n'.join(xml_lines)

# Enhanced data_loader.py with additional functions
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple

def load_area_config(area_config_path: Path) -> List[Dict[str, Any]]:
    """Load area configuration from JSON file"""
    with area_config_path.open(encoding="utf-8") as f:
        return json.load(f)

def load_json_data(fieldlink_path: Path, area_path: Path, filters_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]:
    """Load all required JSON data files"""
    # Load field links
    with fieldlink_path.open(encoding="utf-8") as f:
        field_links_data = json.load(f)
    
    # Load areas data
    with area_path.open(encoding="utf-8") as f:
        areas_data = json.load(f)
        areas_data = areas_data.get("original_json", {}).get("aini", {})
    
    # Load filters
    with filters_path.open(encoding="utf-8") as f:
        filters_list = json.load(f)
    
    return field_links_data, areas_data, filters_list

def create_field_name_mapping(areas_data: Dict[str, Any]) -> Dict[str, str]:
    """Create mapping from field names to their IDs"""
    field_name_to_id = {}
    for field_id, field_data in areas_data.items():
        label2 = field_data.get('label2', '')
        label1 = field_data.get('label1', '')
        label = field_data.get('label', '')
        # Priority to label2 as requested
        if label2:
            field_name_to_id[label2] = field_id
        elif label1:
            field_name_to_id[label1] = field_id
        elif label:
            field_name_to_id[label] = field_id
    return field_name_to_id

def create_filters_map(filters_list: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Create mapping from fields to their filters"""
    filters_map = {}
    for entry in filters_list:
        champ = entry.get("champ")
        params = entry.get("parametres", [])
        cleaned_params = [p.strip("'\"") for p in params if p.strip("'\"")]
        filters_map[champ] = cleaned_params
    return filters_map

def create_field_to_area_mapping(area_config: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Create mapping from fields to their area configuration"""
    field_to_area = {}
    for area_def in area_config:
        for field in area_def['fields']:
            field_name = field['name']
            field_to_area[field_name] = {
                'area_id': field['area'],
                'sort_number': field['sort_number'],
                'column_number': field['columnNumber']
            }
    return field_to_area

def organize_fields_by_area(field_to_area: Dict[str, Dict[str, Any]], 
                          field_name_to_id: Dict[str, str],
                          areas_data: Dict[str, Any]) -> Dict[str, List[Tuple[str, Dict[str, Any]]]]:
    """Organize fields into their respective areas"""
    area_fields = {"area1": [], "area2": [], "area3": []}
    
    # Process fields from field_to_area
    for field_name, field_info in field_to_area.items():
        area_id = field_info['area_id']
        field_id = field_name_to_id.get(field_name)
        
        if field_id and field_id in areas_data:
            field_data = areas_data[field_id].copy()
            # Only multiply sortNumber by 10 for area1
            if area_id == 'area1':
                field_data['sortNumber'] = str(int(field_info['sort_number']) * 10)
            else:
                field_data['sortNumber'] = field_info['sort_number']
            field_data['columnNumber'] = field_info['column_number']
            # Set readOnly to false by default
            field_data['readOnly'] = "false"
            area_fields[area_id].append((field_id, field_data))
    
    # Add static fields for area2 and area3
    static_fields = get_static_fields()
    for field_id, field_data in static_fields.items():
        if field_data.get('area') == 'area2':
            area_fields['area2'].append((field_id, field_data))
    
    consolidation_fields = get_consolidation_fields()
    for field_id, field_data in consolidation_fields.items():
        area_fields['area3'].append((field_id, field_data))
    
    return area_fields

def get_static_fields() -> Dict[str, Dict[str, Any]]:
    """Get static field definitions for area2"""
    return {
        "reiv_rceval": {
            "nature": "fk",
            "functionId": "FK_instrument",
            "valueField": "acecev",
            "fkSearchField": "acecev",
            "displayTemplate": "{acecev}",
            "sortNumber": "1",
            "columnNumber": "2",
            "readOnly": "false",
            "hidden": "False",
            "clearValueIfNotInStore": "true",
            "controls": [{"id": "mandatory", "nature": "MANDATORY"}],
            "area": "area2",
            "label": ""
        },
        "reiv_ridori": {
            "nature": "lov",
            "lov": "IprapRidoriLovQueryServiceImpl",
            "valueField": "value",
            "displayTemplate": "{value} - {longLabel}",
            "sortNumber": "2",
            "columnNumber": "2",
            "readOnly": "false",
            "hidden": "False",
            "clearValueIfNotInStore": "true",
            "controls": [{"id": "mandatory", "nature": "MANDATORY"}],
            "filters": [
                {"id": "reiv_rceval", "fieldId": "reiv_rceval"},
                {"id": "reiv_xidcev", "fieldId": "reiv_xidcev"}
            ],
            "area": "area2",
            "label": ""
        }
    }

def get_consolidation_fields() -> Dict[str, Dict[str, Any]]:
    """Get consolidation field definitions for area3"""
    return {
        "riddev": {
            "nature": "lov",
            "lov": "IprapRiddevLovQueryServiceImpl",
            "valueField": "value",
            "displayTemplate": "{value} - {longLabel}",
            "columnNumber": "1",
            "sortNumber": "1",
            "readOnly": "false",
            "hidden": "False",
            "clearValueIfNotInStore": "true",
            "controls": [{"id": "mandatory", "nature": "MANDATORY"}],
            "label": ""
        },
        "acetdev": {
            "nature": "lov",
            "lov": "IprapAcetdevLovQueryServiceImpl",
            "valueField": "value",
            "displayTemplate": "{value} - {longLabel}",
            "columnNumber": "1",
            "sortNumber": "2",
            "readOnly": "false",
            "hidden": "False",
            "clearValueIfNotInStore": "true",
            "controls": [{"id": "mandatory", "nature": "MANDATORY"}],
            "label": ""
        }
    }

def validate_json_files(fieldlink_path: Path, area_path: Path, filters_path: Path, area_config_path: Path) -> bool:
    """Validate that all required JSON files exist and are readable"""
    required_files = [fieldlink_path, area_path, filters_path, area_config_path]
    
    for file_path in required_files:
        if not file_path.exists():
            print(f"❌ Required file not found: {file_path}")
            return False
        
        try:
            with file_path.open(encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in file {file_path}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return False
    
    return True

