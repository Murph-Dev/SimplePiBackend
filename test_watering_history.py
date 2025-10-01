#!/usr/bin/env python3
"""
Test script to verify the watering history API endpoints work correctly.
"""

import sys
import json
import time

try:
    import requests
except ImportError:
    print("Error: 'requests' module not found!")
    print("Please install it with: pip install requests")
    sys.exit(1)

def get_base_url():
    """Get the base URL from command line arguments or use default"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test the watering history API endpoints')
    parser.add_argument('--url', default='http://192.168.68.78:8000', 
                       help='Base URL of the API server (default: http://192.168.68.78:8000)')
    parser.add_argument('--local', action='store_true', 
                       help='Use localhost instead of Pi IP')
    
    args = parser.parse_args()
    
    if args.local:
        return 'http://127.0.0.1:8000'
    return args.url

def test_watering_history_api(base_url):
    """Test the watering history API endpoints"""
    
    print("Testing Watering History API")
    print("=" * 35)
    print(f"Testing URL: {base_url}")
    print()
    
    device_id = "autogrow_esp32"
    
    # Test 1: Get watering history (should be empty initially)
    print("1. Testing GET watering history...")
    try:
        response = requests.get(f"{base_url}/api/v1/watering-history?device_id={device_id}")
        if response.status_code == 200:
            history = response.json()
            print("[OK] Watering history retrieved successfully!")
            print(f"   Found {len(history)} watering records")
        else:
            print("[ERROR] Failed to get watering history:", response.status_code)
            return False
    except Exception as e:
        print("[ERROR] Error getting watering history:", str(e))
        return False
    
    # Test 2: Start watering (should create history record)
    print("2. Testing watering start (creates history record)...")
    watering_start_data = {
        "pump_active": True,
        "watering_duration": 30,
        "auto_watering": True,
        "device_id": device_id,
        "timestamp": int(time.time())
    }
    
    try:
        response = requests.put(f"{base_url}/api/v1/watering", json=watering_start_data)
        if response.status_code == 200:
            print("[OK] Watering started successfully!")
            print("   Pump Active: True")
        else:
            print("[ERROR] Failed to start watering:", response.status_code)
            return False
    except Exception as e:
        print("[ERROR] Error starting watering:", str(e))
        return False
    
    # Test 3: Check history after watering start
    print("3. Testing GET watering history after start...")
    try:
        response = requests.get(f"{base_url}/api/v1/watering-history?device_id={device_id}")
        if response.status_code == 200:
            history = response.json()
            print("[OK] Watering history retrieved successfully!")
            print(f"   Found {len(history)} watering records")
            if history:
                latest = history[0]
                print(f"   Latest: Started at {latest.get('watering_started')}")
                print(f"   Status: {latest.get('watering_ended') or 'In Progress'}")
        else:
            print("[ERROR] Failed to get watering history:", response.status_code)
            return False
    except Exception as e:
        print("[ERROR] Error getting watering history:", str(e))
        return False
    
    # Test 4: Stop watering (should update history record)
    print("4. Testing watering stop (updates history record)...")
    watering_stop_data = {
        "pump_active": False,
        "device_id": device_id,
        "timestamp": int(time.time())
    }
    
    try:
        response = requests.put(f"{base_url}/api/v1/watering", json=watering_stop_data)
        if response.status_code == 200:
            print("[OK] Watering stopped successfully!")
            print("   Pump Active: False")
        else:
            print("[ERROR] Failed to stop watering:", response.status_code)
            return False
    except Exception as e:
        print("[ERROR] Error stopping watering:", str(e))
        return False
    
    # Test 5: Check final history
    print("5. Testing final watering history...")
    try:
        response = requests.get(f"{base_url}/api/v1/watering-history?device_id={device_id}")
        if response.status_code == 200:
            history = response.json()
            print("[OK] Final watering history retrieved successfully!")
            print(f"   Found {len(history)} watering records")
            if history:
                latest = history[0]
                print(f"   Latest: Started at {latest.get('watering_started')}")
                print(f"   Ended at: {latest.get('watering_ended')}")
                print(f"   Duration: {latest.get('watering_duration')} seconds")
                print(f"   Auto: {latest.get('auto_watering')}")
        else:
            print("[ERROR] Failed to get watering history:", response.status_code)
            return False
    except Exception as e:
        print("[ERROR] Error getting watering history:", str(e))
        return False
    
    print("\nAll watering history API tests passed!")
    return True

if __name__ == "__main__":
    base_url = get_base_url()
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=5)
        if response.status_code != 200:
            print(f"[ERROR] Server health check failed: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Cannot connect to server at {base_url}")
        print("Make sure the server is running:")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    # Test watering history API
    success = test_watering_history_api(base_url)
    
    if success:
        print("\nWatering History API is working correctly!")
        print("You can now:")
        print("1. Open your browser to:", base_url)
        print("2. See the watering history section")
        print("3. View watering events and their details")
    else:
        print("\nFailed to test watering history API.")
        sys.exit(1)
