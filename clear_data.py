#!/usr/bin/env python3
"""
Script to clear all sensor data from the database.
Useful for testing or starting fresh.
"""

import sys
import requests

try:
    import requests
except ImportError:
    print("Error: 'requests' module not found!")
    print("Please install it with: pip install requests")
    sys.exit(1)

def get_base_url():
    """Get the base URL from command line arguments or use default"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clear all sensor data from the database')
    parser.add_argument('--url', default='http://192.168.68.78:8000', 
                       help='Base URL of the API server (default: http://192.168.68.78:8000)')
    parser.add_argument('--local', action='store_true', 
                       help='Use localhost instead of Pi IP')
    parser.add_argument('--confirm', action='store_true',
                       help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    if args.local:
        return 'http://127.0.0.1:8000', args.confirm
    return args.url, args.confirm

def clear_all_data(base_url, skip_confirm=False):
    """Clear all sensor data from the database"""
    
    print("Clear All Sensor Data")
    print("=" * 30)
    print(f"API URL: {base_url}")
    print()
    
    # Get all sensor data first
    try:
        response = requests.get(f"{base_url}/api/sensor-data")
        if response.status_code == 200:
            data = response.json()
            total_records = len(data)
            
            if total_records == 0:
                print("Database is already empty. Nothing to clear.")
                return True
                
            print(f"Found {total_records} records in the database.")
            
            if not skip_confirm:
                print()
                print("WARNING: This will permanently delete ALL sensor data!")
                confirm = input("Are you sure you want to continue? (yes/no): ")
                if confirm.lower() not in ['yes', 'y']:
                    print("Operation cancelled.")
                    return False
            
            print()
            print("Deleting records...")
            
            deleted_count = 0
            error_count = 0
            
            for record in data:
                try:
                    response = requests.delete(f"{base_url}/api/sensor-data/{record['id']}")
                    if response.status_code == 204:
                        deleted_count += 1
                    else:
                        error_count += 1
                        print(f"[ERROR] Failed to delete record {record['id']}: {response.status_code}")
                        
                except Exception as e:
                    error_count += 1
                    print(f"[ERROR] Exception deleting record {record['id']}: {str(e)}")
            
            print()
            print("=" * 30)
            print(f"Deletion Complete!")
            print(f"Successfully deleted: {deleted_count} records")
            print(f"Errors: {error_count}")
            
            # Verify deletion
            try:
                response = requests.get(f"{base_url}/api/sensor-data")
                if response.status_code == 200:
                    remaining = response.json()
                    print(f"Remaining records: {len(remaining)}")
                    
                    if len(remaining) == 0:
                        print("✓ Database successfully cleared!")
                        return True
                    else:
                        print("⚠ Some records may not have been deleted.")
                        return False
            except Exception as e:
                print(f"[ERROR] Could not verify deletion: {str(e)}")
                return False
                
        else:
            print(f"[ERROR] Failed to get sensor data: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception getting sensor data: {str(e)}")
        return False

if __name__ == "__main__":
    base_url, skip_confirm = get_base_url()
    
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
    
    # Clear data
    success = clear_all_data(base_url, skip_confirm)
    
    if success:
        print("\nDatabase cleared successfully!")
        print("You can now:")
        print("- Add new data with populate_dummy_data.py")
        print("- Start fresh with real Arduino data")
        print("- Test the empty state of the dashboard")
    else:
        print("\nFailed to clear database completely.")
        sys.exit(1)
