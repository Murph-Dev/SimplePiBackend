#!/usr/bin/env python3
"""
Test script to verify the sensor API endpoints work correctly.
This simulates the Arduino POST request.
"""

import sys
import json
import time
import argparse

try:
    import requests
except ImportError:
    print("Error: 'requests' module not found!")
    print("Please install it with: pip install requests")
    print("   Or install all requirements: pip install -r requirements.txt")
    sys.exit(1)

def get_base_url():
    """Get the base URL from command line arguments or use default"""
    parser = argparse.ArgumentParser(description='Test the Pi Sensor Backend API')
    parser.add_argument('--url', default='http://192.168.68.78:8000', 
                       help='Base URL of the API server (default: http://192.168.68.78:8000)')
    parser.add_argument('--local', action='store_true', 
                       help='Use localhost instead of Pi IP')
    
    args = parser.parse_args()
    
    if args.local:
        return 'http://127.0.0.1:8000'
    return args.url

def test_sensor_api(base_url):
    """Test the sensor data API endpoints"""
    
    print("Testing Pi Sensor Backend API")
    print("=" * 40)
    print(f"Testing URL: {base_url}")
    print()
    
    api_endpoint = f"{base_url}/api/v1/sensor-data"
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        if response.status_code == 200:
            print("[OK] Health check passed:", response.json())
        else:
            print("[ERROR] Health check failed:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server. Make sure the server is running on", base_url)
        return False
    
    # Test 2: Simulate Arduino POST request
    print("2. Testing Arduino sensor data POST...")
    
    # Simulate the exact JSON structure from Arduino
    sensor_data = {
        "temperature": 25.5,
        "humidity": 60.2,
        "lux": 150.0,
        "pumpActive": False,
        "timestamp": int(time.time()),
        "device_id": "autogrow_esp32",
        "firmware_version": "1.0.0",
        "sensor_type": "DHT11_LDR"
    }
    
    headers = {
        "Content-Type": "application/json"
        # Note: device_id is now in the payload, not header
    }
    
    try:
        response = requests.post(api_endpoint, json=sensor_data, headers=headers)
        if response.status_code == 201:
            created_data = response.json()
            print("[OK] Sensor data created successfully!")
            print("   ID:", created_data["id"])
            print("   Temperature:", created_data["temperature"])
            print("   Device ID:", created_data["device_id"])
            sensor_id = created_data["id"]
        else:
            print("[ERROR] Failed to create sensor data:", response.status_code)
            print("   Response:", response.text)
            return False
    except Exception as e:
        print("[ERROR] Error creating sensor data:", str(e))
        return False
    
    # Test 3: Get all sensor data
    print("3. Testing GET all sensor data...")
    try:
        response = requests.get(f"{base_url}/api/v1/sensor-data")
        if response.status_code == 200:
            all_data = response.json()
            print(f"[OK] Retrieved {len(all_data)} sensor readings")
            if all_data:
                latest = all_data[0]
                print(f"   Latest: {latest['temperature']}°C, {latest['humidity']}%, {latest['lux']} lux")
        else:
            print("[ERROR] Failed to get sensor data:", response.status_code)
            return False
    except Exception as e:
        print("[ERROR] Error getting sensor data:", str(e))
        return False
    
    # Test 4: Update sensor data
    print("4. Testing UPDATE sensor data...")
    update_data = {
        "temperature": 24.1,
        "pump_active": False,
        "firmware_version": "1.0.1"
    }
    
    try:
        response = requests.put(f"{base_url}/api/v1/sensor-data/{sensor_id}", json=update_data)
        if response.status_code == 200:
            updated_data = response.json()
            print("[OK] Sensor data updated successfully!")
            print("   New temperature:", updated_data["temperature"])
            print("   Pump status:", updated_data["pump_active"])
        else:
            print("[ERROR] Failed to update sensor data:", response.status_code)
            return False
    except Exception as e:
        print("[ERROR] Error updating sensor data:", str(e))
        return False
    
    # Test 5: Delete sensor data
    print("5. Testing DELETE sensor data...")
    try:
        response = requests.delete(f"{base_url}/api/v1/sensor-data/{sensor_id}")
        if response.status_code == 204:
            print("[OK] Sensor data deleted successfully!")
        else:
            print("[ERROR] Failed to delete sensor data:", response.status_code)
            return False
    except Exception as e:
        print("[ERROR] Error deleting sensor data:", str(e))
        return False
    
    print("\nAll tests passed! The API is working correctly.")
    return True

if __name__ == "__main__":
    base_url = get_base_url()
    success = test_sensor_api(base_url)
    if not success:
        print("\nMake sure to:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Start the server: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print("   3. Update the IP address in this script or use --local flag")
        print("   4. Run this test script")
        print("\nUsage examples:")
        print("   python test_sensor_api.py --local                    # Test localhost")
        print("   python test_sensor_api.py --url http://192.168.1.100:8000  # Test specific IP")
        exit(1)
