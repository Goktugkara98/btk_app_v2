#!/usr/bin/env python3
"""Test script to verify AI endpoints are working"""

import requests
import json

def test_ai_endpoints():
    base_url = "http://localhost:5000"
    
    print("=== TESTING AI ENDPOINTS ===")
    
    # Test 1: AI System Status
    try:
        response = requests.get(f"{base_url}/api/ai/system/status")
        print(f"✓ /api/ai/system/status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Status: {data.get('status')}")
            print(f"  Services: {data.get('data', {}).get('services', {})}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ /api/ai/system/status failed: {e}")
    
    # Test 2: AI System Health
    try:
        response = requests.get(f"{base_url}/api/ai/system/health")
        print(f"✓ /api/ai/system/health: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Healthy: {data.get('data', {}).get('healthy')}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ /api/ai/system/health failed: {e}")
    
    # Test 3: Favicon
    try:
        response = requests.get(f"{base_url}/favicon.ico")
        print(f"✓ /favicon.ico: {response.status_code}")
    except Exception as e:
        print(f"✗ /favicon.ico failed: {e}")

if __name__ == '__main__':
    test_ai_endpoints()
