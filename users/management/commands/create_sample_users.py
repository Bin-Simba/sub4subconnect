from django.core.management.base import BaseCommand
from users.models import AppUser
from django.utils import timezone
import hashlib

class Command(BaseCommand):
    help = 'Create sample users with YouTube URLs for testing the explore page'

    def handle(self, *args, **options):
        # Sample users with popular YouTube channels (these are real channels)
        sample_users = [
            {
                'first_name': 'Mr',
                'last_name': 'Beast',
                'email': 'mrbeast@example.com',
                'youtube_url': 'https://youtube.com/@MrBeast',
                'social_url': 'https://twitter.com/MrBeast',
            },
            {
                'first_name': 'PewDiePie',
                'last_name': '',
                'email': 'pewdiepie@example.com',
                'youtube_url': 'https://youtube.com/@PewDiePie',
                'social_url': 'https://twitter.com/pewdiepie',
            },
            {
                'first_name': 'Mark',
                'last_name': 'Rober',
                'email': 'mark.rober@example.com',
                'youtube_url': 'https://youtube.com/@MarkRober',
                'social_url': 'https://twitter.com/MarkRober',
            },
            {
                'first_name': 'Marques',
                'last_name': 'Brownlee',
                'email': 'marques@example.com',
                'youtube_url': 'https://youtube.com/@mkbhd',
                'social_url': 'https://twitter.com/MKBHD',
            },
            {
                'first_name': 'Linus',
                'last_name': 'Sebastian',
                'email': 'linus@example.com',
                'youtube_url': 'https://youtube.com/@LinusTechTips',
                'social_url': 'https://twitter.com/LinusTech',
            },
            {
                'first_name': 'Dude',
                'last_name': 'Perfect',
                'email': 'dudeperfect@example.com',
                'youtube_url': 'https://youtube.com/@DudePerfect',
                'social_url': 'https://twitter.com/DudePerfect',
            },
            {
                'first_name': 'Kurzgesagt',
                'last_name': '',
                'email': 'kurzgesagt@example.com',
                'youtube_url': 'https://youtube.com/@kurzgesagt',
                'social_url': 'https://twitter.com/kurzgesagt',
            },
            {
                'first_name': 'Veritasium',
                'last_name': '',
                'email': 'veritasium@example.com',
                'youtube_url': 'https://youtube.com/@veritasium',
                'social_url': 'https://twitter.com/veritasium',
            },
        ]

        created_count = 0
        for user_data in sample_users:
            # Check if user already exists
            if not AppUser.objects.filter(email=user_data['email']).exists():
                # Create a simple password hash for the sample user
                password_hash = hashlib.sha256(f"password123{user_data['email']}".encode()).hexdigest()
                
                user = AppUser.objects.create(
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    email=user_data['email'],
                    youtube_url=user_data['youtube_url'],
                    social_url=user_data['social_url'],
                    password_hash=password_hash,
                    is_active=True,
                    created_at=timezone.now(),
                    updated_at=timezone.now(),
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {user.first_name} {user.last_name} ({user.email})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'User already exists: {user_data["email"]}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample users')
        )
        
        total_users = AppUser.objects.filter(youtube_url__isnull=False).exclude(youtube_url='').count()
        self.stdout.write(
            self.style.SUCCESS(f'Total users with YouTube URLs: {total_users}')
        )
