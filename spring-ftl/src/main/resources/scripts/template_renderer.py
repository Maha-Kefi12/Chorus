from pathlib import Path
from typing import Dict, List, Any, Tuple
from jinja2 import Environment, FileSystemLoader, select_autoescape

def prepare_template_data(field_links_data: Dict[str, Any], 
                        area_fields: Dict[str, List[Tuple[str, Dict[str, Any]]]], 
                        filters_map: Dict[str, List[str]]) -> Dict[str, Any]:
    """Prepare data for the template"""
    template_data = {
        'father_id': '',
        'fieldLinks': [],
        'fields': []
    }

    # Process field links
    for link in field_links_data:
        template_data['fieldLinks'].append({
            'childFieldId': link['childFieldId'],
            'id': link['id'],
            'methodName': link['methodName'],
            'nature': link['nature'],
            'beanId': link['beanId'],
            'fatherFieldIds': link['fatherFieldIds']
        })

    # Define area sort numbers
    area_sort_numbers = {
        'area1': 1,
        'area2': 3,  # Changed from 2 to 3
        'area3': 2   # Changed from 3 to 2
    }

    # Process fields by area
    for area_id, fields in area_fields.items():
        area_sort_number = area_sort_numbers[area_id]
        
        for field_id, field_data in fields:
            field = {
                'id': field_id,
                'area': area_id,
                'nature': field_data.get('nature', 'string'),
                'columnNumber': field_data.get('columnNumber', '1'),
                'sortNumber': field_data.get('sortNumber', '1'),
                'readOnly': field_data.get('readOnly', 'false'),
                'hidden': field_data.get('hidden', 'false')
            }

            # Handle labels - prioritize label2
            if 'label2' in field_data:
                field['label'] = field_data['label2']
            else:
                field['label'] = field_data.get('label', '')

            # Add optional fields only if they exist and have values
            for attr in ['lov', 'valueField', 'displayTemplate', 'maxLength', 'defaultValue', 'setWithValuesList']:
                if attr in field_data and field_data[attr]:
                    field[attr] = field_data[attr]

            # Add filters if they exist for this field
            if field_id in filters_map:
                field['filters'] = [{'id': f_id, 'fieldId': f_id} for f_id in filters_map[field_id]]

            template_data['fields'].append(field)

    return template_data

def render_template(template_dir: Path, template_name: str, data: Dict[str, Any], output_path: Path) -> None:
    """Render template with data and write to output file"""
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    template = env.get_template(template_name)
    output = template.render(**data)
    
    # Write output with proper encoding
    output_path.write_text(output, encoding='cp1252') 