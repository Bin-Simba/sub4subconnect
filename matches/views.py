from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Connection
from users.models import AppUser

# Create your views here.

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_connections(request, user_email):
    """Get all connections for a specific user"""
    try:
        # Get the user
        user = AppUser.objects.filter(email=user_email).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get all accepted connections (both sent and received)
        sent_connections = Connection.objects.filter(
            from_user=user, 
            status='accepted'
        ).select_related('to_user')
        
        received_connections = Connection.objects.filter(
            to_user=user, 
            status='accepted'
        ).select_related('from_user')
        
        # Combine and format connections
        connections_data = []
        
        # Add sent connections
        for connection in sent_connections:
            connections_data.append({
                'id': connection.id,
                'connected_user': {
                    'id': connection.to_user.id,
                    'first_name': connection.to_user.first_name,
                    'last_name': connection.to_user.last_name,
                    'email': connection.to_user.email,
                    'youtube_url': connection.to_user.youtube_url,
                    'social_url': connection.to_user.social_url,
                },
                'connection_type': 'sent',
                'created_at': connection.created_at.isoformat(),
                'is_mutual': connection.is_mutual,
            })
        
        # Add received connections
        for connection in received_connections:
            connections_data.append({
                'id': connection.id,
                'connected_user': {
                    'id': connection.from_user.id,
                    'first_name': connection.from_user.first_name,
                    'last_name': connection.from_user.last_name,
                    'email': connection.from_user.email,
                    'youtube_url': connection.from_user.youtube_url,
                    'social_url': connection.from_user.social_url,
                },
                'connection_type': 'received',
                'created_at': connection.created_at.isoformat(),
                'is_mutual': connection.is_mutual,
            })
        
        # Sort by creation date (most recent first)
        connections_data.sort(key=lambda x: x['created_at'], reverse=True)
        
        return Response({
            'user_id': user.id,
            'user_email': user.email,
            'total_connections': len(connections_data),
            'connections': connections_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
