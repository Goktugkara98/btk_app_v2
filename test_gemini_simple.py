#!/usr/bin/env python3
"""Simple test for Gemini API format"""

import json
import sys
import os

# Add current directory to path
sys.path.append('.')

def test_gemini_format():
    try:
        from app.services.chat_session_service import ChatSessionService
        from app.database.db_connection import DatabaseConnection
        
        # Initialize services
        db_connection = DatabaseConnection()
        chat_service = ChatSessionService(db_connection)
        
        print("=== TESTING GEMINI FORMAT ===")
        
        # Test build_gemini_contents_scenario with minimal data
        test_result = chat_service.build_gemini_contents_scenario(
            chat_session_id="test_123",
            user_message="Merhaba",
            scenario_type='direct',
            is_first_message=True,
            question_context=None,
            files_only=False  # Use fallback if no file templates
        )
        
        contents = test_result.get('contents', [])
        final_text = test_result.get('final_user_text', '')
        
        print(f"Contents count: {len(contents)}")
        print(f"Final text length: {len(final_text)}")
        
        # Validate format
        valid = True
        for i, content in enumerate(contents):
            role = content.get('role')
            parts = content.get('parts', [])
            
            if role not in ['user', 'model']:
                print(f"✗ Invalid role: {role}")
                valid = False
            
            if not parts or not isinstance(parts, list):
                print(f"✗ Invalid parts: {parts}")
                valid = False
            
            for part in parts:
                if 'text' not in part:
                    print(f"✗ Missing text in part: {part}")
                    valid = False
        
        if valid:
            print("✓ Format is valid for Gemini API")
        else:
            print("✗ Format validation failed")
        
        # Show structure
        print("\n=== CONTENTS STRUCTURE ===")
        for i, content in enumerate(contents):
            role = content.get('role')
            text = content.get('parts', [{}])[0].get('text', '')
            print(f"{i+1}. Role: {role}, Text: {text[:50]}...")
            
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_gemini_format()
