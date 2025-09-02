from django.core.management.base import BaseCommand
from users.models import AppUser
from matches.models import Connection
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Create sample connections between users for testing'

    def handle(self, *args, **options):
        # Get all users with YouTube URLs
        users = AppUser.objects.filter(
            youtube_url__isnull=False
        ).exclude(youtube_url='')
        
        if users.count() < 2:
            self.stdout.write(
                self.style.WARNING('Need at least 2 users to create connections. Run create_sample_users first.')
            )
            return
        
        # Create some sample connections
        connections_created = 0
        
        # Create connections between different users
        for i, from_user in enumerate(users):
            # Connect to 2-3 other users
            for j in range(2, 4):
                to_user_index = (i + j) % users.count()
                to_user = users[to_user_index]
                
                # Skip if it's the same user
                if from_user == to_user:
                    continue
                
                # Check if connection already exists
                if not Connection.objects.filter(
                    from_user=from_user,
                    to_user=to_user
                ).exists():
                    # Create connection with random status
                    status = random.choice(['pending', 'accepted'])
                    
                    connection = Connection.objects.create(
                        from_user=from_user,
                        to_user=to_user,
                        status=status,
                        message=f"Hey {to_user.first_name}! Let's connect and grow together! 🚀"
                    )
                    
                    connections_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created connection: {from_user.first_name} → {to_user.first_name} ({status})'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {connections_created} sample connections')
        )
        
        # Show connection statistics
        total_connections = Connection.objects.count()
        accepted_connections = Connection.objects.filter(status='accepted').count()
        pending_connections = Connection.objects.filter(status='pending').count()
        
        self.stdout.write(f'Total connections: {total_connections}')
        self.stdout.write(f'Accepted connections: {accepted_connections}')
        self.stdout.write(f'Pending connections: {pending_connections}')
