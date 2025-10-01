#!/usr/bin/env python3
"""
Test script to verify the sensor API endpoints work correctly.
This simulates the Arduino POST request.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/v1/sensor-data"

def test_sensor_api():
    """Test the sensor data API endpoints"""
    
    print("🧪 Testing Pi Sensor Backend API")
    print("=" * 40)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Health check passed:", response.json())
        else:
            print("❌ Health check failed:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on", BASE_URL)
        return False
    
    # Test 2: Simulate Arduino POST request
    print("\n2. Testing Arduino sensor data POST...")
    
    # Simulate the exact JSON structure from Arduino
    sensor_data = {
        "temperature": 23.5,
        "humidity": 65.2,
        "lux": 850,
        "pumpActive": True,  # Note: Arduino sends "pumpActive" but our model expects "pump_active"
        "lastReading": int(time.time())
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Device-ID": "arduino_001"
    }
    
    try:
        response = requests.post(API_ENDPOINT, json=sensor_data, headers=headers)
        if response.status_code == 201:
            created_data = response.json()
            print("✅ Sensor data created successfully!")
            print("   ID:", created_data["id"])
            print("   Temperature:", created_data["temperature"])
            print("   Device ID:", created_data["device_id"])
            sensor_id = created_data["id"]
        else:
            print("❌ Failed to create sensor data:", response.status_code)
            print("   Response:", response.text)
            return False
    except Exception as e:
        print("❌ Error creating sensor data:", str(e))
        return False
    
    # Test 3: Get all sensor data
    print("\n3. Testing GET all sensor data...")
    try:
        response = requests.get(f"{BASE_URL}/api/sensor-data")
        if response.status_code == 200:
            all_data = response.json()
            print(f"✅ Retrieved {len(all_data)} sensor readings")
            if all_data:
                latest = all_data[0]
                print(f"   Latest: {latest['temperature']}°C, {latest['humidity']}%, {latest['lux']} lux")
        else:
            print("❌ Failed to get sensor data:", response.status_code)
            return False
    except Exception as e:
        print("❌ Error getting sensor data:", str(e))
        return False
    
    # Test 4: Update sensor data
    print("\n4. Testing UPDATE sensor data...")
    update_data = {
        "temperature": 24.1,
        "pump_active": False
    }
    
    try:
        response = requests.put(f"{BASE_URL}/api/sensor-data/{sensor_id}", json=update_data)
        if response.status_code == 200:
            updated_data = response.json()
            print("✅ Sensor data updated successfully!")
            print("   New temperature:", updated_data["temperature"])
            print("   Pump status:", updated_data["pump_active"])
        else:
            print("❌ Failed to update sensor data:", response.status_code)
            return False
    except Exception as e:
        print("❌ Error updating sensor data:", str(e))
        return False
    
    # Test 5: Delete sensor data
    print("\n5. Testing DELETE sensor data...")
    try:
        response = requests.delete(f"{BASE_URL}/api/sensor-data/{sensor_id}")
        if response.status_code == 204:
            print("✅ Sensor data deleted successfully!")
        else:
            print("❌ Failed to delete sensor data:", response.status_code)
            return False
    except Exception as e:
        print("❌ Error deleting sensor data:", str(e))
        return False
    
    print("\n🎉 All tests passed! The API is working correctly.")
    return True

if __name__ == "__main__":
    success = test_sensor_api()
    if not success:
        print("\n💡 Make sure to:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Start the server: uvicorn app.main:app --reload")
        print("   3. Run this test script")
        exit(1)
