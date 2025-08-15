#!/usr/bin/env python3
"""Debug script to test Gemini API request format"""

import json
from main import create_app

def test_gemini_format():
    app = create_app()
    
    with app.app_context():
        # Import services
        from app.services.chat_session_service import ChatSessionService
        from app.services.gemini_api_service import GeminiAPIService
        from app.database.db_connection import DatabaseConnection
        
        # Initialize services
        db_connection = DatabaseConnection()
        chat_service = ChatSessionService(db_connection)
        gemini_service = GeminiAPIService()
        
        print("=== TESTING GEMINI API FORMAT ===")
        
        # Test 1: Create a test chat session
        test_session_id = "test_session_123"
        test_question_id = 1
        
        try:
            # Create session
            session_id = chat_service.create_session_for_question(
                quiz_session_id="test_quiz_123",
                question_id=test_question_id,
                user_context={
                    'subject': 'Matematik',
                    'topic': 'Cebir',
                    'difficulty': 'orta'
                },
                user_id=1
            )
            print(f"✓ Created test session: {session_id}")
            
            # Test 2: Build Gemini contents
            test_message = "Bu soruyu açıklar mısın?"
            test_question_context = {
                'question_text': '2x + 3 = 7 denkleminde x kaçtır?',
                'options': [
                    {'option_text': 'x = 1'},
                    {'option_text': 'x = 2'},
                    {'option_text': 'x = 3'},
                    {'option_text': 'x = 4'}
                ]
            }
            
            contents_result = chat_service.build_gemini_contents_scenario(
                chat_session_id=session_id,
                user_message=test_message,
                scenario_type='direct',
                is_first_message=True,
                question_context=test_question_context,
                files_only=True
            )
            
            print(f"✓ Built Gemini contents")
            print(f"Contents length: {len(contents_result.get('contents', []))}")
            
            # Test 3: Check contents format
            contents = contents_result.get('contents', [])
            if contents:
                print("\n=== CONTENTS STRUCTURE ===")
                for i, content in enumerate(contents):
                    print(f"Content {i+1}:")
                    print(f"  Role: {content.get('role')}")
                    print(f"  Parts count: {len(content.get('parts', []))}")
                    if content.get('parts'):
                        text = content['parts'][0].get('text', '')
                        print(f"  Text preview: {text[:100]}...")
            
            # Test 4: Validate Gemini API format
            print("\n=== GEMINI API FORMAT VALIDATION ===")
            valid_format = True
            
            for i, content in enumerate(contents):
                # Check required fields
                if 'role' not in content:
                    print(f"✗ Content {i+1}: Missing 'role' field")
                    valid_format = False
                elif content['role'] not in ['user', 'model']:
                    print(f"✗ Content {i+1}: Invalid role '{content['role']}' (must be 'user' or 'model')")
                    valid_format = False
                
                if 'parts' not in content:
                    print(f"✗ Content {i+1}: Missing 'parts' field")
                    valid_format = False
                elif not isinstance(content['parts'], list):
                    print(f"✗ Content {i+1}: 'parts' must be a list")
                    valid_format = False
                elif len(content['parts']) == 0:
                    print(f"✗ Content {i+1}: 'parts' cannot be empty")
                    valid_format = False
                else:
                    for j, part in enumerate(content['parts']):
                        if 'text' not in part:
                            print(f"✗ Content {i+1}, Part {j+1}: Missing 'text' field")
                            valid_format = False
            
            if valid_format:
                print("✓ All contents have valid Gemini API format")
            else:
                print("✗ Format validation failed")
            
            # Test 5: Try actual API call (if configured)
            if gemini_service.is_available():
                print("\n=== TESTING ACTUAL API CALL ===")
                try:
                    response = gemini_service.generate_content(contents=contents)
                    if response:
                        print(f"✓ API call successful")
                        print(f"Response preview: {response[:200]}...")
                    else:
                        print("✗ API call returned None")
                except Exception as e:
                    print(f"✗ API call failed: {e}")
            else:
                print("\n=== GEMINI API NOT CONFIGURED ===")
                print("Set GEMINI_API_KEY environment variable to test actual API calls")
            
        except Exception as e:
            print(f"✗ Test failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_gemini_format()
