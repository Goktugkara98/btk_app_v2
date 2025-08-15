#!/usr/bin/env python3
"""Debug script to check import issues with AI chat routes"""

import traceback

def test_imports():
    print("=== TESTING AI CHAT ROUTE IMPORTS ===")
    
    try:
        from app.routes.api.ai_chat_v2_routes import ai_chat_v2_bp
        print("✓ AI chat routes imported successfully")
        print(f"Blueprint name: {ai_chat_v2_bp.name}")
    except Exception as e:
        print(f"✗ Failed to import AI chat routes: {e}")
        traceback.print_exc()
    
    print("\n=== TESTING SERVICE IMPORTS ===")
    
    services = [
        ('GeminiAPIService', 'app.services.gemini_api_service'),
        ('ChatSessionService', 'app.services.chat_session_service'),
        ('ChatMessageService', 'app.services.chat_message_service'),
        ('QuizSessionService', 'app.services.quiz_session_service'),
        ('DatabaseConnection', 'app.database.db_connection')
    ]
    
    for service_name, module_path in services:
        try:
            module = __import__(module_path, fromlist=[service_name])
            service_class = getattr(module, service_name)
            print(f"✓ {service_name} imported successfully")
        except Exception as e:
            print(f"✗ Failed to import {service_name}: {e}")

if __name__ == '__main__':
    test_imports()
