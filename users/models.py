from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom User model - primarily for admin users"""
    email = models.EmailField(unique=True)
    social_url = models.URLField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="User's main social profile URL (Twitter, Instagram, etc.)"
    )
    youtube_url = models.URLField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="User's YouTube channel URL"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return f"{self.email} ({self.first_name} {self.last_name})"
    
    class Meta:
        verbose_name = "Admin User"
        verbose_name_plural = "Admin Users"

class AppUser(models.Model):
    """App users model - appears in Social Accounts section"""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True)
    password_hash = models.CharField(max_length=128)  # Store hashed password
    social_url = models.URLField(max_length=200, blank=True)
    youtube_url = models.URLField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.email} - {self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = "App User"
        verbose_name_plural = "App Users"
