#!/usr/bin/env python3
"""
Test script to verify bidirectional sync between web and desktop
"""

import requests
import json
import time

def test_parameter_sync():
    """Test parameter synchronization"""
    base_url = "http://localhost:5000/api"
    
    print("🧪 Testing Parameter Sync...")
    
    # 1. Create parameter via web API
    print("\n1. Creating parameter via web API...")
    param_data = {
        "name": "Test Sync Parameter",
        "unit": "sync_unit",
        "description": "Testing bidirectional sync",
        "enabled": True
    }
    
    try:
        response = requests.post(f"{base_url}/parameters", json=param_data)
        if response.status_code == 201:
            created_param = response.json()['parameter']
            print(f"✅ Parameter created: {created_param['name']} (ID: {created_param['id']})")
            
            # Wait for sync
            time.sleep(2)
            
            # 2. Verify parameter appears in list
            print("\n2. Verifying parameter in list...")
            response = requests.get(f"{base_url}/parameters")
            if response.status_code == 200:
                parameters = response.json()['parameters']
                sync_param = next((p for p in parameters if p['name'] == param_data['name']), None)
                if sync_param:
                    print(f"✅ Parameter found in list: {sync_param['name']}")
                else:
                    print("❌ Parameter not found in list")
            
            # 3. Update parameter
            print("\n3. Updating parameter...")
            update_data = {
                "description": "Updated via sync test",
                "enabled": False
            }
            response = requests.put(f"{base_url}/parameters/{created_param['id']}", json=update_data)
            if response.status_code == 200:
                print("✅ Parameter updated successfully")
                time.sleep(2)
            
            # 4. Delete parameter
            print("\n4. Deleting parameter...")
            response = requests.delete(f"{base_url}/parameters/{created_param['id']}")
            if response.status_code == 200:
                print("✅ Parameter deleted successfully")
            else:
                print(f"❌ Failed to delete parameter: {response.status_code}")
        else:
            print(f"❌ Failed to create parameter: {response.status_code} - {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_backend_connection():
    """Test backend connection"""
    print("🔗 Testing Backend Connection...")
    
    try:
        response = requests.get("http://localhost:5000/api/parameters", timeout=5)
        if response.status_code == 200:
            params = response.json().get('parameters', [])
            print(f"✅ Backend connected. Found {len(params)} parameters")
            return True
        else:
            print(f"❌ Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PrecisionPulse Sync Test")
    print("=" * 40)
    
    if test_backend_connection():
        test_parameter_sync()
    
    print("\n" + "=" * 40)
    print("✅ Test completed")