from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, AppUser
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer, UserProfileUpdateSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests
from django.conf import settings
import re

def extract_youtube_channel_id(url):
    """Extract YouTube channel ID from various URL formats"""
    if not url:
        return None
    
    # Handle different YouTube URL formats
    patterns = [
        # Channel ID format: /channel/UC...
        r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
        # Custom URL format: /c/ or /user/
        r'youtube\.com/(?:c/|user/)([a-zA-Z0-9_-]+)',
        # Handle @username URLs
        r'youtube\.com/@([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def get_youtube_channel_data(channel_id, api_key):
    """Fetch YouTube channel data using YouTube API v3"""
    try:
        # First, get channel info
        channel_url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={api_key}"
        
        response = requests.get(channel_url, timeout=10)
        if response.status_code != 200:
            print(f"❌ YouTube API error: {response.status_code}")
            return None
        
        channel_data = response.json()
        
        if not channel_data.get('items'):
            print(f"❌ No channel data found for ID: {channel_id}")
            return None
        
        channel = channel_data['items'][0]
        
        # Check if channel is currently live
        is_live = False
        live_stream_id = ''
        live_viewer_count = ''
        
        try:
            live_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&eventType=live&key={api_key}"
            live_response = requests.get(live_url, timeout=10)
            
            if live_response.status_code == 200:
                live_data = live_response.json()
                if live_data.get('items'):
                    is_live = True
                    live_stream_id = live_data['items'][0]['id']['videoId']
                    
                    # Get live stream details for viewer count
                    stream_url = f"https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails,statistics&id={live_stream_id}&key={api_key}"
                    stream_response = requests.get(stream_url, timeout=10)
                    
                    if stream_response.status_code == 200:
                        stream_data = stream_response.json()
                        if stream_data.get('items'):
                            live_viewer_count = stream_data['items'][0]['statistics'].get('viewCount', '0')
        except Exception as e:
            print(f"⚠️ Error checking live status: {e}")
        
        return {
            'channel_id': channel_id,
            'title': channel['snippet']['title'],
            'description': channel['snippet']['description'],
            'subscriber_count': channel['statistics'].get('subscriberCount', '0'),
            'video_count': channel['statistics'].get('videoCount', '0'),
            'view_count': channel['statistics'].get('viewCount', '0'),
            'thumbnails': channel['snippet']['thumbnails'],
            'is_live': is_live,
            'live_stream_id': live_stream_id,
            'live_viewer_count': live_viewer_count,
        }
        
    except Exception as e:
        print(f"❌ Error fetching YouTube data: {e}")
        return None

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new app user - appears in Social Accounts section"""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        app_user = serializer.save()
        
        # If user has YouTube URL, fetch YouTube data
        youtube_data = None
        if app_user.youtube_url:
            print(f"🔍 User registered with YouTube URL: {app_user.youtube_url}")
            
            # Extract channel ID
            channel_id = extract_youtube_channel_id(app_user.youtube_url)
            if channel_id:
                print(f"🔍 Extracted channel ID: {channel_id}")
                
                # Get YouTube API key from settings
                api_key = getattr(settings, 'YOUTUBE_API_KEY', 'AIzaSyCyrLA3pmrWdRHQR7CymuODE5a6ISSRmGY')
                
                # Fetch YouTube data
                youtube_data = get_youtube_channel_data(channel_id, api_key)
                if youtube_data:
                    print(f"✅ YouTube data fetched successfully: {youtube_data['subscriber_count']} subscribers")
                else:
                    print("⚠️ Failed to fetch YouTube data")
            else:
                print("⚠️ Could not extract channel ID from YouTube URL")
        
        # Create a temporary User for JWT token generation
        temp_user = User.objects.create_user(
            username=f"temp_{app_user.id}_{app_user.email}",
            email=app_user.email,
            first_name=app_user.first_name,
            last_name=app_user.last_name,
            is_active=False  # Mark as inactive so it doesn't appear in admin
        )
        
        # Generate JWT tokens using temp user
        refresh = RefreshToken.for_user(temp_user)
        access_token = refresh.access_token
        
        # Prepare app user data
        user_data = UserSerializer(app_user).data
        
        # Add YouTube data to response if available
        if youtube_data:
            user_data['youtube_data'] = youtube_data
        
        return Response({
            'message': 'User registered successfully',
            'user': user_data,
            'token': str(access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user and return JWT tokens"""
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        # Check if it's an app user or admin user
        if 'app_user' in serializer.validated_data:
            app_user = serializer.validated_data['app_user']
            
            # Find or create temp user for JWT
            temp_user, created = User.objects.get_or_create(
                username=f"temp_{app_user.id}_{app_user.email}",
                defaults={
                    'email': app_user.email,
                    'first_name': app_user.first_name,
                    'last_name': app_user.last_name,
                    'is_active': False
                }
            )
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(temp_user)
            access_token = refresh.access_token
            
            # Prepare app user data
            user_data = UserSerializer(app_user).data
        else:
            # Admin user login
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            user_data = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_admin': True
            }
        
        return Response({
            'message': 'Login successful',
            'user': user_data,
            'token': str(access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get current user profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout user by blacklisting the refresh token"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_users_with_youtube(request):
    """Get all users who have added YouTube URLs for the explore page"""
    try:
        # Get all AppUsers who have YouTube URLs
        app_users = AppUser.objects.filter(
            youtube_url__isnull=False,
            youtube_url__gt='',  # Not empty
            is_active=True
        ).exclude(youtube_url='').order_by('-created_at')
        
        # Serialize the data
        users_data = []
        for user in app_users:
            users_data.append({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'youtube_url': user.youtube_url,
                'social_url': user.social_url or '',
                'created_at': user.created_at.isoformat() if user.created_at else None,
            })
        
        return Response(users_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def explore_users(request):
    """Get all users for the explore page - shows everyone including current user"""
    try:
        # Get all AppUsers (active and inactive)
        app_users = AppUser.objects.all().order_by('-created_at')
        
        # Get YouTube API key from settings
        api_key = getattr(settings, 'YOUTUBE_API_KEY', 'AIzaSyCyrLA3pmrWdRHQR7CymuODE5a6ISSRmGY')
        
        # Serialize the data with YouTube data
        users_data = []
        for user in app_users:
            user_data = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'youtube_url': user.youtube_url or '',
                'social_url': user.social_url or '',
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'is_active': user.is_active,
            }
            
            # If user has YouTube URL, fetch YouTube data
            if user.youtube_url:
                try:
                    channel_id = extract_youtube_channel_id(user.youtube_url)
                    if channel_id:
                        youtube_data = get_youtube_channel_data(channel_id, api_key)
                        if youtube_data:
                            user_data['youtube_data'] = youtube_data
                            print(f"✅ YouTube data fetched for {user.first_name}: {youtube_data['subscriber_count']} subscribers")
                        else:
                            print(f"⚠️ Failed to fetch YouTube data for {user.first_name}")
                    else:
                        print(f"⚠️ Could not extract channel ID for {user.first_name}")
                except Exception as e:
                    print(f"❌ Error fetching YouTube data for {user.first_name}: {e}")
            
            users_data.append(user_data)
        
        return Response(users_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_youtube_data(request):
    """Update YouTube data for the current user"""
    try:
        # Get the current user's YouTube URL
        user_email = request.user.email
        
        # Find the corresponding AppUser
        try:
            app_user = AppUser.objects.get(email=user_email)
        except AppUser.DoesNotExist:
            return Response({'error': 'AppUser not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not app_user.youtube_url:
            return Response({'error': 'No YouTube URL found for this user'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract channel ID
        channel_id = extract_youtube_channel_id(app_user.youtube_url)
        if not channel_id:
            return Response({'error': 'Could not extract channel ID from YouTube URL'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get YouTube API key from settings
        api_key = getattr(settings, 'YOUTUBE_API_KEY', 'AIzaSyCyrLA3pmrWdRHQR7CymuODE5a6ISSRmGY')
        
        # Fetch YouTube data
        youtube_data = get_youtube_channel_data(channel_id, api_key)
        if not youtube_data:
            return Response({'error': 'Failed to fetch YouTube data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Return the updated data
        user_data = UserSerializer(app_user).data
        user_data['youtube_data'] = youtube_data
        
        return Response({
            'message': 'YouTube data updated successfully',
            'user': user_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """Update user profile information"""
    try:
        # Get the current user's email
        user_email = request.user.email
        
        # Find the corresponding AppUser
        try:
            app_user = AppUser.objects.get(email=user_email)
        except AppUser.DoesNotExist:
            return Response({'error': 'AppUser not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Use the profile update serializer
        serializer = UserProfileUpdateSerializer(app_user, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Save the updated data
            updated_user = serializer.save()
            
            # If YouTube URL was updated, fetch new YouTube data
            youtube_data = None
            if 'youtube_url' in serializer.validated_data and updated_user.youtube_url:
                print(f"🔍 YouTube URL updated: {updated_user.youtube_url}")
                
                # Extract channel ID
                channel_id = extract_youtube_channel_id(updated_user.youtube_url)
                if channel_id:
                    print(f"🔍 Extracted channel ID: {channel_id}")
                    
                    # Get YouTube API key from settings
                    api_key = getattr(settings, 'YOUTUBE_API_KEY', 'AIzaSyCyrLA3pmrWdRHQR7CymuODE5a6ISSRmGY')
                    
                    # Fetch YouTube data
                    youtube_data = get_youtube_channel_data(channel_id, api_key)
                    if youtube_data:
                        print(f"✅ YouTube data fetched successfully: {youtube_data['subscriber_count']} subscribers")
                    else:
                        print("⚠️ Failed to fetch YouTube data")
                else:
                    print("⚠️ Could not extract channel ID from YouTube URL")
            
            # Prepare response data
            user_data = UserSerializer(updated_user).data
            
            # Add YouTube data if available
            if youtube_data:
                user_data['youtube_data'] = youtube_data
            
            return Response({
                'message': 'Profile updated successfully',
                'user': user_data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
def youtube_api_proxy(request):
    """Proxy for YouTube API calls to avoid CORS issues"""
    try:
        data = json.loads(request.body)
        url = data.get('url')
        
        if not url:
            return JsonResponse({'error': 'URL parameter is required'}, status=400)
        
        print(f"🔗 YouTube API Proxy: Making request to {url}")
        
        # Make the request to YouTube API with timeout
        response = requests.get(url, timeout=15)
        
        print(f"📊 YouTube API Proxy: Response status {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ YouTube API Proxy: Success - {len(response_data.get('items', []))} items")
            return JsonResponse(response_data)
        else:
            error_msg = f'YouTube API error: {response.status_code}'
            print(f"❌ YouTube API Proxy: {error_msg}")
            print(f"📄 Response text: {response.text[:200]}")
            
            return JsonResponse(
                {'error': error_msg, 'details': response.text},
                status=response.status_code
            )
            
    except requests.exceptions.Timeout:
        error_msg = "YouTube API request timed out"
        print(f"❌ YouTube API Proxy: {error_msg}")
        return JsonResponse({'error': error_msg}, status=408)
    except requests.exceptions.ConnectionError:
        error_msg = "Failed to connect to YouTube API"
        print(f"❌ YouTube API Proxy: {error_msg}")
        return JsonResponse({'error': error_msg}, status=503)
    except json.JSONDecodeError:
        error_msg = "Invalid JSON in request body"
        print(f"❌ YouTube API Proxy: {error_msg}")
        return JsonResponse({'error': error_msg}, status=400)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"❌ YouTube API Proxy: {error_msg}")
        return JsonResponse({'error': error_msg}, status=500)
