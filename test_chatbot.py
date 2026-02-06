#!/usr/bin/env python
"""Test script for chatbot API endpoint"""

import requests
import json
import sys

url = "http://localhost:5000/api/chat-with-ai"
payload = {
    "message": "What are the risks of having accounts on multiple social media platforms?",
    "scan_context": {}
}

print("=" * 60)
print("TESTING CHATBOT ENDPOINT")
print("=" * 60)
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("-" * 60)

try:
    print("🚀 Sending request to chatbot endpoint...")
    response = requests.post(url, json=payload, timeout=15)
    
    print(f"✅ Response Status Code: {response.status_code}")
    
    try:
        response_json = response.json()
        print(f"\n📋 Response JSON:")
        print(json.dumps(response_json, indent=2))
        
        if response.status_code == 200:
            if response_json.get("status") == "success":
                print("\n✅ CHATBOT IS WORKING PERFECTLY!")
                print(f"AI Response: {response_json.get('response')}")
            else:
                print("\n❌ Response indicates error:")
                print(response_json.get("error", "Unknown error"))
        else:
            print(f"\n❌ Error response: {response_json}")
            
    except json.JSONDecodeError:
        print(f"❌ Failed to parse JSON response")
        print(f"Raw Response: {response.text}")
        sys.exit(1)
        
except requests.exceptions.Timeout:
    print("❌ Request timed out - Groq API might be slow or unreachable")
    sys.exit(1)
except requests.exceptions.ConnectError:
    print("❌ Connection error - Flask server might not be running")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)
