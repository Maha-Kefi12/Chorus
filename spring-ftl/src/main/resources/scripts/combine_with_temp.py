import json
import re
from pathlib import Path
from xml.sax.saxutils import escape
from typing import Dict, List, Tuple, Any
from jinja2 import Template
import traceback

TEMPLATE = """\
{# Template Jinja2 généré automatiquement #}
<form xmlns:jxb="http://java.sun.com/xml/ns/jaxb"
      xmlns:xjc="http://java.sun.com/xml/ns/jaxb/xjc"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      id="{{ form_id }}"
      xsi:noNamespaceSchemaLocation="http://scheme.cf.linedata.com/function.xsd"
      fatherId="LotIntervallePortefeuille"
      beanId="{{ form_id }}FormService">
  <graphic>
    <headerVisible>false</headerVisible>
    <collapsible>false</collapsible>
    <collapsed>false</collapsed>
  </graphic>

  <fieldLinks>
    {% for link in fieldLinks %}
      <fieldLink childFieldId="{{ link.childFieldId }}" id="{{ link.id }}"
                 methodName="{{ link.methodName }}" nature="{{ link.nature }}" disabled="false"
                 beanId="{{ link.beanId }}FieldLinkService">
        {% for father in link.fatherFieldIds %}
          <fieldLinkFather fatherFieldId="{{ father }}" />
        {% endfor %}
      </fieldLink>
    {% endfor %}
  </fieldLinks>

  <areas>
    <area id="area1" sortNumber="1">
      <fields>
        {% set sort = 10 %}
        {% for field in fields %}
          {% if field.id != "valeurPanel" and field.id != "csoPanel" %}
            <field
              {% if field.id is defined %}id="{{ field.id }}"{% endif %}
              {% if field.id == "optionStock" %}nature="LdsComboBox"{% elif field.setWithValuesList is defined and field.setWithValuesList %}nature="lov"{% else %}nature="{{ field.nature }}"{% endif %}
              {% if field.defaultValue is defined %}defaultValue="{{ field.defaultValue }}"{% endif %}
              columnNumber="1"
              sortNumber="{{ sort }}"
              {% if field.maxLength is defined %}maxLength="{{ field.maxLength }}"{% endif %}
              {% if field.readOnly is defined %}readOnly="{{ field.readOnly }}"{% endif %}
              {% if field.hidden is defined %}hidden="{{ field.hidden }}"{% endif %}
              {% if field.lov is defined %}lov="{{ field.lov }}"{% endif %}
              {% if field.valueField is defined %}valueField="{{ field.valueField }}"{% endif %}
              {% if field.setWithValuesList is defined %}setWithValuesList="{{ field.setWithValuesList }}"{% endif %}
            />
            {% if field.id == "ridtins" %}<label>Type(s) d'instrument(s)</label>{% endif %}
            {% set sort = sort + 10 %}
          {% endif %}
        {% endfor %}
      </fields>
    </area>

    {% set field_ids = fields | map(attribute='id') | list %}
    {% if 'csoPanel' in field_ids %}
      <area id="area2" sortNumber="3">
        <fields>
          <field id="riddev" nature="lov" lov="IprapRiddevLovQueryServiceImpl" valueField="value"
                 displayTemplate="{value} - {longLabel}" columnNumber="1" sortNumber="1" clearValueIfNotInStore="true">
            <controls><control id="mandatory" nature="MANDATORY" /></controls>
          </field>
          <field id="acetdev" nature="lov" lov="IprapAcetdevLovQueryServiceImpl" valueField="value"
                 displayTemplate="{value} - {longLabel}" columnNumber="1" sortNumber="2" clearValueIfNotInStore="true">
            <controls><control id="mandatory" nature="MANDATORY" /></controls>
          </field>
          <field id="adtchgo" nature="date" sortNumber="3" columnNumber="2">
            <controls><control id="mandatory" nature="MANDATORY" /></controls>
          </field>
          <field id="rcepla" nature="lov" lov="IprapRceplaLovQueryServiceImpl" valueField="value"
                 displayTemplate="{value} - {longLabel}" columnNumber="2" sortNumber="4" clearValueIfNotInStore="true">
            <controls><control id="mandatory" nature="MANDATORY" /></controls>
          </field>
        </fields>
      </area>
    {% endif %}

    {% if 'valeurPanel' in field_ids %}
      <area id="area3" sortNumber="2">
        <fields>
          <field id="reiv_rceval" nature="fk" functionId="FK_instrument" valueField="acecev" fkSearchField="acecev"
                 displayTemplate="{acecev}" sortNumber="1" columnNumber="1" clearValueIfNotInStore="true">
            <controls><control id="mandatory" nature="MANDATORY" /></controls>
          </field>
          <field id="reiv_ridori" nature="lov" lov="IprapRidoriLovQueryServiceImpl" valueField="value"
                 displayTemplate="{value} - {longLabel}" sortNumber="2" columnNumber="1" clearValueIfNotInStore="true">
            <controls><control id="mandatory" nature="MANDATORY" /></controls>
            <filters>
              <filter id="reiv_rceval" fieldId="reiv_rceval" />
              <filter id="reiv_xidcev" fieldId="reiv_xidcev" />
            </filters>
          </field>
          <field id="reic_rcepla" nature="lov" lov="IprapRceplaLovQueryServiceImpl" valueField="value"
                 displayTemplate="{value} - {longLabel}" sortNumber="3" columnNumber="1" clearValueIfNotInStore="true">
            <controls><control id="mandatory" nature="MANDATORY" /></controls>
            <filters>
              <filter id="reiv_rceval" fieldId="reiv_rceval" />
              <filter id="reiv_xidcev" fieldId="reiv_xidcev" />
              <filter id="reiv_ridori" fieldId="reiv_ridori" />
            </filters>
          </field>
          <field id="iprap_adtvalid" nature="lov" lov="IprapAdtpalLovQueryServiceImpl" valueField="value"
                 displayTemplate="{value}" sortNumber="4" columnNumber="1" clearValueIfNotInStore="true">
            <controls><control id="mandatory" nature="MANDATORY" /></controls>
            <filters>
              <filter id="reiv_rceval" fieldId="reiv_rceval" />
              <filter id="reiv_xidcev" fieldId="reiv_xidcev" />
              <filter id="reiv_ridori" fieldId="reiv_ridori" />
              <filter id="xetb_xidcec" fieldId="xetb_xidcec" />
              <filter id="xetb_xidced" fieldId="xetb_xidced" />
              <filter id="reic_rcepla" fieldId="reic_rcepla" />
              <filter id="xuti_xidclg" fieldId="xuti_xidclg" />
            </filters>
          </field>
          <field id="rgvlm_rllgvl" nature="string" readOnly="true" hidden="false" sortNumber="5" columnNumber="1" />
        </fields>
      </area>
    {% endif %}
  </areas>
"""

def escape_attr(value):
    if value is None:
        return ""
    return escape(str(value), {'"': "&quot;", "'": "&apos;"})

def load_area_config():
    """Charge la configuration des areas depuis le fichier JSON"""
    area_config_path = Path(r"C:\Users\USER\Downloads\spring-ftl\output\area_data.json")
    with area_config_path.open(encoding="utf-8") as f:
        return json.load(f)

def get_field_id_from_label(label, areas_data):
    """Trouve l'ID technique d'un champ à partir de son label"""
    for field_id, field_data in areas_data.items():
        if (field_data.get('label2') == label or
            field_data.get('label1') == label or
            field_data.get('label') == label):
            return field_id
    return None

def contains_field(data, field_id):
    """Vérifie si un champ avec l'id donné existe dans les données"""
    if isinstance(data, list):
        return any(item.get("id") == field_id for item in data)
    elif isinstance(data, dict):
        return field_id in data
    return False

def check_static_area_dependencies(transformed_result_path):
    """Vérifie les dépendances pour les champs statiques des areas"""
    try:
        if not transformed_result_path.exists():
            print("❌ Fichier transformed_result.json introuvable.")
            return {"valeurPanel": False, "csoPanel": False}

        with transformed_result_path.open(encoding='utf-8') as f:
            data = json.load(f)

        original_json = data.get("original_json", {})
        aini_data = original_json.get("aini", {}) if isinstance(original_json, dict) else {}

        dependencies = {
            "valeurPanel": contains_field(aini_data, "valeurPanel"),
            "csoPanel": contains_field(aini_data, "csoPanel")
        }

        if not dependencies.get("valeurPanel", False):
            print("ℹ️ Static fields for area2 were skipped (valeurPanel not found)")
        if not dependencies.get("csoPanel", False):
            print("ℹ️ Static fields for area3 were skipped (csoPanel not found)")

        return dependencies

    except Exception as e:
        print(f"❌ Erreur lors de la lecture de transformed_result.json: {e}")
        # Always return a dict, never a bool
        return {"valeurPanel": False, "csoPanel": False}

def find_field_id_by_label(label, transformed_result_path):
    """
    Find a field ID by its label using various matching strategies
    """
    with transformed_result_path.open(encoding='utf-8') as f:
        data = json.load(f)

    # First try direct match in original_json
    aini_data = data.get("original_json", {}).get("aini", {})
    for field_id, field_data in aini_data.items():
        if any(field_data.get(label_type) == label or field_data.get(label_type) == "Type instrument"
               for label_type in ['label', 'label1', 'label2']):
            return field_id

    # Try matching through label_mappings
    label_mappings = data.get("label_mappings", [])
    for mapping in label_mappings:
        if mapping.get("nouveau") == label or mapping.get("ancien") == "Type instrument":
            # Found the new label, now find the field with the old label
            old_label = mapping.get("ancien")
            for field_id, field_data in aini_data.items():
                if any(field_data.get(label_type) == old_label
                      for label_type in ['label', 'label1', 'label2']):
                    return field_id

    # Try matching in area_configs
    area_configs = data.get("area_configs", [])
    for area in area_configs:
        for field in area.get("fields", []):
            if field.get("name") == label or field.get("name") == "Type instrument":
                # Found the field, now find its ID in aini_data
                for field_id, field_data in aini_data.items():
                    if any(field_data.get(label_type) == field.get("name")
                          for label_type in ['label', 'label1', 'label2']):
                        return field_id

    return None

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
            field_data['sortNumber'] = field_info['sort_number']
            field_data['columnNumber'] = field_info['column_number']
            # Set readOnly to false by default
            field_data['readOnly'] = "false"
            area_fields[area_id].append((field_id, field_data))
   
    return area_fields

def prepare_template_data(field_links_data: Any,
                        area_fields: Dict[str, List[Tuple[str, Dict[str, Any]]]],
                        filters_map: Dict[str, List[str]]) -> Dict[str, Any]:
    """Prepare data for the template"""
    template_data = {
        'form_id': 'aini',
        'fieldLinks': [],
        'area_groups': {
            'area1': [],
            'area2': [],
            'area3': []
        }
    }

    # Correction ici : supporte dict ou list
    if isinstance(field_links_data, dict):
        links_iter = field_links_data.values()
    else:
        links_iter = field_links_data

    for link in links_iter:
        if not isinstance(link, dict):
            print("Skipping non-dict link:", link, type(link))
            continue
        template_data['fieldLinks'].append({
            'childFieldId': link['childFieldId'],
            'id': link['id'],
            'methodName': link['methodName'],
            'nature': link['nature'],
            'beanId': link['beanId'],
            'fatherFieldIds': link['fatherFieldIds']
        })

    # Process fields by area
    for area_id, fields in area_fields.items():
        for field_id, field_data in fields:
            field = {
                'id': field_id,
                'nature': field_data.get('nature', 'string'),
                'columnNumber': field_data.get('columnNumber', '1'),
                'readOnly': field_data.get('readOnly', 'false'),
                'hidden': field_data.get('hidden', 'false'),
                'label': field_data.get('label', '')
            }
           
            if area_id == 'area1':
                field['sortNumber'] = str(int(field_data.get('sortNumber', '1')))
            else:
                field['sortNumber'] = field_data.get('sortNumber', '1')

            # Add optional fields only if they exist
            for attr in ['lov', 'valueField', 'displayTemplate', 'maxLength', 'defaultValue', 'setWithValuesList']:
                if attr in field_data:
                    field[attr] = field_data[attr]

            # Add filters if they exist for this field
            if field_id in filters_map:
                field['filters'] = [{'id': f_id, 'fieldId': f_id} for f_id in filters_map[field_id]]

            template_data['area_groups'][area_id].append(field)

    return template_data

def correct_area_sort_numbers_and_readonly(area_id: str, field_data: Dict[str, Any], area1_sort_counter: Dict[str, int] = None) -> Dict[str, Any]:
    """
    Corriger les sortNumber des areas et s'assurer que readOnly est false par défaut
    """
    corrected_data = field_data.copy()
   
    # FORCER readOnly à false TOUJOURS
    corrected_data['readOnly'] = 'false'
   
    # Correction des sortNumbers selon l'area
    if area_id == 'area1' and area1_sort_counter is not None:
        # Pour area1: le premier champ garde son sortNumber, puis +10 à chaque fois
        if area1_sort_counter['count'] == 0:
            # Premier champ: garder son sortNumber original
            try:
                original_sort = int(corrected_data.get('sortNumber', '1'))
                area1_sort_counter['current'] = original_sort
                corrected_data['sortNumber'] = str(original_sort)
            except (ValueError, TypeError):
                area1_sort_counter['current'] = 1
                corrected_data['sortNumber'] = '1'
        else:
            # Champs suivants: ajouter +10 à chaque fois
            area1_sort_counter['current'] += 10
            corrected_data['sortNumber'] = str(area1_sort_counter['current'])
       
        area1_sort_counter['count'] += 1
    elif area_id == 'area1':
        # Fallback si pas de counter (ne devrait pas arriver)
        try:
            original_sort = int(corrected_data.get('sortNumber', '1'))
            corrected_data['sortNumber'] = str(original_sort * 10)
        except (ValueError, TypeError):
            corrected_data['sortNumber'] = '10'
   
    return corrected_data

def main():
    # === Paths ===
    fieldlink_json_path = Path(r"C:\Users\USER\Downloads\spring-ftl\output\fieldlink.json")
    area_json_path = Path(r"C:\Users\USER\Downloads\spring-ftl\output\transformed_result.json")
    filters_json_path = Path(r"C:\Users\USER\Downloads\spring-ftl\output\parsed_result.json")
    base_output_dir = Path(r"C:\Users\USER\Downloads\spring-ftl\.idea\demo")

    try:
        # Load JSON data
        with fieldlink_json_path.open(encoding="utf-8") as f:
            field_links_data = json.load(f)
        with area_json_path.open(encoding="utf-8") as f:
            areas_data = json.load(f)
            areas_data = areas_data.get("original_json", {}).get("aini", {})
        with filters_json_path.open(encoding="utf-8") as f:
            filters_list = json.load(f)

        # Check dependencies for static fields
        dependencies = check_static_area_dependencies(area_json_path)
        print("DEBUG dependencies:", dependencies, type(dependencies))
        valeurpanel_exists = dependencies.get("valeurPanel", False)
        csopanel_exists = dependencies.get("csoPanel", False)
    
        area_config = load_area_config()

        # Créer un mapping des noms de champs vers leurs IDs techniques
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

        # Build filters_map
        filters_map = {}
        for entry in filters_list:
            champ = entry.get("champ")
            params = entry.get("parametres", [])
            cleaned_params = [p.strip("'\"") for p in params if p.strip("'\"")]
            filters_map[champ] = cleaned_params

        # Excluded filter values
        excluded_filter_values = {"AINI", "ATCN", "1", "", "AIMM"}

        # Prepare output
        form_id = "aini"
        output_subfolder = base_output_dir / form_id
        output_subfolder.mkdir(parents=True, exist_ok=True)
        output_xml_path = output_subfolder / f"{form_id}BlockForm.block.xml"

        # Créer un mapping des champs vers leurs areas basé sur area_data.json
        field_to_area = {}
        for area_def in area_config:
            for field in area_def['fields']:
                field_name = field['name']
                field_to_area[field_name] = {
                    'area_id': field['area'],
                    'sort_number': field['sort_number'],
                    'column_number': field['columnNumber']
                }

        # Find the correct ID for Type(s) d'instrument(s)
        instrument_types_id = find_field_id_by_label("Type(s) d'instrument(s)", area_json_path) or "ridtins"

        # Add instrument types field
        instrument_types_field = {
            "id": instrument_types_id,
            "nature": "lov",
            "label": "Type(s) d'instrument(s)",
            "columnNumber": 2,
            "sortNumber": 12,
            "editable": "true",
            "hidden": "false",
            "lov": "InstrumentTypesLovQueryServiceImpl",
            "valueField": "value",
            "displayTemplate": "{value} - {label}"
        }
       
        # Convert editable to readOnly
        if "editable" in instrument_types_field:
            is_editable = instrument_types_field.pop("editable").lower() == "true"
            instrument_types_field["readOnly"] = str(not is_editable).lower()
       
        areas_data[instrument_types_id] = instrument_types_field

        # Organiser les champs dans leurs areas respectives
        area_fields = {"area1": [], "area2": [], "area3": []}
        area1_sort_counter = {'count': 0, 'current': 0}
       
        for field_name, field_info in field_to_area.items():
            area_id = field_info['area_id']
            field_id = field_name_to_id.get(field_name)
           
            if field_id and field_id in areas_data:
                field_data = areas_data[field_id].copy()
                field_data['sortNumber'] = field_info['sort_number']
                field_data['columnNumber'] = field_info['column_number']
               
                if area_id == 'area1':
                    field_data = correct_area_sort_numbers_and_readonly(area_id, field_data, area1_sort_counter)
                else:
                    field_data = correct_area_sort_numbers_and_readonly(area_id, field_data)

                area_fields[area_id].append((field_id, field_data))

        # Préparer les listes de champs pour chaque area
        fields_area1 = [field_data for field_id, field_data in area_fields['area1']]
        fields_area2 = [field_data for field_id, field_data in area_fields['area2']]
        fields_area3 = [field_data for field_id, field_data in area_fields['area3']]

        # Construire la liste complète des champs pour la variable 'fields' (pour area1)
        # et fournir les autres areas séparément
        all_fields = fields_area1 + fields_area2 + fields_area3
        field_ids = [field.get('id') for field in all_fields if 'id' in field]

        template_data = {
            'form_id': form_id,
            'fieldLinks': [],
            'fields': fields_area1,  # area1
            'fields_area2': fields_area2,
            'fields_area3': fields_area3,
            'field_ids': field_ids
        }

        # Correction ici : supporte dict ou list
        if isinstance(field_links_data, dict):
            links_iter = field_links_data.values()
        else:
            links_iter = field_links_data

        for link in links_iter:
            if not isinstance(link, dict):
                print("Skipping non-dict link:", link, type(link))
                continue
            template_data['fieldLinks'].append({
                'childFieldId': link['childFieldId'],
                'id': link['id'],
                'methodName': link['methodName'],
                'nature': link['nature'],
                'beanId': link['beanId'],
                'fatherFieldIds': link['fatherFieldIds']
            })

        # Render template
        template = Template(TEMPLATE)
        xml_content = template.render(template_data)

        # Write XML to file
        output_xml_path.write_text(xml_content, encoding="utf-8")
        print(f"✅ Fichier XML généré : {output_xml_path}")

    except Exception as e:
        print(f"❌ Erreur : {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()