#!/usr/bin/env python3
"""
Script to populate the Pi Sensor Backend with realistic dummy data.
This creates multiple sensor readings over time to test the dashboard.
"""

import sys
import json
import time
import random
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("Error: 'requests' module not found!")
    print("Please install it with: pip install requests")
    print("   Or install all requirements: pip install -r requirements.txt")
    sys.exit(1)

def get_base_url():
    """Get the base URL from command line arguments or use default"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate Pi Sensor Backend with dummy data')
    parser.add_argument('--url', default='http://192.168.68.78:8000', 
                       help='Base URL of the API server (default: http://192.168.68.78:8000)')
    parser.add_argument('--local', action='store_true', 
                       help='Use localhost instead of Pi IP')
    parser.add_argument('--count', type=int, default=50,
                       help='Number of dummy records to create (default: 50)')
    parser.add_argument('--devices', type=int, default=3,
                       help='Number of different devices to simulate (default: 3)')
    
    args = parser.parse_args()
    
    if args.local:
        return 'http://127.0.0.1:8000', args.count, args.devices
    return args.url, args.count, args.devices

def generate_realistic_sensor_data(device_id, reading_time):
    """Generate realistic sensor data based on time of day and device"""
    
    # Base values that vary by device
    device_bases = {
        'arduino_001': {'temp_base': 22.0, 'humidity_base': 60.0, 'lux_base': 500},
        'arduino_002': {'temp_base': 24.0, 'humidity_base': 55.0, 'lux_base': 800},
        'arduino_003': {'temp_base': 21.0, 'humidity_base': 70.0, 'lux_base': 300},
    }
    
    base = device_bases.get(device_id, device_bases['arduino_001'])
    
    # Time-based variations
    hour = reading_time.hour
    
    # Temperature varies throughout the day (warmer during day)
    temp_variation = 3 * (1 + 0.5 * (1 + (hour - 12) / 12))  # Peak around noon
    temperature = base['temp_base'] + temp_variation + random.uniform(-2, 2)
    
    # Humidity inversely related to temperature
    humidity_variation = -0.3 * (temperature - base['temp_base'])
    humidity = base['humidity_base'] + humidity_variation + random.uniform(-5, 5)
    humidity = max(20, min(90, humidity))  # Keep within realistic bounds
    
    # Light varies dramatically by time of day
    if 6 <= hour <= 18:  # Daytime
        lux_variation = base['lux_base'] * (0.5 + 0.5 * (hour - 6) / 12)
        lux = lux_variation + random.uniform(-100, 200)
    else:  # Nighttime
        lux = random.uniform(0, 50)  # Very low light at night
    
    lux = max(0, int(lux))  # Ensure non-negative integer
    
    # Pump activity (more likely during day, and when humidity is low)
    pump_probability = 0.3 if 6 <= hour <= 18 else 0.1
    if humidity < 40:  # Low humidity increases pump activity
        pump_probability += 0.4
    
    pump_active = random.random() < pump_probability
    
    return {
        "temperature": round(temperature, 1),
        "humidity": round(humidity, 1),
        "lux": float(lux),
        "pumpActive": pump_active,
        "timestamp": int(reading_time.timestamp()),
        "device_id": device_id,
        "firmware_version": "1.0.0",
        "sensor_type": "DHT11_LDR"
    }

def populate_dummy_data(base_url, count, num_devices):
    """Populate the API with dummy sensor data"""
    
    print("Populating Pi Sensor Backend with Dummy Data")
    print("=" * 50)
    print(f"API URL: {base_url}")
    print(f"Records to create: {count}")
    print(f"Number of devices: {num_devices}")
    print()
    
    # Generate device IDs
    device_ids = [f"arduino_{i:03d}" for i in range(1, num_devices + 1)]
    
    # Start from 7 days ago and work forward
    start_time = datetime.now() - timedelta(days=7)
    
    # Calculate time interval between readings (to spread over 7 days)
    time_interval = timedelta(days=7) / count
    
    success_count = 0
    error_count = 0
    
    for i in range(count):
        # Calculate reading time
        reading_time = start_time + (i * time_interval)
        
        # Pick a random device
        device_id = random.choice(device_ids)
        
        # Generate sensor data
        sensor_data = generate_realistic_sensor_data(device_id, reading_time)
        
        # Prepare request
        headers = {
            "Content-Type": "application/json"
            # Note: device_id is now in the payload
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/sensor-data",
                json=sensor_data,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 201:
                success_count += 1
                if success_count % 10 == 0:  # Progress indicator
                    print(f"[OK] Created {success_count} records...")
            else:
                error_count += 1
                print(f"[ERROR] Failed to create record {i+1}: {response.status_code}")
                if error_count > 5:  # Stop if too many errors
                    print("Too many errors, stopping...")
                    break
                    
        except Exception as e:
            error_count += 1
            print(f"[ERROR] Exception creating record {i+1}: {str(e)}")
            if error_count > 5:
                print("Too many errors, stopping...")
                break
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)
    
    print()
    print("=" * 50)
    print(f"Population Complete!")
    print(f"Successfully created: {success_count} records")
    print(f"Errors: {error_count}")
    
    if success_count > 0:
        print()
        print("You can now:")
        print(f"1. Open your browser to: {base_url}")
        print("2. View the sensor dashboard with real data")
        print("3. Test filtering, editing, and deleting records")
        print("4. See how the dashboard looks with multiple devices")
    
    return success_count > 0

def verify_data(base_url):
    """Verify that data was created successfully"""
    try:
        response = requests.get(f"{base_url}/api/sensor-data")
        if response.status_code == 200:
            data = response.json()
            print(f"\nVerification: Found {len(data)} total records in database")
            
            if data:
                # Group by device
                devices = {}
                for record in data:
                    device = record.get('device_id', 'Unknown')
                    devices[device] = devices.get(device, 0) + 1
                
                print("Records by device:")
                for device, count in devices.items():
                    print(f"  {device}: {count} records")
                
                # Show latest reading
                latest = data[0]
                print(f"\nLatest reading:")
                print(f"  Device: {latest.get('device_id', 'Unknown')}")
                print(f"  Temperature: {latest.get('temperature', 'N/A')}°C")
                print(f"  Humidity: {latest.get('humidity', 'N/A')}%")
                print(f"  Light: {latest.get('lux', 'N/A')} lux")
                print(f"  Pump: {'Active' if latest.get('pump_active') else 'Inactive'}")
                print(f"  Time: {latest.get('created_at', 'N/A')}")
            
            return True
        else:
            print(f"[ERROR] Failed to verify data: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Exception verifying data: {str(e)}")
        return False

if __name__ == "__main__":
    base_url, count, num_devices = get_base_url()
    
    print("This script will create realistic dummy sensor data.")
    print("The data includes:")
    print("- Multiple Arduino devices (arduino_001, arduino_002, etc.)")
    print("- Temperature variations throughout the day")
    print("- Humidity changes based on temperature")
    print("- Light levels that vary by time of day")
    print("- Pump activity based on humidity and time")
    print("- Data spread over the last 7 days")
    print()
    
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
    
    # Populate data
    success = populate_dummy_data(base_url, count, num_devices)
    
    if success:
        # Verify the data
        verify_data(base_url)
        
        print()
        print("Sample data created successfully!")
        print("The web dashboard should now show:")
        print("- Latest readings from each device")
        print("- Historical data in the table")
        print("- Realistic sensor values")
        print("- Multiple devices for testing")
    else:
        print("\nFailed to create dummy data. Check the server and try again.")
        sys.exit(1)
