#!/usr/bin/env python3
"""Test script for parameter management functionality"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.models.parameter import Parameter
from app.models.user import User
from app.utils.jwt_utils import create_token

def test_parameter_functionality():
    """Test parameter CRUD operations"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("PARAMETER MANAGEMENT TEST SUITE")
        print("=" * 60)
        
        # Test 1: Check default parameters
        print("\n[TEST 1] Checking default parameters...")
        params = Parameter.query.all()
        print(f"✓ Found {len(params)} parameters in database")
        for param in params:
            print(f"  - {param.name} ({param.unit}): {param.description}")
        
        # Test 2: Verify parameter fields
        print("\n[TEST 2] Verifying parameter fields...")
        if params:
            param = params[0]
            required_fields = ['id', 'name', 'unit', 'description', 'enabled', 'is_default', 'created_at']
            param_dict = param.to_dict()
            for field in required_fields:
                if field in param_dict:
                    print(f"✓ Field '{field}' present: {param_dict[field]}")
                else:
                    print(f"✗ Field '{field}' missing!")
        
        # Test 3: Create new parameter
        print("\n[TEST 3] Creating new parameter...")
        new_param = Parameter(
            name='Humidity',
            unit='%',
            description='Relative humidity measurement',
            enabled=True,
            is_default=False
        )
        db.session.add(new_param)
        db.session.commit()
        print(f"✓ Created parameter: {new_param.name}")
        print(f"  ID: {new_param.id}")
        print(f"  Unit: {new_param.unit}")
        print(f"  Description: {new_param.description}")
        
        # Test 4: Update parameter
        print("\n[TEST 4] Updating parameter...")
        param_to_update = Parameter.query.filter_by(name='Humidity').first()
        if param_to_update:
            param_to_update.enabled = False
            db.session.commit()
            print(f"✓ Updated parameter: {param_to_update.name}")
            print(f"  Enabled: {param_to_update.enabled}")
        
        # Test 5: Query parameters
        print("\n[TEST 5] Querying parameters...")
        enabled_params = Parameter.query.filter_by(enabled=True).all()
        disabled_params = Parameter.query.filter_by(enabled=False).all()
        print(f"✓ Enabled parameters: {len(enabled_params)}")
        print(f"✓ Disabled parameters: {len(disabled_params)}")
        
        # Test 6: Verify serialization
        print("\n[TEST 6] Verifying parameter serialization...")
        all_params = Parameter.query.all()
        serialized = [p.to_dict() for p in all_params]
        print(f"✓ Successfully serialized {len(serialized)} parameters")
        
        # Test 7: Check database integrity
        print("\n[TEST 7] Checking database integrity...")
        total_params = Parameter.query.count()
        print(f"✓ Total parameters in database: {total_params}")
        
        # Test 8: Verify default parameters exist
        print("\n[TEST 8] Verifying default parameters...")
        default_names = ['Temperature', 'Pressure', 'Flow Rate']
        for name in default_names:
            param = Parameter.query.filter_by(name=name).first()
            if param:
                print(f"✓ Default parameter found: {name}")
            else:
                print(f"✗ Default parameter missing: {name}")
        
        print("\n" + "=" * 60)
        print("TEST SUITE COMPLETED")
        print("=" * 60)
        
        # Cleanup: Remove test parameter
        print("\n[CLEANUP] Removing test parameter...")
        test_param = Parameter.query.filter_by(name='Humidity').first()
        if test_param:
            db.session.delete(test_param)
            db.session.commit()
            print("✓ Test parameter removed")

if __name__ == '__main__':
    try:
        test_parameter_functionality()
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
