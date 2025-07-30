#!/usr/bin/env python3
"""
HTTP Data Integration Script
Integrates data from Spring Boot HTTP endpoints with XML generation
"""

import requests
import json
import os
import time
from pathlib import Path

class HTTPDataIntegration:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
    def test_server_connection(self):
        """Test if the Spring Boot server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/analyze", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_analyze_data(self):
        """Get data from /api/analyze endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/analyze")
            if response.status_code == 200:
                data = response.json()
                with open(self.output_dir / "analyze_response.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("✅ Saved analyze response")
                return data
            else:
                print(f"❌ Analyze endpoint failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error getting analyze data: {e}")
            return None
    
    def get_extract_function_data(self, path="test.java"):
        """Get data from /api/extract-function endpoint"""
        try:
            params = {"path": path}
            response = requests.get(f"{self.base_url}/api/extract-function", params=params)
            if response.status_code == 200:
                data = response.json()
                with open(self.output_dir / "extract_function_response.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("✅ Saved extract-function response")
                return data
            else:
                print(f"❌ Extract-function endpoint failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error getting extract-function data: {e}")
            return None
    
    def get_extract_function_name_data(self, path="test.java"):
        """Get data from /api/extract-function-name endpoint"""
        try:
            params = {"path": path}
            response = requests.get(f"{self.base_url}/api/extract-function-name", params=params)
            if response.status_code == 200:
                data = response.json()
                with open(self.output_dir / "extract_function_name_response.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("✅ Saved extract-function-name response")
                return data
            else:
                print(f"❌ Extract-function-name endpoint failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error getting extract-function-name data: {e}")
            return None
    
    def post_parser_fromcode_data(self, java_code="public class Test { }"):
        """Post data to /api/parser/fromCode endpoint"""
        try:
            headers = {"Content-Type": "text/plain"}
            response = requests.post(f"{self.base_url}/api/parser/fromCode", 
                                  data=java_code, headers=headers)
            if response.status_code == 200:
                data = response.json()
                with open(self.output_dir / "parser_fromcode_response.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("✅ Saved parser fromCode response")
                return data
            else:
                print(f"❌ Parser fromCode endpoint failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error posting parser fromCode data: {e}")
            return None
    
    def post_update_field_order_data(self, fields=None):
        """Post data to /transform/updateFieldOrder endpoint"""
        if fields is None:
            fields = ["field1", "field2"]
        
        try:
            headers = {"Content-Type": "application/json"}
            data = {"fields": fields}
            response = requests.post(f"{self.base_url}/transform/updateFieldOrder", 
                                  json=data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                with open(self.output_dir / "update_field_order_response.json", "w") as f:
                    json.dump(result, f, indent=2)
                print("✅ Saved updateFieldOrder response")
                return result
            else:
                print(f"❌ UpdateFieldOrder endpoint failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error posting updateFieldOrder data: {e}")
            return None
    
    def post_save_transformation_data(self, transformation="test"):
        """Post data to /transform/save-transformation endpoint"""
        try:
            headers = {"Content-Type": "application/json"}
            data = {"transformation": transformation}
            response = requests.post(f"{self.base_url}/transform/save-transformation", 
                                  json=data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                with open(self.output_dir / "save_transformation_response.json", "w") as f:
                    json.dump(result, f, indent=2)
                print("✅ Saved save-transformation response")
                return result
            else:
                print(f"❌ Save-transformation endpoint failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error posting save-transformation data: {e}")
            return None
    
    def collect_all_data(self):
        """Collect data from all endpoints"""
        print("🔍 Collecting data from all HTTP endpoints...")
        
        all_data = {}
        
        # GET endpoints
        all_data['analyze'] = self.get_analyze_data()
        all_data['extract_function'] = self.get_extract_function_data()
        all_data['extract_function_name'] = self.get_extract_function_name_data()
        
        # POST endpoints
        all_data['parser_fromcode'] = self.post_parser_fromcode_data()
        all_data['update_field_order'] = self.post_update_field_order_data()
        all_data['save_transformation'] = self.post_save_transformation_data()
        
        # Save combined data
        with open(self.output_dir / "all_endpoint_data.json", "w") as f:
            json.dump(all_data, f, indent=2)
        
        print("✅ All endpoint data collected and saved")
        return all_data
    
    def wait_for_server(self, max_wait=60):
        """Wait for server to be ready"""
        print(f"⏳ Waiting for server to be ready (max {max_wait}s)...")
        
        for i in range(max_wait):
            if self.test_server_connection():
                print("✅ Server is ready!")
                return True
            time.sleep(1)
            if i % 10 == 0:
                print(f"   Still waiting... ({i}s)")
        
        print("❌ Server not ready after maximum wait time")
        return False

def main():
    """Main function to run the HTTP data integration"""
    print("🚀 Starting HTTP Data Integration...")
    
    # Initialize the integration
    integration = HTTPDataIntegration()
    
    # Wait for server to be ready
    if not integration.wait_for_server():
        print("❌ Cannot proceed without server connection")
        return
    
    # Collect all data
    data = integration.collect_all_data()
    
    print("\n📊 Data Collection Summary:")
    for endpoint, result in data.items():
        status = "✅" if result is not None else "❌"
        print(f"  {status} {endpoint}")
    
    print(f"\n📁 All data saved to: {integration.output_dir}")
    print("🎯 Ready for XML generation!")

if __name__ == "__main__":
    main() 