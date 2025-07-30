#!/usr/bin/env python3
"""
Script to generate Spring XML configuration from parsed_result.json using the provided template.
"""

import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

import json
from jinja2 import Template

def load_json_data(file_path):
    """Load and parse the JSON data file."""
    try:
        with open(resource_path(file_path), 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

def load_function_id(file_path):
    """Load the function ID from the function-name-f.json file."""
    try:
        with open(resource_path(file_path), 'r', encoding='utf-8') as file:
            data = json.load(file)
        # Assuming the function ID is stored as a simple string or in a key
        # You may need to adjust this based on the actual structure of your JSON
        if isinstance(data, str):
            return data
        elif isinstance(data, dict) and 'functionId' in data:
            return data['functionId']
        elif isinstance(data, dict) and 'function_id' in data:
            return data['function_id']
        elif isinstance(data, dict) and 'name' in data:
            return data['name']
        else:
            # If it's a dict, try to get the first value
            if isinstance(data, dict) and data:
                return list(data.values())[0]
            return str(data) if data else ""
    except FileNotFoundError:
        print(f"Warning: Function ID file {file_path} not found. Using empty function ID.")
        return ""
    except json.JSONDecodeError as e:
        print(f"Error parsing function ID JSON: {e}")
        return ""

def process_fields(data):
    """Process the JSON data to match template expectations."""
    fields = []
    
    for item in data:
        # Only process fields with type "lov"
        if item.get('type') == 'lov':
            # Map JSON structure to template variables
            # INVERTED LOGIC: withParams=false means HAS parameters (goes to individual beans)
            # withParams=true means NO parameters (goes to generic bean)
            field = {
                'fieldId': item['champ'],
                'isWithParam': item['withParams'],  # Keep original value
                'parametres': item.get('parametres', []),
                'methode': item['methode'],
                'type': item['type'],
                'filters': item.get('filters', [])
            }
            fields.append(field)
    
    return fields

    

def generate_spring_config(fields, function_id=''):
    """Generate Spring XML configuration using the template."""
    
    # Define the template string with INVERTED logic
    template_str = '''<bean id="genericLovQueryService"
        class="com.linedata.chorus.std.services.commons.service.lov.service.impl.GenericLovQueryServiceImpl">
    <property name="frameworkJdbcTemplate" ref="chorusDaoTemplate" />
    <property name="sqlListOfValuesQuery">
      <map merge="true">
        {% for field in fields if field.isWithParam %}
        <entry key="{{ field.fieldId }}{{ functionId }}_valuesList_01">
          <bean class="org.apache.commons.io.IOUtils" factory-method="toString">
            <constructor-arg type="java.io.InputStream"
              value="classpath:com/linedata/chorus/std/services/commons/dao/lovvalue/{{ field.methode }}.sql" />
          </bean>
        </entry>
        {% endfor %}
      </map>
    </property>
  </bean>
  {% for field in fields if not field.isWithParam %}
  <bean id="{{ field.fieldId }}{{ functionId }}LovQueryService"
        class="com.linedata.chorus.std.services.commons.service.lov.service.impl.{{ field.fieldId }}{{ functionId }}LovQueryServiceImpl">
    <property name="frameworkJdbcTemplate" ref="chorusDaoTemplate" />
    <property name="sqlListOfValuesQuery">
      <map merge="true">
        <entry key="{{ field.fieldId }}{{ functionId }}LovQueryService">
          <bean class="org.apache.commons.io.IOUtils" factory-method="toString">
            <constructor-arg type="java.io.InputStream"
              value="classpath:com/linedata/chorus/std/services/commons/dao/lovvalue/{{ field.methode }}.sql" />
          </bean>
        </entry>
      </map>
    </property>
  </bean>
  {% endfor %}'''
    
    # Create Jinja2 template
    template = Template(template_str)
    
    # Render the template
    output = template.render(fields=fields, functionId=function_id)
    
    return output

def main():
    """Main function to execute the script."""
    # File paths
    json_file_path = resource_path(r"output\parsed_result.json")
    function_id_file_path = resource_path(r"output\function-name-f.json")
    
    # Load JSON data
    print("Loading JSON data...")
    data = load_json_data(json_file_path)
    
    if data is None:
        return
    
    # Load function ID
    print("Loading function ID...")
    function_id = load_function_id(function_id_file_path)
    print(f"Function ID loaded: '{function_id}'")
    
    # Process fields
    print("Processing fields...")
    fields = process_fields(data)
    
    # Generate Spring configuration
    print("Generating Spring configuration...")
    spring_config = generate_spring_config(fields, function_id)
    
    # Output the result
    print("\n" + "="*80)
    print("GENERATED SPRING XML CONFIGURATION:")
    print("="*80)
    print(spring_config)
    
    # Optionally save to file
    output_file = resource_path(rf".idea\demo\{function_id}\{function_id}LovServiceImpl.spring.xml")
    try:
        # Create directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(spring_config)
        print(f"\nConfiguration saved to: {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")
    
    # Display summary with INVERTED logic explanation
    print(f"\nSummary:")
    print(f"- Function ID: '{function_id}'")
    print(f"- Total LOV fields processed: {len(fields)}")
    
    # INVERTED LOGIC for summary:
    # withParams=true means NO parameters (goes to genericLovQueryService)
    # withParams=false means HAS parameters (gets individual service bean)
    fields_without_params = [f for f in fields if f['isWithParam']]  # withParams=true = NO params
    fields_with_params = [f for f in fields if not f['isWithParam']]  # withParams=false = HAS params
    
    print(f"- Fields with parameters: {len(fields_with_params)} (withParams=false)")
    print(f"- Fields without parameters: {len(fields_without_params)} (withParams=true)")
    
    # Show field details
    if fields_with_params:
        print(f"- Fields with parameters (individual beans): {[f['fieldId'] for f in fields_with_params]}")
    if fields_without_params:
        print(f"- Fields without parameters (generic bean): {[f['fieldId'] for f in fields_without_params]}")

if __name__ == "__main__":
    main()