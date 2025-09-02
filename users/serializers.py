from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from allauth.socialaccount.models import SocialAccount
import re
from urllib.parse import urlparse
from .models import User, AppUser

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for app user registration - creates AppUser entries"""
    password = serializers.CharField(
        write_only=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = AppUser
        fields = ('email', 'first_name', 'last_name', 'password', 'password_confirm', 'social_url', 'youtube_url')
        extra_kwargs = {
            'first_name': {'required': True},
            'email': {'required': True},
            'social_url': {'required': False, 'allow_blank': True},
            'youtube_url': {'required': False, 'allow_blank': True},
        }
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def _extract_provider_info(self, url):
        """Extract provider and uid from social URL"""
        if not url:
            return None, None
            
        parsed = urlparse(url.lower())
        domain = parsed.netloc.replace('www.', '')
        
        # YouTube patterns
        if 'youtube.com' in domain:
            # Handle different YouTube URL formats
            if '/channel/' in parsed.path:
                uid = parsed.path.split('/channel/')[-1].split('/')[0]
            elif '/@' in parsed.path:
                uid = parsed.path.split('/@')[-1].split('/')[0]
            elif '/c/' in parsed.path:
                uid = parsed.path.split('/c/')[-1].split('/')[0]
            elif '/user/' in parsed.path:
                uid = parsed.path.split('/user/')[-1].split('/')[0]
            else:
                uid = parsed.path.strip('/')
            return 'youtube', uid
            
        elif 'youtu.be' in domain:
            return 'youtube', parsed.path.strip('/')
            
        # Twitter/X patterns
        elif domain in ['twitter.com', 'x.com']:
            uid = parsed.path.strip('/').split('/')[0]
            return 'twitter', uid
            
        # Instagram patterns
        elif 'instagram.com' in domain:
            uid = parsed.path.strip('/').split('/')[0]
            return 'instagram', uid
            
        # TikTok patterns
        elif 'tiktok.com' in domain:
            if '/@' in parsed.path:
                uid = parsed.path.split('/@')[-1].split('/')[0]
            else:
                uid = parsed.path.strip('/')
            return 'tiktok', uid
            
        # Generic fallback - use domain as provider
        else:
            provider = domain.split('.')[0] if '.' in domain else domain
            uid = parsed.path.strip('/') or parsed.netloc
            return provider, uid
    
    def create(self, validated_data):
        """Create app user - appears only in Social Accounts section"""
        # Extract social URLs before removing from validated_data
        social_url = validated_data.get('social_url', '')
        youtube_url = validated_data.get('youtube_url', '')
        
        # Remove password_confirm and hash the password
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        validated_data['password_hash'] = make_password(password)
        
        # Create AppUser (appears in Social Accounts section)
        app_user = AppUser.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data.get('last_name', ''),
            password_hash=validated_data['password_hash'],
            social_url=social_url,
            youtube_url=youtube_url
        )
        
        # Create SocialAccount entries for provided URLs
        social_accounts_created = []
        
        # Handle YouTube URL
        if youtube_url:
            provider, uid = self._extract_provider_info(youtube_url)
            if provider and uid:
                try:
                    social_account = SocialAccount.objects.create(
                        user_id=1,  # Use a dummy user ID since we don't create User entries
                        provider='youtube',
                        uid=uid,
                        extra_data={
                            'url': youtube_url,
                            'platform': 'youtube',
                            'username': uid,
                            'email': app_user.email,
                            'first_name': app_user.first_name,
                            'last_name': app_user.last_name,
                            'app_user_id': app_user.id
                        }
                    )
                    social_accounts_created.append(social_account)
                except Exception as e:
                    print(f"Error creating YouTube social account: {e}")
        
        # Handle general social URL
        if social_url:
            provider, uid = self._extract_provider_info(social_url)
            if provider and uid and provider != 'youtube':
                try:
                    social_account = SocialAccount.objects.create(
                        user_id=1,  # Use a dummy user ID since we don't create User entries
                        provider=provider,
                        uid=uid,
                        extra_data={
                            'url': social_url,
                            'platform': provider,
                            'username': uid,
                            'email': app_user.email,
                            'first_name': app_user.first_name,
                            'last_name': app_user.last_name,
                            'app_user_id': app_user.id
                        }
                    )
                    social_accounts_created.append(social_account)
                except Exception as e:
                    print(f"Error creating {provider} social account: {e}")
        
        return app_user

class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        from django.contrib.auth.hashers import check_password
        
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            try:
                # Check if it's an app user
                app_user = AppUser.objects.get(email=email)
                if check_password(password, app_user.password_hash):
                    if app_user.is_active:
                        attrs['app_user'] = app_user
                    else:
                        raise serializers.ValidationError('User account is disabled')
                else:
                    raise serializers.ValidationError('Invalid credentials')
            except AppUser.DoesNotExist:
                # Fallback to admin user authentication
                user = authenticate(username=email, password=password)
                if not user:
                    raise serializers.ValidationError('Invalid credentials')
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled')
                attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs

class UserSerializer(serializers.ModelSerializer):
    """Serializer for app user data"""
    class Meta:
        model = AppUser
        fields = ('id', 'email', 'first_name', 'last_name', 'social_url', 'youtube_url', 'created_at')
        read_only_fields = ('id', 'created_at')

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile information"""
    class Meta:
        model = AppUser
        fields = ('first_name', 'last_name', 'social_url', 'youtube_url')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'social_url': {'required': False, 'allow_blank': True},
            'youtube_url': {'required': False, 'allow_blank': True},
        }
    
    def validate_social_url(self, value):
        """Validate social URL format"""
        if value and value.strip():
            # Basic URL validation
            if not value.startswith(('http://', 'https://')):
                raise serializers.ValidationError("Social URL must start with http:// or https://")
        return value
    
    def validate_youtube_url(self, value):
        """Validate YouTube URL format"""
        if value and value.strip():
            # Basic YouTube URL validation
            if not any(domain in value.lower() for domain in ['youtube.com', 'youtu.be']):
                raise serializers.ValidationError("Please enter a valid YouTube URL")
        return value
