import json
from pathlib import Path
from collections import defaultdict
import os
import re

# === STATIC CONFIGURATIONS ===
STATIC_PANELS = {
    'valeurPanel': {
        'area': 'area2',
        'fields': [
            {
                'id': 'reiv_rceval',
                'nature': 'fk',
                'functionId': 'FK_instrument',
                'valueField': 'acecev',
                'fkSearchField': 'acecev',
                'displayTemplate': '{acecev}',
                'sortNumber': '1',
                'columnNumber': '2',
                'readOnly': 'false',
                'clearValueIfNotInStore': 'true',
                'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}]
            },
            {
                'id': 'reiv_ridori',
                'nature': 'lov',
                'lov': 'IprapRidoriLovQueryServiceImpl',
                'valueField': 'value',
                'displayTemplate': '{value} - {longLabel}',
                'sortNumber': '2',
                'columnNumber': '2',
                'readOnly': 'false',
                'clearValueIfNotInStore': 'true',
                'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}],
                'filters': [
                    {'id': 'reiv_rceval', 'fieldId': 'reiv_rceval'},
                    {'id': 'reiv_xidcev', 'fieldId': 'reiv_xidcev'}
                ]
            }
        ]
    },
    'csoPanel': {
        'area': 'area3',
        'fields': [
            {
                'id': 'riddev',
                'nature': 'lov',
                'lov': 'IprapRiddevLovQueryServiceImpl',
                'valueField': 'value',
                'displayTemplate': '{value} - {longLabel}',
                'columnNumber': '1',
                'sortNumber': '1',
                'readOnly': 'false',
                'clearValueIfNotInStore': 'true',
                'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}]
            },
            {
                'id': 'acetdev',
                'nature': 'lov',
                'lov': 'IprapAcetdevLovQueryServiceImpl',
                'valueField': 'value',
                'displayTemplate': '{value} - {longLabel}',
                'columnNumber': '1',
                'sortNumber': '2',
                'readOnly': 'false',
                'clearValueIfNotInStore': 'true',
                'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}]
            }
        ]
    }
}

class FieldMapper:
    """Generic field mapper that can work with any form configuration"""
    
    def __init__(self, transformed_data):
        self.transformed_data = transformed_data
        self.field_mapping = {}
        self.create_field_mapping()
    
    def normalize_text(self, text):
        """Normalize text by removing accents and special characters"""
        if not text:
            return ""
        # Remove accents and convert to lowercase
        text = text.lower()
        text = re.sub(r'[éèêë]', 'e', text)
        text = re.sub(r'[àâä]', 'a', text)
        text = re.sub(r'[ïî]', 'i', text)
        text = re.sub(r'[ôö]', 'o', text)
        text = re.sub(r'[ùûü]', 'u', text)
        text = re.sub(r'[ç]', 'c', text)
        return text
    
    def find_field_by_label(self, search_label, form_data):
        """Find field ID by matching labels"""
        search_label_norm = self.normalize_text(search_label)
        
        # First try exact match
        for field_id, field_data in form_data.items():
            if isinstance(field_data, dict):
                for label_key in ['label2', 'label']:
                    if label_key in field_data:
                        field_label = self.normalize_text(field_data[label_key])
                        if field_label == search_label_norm:
                            return field_id
        
        # Then try partial match
        for field_id, field_data in form_data.items():
            if isinstance(field_data, dict):
                for label_key in ['label2', 'label']:
                    if label_key in field_data:
                        field_label = self.normalize_text(field_data[label_key])
                        if search_label_norm in field_label or field_label in search_label_norm:
                            return field_id
        
        return None
    
    def create_field_mapping(self):
        """Create mapping between area_data fields and form fields"""
        # Get original form data
        original_json = self.transformed_data.get("originalJson", {})
        form_key = next(iter(original_json.keys()), None)
        if not form_key:
            return
            
        form_data = original_json[form_key]
        label_mappings = {
            self.normalize_text(item["ancien"]): self.normalize_text(item["nouveau"])
            for item in self.transformed_data.get("labelMappings", [])
        }
        
        # First, process static panel fields
        for panel_id, panel_config in STATIC_PANELS.items():
            for field in panel_config['fields']:
                field_id = field['id']
                self.field_mapping[field_id] = {
                    'id': field_id,
                    'sort_number': int(field.get('sortNumber', 999)),
                    'columnNumber': int(field.get('columnNumber', 1)),
                    'area': panel_config['area'],
                    'label': field_id  # Default label is the field ID
                }
        
        # Create a mapping of field names to their area data
        area_field_mapping = {}
        for area_config in self.transformed_data.get("areaConfigs", []):
            area_id = "area" + area_config['area'][-1]  # Convert to area1, area2, etc.
            for field in area_config.get("fields", []):
                field_name = field.get("name")
                if field_name:
                    area_field_mapping[self.normalize_text(field_name)] = {
                        'sort_number': field.get('sort_number', 999),
                        'columnNumber': field.get('columnNumber', 1),
                        'area': area_id,
                        'original_name': field_name
                    }
        
        # Process each field in form data
        for field_id, field_data in form_data.items():
            if not isinstance(field_data, dict) or field_id in STATIC_PANELS:
                continue
                
            # Get field labels
            label2 = field_data.get('label2', '')
            label = field_data.get('label', '')
            
            # Try to find matching area field
            area_field = None
            normalized_label2 = self.normalize_text(label2)
            normalized_label = self.normalize_text(label)
            
            # Try label2 first
            if normalized_label2 in area_field_mapping:
                area_field = area_field_mapping[normalized_label2]
            # Then try label
            elif normalized_label in area_field_mapping:
                area_field = area_field_mapping[normalized_label]
            # Then try label mappings
            elif normalized_label in label_mappings:
                mapped_label = label_mappings[normalized_label]
                if mapped_label in area_field_mapping:
                    area_field = area_field_mapping[mapped_label]
            
            if area_field:
                self.field_mapping[field_id] = {
                    'id': field_id,
                    'sort_number': area_field['sort_number'],
                    'columnNumber': area_field['columnNumber'],
                    'area': area_field['area'],
                    'label': area_field['original_name']
                }
            else:
                # Default to area1 with high sort number
                self.field_mapping[field_id] = {
                    'id': field_id,
                    'sort_number': 999,
                    'columnNumber': 1,
                    'area': 'area1',
                    'label': label2 or label or field_id
                }

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

def get_script_dir():
    return Path(__file__).parent.resolve()

def find_matching_field_name(field_id: str, field_label: str, area_configs: dict, label_mappings: dict) -> tuple:
    """Find matching field name and area from area_data.json"""
    # First try by label
    if field_label:
        # Try direct match
        for area_id, configs in area_configs.items():
            for config in configs:
                if config["name"] == field_label:
                    return config["name"], area_id
                
        # Try through label mappings
        if field_label in label_mappings:
            mapped_label = label_mappings[field_label]
            for area_id, configs in area_configs.items():
                for config in configs:
                    if config["name"] == mapped_label:
                        return config["name"], area_id
    
    # Special handling for opt_ fields
    if field_id.startswith('opt_'):
        # Map common patterns
        if field_id == 'opt_libimmo':
            return "Option sur l'immobilier", "area2"
        elif field_id == 'opt_libcpta':
            return "Option compta TCN précomptes", "area2"
        elif field_id == 'opt_amti':
            return "Intérêts échus décalés", "area2"
        elif field_id == 'opt_cpta':
            return "Option compta TCN précomptes", "area2"
    
    # Try to find by similar patterns
    field_id_normalized = field_id.lower().replace('_', ' ')
    for area_id, configs in area_configs.items():
        for config in configs:
            config_name_normalized = config["name"].lower()
            # Check if the field_id contains significant parts of the config name or vice versa
            if (field_id_normalized in config_name_normalized or 
                config_name_normalized in field_id_normalized):
                return config["name"], area_id
    
    return None, None

def generate_properties_file(transformed_data, output_path):
    """Generate the properties file with correct format and sorting"""
    # Extract form data
    form_id = next(iter(transformed_data.get("originalJson", {}).keys()))
    form_data = transformed_data.get("originalJson", {}).get(form_id, {})
    
    # Create label mappings
    label_mappings = {
        item["ancien"]: item["nouveau"]
        for item in transformed_data.get("labelMappings", [])
    }
    
    # Initialize area fields with their configurations from area_data.json
    area_configs = {}
    for area_config in transformed_data.get("areaConfigs", []):
        area_name = area_config["area"]
        area_id = "area1" if "lancement" in area_name.lower() else "area2" if "avancés" in area_name.lower() else "area3"
        
        if area_id not in area_configs:
            area_configs[area_id] = []
            
        for field in area_config["fields"]:
            area_configs[area_id].append({
                "name": field["name"],
                "sort_number": int(field.get("sort_number", 999)),
                "column_number": int(field.get("columnNumber", 1))
            })
    
    # Sort configurations by sort_number and column_number
    for area_id in area_configs:
        area_configs[area_id].sort(key=lambda x: (x["sort_number"], x["column_number"]))
    
    # Initialize result areas
    area_fields = {
        "area1": [],
        "area2": [],
        "area3": []
    }
    
    # Process all fields from form_data
    processed_fields = set()
    
    # First, process fields from area_data.json
    for area_id, configs in area_configs.items():
        for config in configs:
            field_name = config["name"]
            sort_number = config["sort_number"]
            column_number = config["column_number"]
            
            # Try to find matching field
            matched_field_id = None
            
            # Try direct match
            for field_id, field_data in form_data.items():
                if not isinstance(field_data, dict) or field_id in ["valeurPanel", "csoPanel"]:
                    continue
                    
                field_label = field_data.get("label2", field_data.get("label", ""))
                
                # Check various matching conditions
                if (field_label == field_name or
                    (field_label in label_mappings and label_mappings[field_label] == field_name) or
                    field_id == field_name):
                    matched_field_id = field_id
                    break
            
            if matched_field_id:
                area_fields[area_id].append({
                    "id": matched_field_id,
                    "label": field_name,
                    "sort_number": sort_number,
                    "column_number": column_number
                })
                processed_fields.add(matched_field_id)
    
    # Process remaining fields
    for field_id, field_data in form_data.items():
        if not isinstance(field_data, dict) or field_id in ["valeurPanel", "csoPanel"]:
            continue
            
        if field_id not in processed_fields:
            field_label = field_data.get("label2", field_data.get("label", ""))
            
            # Try to find matching field name and area
            matching_name, matching_area = find_matching_field_name(field_id, field_label, area_configs, label_mappings)
            
            if matching_name and matching_area:
                # Find the configuration for this field
                matching_config = None
                for config in area_configs[matching_area]:
                    if config["name"] == matching_name:
                        matching_config = config
                        break
                
                area_fields[matching_area].append({
                    "id": field_id,
                    "label": matching_name,
                    "sort_number": matching_config["sort_number"] if matching_config else 999,
                    "column_number": matching_config["column_number"] if matching_config else 1
                })
            else:
                # Default to area1
                area_fields["area1"].append({
                    "id": field_id,
                    "label": field_label or field_id,
                    "sort_number": 999,
                    "column_number": 1
                })
    
    # Add static panel fields
    static_area_fields = {
        "area2": {
            "reiv_rceval": "Code instrument",
            "reiv_ridori": "Origine",
            "reic_rcepla": "Place de cotation",
            "iprap_adtvalid": "Date palier",
            "rgvlm_rllgvl": "Libelle instrument"
        },
    "area3": [
        "riddev", "adtchgo", "rcepla", "acetdev"
    ]
}

    # Add static panel fields
    for area_id, static_fields in static_area_fields.items():
        if isinstance(static_fields, dict):
            # For area2 with specific labels
            for field_id, label in static_fields.items():
                if field_id not in [f["id"] for f in area_fields[area_id]]:
                    # Get configuration from STATIC_PANELS if available
                    static_config = None
                    for panel in STATIC_PANELS.values():
                        if panel["area"] == area_id:
                            for field in panel["fields"]:
                                if field["id"] == field_id:
                                    static_config = field
                                    break
                    
                    sort_number = int(static_config["sortNumber"]) if static_config else 999
                    column_number = int(static_config["columnNumber"]) if static_config else 1
                    
                    area_fields[area_id].append({
                        "id": field_id,
                        "label": label,
                        "sort_number": sort_number,
                        "column_number": column_number
                    })
        else:
            # For area3 with default labels
            for field_id in static_fields:
                if field_id not in [f["id"] for f in area_fields[area_id]]:
                    # Get configuration from STATIC_PANELS if available
                    static_config = None
                    for panel in STATIC_PANELS.values():
                        if panel["area"] == area_id:
                            for field in panel["fields"]:
                                if field["id"] == field_id:
                                    static_config = field
                                    break
                    
                    sort_number = int(static_config["sortNumber"]) if static_config else 999
                    column_number = int(static_config["columnNumber"]) if static_config else 1
                    
                    area_fields[area_id].append({
                        "id": field_id,
                        "label": field_id,
                        "sort_number": sort_number,
                        "column_number": column_number
                    })
    
    # Generate output
    lines = ["title=\n"]
    
    # Process areas in order
    for area_id in ["area1", "area2", "area3"]:
        if area_fields[area_id]:
            # Add area title
            lines.append(f"{area_id}.title=Criteres de lancement" if area_id == "area1" else
                        f"{area_id}.title=Criteres avances" if area_id == "area2" else
                        f"{area_id}.title=Criteres de consolidation")
            
            # Sort fields by sort_number and column_number
            sorted_fields = sorted(
                area_fields[area_id],
                key=lambda x: (int(x["sort_number"]), int(x["column_number"]))
            )
            
            # Add fields
            for field in sorted_fields:
                lines.append(f"    {field['id']}.label={field['label']}")
            
            lines.append("")
    
    # Write to file
    with open(output_path, "w", encoding="ansi") as f:
        f.write("\n".join(lines))

# === CHARGEMENT DES DONNÉES ===
script_dir = get_script_dir()
workspace_root = find_workspace_root(script_dir)

if not workspace_root:
    print("❌ Impossible de trouver le repertoire racine du workspace")
    exit()

print(f"Workspace root: {workspace_root}")
json_path = workspace_root / "output" / "transformed_result.json"
print(f"Looking for JSON at: {json_path}")

try:
    with open(json_path, encoding="utf-8") as f:
        transformed_data = json.load(f)
    print("✅ Fichier JSON charge avec succes")
except Exception as e:
    print(f"❌ Erreur lors du chargement du JSON: {e}")
    exit()

# === EXTRACTION ===
if not transformed_data:
    print("❌ Le fichier JSON est vide")
    exit()

# Extract form data and formId
form_id = next(iter(transformed_data.get("originalJson", {}).keys())) if isinstance(transformed_data.get("originalJson"), dict) else "default"

# === SAUVEGARDE ===
output_dir = workspace_root / ".idea" / "demo" / form_id
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / f"{form_id}BlockForm.bloc.properties"

try:
    generate_properties_file(transformed_data, output_path)
    print(f"✅ Fichier genere avec succes: {output_path}")
    os.startfile(output_dir)
except Exception as e:
    print(f"❌ Erreur lors de l'ecriture du fichier: {e}")