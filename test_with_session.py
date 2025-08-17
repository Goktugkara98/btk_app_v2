#!/usr/bin/env python3
"""
Test script to create a session and then test quick-action
"""
import requests
import json

def test_with_valid_session():
    """Create a valid session first, then test quick-action"""
    base_url = "http://127.0.0.1:5000"
    
    # Step 1: Create a chat session
    session_data = {
        "quiz_session_id": "test_quiz_session",
        "question_id": 1
    }
    
    try:
        print("Step 1: Creating chat session...")
        session_response = requests.post(f"{base_url}/api/ai/session/start", json=session_data)
        print(f"Session creation status: {session_response.status_code}")
        print(f"Session response: {session_response.text}")
        
        if session_response.status_code != 200:
            print("Failed to create session, testing quick-action anyway...")
            chat_session_id = "chat_test_session"
        else:
            session_info = session_response.json()
            chat_session_id = session_info['data']['chat_session_id']
            print(f"Created session: {chat_session_id}")
        
        # Step 2: Test quick-action with the session
        print(f"\nStep 2: Testing quick-action...")
        quick_action_data = {
            "action": "how_to_solve",
            "chat_session_id": chat_session_id,
            "question_id": 1,
            "question_context": {
                "question_text": "Test question",
                "options": [
                    {"option_id": 1, "option_text": "Option A", "is_correct": False},
                    {"option_id": 2, "option_text": "Option B", "is_correct": True}
                ]
            }
        }
        
        quick_response = requests.post(f"{base_url}/api/ai/chat/quick-action", json=quick_action_data)
        print(f"Quick-action status: {quick_response.status_code}")
        print(f"Quick-action response: {quick_response.text}")
        
        if quick_response.status_code == 500:
            try:
                error_data = quick_response.json()
                if 'traceback' in error_data:
                    print(f"\nFull Traceback:")
                    print(error_data['traceback'])
            except:
                pass
                
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_with_valid_session()
