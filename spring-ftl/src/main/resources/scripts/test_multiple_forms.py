#!/usr/bin/env python3
"""
Test script to demonstrate multi-form XML generation
"""

import json
import os
from pathlib import Path

def create_test_data():
    """Create test data with multiple forms"""
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Sample data with multiple forms
    test_data = {
        "originalJson": {
            "aini": {
                "xceopt": {"nature": "lov", "label": "Option", "sortNumber": "1"},
                "optcrm": {"nature": "string", "label": "CRM Option", "sortNumber": "2"},
                "ridtins": {"nature": "lov", "label": "Instrument Type", "sortNumber": "3"}
            },
            "user": {
                "username": {"nature": "string", "label": "Username", "sortNumber": "1"},
                "email": {"nature": "string", "label": "Email", "sortNumber": "2"},
                "role": {"nature": "lov", "label": "Role", "sortNumber": "3"}
            },
            "product": {
                "name": {"nature": "string", "label": "Product Name", "sortNumber": "1"},
                "price": {"nature": "number", "label": "Price", "sortNumber": "2"},
                "category": {"nature": "lov", "label": "Category", "sortNumber": "3"}
            }
        }
    }
    
    # Save test data
    transformed_path = output_dir / "transformed_result.json"
    with open(transformed_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2)
    
    # Create area map for each form
    area_map = {
        "xceopt": {"area": "area1", "sortNumber": "1", "columnNumber": "1"},
        "optcrm": {"area": "area1", "sortNumber": "2", "columnNumber": "1"},
        "ridtins": {"area": "area1", "sortNumber": "3", "columnNumber": "1"},
        "username": {"area": "area1", "sortNumber": "1", "columnNumber": "1"},
        "email": {"area": "area1", "sortNumber": "2", "columnNumber": "1"},
        "role": {"area": "area1", "sortNumber": "3", "columnNumber": "1"},
        "name": {"area": "area1", "sortNumber": "1", "columnNumber": "1"},
        "price": {"area": "area1", "sortNumber": "2", "columnNumber": "1"},
        "category": {"area": "area1", "sortNumber": "3", "columnNumber": "1"}
    }
    
    area_map_path = output_dir / "area_map.json"
    with open(area_map_path, 'w', encoding='utf-8') as f:
        json.dump(area_map, f, indent=2)
    
    # Create field links
    fieldlinks_data = {
        "links": [
            {
                "childFieldId": "optcrm",
                "id": "link_optcrm",
                "methodName": "isOptcrmVisible",
                "nature": "CONDITIONNALHIDDEN",
                "disabled": "false",
                "fatherFieldIds": ["xceopt"]
            }
        ]
    }
    
    fieldlinks_path = output_dir / "fieldlink.json"
    with open(fieldlinks_path, 'w', encoding='utf-8') as f:
        json.dump(fieldlinks_data, f, indent=2)
    
    print("✅ Test data created successfully!")
    print(f"📁 Output directory: {output_dir}")
    print("📋 Forms available: aini, user, product")

def test_form_detection():
    """Test the form detection functionality"""
    print("\n🔍 Testing form detection...")
    
    output_dir = Path("output")
    if output_dir.exists():
        transformed_path = output_dir / "transformed_result.json"
        if transformed_path.exists():
            try:
                with open(transformed_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                forms = []
                if 'originalJson' in data:
                    forms = list(data['originalJson'].keys())
                elif isinstance(data, dict):
                    forms = list(data.keys())
                
                print(f"✅ Detected forms: {forms}")
                return forms
            except Exception as e:
                print(f"❌ Error reading data: {e}")
    
    print("❌ No test data found")
    return []

def main():
    """Main test function"""
    print("🧪 Testing multi-form XML generation...")
    
    # Create test data
    create_test_data()
    
    # Test form detection
    forms = test_form_detection()
    
    if forms:
        print(f"\n📋 Forms to process: {forms}")
        print("\n🎯 The XML generator should now work with multiple forms:")
        for form_id in forms:
            print(f"  - {form_id}")
        
        print("\n💡 To test with a specific form, set the FORM_ID environment variable:")
        for form_id in forms:
            print(f"  FORM_ID={form_id} python main.py")
        
        print("\n📄 Check the .idea/demo directory for generated XML files")
    else:
        print("❌ No forms detected")

if __name__ == "__main__":
    main() 