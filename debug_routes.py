#!/usr/bin/env python3
"""Debug script to check registered Flask routes"""

from main import create_app

def list_routes():
    app = create_app()
    with app.app_context():
        print("=== REGISTERED ROUTES ===")
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
            print(f"{rule.rule:<50} {methods:<20} {rule.endpoint}")
        
        print("\n=== AI ROUTES ONLY ===")
        ai_routes = [rule for rule in app.url_map.iter_rules() if '/ai/' in rule.rule]
        for rule in ai_routes:
            methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
            print(f"{rule.rule:<50} {methods:<20} {rule.endpoint}")

if __name__ == '__main__':
    list_routes()
