#!/usr/bin/env python3
"""
Test script for Parameter API endpoints
"""
import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_parameters_api():
    """Test parameter CRUD operations"""
    
    # First, we need to authenticate (assuming you have auth setup)
    # For now, we'll test without auth - you may need to modify this
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    print("Testing Parameter API...")
    
    # Test 1: Get all parameters
    print("\n1. Testing GET /api/parameters")
    try:
        response = requests.get(f"{BASE_URL}/parameters", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('parameters', []))} parameters")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Create a new parameter
    print("\n2. Testing POST /api/parameters")
    new_parameter = {
        "name": "Test Parameter",
        "unit": "units",
        "description": "A test parameter for API testing",
        "enabled": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/parameters", 
            headers=headers,
            json=new_parameter
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            created_param = response.json().get('parameter')
            param_id = created_param.get('id') if created_param else None
            
            if param_id:
                # Test 3: Get specific parameter
                print(f"\n3. Testing GET /api/parameters/{param_id}")
                response = requests.get(f"{BASE_URL}/parameters/{param_id}", headers=headers)
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                
                # Test 4: Update parameter
                print(f"\n4. Testing PUT /api/parameters/{param_id}")
                update_data = {
                    "description": "Updated test parameter description"
                }
                response = requests.put(
                    f"{BASE_URL}/parameters/{param_id}",
                    headers=headers,
                    json=update_data
                )
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                
                # Test 5: Delete parameter
                print(f"\n5. Testing DELETE /api/parameters/{param_id}")
                response = requests.delete(f"{BASE_URL}/parameters/{param_id}", headers=headers)
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_parameters_api()