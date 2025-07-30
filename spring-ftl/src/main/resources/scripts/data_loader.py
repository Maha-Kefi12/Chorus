import json
from pathlib import Path
from typing import Dict, List, Any, Tuple

def load_area_config(area_config_path: Path) -> List[Dict[str, Any]]:
    """Load area configuration from JSON file"""
    with area_config_path.open(encoding="utf-8") as f:
        return json.load(f)

def load_json_data(fieldlink_path, area_path, filters_path):
    with open(fieldlink_path, encoding='utf-8') as f:
        field_links_data = json.load(f)

    with open(area_path, encoding='utf-8') as f:
        area_data = json.load(f)
        
        # Corrige si les éléments sont des chaînes JSON
        if isinstance(area_data, list) and isinstance(area_data[0], str):
            area_data = [json.loads(item) for item in area_data]
        elif isinstance(area_data, dict):
            for key, value in area_data.items():
                if isinstance(value, str):
                    area_data[key] = json.loads(value)

    with open(filters_path, encoding='utf-8') as f:
        filters_data = json.load(f)

    return field_links_data, area_data, filters_data

def create_field_name_mapping(areas_data: Dict[str, Any]) -> Dict[str, str]:
    """Create mapping from field names to their IDs"""
    field_name_to_id = {}
    for field_id, field_data in areas_data.items():
        label2 = field_data.get('label2', '')
        label1 = field_data.get('label1', '')
        label = field_data.get('label', '')
        if label2:
            field_name_to_id[label2] = field_id
        if label1:
            field_name_to_id[label1] = field_id
        if label:
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

def create_field_to_area_mapping(area_config):
    field_to_area = {}

    for i, area in enumerate(area_config):
        if not isinstance(area, dict):
            print(f"❌ L’élément area[{i}] n’est pas un dict : {type(area)}")
            continue

        area_name = area.get("area")
        fields = area.get("fields", [])

        if not isinstance(fields, list):
            print(f"❌ fields n’est pas une liste dans area[{i}]: {type(fields)}")
            continue

        for j, field in enumerate(fields):
            if not isinstance(field, dict):
                print(f"❌ field[{j}] dans area[{i}] n’est pas un dict : {type(field)}")
                continue

            field_id = field.get("name")
            field_area = field.get("area", area_name)

            if field_id and field_area:
                field_to_area[field_id] = field_area
            else:
                print(f"⚠️ Champ ignoré - ID: {field_id}, Area: {field_area}")

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
            "clearValueIfNotInStore": "true",
            "controls": [{"id": "mandatory", "nature": "MANDATORY"}]
        },
        "reiv_ridori": {
            "nature": "lov",
            "lov": "IprapRidoriLovQueryServiceImpl",
            "valueField": "value",
            "displayTemplate": "{value} - {longLabel}",
            "sortNumber": "2",
            "columnNumber": "2",
            "clearValueIfNotInStore": "true",
            "controls": [{"id": "mandatory", "nature": "MANDATORY"}],
            "filters": [
                {"id": "reiv_rceval", "fieldId": "reiv_rceval"},
                {"id": "reiv_xidcev", "fieldId": "reiv_xidcev"}
            ]
        },
        # ... other static fields
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
            "clearValueIfNotInStore": "true",
            "controls": [{"id": "mandatory", "nature": "MANDATORY"}]
        },
        "acetdev": {
            "nature": "lov",
            "lov": "IprapAcetdevLovQueryServiceImpl",
            "valueField": "value",
            "displayTemplate": "{value} - {longLabel}",
            "columnNumber": "1",
            "sortNumber": "2",
            "clearValueIfNotInStore": "true",
            "controls": [{"id": "mandatory", "nature": "MANDATORY"}]
        },
        # ... other consolidation fields
    } 