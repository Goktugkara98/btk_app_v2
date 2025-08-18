#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_admin_panel():
    base_url = "http://localhost:5000"
    
    print("Admin Panel Test Ediliyor...")
    print("=" * 50)
    
    # Test 1: Dashboard sayfası
    try:
        print("1. Dashboard sayfası test ediliyor...")
        response = requests.get(f"{base_url}/admin/dashboard")
        if response.status_code == 200:
            print("✓ Dashboard sayfası çalışıyor")
        else:
            print(f"✗ Dashboard hatası: {response.status_code}")
    except Exception as e:
        print(f"✗ Dashboard bağlantı hatası: {e}")
    
    # Test 2: API endpoint'leri
    try:
        print("\n2. API endpoint'leri test ediliyor...")
        
        # Curriculum overview
        response = requests.get(f"{base_url}/admin/api/curriculum/overview")
        if response.status_code == 200:
            data = response.json()
            print("✓ Curriculum overview API çalışıyor")
            print(f"  - Veri: {data}")
        else:
            print(f"✗ Curriculum overview API hatası: {response.status_code}")
        
        # Recent activity
        response = requests.get(f"{base_url}/admin/api/curriculum/recent-activity")
        if response.status_code == 200:
            data = response.json()
            print("✓ Recent activity API çalışıyor")
            print(f"  - Veri: {data}")
        else:
            print(f"✗ Recent activity API hatası: {response.status_code}")
            
    except Exception as e:
        print(f"✗ API test hatası: {e}")
    
    # Test 3: Sayfa yönlendirmeleri
    try:
        print("\n3. Sayfa yönlendirmeleri test ediliyor...")
        
        pages = [
            "/admin/grades",
            "/admin/subjects", 
            "/admin/units",
            "/admin/topics",
            "/admin/import-export"
        ]
        
        for page in pages:
            response = requests.get(f"{base_url}{page}")
            if response.status_code == 200:
                print(f"✓ {page} sayfası çalışıyor")
            else:
                print(f"✗ {page} hatası: {response.status_code}")
                
    except Exception as e:
        print(f"✗ Sayfa test hatası: {e}")
    
    print("\n" + "=" * 50)
    print("Test tamamlandı!")

if __name__ == "__main__":
    # Uygulamanın başlaması için biraz bekle
    print("Uygulama başlatılıyor...")
    time.sleep(3)
    
    test_admin_panel()
