#!/usr/bin/env python3
"""
Quick test script to reproduce the quick-action 500 error
"""
import requests
import json

def test_quick_action():
    """Test the quick-action endpoint with sample data"""
    url = "http://127.0.0.1:5000/api/ai/chat/quick-action"
    
    # Sample data similar to what frontend sends
    test_data = {
        "action": "how_to_solve",
        "chat_session_id": "chat_test_session",
        "question_id": 1,
        "question_context": {
            "question_text": "Test question",
            "options": [
                {"option_id": 1, "option_text": "Option A", "is_correct": False},
                {"option_id": 2, "option_text": "Option B", "is_correct": True}
            ]
        }
    }
    
    try:
        print(f"Testing quick-action endpoint...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 500:
            try:
                error_data = response.json()
                if 'traceback' in error_data:
                    print(f"\nFull Traceback:")
                    print(error_data['traceback'])
            except:
                pass
                
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_quick_action()
