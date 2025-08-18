#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return None

def test_admin_panel():
    base_url = "http://localhost:5000"
    s = requests.Session()
    s.headers.update({
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json'
    })
    
    print("Admin Panel Test Ediliyor...")
    print("=" * 50)
    
    # Test 1: Dashboard sayfası
    try:
        print("1. Dashboard sayfası test ediliyor...")
        response = s.get(f"{base_url}/admin/")
        if response.status_code == 200:
            print("✓ Dashboard sayfası çalışıyor")
        elif response.status_code in (302, 401):
            print(f"• Dashboard yönlendirme/oturum gerektiriyor (status: {response.status_code})")
        else:
            print(f"✗ Dashboard hatası: {response.status_code}")
    except Exception as e:
        print(f"✗ Dashboard bağlantı hatası: {e}")
    
    # Test 2: API endpoint'leri
    try:
        print("\n2. API endpoint'leri test ediliyor...")
        
        # Curriculum overview
        response = s.get(f"{base_url}/api/admin/curriculum/overview")
        if response.status_code == 200:
            data = safe_json(response)
            print("✓ Curriculum overview API çalışıyor")
            print(f"  - Veri: {data}")
        elif response.status_code in (401, 403):
            data = safe_json(response)
            print(f"• Curriculum overview yetkisiz beklenen durum (status: {response.status_code})")
            print(f"  - JSON: {data}")
        else:
            print(f"✗ Curriculum overview API hatası: {response.status_code}")

        # Overview alias
        response = s.get(f"{base_url}/api/admin/overview")
        if response.status_code == 200:
            print("✓ Overview alias API çalışıyor")
        elif response.status_code in (401, 403):
            data = safe_json(response)
            print(f"• Overview alias yetkisiz beklenen durum (status: {response.status_code})")
            print(f"  - JSON: {data}")
        else:
            print(f"✗ Overview alias API hatası: {response.status_code}")
            
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
            response = s.get(f"{base_url}{page}")
            if response.status_code == 200:
                print(f"✓ {page} sayfası çalışıyor")
            elif response.status_code in (302, 401):
                print(f"• {page} yönlendirme/oturum gerektiriyor (status: {response.status_code})")
            else:
                print(f"✗ {page} hatası: {response.status_code}")
                
    except Exception as e:
        print(f"✗ Sayfa test hatası: {e}")
    
    print("\n" + "=" * 50)
    print("Test tamamlandı!")

if __name__ == "__main__":
    # Uygulamanın başlaması için biraz bekle
    print("Uygulama başlatılıyor...")
    time.sleep(5)

    test_admin_panel()
