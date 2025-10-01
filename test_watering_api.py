#!/usr/bin/env python3
"""
Test script to verify the watering API endpoints work correctly.
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
    
    parser = argparse.ArgumentParser(description='Test the watering API endpoints')
    parser.add_argument('--url', default='http://192.168.68.78:8000', 
                       help='Base URL of the API server (default: http://192.168.68.78:8000)')
    parser.add_argument('--local', action='store_true', 
                       help='Use localhost instead of Pi IP')
    
    args = parser.parse_args()
    
    if args.local:
        return 'http://127.0.0.1:8000'
    return args.url

def test_watering_api(base_url):
    """Test the watering API endpoints"""
    
    print("Testing Watering API")
    print("=" * 30)
    print(f"Testing URL: {base_url}")
    print()
    
    # Test 1: Get watering data (should create default if not exists)
    print("1. Testing GET watering data...")
    try:
        response = requests.get(f"{base_url}/api/watering/autogrow_esp32")
        if response.status_code == 200:
            watering_data = response.json()
            print("[OK] Watering data retrieved successfully!")
            print("   Pump Active:", watering_data.get("pump_active", "N/A"))
            print("   Auto Watering:", watering_data.get("auto_watering", "N/A"))
            print("   Watering Duration:", watering_data.get("watering_duration", "N/A"), "seconds")
            print("   Last Watering:", watering_data.get("last_watering", "Never"))
        else:
            print("[ERROR] Failed to get watering data:", response.status_code)
            return False
    except Exception as e:
        print("[ERROR] Error getting watering data:", str(e))
        return False
    
    # Test 2: Update watering data
    print("2. Testing UPDATE watering data...")
    update_data = {
        "pump_active": True,
        "last_watering": "2024-01-15T10:30:00Z",
        "watering_duration": 45,
        "auto_watering": False,
        "device_id": "autogrow_esp32",
        "timestamp": 1234567890
    }
    
    try:
        response = requests.put(f"{base_url}/api/watering", json=update_data)
        if response.status_code == 200:
            updated_data = response.json()
            print("[OK] Watering data updated successfully!")
            print("   Pump Active:", updated_data.get("pump_active"))
            print("   Watering Duration:", updated_data.get("watering_duration"), "seconds")
            print("   Auto Watering:", updated_data.get("auto_watering"))
            print("   Updated At:", updated_data.get("updated_at"))
        else:
            print("[ERROR] Failed to update watering data:", response.status_code)
            return False
    except Exception as e:
        print("[ERROR] Error updating watering data:", str(e))
        return False
    
    # Test 3: Update pump status to false (simulate watering finished)
    print("3. Testing UPDATE pump status (watering finished)...")
    finish_data = {
        "pump_active": False
    }
    
    try:
        response = requests.put(f"{base_url}/api/watering", json=finish_data)
        if response.status_code == 200:
            finished_data = response.json()
            print("[OK] Pump status updated successfully!")
            print("   Pump Active:", finished_data.get("pump_active"))
            print("   Updated At:", finished_data.get("updated_at"))
        else:
            print("[ERROR] Failed to update pump status:", response.status_code)
            return False
    except Exception as e:
        print("[ERROR] Error updating pump status:", str(e))
        return False
    
    print("\nAll watering API tests passed!")
    return True

if __name__ == "__main__":
    base_url = get_base_url()
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code != 200:
            print(f"[ERROR] Server health check failed: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Cannot connect to server at {base_url}")
        print("Make sure the server is running:")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    # Test watering API
    success = test_watering_api(base_url)
    
    if success:
        print("\nWatering API is working correctly!")
        print("You can now:")
        print("1. Open your browser to:", base_url)
        print("2. See the watering status in the latest readings")
        print("3. Test updating watering status from your Arduino")
    else:
        print("\nFailed to test watering API.")
        sys.exit(1)
