#!/usr/bin/env python
"""
Test script to verify YouTube integration
Run this after starting the Django server
"""

import requests
import json

def test_youtube_integration():
    """Test the YouTube integration endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing YouTube Integration...")
    print("=" * 50)
    
    try:
        # Test 1: Explore endpoint (should show all users with YouTube data)
        print("\n1️⃣ Testing explore endpoint...")
        response = requests.get(f"{base_url}/api/explore/explore/")
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Success! Found {len(users)} users")
            
            # Show users with YouTube data
            users_with_youtube = [u for u in users if u.get('youtube_data')]
            print(f"📺 Users with YouTube data: {len(users_with_youtube)}")
            
            for i, user in enumerate(users_with_youtube[:3]):  # Show first 3
                yt_data = user['youtube_data']
                print(f"👤 {user['first_name']} {user['last_name']}")
                print(f"   📊 Subscribers: {yt_data.get('subscriber_count', 'N/A')}")
                print(f"   🎥 Videos: {yt_data.get('video_count', 'N/A')}")
                print(f"   👀 Views: {yt_data.get('view_count', 'N/A')}")
                print(f"   🔴 Live: {yt_data.get('is_live', False)}")
                print()
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
        # Test 2: Users with YouTube endpoint
        print("\n2️⃣ Testing users-with-youtube endpoint...")
        response = requests.get(f"{base_url}/api/auth/users-with-youtube/")
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Success! Found {len(users)} users with YouTube URLs")
        else:
            print(f"❌ Error: {response.status_code}")
            
        # Test 3: YouTube proxy endpoint
        print("\n3️⃣ Testing YouTube proxy endpoint...")
        test_data = {
            'url': 'https://www.googleapis.com/youtube/v3/channels?part=snippet&id=UCBR8-60-B28hp2BmDPdntcQ&key=AIzaSyCyrLA3pmrWdRHQR7CymuODE5a6ISSRmGY'
        }
        
        response = requests.post(
            f"{base_url}/api/auth/youtube-proxy/",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ YouTube proxy working! Got {len(data.get('items', []))} items")
        else:
            print(f"❌ YouTube proxy error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure Django server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_youtube_integration()
