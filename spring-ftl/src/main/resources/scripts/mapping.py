import json
from pathlib import Path
from jinja2 import Template
import unicodedata
import re
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
            {'id': 'reiv_rceval', 'nature': 'fk', 'functionId': 'FK_instrument', 'valueField': 'acecev', 'fkSearchField': 'acecev', 'displayTemplate': '{acecev}', 'sortNumber': '1', 'columnNumber': '2', 'readOnly': 'false', 'clearValueIfNotInStore': 'true', 'label': 'Revenu évalué', 'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}]},
            {'id': 'reiv_ridori', 'nature': 'lov', 'lov': 'IprapRidoriLovQueryServiceImpl', 'valueField': 'value', 'displayTemplate': '{value} - {longLabel}', 'sortNumber': '2', 'columnNumber': '2', 'readOnly': 'false', 'clearValueIfNotInStore': 'true', 'label': 'Revenu origine', 'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}], 'filters': [{'id': 'reiv_rceval', 'fieldId': 'reiv_rceval'}, {'id': 'reiv_xidcev', 'fieldId': 'reiv_xidcev'}]},
            {'id': 'reic_rcepla', 'nature': 'lov', 'lov': 'IprapRceplaLovQueryServiceImpl', 'valueField': 'value', 'displayTemplate': '{value} - {longLabel}', 'sortNumber': '3', 'columnNumber': '2', 'readOnly': 'false', 'clearValueIfNotInStore': 'true', 'label': 'Revenu crédit place', 'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}], 'filters': [{'id': 'reiv_rceval', 'fieldId': 'reiv_rceval'}, {'id': 'reiv_xidcev', 'fieldId': 'reiv_xidcev'}, {'id': 'reiv_ridori', 'fieldId': 'reiv_ridori'}]},
            {'id': 'iprap_adtvalid', 'nature': 'lov', 'lov': 'IprapAdtpalLovQueryServiceImpl', 'valueField': 'value', 'displayTemplate': '{value}', 'sortNumber': '4', 'columnNumber': '2', 'readOnly': 'false', 'clearValueIfNotInStore': 'true', 'label': 'Date de validation', 'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}], 'filters': [{'id': 'reiv_rceval', 'fieldId': 'reiv_rceval'}, {'id': 'reiv_xidcev', 'fieldId': 'reiv_xidcev'}, {'id': 'reiv_ridori', 'fieldId': 'reiv_ridori'}, {'id': 'xetb_xidcec', 'fieldId': 'xetb_xidcec'}, {'id': 'xetb_xidced', 'fieldId': 'xetb_xidced'}, {'id': 'reic_rcepla', 'fieldId': 'reic_rcepla'}, {'id': 'xuti_xidclg', 'fieldId': 'xuti_xidclg'}]},
            {'id': 'rgvlm_rllgvl', 'nature': 'string', 'sortNumber': '5', 'columnNumber': '2', 'readOnly': 'false', 'hidden': 'false', 'label': 'Réglement valeur'}
        ]
    },
    'csoPanel': {
        'area': 'area3',
        'fields': [
            {'id': 'riddev', 'nature': 'lov', 'lov': 'IprapRiddevLovQueryServiceImpl', 'valueField': 'value', 'displayTemplate': '{value} - {longLabel}', 'columnNumber': '1', 'sortNumber': '1', 'readOnly': 'false', 'clearValueIfNotInStore': 'true', 'label': 'Risque de défaut', 'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}]},
            {'id': 'adtchgo', 'nature': 'date', 'sortNumber': '1', 'columnNumber': '2', 'readOnly': 'false', 'label': 'Date de changement', 'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}]},
            {'id': 'rcepla', 'nature': 'lov', 'lov': 'IprapRceplaLovQueryServiceImpl', 'valueField': 'value', 'displayTemplate': '{value} - {longLabel}', 'columnNumber': '2', 'sortNumber': '2', 'readOnly': 'false', 'clearValueIfNotInStore': 'true', 'label': 'Risque de crédit', 'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}]},
            {'id': 'acetdev', 'nature': 'lov', 'lov': 'IprapAcetdevLovQueryServiceImpl', 'valueField': 'value', 'displayTemplate': '{value} - {longLabel}', 'columnNumber': '1', 'sortNumber': '2', 'readOnly': 'false', 'clearValueIfNotInStore': 'true', 'label': 'Acceptation de défaut', 'controls': [{'id': 'mandatory', 'nature': 'MANDATORY'}]}
        ]
    }
}

AREA_TITLES = {
    'area1': "Critères de lancement",
    'area2': "Critères avancés",
    'area3': "Critères de consolidation"
}

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
    <fieldLink childFieldId="{{ link.childFieldId }}" 
               id="{{ link.id }}"
               methodName="{{ link.methodName }}" 
               nature="{{ link.nature }}" 
               disabled="false"
               beanId="{{ link.beanId }}FieldLinkService">
      {% for father in link.fatherFieldIds %}
      <fieldLinkFather fatherFieldId="{{ father }}" />
      {% endfor %}
    </fieldLink>
    {% endfor %}
  </fieldLinks>

  <areas>
    {% for area_name, area_fields in area_groups.items() %}
    {% if area_name == 'area2' %}
    <area id="area2" sortNumber="3">
    {% elif area_name == 'area3' %}
    <area id="area3" sortNumber="2">
    {% else %}
    <area id="{{ area_name }}" sortNumber="1">
    {% endif %}
      <graphic>
        <headerVisible>false</headerVisible>
      </graphic>
      <fields>
        {% for field in area_fields %}
        <field id="{{ field.id }}"
               nature="{{ field.nature }}"
               {% if field.defaultValue is defined %}defaultValue="{{ field.defaultValue }}"{% endif %}
               columnNumber="{{ field.columnNumber }}"
               sortNumber="{{ field.sortNumber }}"
               {% if field.maxLength is defined %}maxLength="{{ field.maxLength }}"{% endif %}
               {% if field.readOnly is defined %}readOnly="{{ field.readOnly }}"{% endif %}
               {% if field.hidden is defined %}hidden="{{ field.hidden }}"{% endif %}
               {% if field.lov is defined %}lov="{{ field.lov }}"{% endif %}
               {% if field.valueField is defined %}valueField="{{ field.valueField }}"{% endif %}
               {% if field.setWithValuesList is defined %}setWithValuesList="{{ field.setWithValuesList }}"{% endif %}>
          {% if field.label is defined %}<label>{{ field.label }}</label>{% endif %}
          {% if field.nature == "lov" and field.filters is defined %}
          <filters>
            {% for filter in field.filters %}
            <filter id="{{ filter.id }}" fieldId="{{ filter.fieldId }}" />
            {% endfor %}
          </filters>
          {% endif %}
        </field>
        {% endfor %}
      </fields>
    </area>
    {% endfor %}

    {% if 'area2' not in area_groups %}
    <area id="area2" sortNumber="3">
      <fields>
        <field id="csoPanel" nature="string" sortNumber="1" columnNumber="1">
          <label>CSO Panel</label>
        </field>
        <field id="csoOption" nature="LdsComboBox" sortNumber="2" columnNumber="1">
          <label>Option CSO</label>
        </field>
      </fields>
    </area>
    {% endif %}

    {% if 'area3' not in area_groups %}
    <area id="area3" sortNumber="3">
      <fields>
        <field id="valeurPanel" nature="string" sortNumber="1" columnNumber="1">
          <label>Valeur Panel</label>
        </field>
        <field id="valeurOption" nature="lov" sortNumber="2" columnNumber="1" setWithValuesList="true">
          <label>Option Valeur</label>
          <filters>
            <filter id="filter1" fieldId="valeurFilter1" />
            <filter id="filter2" fieldId="valeurFilter2" />
          </filters>
        </field>
      </fields>
    </area>
    {% endif %}
  </areas>
</form>
"""

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text.lower())
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^ -~\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def build_label2_area_map(area_data):
    # Map normalized name -> (area, sortNumber, columnNumber)
    label2_map = {}
    for area in area_data:
        for field in area.get('fields', []):
            name = field.get('name', '')
            norm = normalize_text(name)
            label2_map[norm] = {
                'area': field.get('area', 'area1'),
                'sortNumber': field.get('sort_number', 10),
                'columnNumber': field.get('columnNumber', 1)
            }
    return label2_map

def build_field_mapping_from_area_map(area_map, form_fields):
    mapped = {}
    # Map area names
    area_name_map = {
        "Critères de lancement": "area1",
        "Critères avancés": "area2",
        "Critères de consolidation": "area3"
    }
    
    # Create area_map lookup by fieldId for the new structure
    area_map_lookup = {}
    area1_sort_numbers = []
    for entry in area_map:
        if 'fieldId' in entry:
            area_name = entry.get('area', 'Critères de lancement')
            mapped_area = area_name_map.get(area_name, 'area1')
            if mapped_area == 'area1' and 'sortNumber' in entry:
                try:
                    area1_sort_numbers.append(int(entry['sortNumber']))
                except Exception:
                    pass
            area_map_lookup[entry['fieldId']] = {
                'area': mapped_area,
                'sortNumber': entry.get('sortNumber', 10),
                'columnNumber': entry.get('columnNumber', 1),
                'label': entry.get('label', '')
            }
    
    # Find the starting sortNumber for unmapped area1 fields
    if area1_sort_numbers:
        next_area1_sort = min(area1_sort_numbers)
    else:
        next_area1_sort = 10
    
    # Collect unmapped area1 fields in order
    unmapped_area1_fields = []
    for field_id, field_data in form_fields.items():
        if not isinstance(field_data, dict):
            continue
        if field_id not in area_map_lookup:
            unmapped_area1_fields.append((field_id, field_data))
    
    # Assign sortNumbers to unmapped area1 fields in order
    unmapped_sort_numbers = {}
    for field_id, field_data in unmapped_area1_fields:
        unmapped_sort_numbers[field_id] = next_area1_sort
        next_area1_sort += 10
    
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
            field['label'] = mapping['label']
        elif field_id in unmapped_sort_numbers:
            # Default to area1 with incremental sort numbers, in order
            field['area'] = 'area1'
            field['sortNumber'] = unmapped_sort_numbers[field_id]
            field['columnNumber'] = field.get('columnNumber', 1)
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

def group_fields_by_area(mapped_fields: dict) -> dict:
    area_fields = {'area1': [], 'area2': [], 'area3': []}
    for field in mapped_fields.values():
        area = field.get('area', 'area1')
        if area not in area_fields:
            area_fields[area] = []
        area_fields[area].append(field)
    # Keep original order from area_map.json, don't sort by sortNumber
    return area_fields

def main():
    base_path = Path(resource_path("output"))
    area_config_path = base_path / "area_data.json"
    transformed_path = base_path / "transformed_result.json"
    response_path = base_path / "fieldlink.json"
    area_map_path = base_path / "area_map.json"
    
    # Load data
    area_data = json.load(area_config_path.open(encoding="utf-8"))
    transformed_data = json.load(transformed_path.open(encoding="utf-8"))
    area_map = json.load(area_map_path.open(encoding="utf-8"))
    
    # Get form data
    if 'originalJson' in transformed_data:
        form_id = next(iter(transformed_data['originalJson']))
        form_fields = transformed_data['originalJson'][form_id]
    else:
        form_id = next(iter(transformed_data))
        form_fields = transformed_data[form_id]
    
    print(f"📊 Processing form: {form_id}")
    print(f"📊 Total fields in transformed_result.json: {len(form_fields)}")
    print(f"📊 Total entries in area_map.json: {len(area_map)}")
    
    # Check for panel fields
    panel_fields = [field_id for field_id in form_fields.keys() if field_id in STATIC_PANELS]
    print(f"📊 Panel fields found: {panel_fields}")
    
    # Load field links
    field_links = []
    if response_path.exists():
        response_data = json.load(response_path.open(encoding="utf-8"))
        for link in response_data.get("links", []):
            if isinstance(link, dict):
                field_links.append({
                    "childFieldId": link.get("childFieldId"),
                    "id": link.get("id"),
                    "methodName": link.get("methodName"),
                    "nature": link.get("nature"),
                    "beanId": link.get("beanId"),
                    "fatherFieldIds": link.get("fatherFieldIds", [])
                })
    
    # Build mapping
    mapped_fields = build_field_mapping_from_area_map(area_map, form_fields)
    area_fields = group_fields_by_area(mapped_fields)
    
    # Generate XML
    output_dir = Path(resource_path(f'C:/Users/USER/Downloads/spring-ftl/.idea/demo/{form_id}'))
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f'{form_id}.mapping.xml'
    template = Template(TEMPLATE)
    xml_content = template.render({
        "form_id": form_id,
        "fieldLinks": field_links,
        "area_groups": area_fields,
        "area_titles": AREA_TITLES
    })
    output_path.write_text(xml_content, encoding="utf-8")
    
    print(f"\n✅ XML generated at: {output_path}")
    print(f"\n📊 Summary:")
    for area_id, fields in area_fields.items():
        print(f"  {area_id}: {len(fields)} fields")
        if area_id == 'area3' and len(fields) == 0:
            print(f"    ⚠️  WARNING: {area_id} is empty! Check if csoPanel exists in transformed_result.json")
        elif area_id == 'area3' and len(fields) > 0:
            print(f"    ✅ {area_id} has {len(fields)} fields (including static panel fields)")
    
    print(f"Total mapped fields: {len(mapped_fields)}")
    
    # Verify area3 is not empty
    if len(area_fields.get('area3', [])) == 0:
        print("\n❌ ERROR: area3 is empty! This should not happen when csoPanel exists.")
        return
    else:
        print(f"\n✅ SUCCESS: area3 has {len(area_fields['area3'])} fields")
        print(f"   Static fields in area3: {[f['id'] for f in area_fields['area3']]}")

if __name__ == "__main__":
    main()