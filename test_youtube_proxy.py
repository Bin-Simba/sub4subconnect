#!/usr/bin/env python3
"""
Test script for YouTube API proxy
Run this script to test if the YouTube API proxy is working correctly
"""

import requests
import json
import sys

def test_youtube_proxy():
    """Test the YouTube API proxy endpoint"""
    
    # Test URL - YouTube's official channel
    test_url = "https://www.googleapis.com/youtube/v3/channels?part=snippet&id=UCBR8-60-B28hp2BmDPdntcQ&key=AIzaSyCyrLA3pmrWdRHQR7CymuODE5a6ISSRmGY"
    
    proxy_url = "http://127.0.0.1:8000/api/auth/youtube-proxy/"
    
    print("🧪 Testing YouTube API Proxy...")
    print(f"📡 Proxy URL: {proxy_url}")
    print(f"🔗 Test URL: {test_url}")
    
    try:
        # Make request to proxy
        response = requests.post(
            proxy_url,
            json={"url": test_url},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Proxy test successful!")
            print(f"📺 Channel Title: {data.get('items', [{}])[0].get('snippet', {}).get('title', 'N/A')}")
            print(f"📊 Items returned: {len(data.get('items', []))}")
        else:
            print(f"❌ Proxy test failed: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on port 8000")
        print("💡 Run: python manage.py runserver")
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")

def test_backend_health():
    """Test if the backend is running"""
    
    health_url = "http://127.0.0.1:8000/api/auth/users-with-youtube/"
    
    print("\n🏥 Testing Backend Health...")
    print(f"📡 Health URL: {health_url}")
    
    try:
        response = requests.get(health_url, timeout=10)
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is healthy!")
            print(f"👥 Users with YouTube URLs: {len(data)}")
            
            if data:
                print("📋 Sample users:")
                for i, user in enumerate(data[:3]):
                    print(f"  {i+1}. {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}")
                    print(f"     YouTube: {user.get('youtube_url', 'N/A')}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Django server is not running")
        print("💡 Start the server with: python manage.py runserver")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 YouTube API Integration Test")
    print("=" * 50)
    
    # Test backend health first
    test_backend_health()
    
    # Test YouTube proxy
    test_youtube_proxy()
    
    print("\n" + "=" * 50)
    print("✨ Test completed!")
    print("\n💡 If you see any errors:")
    print("1. Make sure Django server is running: python manage.py runserver")
    print("2. Check if requests library is installed: pip install requests")
    print("3. Verify your YouTube API key is valid")
    print("4. Check Django logs for any errors")


